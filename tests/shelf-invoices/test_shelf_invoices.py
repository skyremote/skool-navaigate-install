"""Tests for shelf-invoices 2.0.1. Run: python3 -m unittest discover -s tests/shelf-invoices

Needs lxml (python3 -m pip install --user lxml). The PDF tests need LibreOffice and skip without it.
"""
import hashlib
import io
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib
from contextlib import redirect_stderr, redirect_stdout
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "plugins" / "shelf-invoices"
sys.path.insert(0, str(PACK / "scripts"))
import generate_invoice as gi  # noqa: E402
import make_clean_template as mct  # noqa: E402

TEMPLATE = PACK / "assets" / "template_v1.docx"
SAMPLE = PACK / "assets" / "sample"
BIN = PACK / "bin" / "shelf-invoices"

# The privacy scans from the shelf v2 brief, applied to every part of every shipped archive. The private strings
# themselves must not be published, so the test holds only (length, SHA-256 prefix of the lower-cased string) and
# hashes every window of that length that starts a word. The generic patterns stay as regular expressions.
PRIVATE = {
    (9, "6fd06f2a4fdd27bd49f6aba6"), (12, "09161f256a96476fdd1526cd"), (13, "6767778e470b5216a9ef0296"),
    (12, "38a84aae6a076c1cca998bb5"), (17, "cdcd28407e19135194eee8e6"), (20, "7904178987efce8f8a1bd086"),
    (7, "fb582ee70e88265c59c0dee5"), (11, "59e6f1d3bc3523b0c80c77bf"), (8, "82ca071df925197017b0197d"),
    (9, "2b9c8c6dec3a356b36775c1e"), (10, "6b1b9415ca033df9b668f4f0"), (10, "8ab272bd8fac78d2ac8c9621"),
    (10, "32d6cd6572c703b15ae6b35a"), (10, "e129d0d8787516914c076abe"), (9, "6a05266e64cf3224ac31f9c2"),
    (10, "ce56d5803d55a8f4f0aebe7c"), (17, "96ce572e1c1000f5f246d949"), (5, "ecd50b07b75cca839862f648"),
    (8, "904516c80aaec28554115539"), (5, "1ba3531ea8129e6858b329f0"), (8, "8589c25b0959ade9695eba45"),
    (10, "563cb4c90f71e3054bc07eb6"), (22, "997cbf837e9af0b30dd194c9"), (14, "01e096604c4c122992157274"),
    (7, "5fa495b84bd1c34d833ad414"), (6, "d300571a34febb044e2e6d14"), (8, "320d597682ed208cdaa58f77"),
    (5, "e3fd7ca42b4557ab6f78ec67"), (6, "e181b3dfcbf4b938b8254b83"), (10, "b1ad0143047aa493a69df4e6"),
    (12, "81743b673c91fd3ced4e0b4e"),
}
GENERIC = re.compile(r"libsql:" r"//|ey" r"J[A-Za-z0-9_-]{20,}|s" r"k-[A-Za-z0-9]{20,}"
                     r"|DE[0-9]{2} ?[0-9]{4} ?[0-9]{4} ?[0-9]{4} ?[0-9]{4} ?[0-9]{2}")
WORD_START = re.compile(r"(?<![a-z0-9])[a-z0-9]")


def private_hits(text):
    hits = [m.group(0) for m in GENERIC.finditer(text)]
    text = text.lower()
    lengths = {n for n, _ in PRIVATE}
    for m in WORD_START.finditer(text):
        i = m.start()
        for n in lengths:
            if (n, hashlib.sha256(text[i:i + n].encode()).hexdigest()[:24]) in PRIVATE:
                hits.append("a private string at offset %d" % i)
    return hits
FIELDS = {"signatory", "company_name", "company_address", "contact_line", "web_line", "title", "subtitle",
          "client_name", "client_address", "requester", "client_extra", "date_long", "invoice_number", "currency",
          "po_number", "po_extra", "greeting", "intro", "item_no", "item_title", "item_description", "item_amount",
          "total_note", "total", "service_line", "vat_label", "vat_text", "vat_row_amount", "bank_line", "tax_line",
          "payment_terms", "closing", "date_short", "legal_footer"}


def tmpdir(test):
    path = Path(tempfile.mkdtemp(prefix="shelf-invoices-test-"))
    test.addCleanup(shutil.rmtree, path, True)
    return path


def parts_of(docx):
    with zipfile.ZipFile(docx) as z:
        return {n: z.read(n) for n in z.namelist()}


def doc_text(docx):
    p = parts_of(docx)
    return " ".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", p["word/document.xml"].decode() +
                               p["word/footer1.xml"].decode()))


def png(w, h):
    raw = b"".join(b"\x00" + b"\xff\x00\x00" * w for _ in range(h))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def sample_company():
    c = gi.load_company(SAMPLE / "company.json")
    c["_sample"] = True
    return c


def sample_spec(name="northwind-website.json", **over):
    spec = json.loads((SAMPLE / "examples" / name).read_text())
    spec.setdefault("invoice_number", "ACME-010")
    spec.update(over)
    return spec


def cli(*args, env=None):
    out, err = io.StringIO(), io.StringIO()
    e = dict(os.environ, **(env or {}))
    r = subprocess.run([sys.executable, str(BIN)] + [str(a) for a in args], capture_output=True, text=True, env=e)
    return r.returncode, r.stdout, r.stderr


class TemplateTests(unittest.TestCase):
    def test_no_private_string_in_any_part(self):
        for name, data in parts_of(TEMPLATE).items():
            self.assertEqual(private_hits(data.decode("utf-8", "ignore")), [], name)

    def test_the_scanner_finds_what_it_looks_for(self):
        home = "/Us" + "ers/" + "s" + "ky/Documents"  # built in pieces so the repo-wide grep stays clean
        self.assertEqual(len(private_hits("path: " + home)), 1)
        self.assertEqual(private_hits("Acme Studio Ltd, Bristol"), [])

    def test_no_thumbnail_or_custom_xml(self):
        p = parts_of(TEMPLATE)
        self.assertNotIn("docProps/thumbnail.jpeg", p)
        self.assertFalse([n for n in p if n.startswith("customXml/")])
        self.assertNotIn(b"thumbnail", p["_rels/.rels"])
        self.assertNotIn(b"customXml", p["[Content_Types].xml"])
        self.assertNotIn(b"customXml", p["word/_rels/document.xml.rels"])

    def test_core_properties_reset(self):
        core = parts_of(TEMPLATE)["docProps/core.xml"].decode()
        for tag in ("dc:title", "dc:creator", "dc:description", "cp:lastModifiedBy"):
            self.assertRegex(core, r"<%s>\s*</%s>|<%s/>" % (tag, tag, tag))

    def test_every_field_is_a_placeholder_the_generator_knows(self):
        found = set(re.findall(r"\{\{(\w+)\}\}", doc_text(TEMPLATE)))
        self.assertEqual(found, FIELDS)

    def test_logo_is_the_neutral_placeholder(self):
        self.assertEqual(parts_of(TEMPLATE)["word/media/image1.png"], (PACK / "assets/placeholder_logo.png").read_bytes())
        self.assertNotIn(b"navaigate", parts_of(TEMPLATE)["word/document.xml"].lower())

    def test_sample_and_shipped_files_are_clean(self):
        for p in PACK.rglob("*"):
            if p.is_file() and p.suffix in (".json", ".md", ".py", "") and p.name != ".DS_Store":
                self.assertEqual(private_hits(p.read_text(encoding="utf-8", errors="ignore")), [], str(p))
        for archive in PACK.rglob("*.docx"):
            for name, data in parts_of(archive).items():
                self.assertEqual(private_hits(data.decode("utf-8", "ignore")), [], "%s:%s" % (archive.name, name))


class BuildTests(unittest.TestCase):
    def test_vat_standard(self):
        values, items, t = gi.build(sample_company(), sample_spec())
        self.assertEqual((t["net"], t["vat"], t["gross"]), (Decimal("3075.00"), Decimal("615.00"), Decimal("3690.00")))
        self.assertEqual(values["total"], "£3,690.00")
        self.assertEqual(values["vat_row_amount"], "£615.00")
        self.assertIn("(incl. 20% VAT)", values["total_note"])
        self.assertEqual(len(items), 3)

    def test_quantity_times_unit_price_and_reverse_charge(self):
        values, items, t = gi.build(sample_company(), sample_spec("contoso-workshop.json"))
        self.assertEqual(t["gross"], Decimal("3600.00"))
        self.assertEqual(t["vat"], Decimal("0"))
        self.assertIn("3 days × €1,200.00", items[0]["item_description"])
        self.assertEqual(values["vat_row_amount"], "€3,600.00")
        self.assertIn("reverse charge", values["vat_text"])
        self.assertIn("DE000000000", values["client_extra"])

    def test_reverse_charge_needs_client_vat_id(self):
        with self.assertRaises(gi.InvoiceError):
            gi.build(sample_company(), sample_spec("contoso-workshop.json", client_vat_id=""))

    def test_not_registered_cannot_charge_vat(self):
        c = sample_company()
        c["vat_mode"] = "not_registered"
        with self.assertRaises(gi.InvoiceError):
            gi.build(c, sample_spec(vat="standard"))
        values, _, t = gi.build(c, sample_spec(vat="not_registered"))
        self.assertEqual(t["vat"], 0)
        self.assertIn("not registered", values["vat_text"])

    def test_wording_comes_from_settings(self):
        c = sample_company()
        c["vat_wording"]["outside_scope"] = {"label": "Export: ", "text": "zero tax for {country}"}
        values, _, _ = gi.build(c, sample_spec(vat="outside_scope"))
        self.assertEqual((values["vat_label"], values["vat_text"]), ("Export: ", "zero tax for the UK"))

    def test_payment_terms_quote_po_and_number(self):
        values, _, _ = gi.build(sample_company(), sample_spec())
        self.assertEqual(values["payment_terms"],
                         "Payment terms: net 14 days, per purchase order NW-0042. Please quote ACME-010 with payment.")
        values, _, _ = gi.build(sample_company(), sample_spec(payment_terms="Due on receipt."))
        self.assertEqual(values["payment_terms"], "Due on receipt.")

    def test_bad_input_is_refused(self):
        for over in ({"items": []}, {"vat": "made_up"}, {"date": "26/10/2026"},
                     {"items": [{"title": "X"}]}, {"items": [{"title": "X", "amount": "lots"}]}):
            with self.assertRaises(gi.InvoiceError, msg=over):
                gi.build(sample_company(), sample_spec(**over))

    def test_company_check(self):
        missing, _ = gi.check_company(gi.load_company(SAMPLE / "company.json"))
        self.assertEqual(missing, [])
        blank = dict(gi.COMPANY_DEFAULTS)
        missing, _ = gi.check_company(blank)
        self.assertTrue({"company_name", "email", "signatory", "address"} <= set(missing))
        _, warnings = gi.check_company(gi.load_company(SAMPLE / "company.json"))
        self.assertTrue(any("SAMPLE" in w for w in warnings), "real books holding SAMPLE values must be flagged")


class DocxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir(self)

    def make(self, spec, name="out.docx", logo=None, company=None):
        values, items, _ = gi.build(company or sample_company(), spec)
        problems = gi.fill_docx(values, items, self.tmp / name, logo)
        return self.tmp / name, problems

    def test_every_placeholder_filled_in_every_part(self):
        out, problems = self.make(sample_spec())
        self.assertEqual(problems, [])
        for name, data in parts_of(out).items():
            self.assertNotIn(b"{{", data, name)
        text = doc_text(out)
        for want in ("Acme Studio Ltd", "Northwind Bakery Ltd", "ACME-010", "NW-0042", "£3,690.00", "Sam Lee",
                     "Service date: October 2026.", "IBAN XX00 SAMPLE", "Alex Morgan"):
            self.assertIn(want, text)

    def test_multi_line_items_clone_rows(self):
        out, _ = self.make(sample_spec())
        xml = parts_of(out)["word/document.xml"].decode()
        rows = [r for r in re.findall(r"<w:tr[ >].*?</w:tr>", xml, re.S)
                if re.search(r">(Booking page redesign|Menu photography|Hosting, October)<", r)]
        self.assertEqual(len(rows), 3)

    def test_never_overwrites(self):
        out, _ = self.make(sample_spec())
        before = out.read_bytes()
        with self.assertRaises(gi.InvoiceError):
            self.make(sample_spec())
        self.assertEqual(out.read_bytes(), before)

    def test_wrong_currency_sign_is_caught(self):
        spec = sample_spec()
        spec["items"][0]["description"] = "Paid €200 deposit"
        _, problems = self.make(spec)
        self.assertTrue(any("EUR sign" in p for p in problems))

    def test_empty_lines_disappear(self):
        spec = sample_spec(po_number="", subtitle="", requester="", service_date="")
        out, problems = self.make(spec)
        self.assertEqual(problems, [])
        text = doc_text(out)
        self.assertNotIn("Purchase order:", text)
        self.assertNotIn("Requester:", text)
        self.assertNotIn("Service date", text)
        self.assertIn("Hello,", text)

    def test_logo_swap_keeps_proportions(self):
        logo = png(400, 100)
        out, _ = self.make(sample_spec(), logo=logo)
        p = parts_of(out)
        self.assertEqual(p["word/media/image1.png"], logo)
        cx, cy = map(int, re.search(rb'<wp:extent cx="(\d+)" cy="(\d+)"', p["word/document.xml"]).groups())
        self.assertAlmostEqual(cx / cy, 4.0, places=2)
        with self.assertRaises(gi.InvoiceError):
            self.make(sample_spec(), name="jpeg.docx", logo=b"\xff\xd8\xff\xe0 not a png")

    def test_clean_template_round_trip(self):
        """A filled one-item invoice, cleaned again, gives back exactly the shipped placeholder text."""
        spec = sample_spec(items=[{"title": "Workshop", "description": "One day", "amount": 900}],
                           client_extra="Cost centre 12")
        out, _ = self.make(spec)
        clean = self.tmp / "clean.docx"
        self.assertEqual(mct.main([str(out), str(clean)]), 0)
        self.assertEqual(doc_text(clean), doc_text(TEMPLATE))
        for name, data in parts_of(clean).items():
            self.assertNotIn(b"Northwind", data, name)
            self.assertNotIn(b"Acme", data, name)

    def test_clean_template_refuses_other_layouts(self):
        out, _ = self.make(sample_spec())  # three items: more runs than the house layout
        with redirect_stderr(io.StringIO()):
            self.assertEqual(mct.main([str(out), str(self.tmp / "clean.docx")]), 1)
        self.assertFalse((self.tmp / "clean.docx").exists())


class NumberTests(unittest.TestCase):
    def test_highest_plus_one(self):
        books = tmpdir(self)
        c = sample_company()
        self.assertEqual(gi.next_number(books, c), ("ACME-001", None))
        for rel in ("2026/09/ACME-001.pdf", "2026/10/ACME-007.pdf", "drafts/ACME-009_v2.docx",
                    "drafts/ACME-NW-030_v1.docx", "notes/ACME-099-notes.txt"):
            (books / rel).parent.mkdir(parents=True, exist_ok=True)
            (books / rel).write_text("x")
        self.assertEqual(gi.next_number(books, c), ("ACME-010", 9))
        self.assertEqual(gi.next_number(books, c, "nw"), ("ACME-NW-031", 30))


@unittest.skipUnless(gi.find_soffice(), "LibreOffice not installed")
class PdfTests(unittest.TestCase):
    def test_renders_one_page(self):
        tmp = tmpdir(self)
        values, items, _ = gi.build(sample_company(), sample_spec())
        gi.fill_docx(values, items, tmp / "ACME-010_v1.docx", (SAMPLE / "acme-studio-logo.png").read_bytes())
        pdf = gi.render_pdf(tmp / "ACME-010_v1.docx")
        self.assertTrue(pdf and pdf.exists())
        self.assertEqual(gi.pdf_pages(pdf), 1)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tmpdir(self)
        self.env = {"AIOS_CONFIG_DIR": str(self.tmp / "cfg"), "SHELF_INVOICES_BOOKS": "",
                    "CLAUDE_PLUGIN_OPTION_BOOKS_FOLDER": ""}

    def test_version(self):
        code, out, _ = cli("--version", env=self.env)
        self.assertEqual((code, out.strip()), (0, "shelf-invoices 2.0.1"))

    def test_sample_make_file_flow(self):
        books = self.tmp / "practice"
        code, out, _ = cli("sample", books, env=self.env)
        self.assertEqual(code, 0, out)
        code, out, _ = cli("next-number", "--books", books, env=self.env)
        self.assertIn("ACME-002  (highest used: ACME-001)", out)
        code, out, err = cli("make", books / "examples/contoso-workshop.json", "--books", books, "--no-pdf",
                             env=self.env)
        self.assertEqual(code, 0, out + err)
        self.assertIn("Invoice ACME-002", out)
        self.assertTrue((books / "drafts/ACME-002_v1.docx").exists())
        self.assertEqual(json.loads((books / "drafts/ACME-002_v1.spec.json").read_text())["invoice_number"], "ACME-002")
        # A second make of the same spec takes the next number; a fixed number gets a new version, never overwrites.
        spec = json.loads((books / "examples/contoso-workshop.json").read_text())
        spec["invoice_number"] = "ACME-002"
        (self.tmp / "fixed.json").write_text(json.dumps(spec))
        code, out, _ = cli("make", self.tmp / "fixed.json", "--books", books, "--no-pdf", env=self.env)
        self.assertTrue((books / "drafts/ACME-002_v2.docx").exists())
        # Filing needs the PDF the member has looked at.
        code, _, err = cli("file", "ACME-002", "--books", books, env=self.env)
        self.assertEqual(code, 1)
        self.assertIn("No PDF", err)
        (books / "drafts/ACME-002_v2.pdf").write_bytes(b"%PDF-1.4 test")
        code, out, err = cli("file", "ACME-002", "--books", books, env=self.env)
        self.assertEqual(code, 0, err)
        self.assertTrue((books / "2026/10/ACME-002.pdf").exists())
        code, _, err = cli("file", "ACME-002", "--books", books, env=self.env)
        self.assertEqual(code, 1)
        code, _, err = cli("make", self.tmp / "fixed.json", "--books", books, "--no-pdf", env=self.env)
        self.assertEqual(code, 1)
        self.assertIn("already filed", err)

    def test_init_never_overwrites_and_check_refuses_blank(self):
        books = self.tmp / "mine"
        code, _, _ = cli("init", books, env=self.env)
        self.assertEqual(code, 0)
        (books / "company.json").write_text('{"company_name": "Mine"}')
        code, out, _ = cli("init", books, env=self.env)
        self.assertIn("Already set up", out)
        self.assertEqual((books / "company.json").read_text(), '{"company_name": "Mine"}')
        code, out, _ = cli("company", "check", env=self.env)  # the remembered default
        self.assertEqual(code, 1)
        self.assertIn("Missing before you can invoice", out)

    def test_plugin_setting_picks_the_books_folder(self):
        books = self.tmp / "practice"
        cli("sample", books, env=self.env)
        env = dict(self.env, CLAUDE_PLUGIN_OPTION_BOOKS_FOLDER=str(books))
        code, out, _ = cli("next-number", env=env)
        self.assertEqual(code, 0)
        self.assertIn("ACME-002", out)

    def test_no_books_folder_says_what_to_do(self):
        code, _, err = cli("next-number", env=self.env)
        self.assertEqual(code, 1)
        self.assertIn("shelf-invoices init", err)


if __name__ == "__main__":
    unittest.main()
