"""Draw an invoice or credit note as an A4 PDF with ReportLab (BSD licence)."""
from pathlib import Path

from .books import resolve_path
from .money import fmt, fmt_qty, fmt_rate


class PdfMissing(RuntimeError):
    pass


def _lib():
    try:
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.utils import ImageReader, simpleSplit
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except ImportError:
        raise PdfMissing('PDF invoices need ReportLab. Run: python3 -m pip install --user reportlab')
    return locals()


def fonts(books, c, lib):
    regular, bold = 'Helvetica', 'Helvetica-Bold'
    if c.get('font_file'):
        lib['pdfmetrics'].registerFont(lib['TTFont']('InvoiceRegular', resolve_path(books, c['font_file'])))
        regular = bold = 'InvoiceRegular'
    if c.get('font_bold_file'):
        lib['pdfmetrics'].registerFont(lib['TTFont']('InvoiceBold', resolve_path(books, c['font_bold_file'])))
        bold = 'InvoiceBold'
    return regular, bold


def render(books, c, doc, out_path, draft=False):
    lib = _lib()
    mm, A4 = lib['mm'], lib['A4']
    width, height = A4
    regular, bold = fonts(books, c, lib)
    accent = lib['HexColor'](c.get('accent') or '#2B5D8A')
    ink, muted, rule = lib['HexColor']('#1E1E1E'), lib['HexColor']('#5C5C5C'), lib['HexColor']('#D9D6CF')
    cur = doc['currency']
    pdf = lib['canvas'].Canvas(str(out_path), pagesize=A4)
    pdf.setTitle('%s %s' % ('Credit note' if doc['kind'] == 'credit' else 'Invoice', doc.get('number') or 'DRAFT'))
    pdf.setAuthor(c['name'])
    pdf.setCreator('shelf-invoices 2.0.0')
    left, right = 20 * mm, width - 20 * mm
    split = lib['simpleSplit']

    def text(x, y, value, size=9.5, font=None, colour=ink, align='left'):
        pdf.setFont(font or regular, size)
        pdf.setFillColor(colour)
        if align == 'right':
            pdf.drawRightString(x, y, value)
        else:
            pdf.drawString(x, y, value)

    if draft:
        pdf.saveState()
        pdf.setFillColor(lib['HexColor']('#E8E4DA'))
        pdf.setFont(bold, 90)
        pdf.translate(width / 2, height / 2)
        pdf.rotate(35)
        pdf.drawCentredString(0, 0, 'DRAFT')
        pdf.restoreState()

    top = height - 20 * mm
    logo = resolve_path(books, c.get('logo', ''))
    if logo and Path(logo).exists():
        img = lib['ImageReader'](logo)
        iw, ih = img.getSize()
        h = 16 * mm
        w = min(70 * mm, iw * h / ih)
        pdf.drawImage(img, left, top - h, w, h, mask='auto', preserveAspectRatio=True)
    else:
        text(left, top - 10 * mm, c['name'], 16, bold)

    y = top - 3 * mm
    for line in [c['name']] + c['address'] + [c['email'], c['phone'], c['website']]:
        if line:
            text(right, y, line, 8.5, bold if line == c['name'] else regular, muted if line != c['name'] else ink, 'right')
            y -= 4.2 * mm
    ids = []
    if c['vat_registered'] and c['vat_id']:
        ids.append('%s ID: %s' % (c['tax_label'], c['vat_id']))
    if c['tax_number']:
        ids.append('Tax number: ' + c['tax_number'])
    if c['company_number']:
        ids.append('Company number: ' + c['company_number'])
    for line in ids:
        text(right, y, line, 8.5, colour=muted, align='right')
        y -= 4.2 * mm

    y = min(y, top - 30 * mm) - 10 * mm
    title = 'CREDIT NOTE' if doc['kind'] == 'credit' else 'INVOICE'
    text(left, y, title, 22, bold, accent)
    y -= 12 * mm

    # Bill to (left) and the details (right).
    text(left, y, 'Bill to', 8, bold, muted)
    details = [('Number', doc.get('number') or 'DRAFT, not numbered'), ('Date', doc['date']),
               ('Due', doc['due'] if doc['kind'] == 'invoice' else '')]
    if doc.get('credits'):
        details.append(('Credits invoice', doc['credits']))
    if doc.get('po'):
        details.append(('Your PO', doc['po']))
    if doc.get('service_date'):
        details.append(('Service date', doc['service_date']))
    by = y
    for label, value in details:
        if value:
            text(right - 60 * mm, by, label, 8.5, colour=muted)
            text(right, by, value, 9.5, bold, align='right')
            by -= 5 * mm
    cy = y - 5 * mm
    client = doc['client']
    for line in [client['name']] + client.get('address', []) + (
            ['%s ID: %s' % (c['tax_label'], client['vat_id'])] if client.get('vat_id') else []):
        text(left, cy, line, 9.5, bold if line == client['name'] else regular)
        cy -= 4.6 * mm
    y = min(cy, by) - 8 * mm

    # Lines. Right edges of the number columns, measured from the right margin.
    show_vat = doc['vat_mode'] == 'standard'
    qty_r, unit_r, vat_r, amt_r = right - 92 * mm, right - 60 * mm, right - 36 * mm, right - 2 * mm
    desc_w = (qty_r - 14 * mm) - (left + 2 * mm)
    pdf.setFillColor(accent)
    pdf.rect(left, y - 2.5 * mm, right - left, 8 * mm, stroke=0, fill=1)
    white = lib['HexColor']('#FFFFFF')
    text(left + 2 * mm, y, 'Description', 8.5, bold, white)
    text(qty_r, y, 'Qty', 8.5, bold, white, 'right')
    text(unit_r, y, 'Unit price', 8.5, bold, white, 'right')
    if show_vat:
        text(vat_r, y, c['tax_label'], 8.5, bold, white, 'right')
    text(amt_r, y, 'Amount', 8.5, bold, white, 'right')
    y -= 10 * mm
    pdf.setStrokeColor(rule)
    for line in doc['totals']['lines']:
        wrapped = split(line['description'], regular, 9.5, desc_w) or ['']
        for i, part in enumerate(wrapped):
            text(left + 2 * mm, y - i * 4.6 * mm, part)
        text(qty_r, y, fmt_qty(line['quantity']), align='right')
        text(unit_r, y, fmt(line['unit_price'], cur), align='right')
        if show_vat:
            text(vat_r, y, fmt_rate(line['vat_rate']), align='right')
        text(amt_r, y, fmt(line['amount'], cur), align='right')
        bottom = y - (len(wrapped) - 1) * 4.6 * mm - 3 * mm
        pdf.line(left, bottom, right, bottom)
        y = bottom - 5.5 * mm

    # Totals.
    y -= 2 * mm
    t = doc['totals']
    rows = [('Subtotal', t['net'])]
    if show_vat:
        for r in t['vat_rows']:
            rows.append(('%s at %s on %s' % (c['tax_label'], fmt_rate(r['rate']), fmt(r['net'], cur)), r['vat']))
    for label, value in rows:
        text(right - 45 * mm, y, label, 9, colour=muted, align='right')
        text(amt_r, y, fmt(value, cur), 9.5, align='right')
        y -= 5.5 * mm
    y -= 3 * mm
    pdf.setFillColor(lib['HexColor']('#F2F2EF'))
    pdf.rect(right - 95 * mm, y - 3.5 * mm, 95 * mm, 10 * mm, stroke=0, fill=1)
    text(right - 45 * mm, y, 'Total %s' % cur, 11, bold, align='right')
    text(amt_r, y, fmt(t['total'], cur), 12, bold, accent, 'right')
    y -= 14 * mm

    notes = [n for n in (doc.get('vat_note'), doc.get('notes')) if n]
    for note in notes:
        for part in split(note, regular, 9, right - left):
            text(left, y, part, 9, colour=ink)
            y -= 4.6 * mm
        y -= 2 * mm

    if doc['kind'] == 'invoice':
        y -= 2 * mm
        text(left, y, 'How to pay', 8, bold, muted)
        y -= 5 * mm
        b = c['bank']
        pay = ['Please pay %s by %s, quoting %s.' % (fmt(t['total'], cur), doc['due'], doc.get('number') or 'the invoice number')]
        for label, key in (('Account name', 'account_name'), ('Bank', 'bank_name'), ('IBAN', 'iban'), ('BIC', 'bic'),
                           ('Sort code', 'sort_code'), ('Account number', 'account_number')):
            if b.get(key):
                pay.append('%s: %s' % (label, b[key]))
        for line in pay:
            text(left, y, line, 9)
            y -= 4.6 * mm

    fy = 14 * mm
    footer = list(c.get('legal_lines', []))
    if c.get('footer_note'):
        footer.append(c['footer_note'])
    pdf.setStrokeColor(rule)
    pdf.line(left, fy + len(footer) * 3.8 * mm + 2 * mm, right, fy + len(footer) * 3.8 * mm + 2 * mm)
    for i, line in enumerate(reversed(footer)):
        text(width / 2 - pdf.stringWidth(line, regular, 7.5) / 2, fy + i * 3.8 * mm, line, 7.5, colour=muted)
    if y < fy + len(footer) * 3.8 * mm + 10 * mm:
        raise ValueError('This invoice does not fit on one page. Combine lines or shorten descriptions.')
    pdf.showPage()
    pdf.save()
    return out_path


def text_of(path):
    """The PDF's text, for verify. Uses pypdf (BSD) if present, else pdftotext."""
    try:
        from pypdf import PdfReader
        return '\n'.join(page.extract_text() or '' for page in PdfReader(str(path)).pages)
    except ImportError:
        import shutil
        import subprocess
        if shutil.which('pdftotext'):
            return subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, text=True).stdout
        return None
