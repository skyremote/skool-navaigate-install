#!/usr/bin/env python3
"""Turn a filled house-design invoice (.docx) into the clean, placeholder template this pack ships.

    python3 make_clean_template.py SOURCE.docx OUT.docx [--logo LOGO.png]

How it works: the house design keeps every piece of text in its own run (<w:t>). This script walks the runs in
document order and replaces each variable run with a {{placeholder}}, by POSITION. The fixed labels ("Bill to",
"Invoice details", "Total due" and so on) are checked as anchors, so a source in a different layout is refused
instead of being half cleaned. The script therefore holds no company, client or invoice text of its own.

It also: swaps word/media/image1.png for a neutral logo, renames the picture, removes docProps/thumbnail.jpeg and
customXml/ with every reference to them, empties the title, author and description in docProps/core.xml, and then
proves that no text from the source's variable runs survives in any part of the output.

Needs Python 3.9+ and lxml (python3 -m pip install --user lxml).
"""
import argparse
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

HERE = Path(__file__).resolve().parent
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"


def keep(label):
    return ("keep", label)


def put(text):
    return ("put", text)


# Every <w:t> in word/document.xml, in order. keep() = a fixed label that must match; put() = the new text.
DOCUMENT = [
    put("{{signatory}}"), put("{{company_name}}"), put("{{company_address}}"), put("{{contact_line}}"),
    put("{{web_line}}"),
    keep("Invoice"), put("{{title}}"), put("{{subtitle}}"),
    keep("Bill to"), put("{{client_name}}"), put("{{client_address}}"),
    keep("Requester: "), put("{{requester}}"), put("{{client_extra}}"),
    keep("Invoice details"), keep("Date  "), put("{{date_long}}"), keep("Invoice no.  "), put("{{invoice_number}}"),
    keep("Currency  "), put("{{currency}}"),
    keep("Purchase order: "), put("{{po_number}}"), put("{{po_extra}}"),
    put("{{greeting}}"), put("{{intro}}"),
    keep("#"), keep("Scope"), put("Amount ({{currency}})"),
    put("{{item_no}}"), put("{{item_title}}"), put("{{item_description}}"), put("{{item_amount}}"),
    keep("Total due "), put("{{total_note}}"), put("{{total}}"),
    put("{{service_line}}"),
    put("{{vat_label}}"), put("{{vat_text}}"), put("{{vat_row_amount}}"),
    keep("Bank: "), put("{{bank_line}}"),
    keep(""), keep("Tax numbers: "), put("{{tax_line}}"),
    put("{{payment_terms}}"),
    put("{{closing}}"), put("{{signatory}}"),
]
FOOTER = [put("{{company_name}} · {{company_address}}"), put("INVOICE {{invoice_number}} · {{date_short}}"),
          put("{{legal_footer}}")]

DROP_PREFIXES = ("customXml/", "docProps/thumbnail")
CORE_RESET = {"title": "", "subject": "", "creator": "", "keywords": "", "description": "", "lastModifiedBy": "",
              "category": ""}


class Refused(ValueError):
    pass


def png_size(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise Refused("The logo must be a PNG file.")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def rewrite_runs(xml, plan, part):
    root = etree.fromstring(xml)
    runs = root.findall(".//{%s}t" % W)
    if len(runs) != len(plan):
        raise Refused("%s has %d text runs; the house design has %d. Not the expected layout." % (
            part, len(runs), len(plan)))
    removed = []
    for t, (kind, value) in zip(runs, plan):
        current = t.text or ""
        if kind == "keep":
            if current != value:
                raise Refused("%s: expected the label %r, found something else. Not the expected layout." % (
                    part, value))
            continue
        if current.strip():
            removed.append(current)
        t.text = value
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return root, removed


def clean(source, out, logo):
    if out.exists():
        raise Refused("Refusing to overwrite %s: choose a new _vN name." % out)
    with zipfile.ZipFile(source) as zi:
        infos = [i for i in zi.infolist() if not i.filename.startswith(DROP_PREFIXES)]
        parts = {i.filename: zi.read(i.filename) for i in zi.infolist()}

    doc, removed = rewrite_runs(parts["word/document.xml"], DOCUMENT, "word/document.xml")
    foot, removed_footer = rewrite_runs(parts["word/footer1.xml"], FOOTER, "word/footer1.xml")
    removed += removed_footer

    # The picture: neutral name, neutral alt text, and an extent that keeps the new logo's proportions.
    logo_bytes = logo.read_bytes()
    lw, lh = png_size(logo_bytes)
    for el in doc.iter("{%s}cNvPr" % PIC, "{%s}docPr" % WP):
        el.set("name", "logo.png" if el.tag.endswith("cNvPr") else "Logo")
        for attr in ("descr", "title"):
            if attr in el.attrib:
                el.set(attr, "Logo")
    for tag in ("{%s}extent" % WP, "{%s}ext" % A):
        for ext in doc.iter(tag):
            if ext.get("cx") and ext.get("cy"):
                ext.set("cy", str(int(int(ext.get("cx")) * lh / lw)))
    parts["word/media/image1.png"] = logo_bytes
    parts["word/document.xml"] = etree.tostring(doc, xml_declaration=True, encoding="UTF-8", standalone=True)
    parts["word/footer1.xml"] = etree.tostring(foot, xml_declaration=True, encoding="UTF-8", standalone=True)

    # References to the dropped parts.
    rels = parts["_rels/.rels"].decode("utf-8")
    parts["_rels/.rels"] = re.sub(r"<Relationship [^>]*thumbnail[^>]*/>", "", rels).encode("utf-8")
    drels = parts["word/_rels/document.xml.rels"].decode("utf-8")
    parts["word/_rels/document.xml.rels"] = re.sub(r"<Relationship [^>]*customXml[^>]*/>", "", drels).encode("utf-8")
    ct = parts["[Content_Types].xml"].decode("utf-8")
    ct = re.sub(r'<Override PartName="/customXml/[^"]*"[^>]*/>', "", ct)
    ct = re.sub(r'<Default Extension="jpe?g"[^>]*/>', "", ct)
    parts["[Content_Types].xml"] = ct.encode("utf-8")

    core = parts["docProps/core.xml"].decode("utf-8")
    for tag, value in CORE_RESET.items():
        core = re.sub(r"<(\w+):%s(\s[^>]*)?(/>|>.*?</\1:%s>)" % (tag, tag),
                      lambda m: "<%s:%s%s>%s</%s:%s>" % (m.group(1), tag, m.group(2) or "", value, m.group(1), tag),
                      core, flags=re.S)
    core = re.sub(r"(<dcterms:(?:created|modified)[^>]*>)[^<]*", r"\g<1>2026-01-01T00:00:00Z", core)
    parts["docProps/core.xml"] = core.encode("utf-8")
    app = parts["docProps/app.xml"].decode("utf-8")
    for tag in ("Company", "Manager"):
        app = re.sub(r"<%s>.*?</%s>" % (tag, tag), "<%s/>" % tag, app, flags=re.S)
    parts["docProps/app.xml"] = app.encode("utf-8")

    # Proof: no text from the source's variable runs, and no word of four letters or more from them that is not
    # also one of this script's own labels, survives anywhere in the output.
    kept_labels = " ".join(v for k, v in DOCUMENT + FOOTER).lower()
    blob = b"".join(parts[i.filename] for i in infos).decode("utf-8", "ignore").lower()

    def found(text):
        return re.search(r"(?<![a-z0-9_])%s(?![a-z0-9_])" % re.escape(text.lower()), blob) is not None

    leaks = sorted({s for s in removed if len(s.strip()) >= 4 and found(s)})
    words = {w for s in removed for w in re.findall(r"[A-Za-zÀ-ÿ0-9][\wÀ-ÿ\-./@]{3,}", s)}
    leaks += sorted(w for w in words if found(w) and w.lower() not in kept_labels
                    and not re.fullmatch(r"[\d.,]+", w) and w.lower() not in GENERIC)
    if leaks:
        raise Refused("Source text survived in the output (%d hits: %s). Not written." % (len(leaks), ", ".join(leaks)))

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in infos:
            zo.writestr(info, parts[info.filename])
    return len(removed)


# Words that are also OOXML markup (<Company/> in docProps/app.xml, the "Quote" style, namespace addresses such
# as schemas.microsoft.com/office/word), not identifying on their own.
GENERIC = {"company", "quote", "office", "word", "document", "theme", "settings", "package", "schemas", "microsoft",
           "relationships", "main", "properties"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("source", type=Path, help="a filled .docx in the house design (never committed)")
    p.add_argument("out", type=Path, help="where to write the clean template")
    p.add_argument("--logo", type=Path, default=HERE.parent / "assets" / "placeholder_logo.png")
    a = p.parse_args(argv)
    try:
        n = clean(a.source, a.out, a.logo)
    except Refused as e:
        print("Refused: %s" % e, file=sys.stderr)
        return 1
    print("Wrote %s: %d variable runs replaced with placeholders, thumbnail and customXml removed." % (a.out, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
