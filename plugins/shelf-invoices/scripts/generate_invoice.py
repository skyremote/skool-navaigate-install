#!/usr/bin/env python3
"""Fill the house invoice template from the member's company.json and one invoice spec, then render the PDF.

    python3 generate_invoice.py spec.json OUT.docx --company company.json [--pdf]

Most members never call this file directly: `shelf-invoices make spec.json` does it, chooses the number and the
file name, and checks the result. The design (logo slot, Poppins, the kicker and big title, Bill to / Invoice
details, the scope table, the total band, the VAT, bank and tax rows and the legal footer) lives in
assets/template_v1.docx. Every name, number and line of wording comes from the two JSON files.

spec.json (one invoice; strings unless noted):
  invoice_number   "ACME-004"         optional with `make`: it takes the highest number used + 1
  date             "2026-10-26"       ISO date; today if left out
  title            "Workshop delivery"                   the big heading
  subtitle         "Bristol · 20–22 October 2026"        "" to drop the line
  client_name      "Northwind Bakery Ltd"
  client_address   "22 Harbour Road, Bristol BS8 4RU"   a string, or a list of lines
  client_vat_id    "GB000000000"      needed for reverse_charge_eu, shown under the client
  requester        "Sam Lee"          "" to drop
  client_extra     "Cost centre 12"   "" to drop
  po_number        "NW-0042"          quote it whenever the client gave one
  po_extra         "Supplier ID 1234" shown after the PO, "" to drop
  currency         "GBP" | "EUR" | "USD" | any ISO code   follows the PO; company default if left out
  greeting         "Dear Sam,"        default from the requester's first name
  intro            "Our invoice for the workshop."
  items            [{"title": "...", "description": "...", "amount": 3600},
                    {"title": "...", "quantity": 3, "unit": "days", "unit_price": 1200}]
  total_note       "(all-in, including travel)"
  service_date     "20–22 October 2026"   the date or period of the work
  vat              "standard" | "reverse_charge_eu" | "outside_scope" | "outside_eu"
                   | "domestic_reverse_charge" | "not_registered"      company default if left out
  vat_rate         20                 standard only; company default if left out
  vat_label, vat_text                 optional one-off wording for this invoice
  payment_days     14                 or payment_terms: the whole sentence, word for word

company.json: see references/settings.md, or run `shelf-invoices init`.
"""
import copy
import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from lxml import etree

HERE = Path(__file__).resolve().parent
PACK = HERE.parent
TEMPLATE = PACK / "assets" / "template_v1.docx"
PLACEHOLDER_LOGO = PACK / "assets" / "placeholder_logo.png"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W}
SYMBOL = {"GBP": "£", "EUR": "€", "USD": "$"}
FIELD = re.compile(r"\{\{(\w+)\}\}")
LOGO_BOX = 914400  # EMU: the house logo slot is one inch wide

VAT_MODES = ("standard", "reverse_charge_eu", "outside_scope", "outside_eu", "domestic_reverse_charge",
             "not_registered")
# Neutral English defaults. Members change the wording in company.json "vat_wording"; their accountant decides
# which mode applies. Fields: {rate} {net} {client_vat_id} {country}.
DEFAULT_VAT_WORDING = {
    "standard": {"label": "VAT {rate}%: ", "text": "charged on the net amount of {net}"},
    "reverse_charge_eu": {"label": "EU business customer: ",
                          "text": "reverse charge, no VAT charged; the customer accounts for the VAT"},
    "outside_scope": {"label": "Customer outside {country}: ",
                      "text": "no VAT charged (place of supply outside {country}); the customer accounts for any "
                              "local tax"},
    "outside_eu": {"label": "Customer outside the EU: ",
                   "text": "no VAT charged (place of supply outside the EU); the customer accounts for any local tax"},
    "domestic_reverse_charge": {"label": "Domestic reverse charge: ",
                                "text": "VAT at {rate}% not charged; the customer accounts for the VAT to the tax "
                                        "authority"},
    "not_registered": {"label": "VAT: ", "text": "not charged; the supplier is not registered for VAT"},
}

COMPANY_DEFAULTS = {
    "company_name": "",
    "address": [],
    "country": "",
    "phone": "",
    "email": "",
    "website": "",
    "vat_id": "",
    "vat_id_label": "VAT ID",
    "tax_number": "",
    "tax_number_label": "Tax number",
    "legal_footer": [],
    "bank": {"bank_name": "", "account_name": "", "iban": "", "bic": "", "sort_code": "", "account_number": ""},
    "bank_line": "",
    "invoice_prefix": "INV-",
    "number_digits": 3,
    "currency": "GBP",
    "payment_days": 14,
    "footer_note": "",
    "signatory": "",
    "closing": "Best,",
    "logo": "logo.png",
    "vat_mode": "standard",
    "vat_rate": 20,
    "vat_wording": {},
    "service_date_label": "Service date",
    "client_vat_id_label": "VAT ID",
    "date_short_format": "%d.%m.%Y",
}


class InvoiceError(ValueError):
    """A problem the member (or Claude) has to fix before an invoice can be made."""


# ---------------------------------------------------------------- money and text

def dec(value, what="amount"):
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        raise InvoiceError("%s is not a number: %r" % (what, value))


def money(x):
    return "{:,.2f}".format(Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def cents(x):
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def plain_number(x):
    s = format(Decimal(x).normalize(), "f")
    return s


def join(*parts, sep=" · "):
    return sep.join(p.strip() for p in parts if p and str(p).strip())


def lines(value):
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    return [s.strip() for s in str(value or "").split("\n") if s.strip()]


# ---------------------------------------------------------------- settings

def load_company(path):
    path = Path(path)
    if not path.exists():
        raise InvoiceError("No company settings at %s. Run: shelf-invoices init <books folder>" % path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise InvoiceError("%s is not valid JSON: %s" % (path, e))
    company = copy.deepcopy(COMPANY_DEFAULTS)
    for key, value in data.items():
        if key == "bank" and isinstance(value, dict):
            company["bank"].update(value)
        else:
            company[key] = value
    wording = copy.deepcopy(DEFAULT_VAT_WORDING)
    for mode, w in (data.get("vat_wording") or {}).items():
        wording.setdefault(mode, {}).update(w)
    company["vat_wording"] = wording
    company["_dir"] = str(path.parent)
    return company


def bank_line(c):
    if c.get("bank_line"):
        return c["bank_line"]
    b = c.get("bank") or {}
    return join(b.get("bank_name", ""),
                ("Account name " + b["account_name"]) if b.get("account_name") else "",
                ("IBAN " + b["iban"]) if b.get("iban") else "",
                ("BIC " + b["bic"]) if b.get("bic") else "",
                ("Sort code " + b["sort_code"]) if b.get("sort_code") else "",
                ("Account " + b["account_number"]) if b.get("account_number") else "")


def logo_path(c):
    if not c.get("logo"):
        return None
    p = Path(str(c["logo"])).expanduser()
    if not p.is_absolute():
        p = Path(c.get("_dir", ".")) / p
    return p


def check_company(c):
    """Return (missing, warnings). Missing items stop an invoice; warnings are printed."""
    missing, warnings = [], []
    for key in ("company_name", "email", "signatory", "invoice_prefix"):
        if not str(c.get(key, "")).strip():
            missing.append(key)
    if not lines(c.get("address")):
        missing.append("address")
    if not bank_line(c):
        missing.append("bank (iban or account_number, or bank_line)")
    if c.get("vat_mode") not in VAT_MODES:
        missing.append("vat_mode (one of %s)" % ", ".join(VAT_MODES))
    if c.get("vat_mode") != "not_registered" and not c.get("vat_id"):
        missing.append("vat_id (or set vat_mode to not_registered)")
    for key in ("phone", "website", "legal_footer", "country"):
        if not c.get(key):
            warnings.append("%s is empty (optional, but most invoices show it)" % key)
    lp = logo_path(c)
    if not lp or not lp.exists():
        warnings.append("logo not found (%s): the neutral placeholder logo will be used" % (lp or "none set"))
    elif lp.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        missing.append("logo must be a PNG file (%s)" % lp)
    flat = json.dumps({k: v for k, v in c.items() if not k.startswith("_")})
    if "SAMPLE" in flat and not c.get("_sample"):
        warnings.append("these settings still contain SAMPLE values: replace them with your own before you invoice")
    return missing, warnings


# ---------------------------------------------------------------- numbering

def number_series(company, code=""):
    prefix = str(company.get("invoice_prefix", ""))
    return prefix + (code.strip().upper() + "-" if code and code.strip() else "")


def used_numbers(books, series):
    """Every invoice number of this series found in the books folder (file names and saved specs)."""
    pat = re.compile(r"^%s(\d+)(?:_v\d+)?(?:\.spec)?$" % re.escape(series))
    found = {}
    for p in Path(books).rglob("*"):
        if p.is_file() and p.suffix.lower() in (".pdf", ".docx", ".json"):
            m = pat.match(p.stem)
            if m:
                found.setdefault(int(m.group(1)), []).append(p)
    return found


def next_number(books, company, code=""):
    series = number_series(company, code)
    used = used_numbers(books, series)
    n = max(used) + 1 if used else 1
    digits = int(company.get("number_digits") or 3)
    return "%s%0*d" % (series, digits, n), (max(used) if used else None)


# ---------------------------------------------------------------- values

def parse_date(value):
    if not value:
        return datetime.date.today()
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        raise InvoiceError("date must be YYYY-MM-DD, got %r" % value)


def build(company, spec):
    """Work out every placeholder value. Returns (values, item_values, totals)."""
    c = company
    for key in ("invoice_number", "title", "client_name", "items"):
        if not spec.get(key):
            raise InvoiceError("The spec needs %s." % key)
    cur = str(spec.get("currency") or c.get("currency") or "GBP").upper()
    sym = SYMBOL.get(cur, cur + " ")
    mode = spec.get("vat") or c.get("vat_mode") or "standard"
    if mode not in VAT_MODES:
        raise InvoiceError("vat must be one of %s, got %r" % (", ".join(VAT_MODES), mode))
    rate = dec(spec.get("vat_rate", c.get("vat_rate", 20)), "vat_rate")
    client_vat = str(spec.get("client_vat_id", "")).strip()
    if mode == "reverse_charge_eu" and not client_vat:
        raise InvoiceError("Reverse charge needs the customer's VAT ID: add client_vat_id to the spec.")
    if mode == "standard" and c.get("vat_mode") == "not_registered":
        raise InvoiceError("Your settings say you are not VAT registered, so you cannot charge VAT (vat: standard).")

    items = []
    for n, it in enumerate(spec["items"], 1):
        if not it.get("title"):
            raise InvoiceError("Item %d needs a title." % n)
        desc = str(it.get("description", "")).strip()
        if it.get("amount") not in (None, ""):
            amount = dec(it["amount"], "item %d amount" % n)
        elif it.get("quantity") not in (None, "") and it.get("unit_price") not in (None, ""):
            q, price = dec(it["quantity"], "quantity"), dec(it["unit_price"], "unit_price")
            amount = q * price
            unit = str(it.get("unit", "")).strip()
            how = "%s%s × %s%s" % (plain_number(q), " " + unit if unit else "", sym, money(price))
            desc = join(desc, how, sep="; ")
        else:
            raise InvoiceError("Item %d needs an amount, or a quantity and a unit_price." % n)
        items.append({"item_no": str(n), "item_title": str(it["title"]), "item_description": desc,
                      "item_amount": money(amount), "_amount": cents(amount)})

    net = sum((i["_amount"] for i in items), Decimal("0"))
    vat_amount = cents(net * rate / 100) if mode == "standard" else Decimal("0")
    gross = net + vat_amount

    fields = {"rate": plain_number(rate), "net": sym + money(net), "client_vat_id": client_vat,
              "country": c.get("country") or "our country"}
    wording = c["vat_wording"].get(mode) or DEFAULT_VAT_WORDING[mode]
    try:
        vat_label = spec.get("vat_label") or wording["label"].format(**fields)
        vat_text = spec.get("vat_text") or wording["text"].format(**fields)
    except (KeyError, IndexError) as e:
        raise InvoiceError("vat_wording for %s uses an unknown field %s" % (mode, e))

    total_note = str(spec.get("total_note", "")).strip()
    if mode == "standard":
        total_note = join(total_note, "(incl. %s%% VAT)" % plain_number(rate), sep=" ")

    d = parse_date(spec.get("date"))
    number = str(spec["invoice_number"]).strip()
    po = str(spec.get("po_number", "")).strip()
    po_extra = str(spec.get("po_extra", "")).strip()
    if po_extra and not po_extra.startswith(("·", ",", "(")):
        po_extra = " · " + po_extra
    elif po_extra:
        po_extra = " " + po_extra
    requester = str(spec.get("requester", "")).strip()
    client_extra = join(str(spec.get("client_extra", "")),
                        ("%s %s" % (c.get("client_vat_id_label", "VAT ID"), client_vat)) if client_vat else "")
    if spec.get("payment_terms"):
        terms = str(spec["payment_terms"]).strip()
    else:
        days = int(spec.get("payment_days") or c.get("payment_days") or 14)
        terms = "Payment terms: net %d days%s. Please quote %s with payment." % (
            days, (", per purchase order " + po) if po else "", number)
    terms = join(terms, str(c.get("footer_note", "")), sep=" ")
    service = str(spec.get("service_date", "")).strip()
    legal = c.get("legal_footer") or []
    legal = join(*lines(legal)) if isinstance(legal, (list, tuple)) else str(legal)

    values = {
        "signatory": str(c.get("signatory", "")),
        "company_name": str(c.get("company_name", "")),
        "company_address": join(*lines(c.get("address"))),
        "contact_line": join(("T " + c["phone"]) if c.get("phone") else "", c.get("email", "")),
        "web_line": join(c.get("website", ""),
                         ("%s %s" % (c.get("vat_id_label", "VAT ID"), c["vat_id"])) if c.get("vat_id") else ""),
        "title": str(spec["title"]),
        "subtitle": str(spec.get("subtitle", "")),
        "client_name": str(spec["client_name"]),
        "client_address": join(*lines(spec.get("client_address", "")), sep=", "),
        "requester": requester,
        "client_extra": client_extra,
        "date_long": "%d %s" % (d.day, d.strftime("%B %Y")),
        "date_short": d.strftime(c.get("date_short_format") or "%d.%m.%Y"),
        "invoice_number": number,
        "currency": cur,
        "po_number": po,
        "po_extra": po_extra,
        "greeting": str(spec.get("greeting") or ("Dear %s," % requester.split()[0] if requester else "Hello,")),
        "intro": str(spec.get("intro") or "Our invoice for the work below."),
        "total_note": total_note,
        "total": sym + money(gross),
        "service_line": ("%s: %s." % (c.get("service_date_label", "Service date"), service.rstrip("."))
                         if service else ""),
        "vat_label": vat_label,
        "vat_text": vat_text,
        "vat_row_amount": sym + money(vat_amount if mode == "standard" else gross),
        "bank_line": bank_line(c),
        "tax_line": join(("%s %s" % (c.get("tax_number_label", "Tax number"), c["tax_number"]))
                         if c.get("tax_number") else "",
                         ("%s %s" % (c.get("vat_id_label", "VAT ID"), c["vat_id"])) if c.get("vat_id") else ""),
        "payment_terms": terms,
        "closing": str(c.get("closing") or "Best,"),
        "legal_footer": legal,
    }
    totals = {"currency": cur, "symbol": sym, "net": net, "vat": vat_amount, "gross": gross, "vat_mode": mode,
              "date": d, "number": number}
    return values, items, totals


# ---------------------------------------------------------------- the document

def _text(el):
    return "".join(el.xpath(".//w:t/text()", namespaces=NS))


def _fill(root, values):
    for t in root.iter("{%s}t" % W):
        if t.text and "{{" in t.text:
            def sub(m):
                if m.group(1) not in values:
                    raise InvoiceError("The template has a field this pack does not know: {{%s}}" % m.group(1))
                return values[m.group(1)]
            t.text = FIELD.sub(sub, t.text)


def _paragraph_with(root, field):
    for p in root.iter("{%s}p" % W):
        if "{{%s}}" % field in _text(p):
            return p
    return None


def _drop(el):
    if el is not None and el.getparent() is not None:
        el.getparent().remove(el)


def _tidy_requester(doc, values):
    p = _paragraph_with(doc, "requester")
    if p is None:
        return
    if not values["requester"] and not values["client_extra"]:
        _drop(p)
        return
    runs = p.findall("{%s}r" % W)
    br_index = next((i for i, r in enumerate(runs) if r.find("{%s}br" % W) is not None), None)
    if br_index is None:
        return
    if not values["requester"]:
        for r in runs[:br_index + 1]:
            _drop(r)
    elif not values["client_extra"]:
        for r in runs[br_index:]:
            _drop(r)


def _swap_logo(doc, parts, logo_bytes):
    if logo_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        raise InvoiceError("The logo must be a PNG file.")
    lw, lh = int.from_bytes(logo_bytes[16:20], "big"), int.from_bytes(logo_bytes[20:24], "big")
    cx, cy = LOGO_BOX, int(LOGO_BOX * lh / lw)
    if cy > LOGO_BOX:  # a tall logo: fit the height instead
        cx, cy = int(LOGO_BOX * lw / lh), LOGO_BOX
    for tag in ("{%s}extent" % WP, "{%s}ext" % A):
        for ext in doc.iter(tag):
            if ext.get("cx") and ext.get("cy"):
                ext.set("cx", str(cx))
                ext.set("cy", str(cy))
    parts["word/media/image1.png"] = logo_bytes


def fill_docx(values, items, out, logo_bytes=None, template=TEMPLATE):
    """Write the filled .docx. Refuses to overwrite. Returns the list of checks that failed (empty = clean)."""
    out = Path(out)
    if out.exists():
        raise InvoiceError("Refusing to overwrite %s: make a new version (_v2) instead." % out)
    with zipfile.ZipFile(template) as zi:
        infos = zi.infolist()
        parts = {i.filename: zi.read(i.filename) for i in infos}
    doc = etree.fromstring(parts["word/document.xml"])

    # Multi-line invoices: clone the item row once per item.
    row = next(r for r in doc.iter("{%s}tr" % W) if "{{item_title}}" in _text(r))
    parent, idx = row.getparent(), row.getparent().index(row)
    parent.remove(row)
    for n, item in enumerate(items):
        clone = copy.deepcopy(row)
        if not item["item_description"]:
            _drop(_paragraph_with(clone, "item_description"))
        _fill(clone, {k: v for k, v in item.items() if not k.startswith("_")})
        parent.insert(idx + n, clone)

    # Lines that disappear when they have nothing to say.
    for field in ("subtitle", "service_line", "bank_line", "tax_line"):
        if not values.get(field):
            _drop(_paragraph_with(doc, field))
    if not values["po_number"] and not values["po_extra"]:
        _drop(_paragraph_with(doc, "po_number"))
    _tidy_requester(doc, values)

    _fill(doc, values)
    if logo_bytes:
        _swap_logo(doc, parts, logo_bytes)
    parts["word/document.xml"] = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
    foot = etree.fromstring(parts["word/footer1.xml"])
    _fill(foot, values)
    parts["word/footer1.xml"] = etree.tostring(foot, xml_declaration=True, encoding="UTF-8", standalone=True)

    problems = check_parts(parts, values["currency"])
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in infos:
            zo.writestr(info, parts[info.filename])
    return problems


def check_parts(parts, currency):
    """The house checks on the filled XML: no field left unfilled, no other currency's sign left behind."""
    problems = []
    text = ""
    for name in ("word/document.xml", "word/footer1.xml"):
        text += " ".join(etree.fromstring(parts[name]).xpath("//w:t/text()", namespaces=NS)) + " "
    left = sorted(set(FIELD.findall(text)))
    if left:
        problems.append("fields left unfilled: " + ", ".join(left))
    mine = SYMBOL.get(currency)
    for cur, sign in SYMBOL.items():
        if sign != mine and sign in text:
            problems.append("a %s sign (%s) is on a %s invoice" % (cur, sign, currency))
    return problems


# ---------------------------------------------------------------- the PDF

def find_soffice():
    for cand in (shutil.which("soffice"), shutil.which("libreoffice"),
                 "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if cand and Path(cand).exists():
            return cand
    return None


def render_pdf(docx):
    """Convert with LibreOffice. Returns the PDF path, or None when LibreOffice is not installed."""
    soffice = find_soffice()
    if not soffice:
        return None
    docx = Path(docx)
    profile = Path(tempfile.mkdtemp(prefix="shelf-invoices-lo-"))  # own profile: works while LibreOffice is open
    try:
        subprocess.run([soffice, "-env:UserInstallation=%s" % profile.as_uri(), "--headless", "--convert-to", "pdf",
                        "--outdir", str(docx.parent), str(docx)], check=True, capture_output=True, timeout=180)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = docx.with_suffix(".pdf")
    return pdf if pdf.exists() else None


def pdf_pages(pdf):
    data = Path(pdf).read_bytes()
    counts = [int(n) for n in re.findall(rb"/Type\s*/Pages\b[^>]*?/Count\s+(\d+)", data)]
    counts += [int(n) for n in re.findall(rb"/Count\s+(\d+)[^>]*?/Type\s*/Pages\b", data)]
    if counts:
        return max(counts)
    return len(re.findall(rb"/Type\s*/Page\b", data))


def preview_png(pdf):
    """First page as a PNG beside the PDF, so Claude (or you) can look at it. None if no converter is found."""
    pdf = Path(pdf)
    png = pdf.with_suffix(".png")
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-singlefile", str(pdf), str(png.with_suffix(""))],
                       check=True, capture_output=True)
    elif shutil.which("sips"):
        subprocess.run(["sips", "-s", "format", "png", str(pdf), "--out", str(png)], check=True, capture_output=True)
    else:
        return None
    return png if png.exists() else None


# ---------------------------------------------------------------- stand-alone use

def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Fill the invoice template from company.json and spec.json.")
    p.add_argument("spec", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--company", type=Path, required=True)
    p.add_argument("--pdf", action="store_true")
    a = p.parse_args(argv)
    try:
        company = load_company(a.company)
        values, items, totals = build(company, json.loads(a.spec.read_text(encoding="utf-8")))
        lp = logo_path(company)
        problems = fill_docx(values, items, a.out, lp.read_bytes() if lp and lp.exists() else None)
    except InvoiceError as e:
        print("Stopped: %s" % e, file=sys.stderr)
        return 1
    print("Wrote %s: %s net %s, VAT %s, total %s" % (a.out, totals["currency"], money(totals["net"]),
                                                     money(totals["vat"]), money(totals["gross"])))
    for prob in problems:
        print("CHECK FAILED: " + prob)
    if a.pdf:
        pdf = render_pdf(a.out)
        print("PDF: %s" % pdf if pdf else "No PDF: install LibreOffice for the PDF (https://www.libreoffice.org).")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
