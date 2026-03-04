from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
import os
import random
import argparse
from datetime import datetime, timedelta

NAVY       = colors.HexColor("#1B2A4A")
LIGHT_GREY = colors.HexColor("#F4F4F4")
MID_GREY   = colors.HexColor("#CCCCCC")
DARK_GREY  = colors.HexColor("#555555")
WHITE      = colors.white
BLACK      = colors.black
PAGE_W, PAGE_H = A4
LEFT_M = RIGHT_M = 18 * mm
TOP_M  = 20 * mm
BOT_M  = 20 * mm
USABLE_W = PAGE_W - LEFT_M - RIGHT_M


# Data pools for random generation
BUSINESS_NAMES = [
    "Pinnacle Consulting Group", "Tech Solutions Australia", "Green Energy Co",
    "Metro Design Studio", "Apex Financial Services", "Harbour Engineering",
    "Summit Marketing Group", "Gateway IT Solutions", "Pacific Trade Co",
    "Horizon Construction", "Nexus Business Solutions", "Velocity Digital"
]

CUSTOMER_NAMES = [
    "BGL Corp", "Stellar Industries", "Quantum Enterprises",
    "Atlas Corporation", "Meridian Holdings", "Vertex Systems",
    "Catalyst Group", "Zenith Partners", "Omega Solutions"
]

STREET_NAMES = [
    "Collins Street", "Queen Street", "George Street", "Bourke Street",
    "Elizabeth Street", "Market Street", "King Street", "Pitt Street"
]

SUBURBS = [
    ("Sydney", "NSW", "2000"), ("Melbourne", "VIC", "3000"),
    ("Brisbane", "QLD", "4000"), ("Perth", "WA", "6000"),
    ("Adelaide", "SA", "5000"), ("Canberra", "ACT", "2600")
]

SERVICE_ITEMS = [
    "Software Development", "Consulting Services", "Project Management",
    "Technical Support", "System Integration", "Data Migration",
    "Business Analysis", "Quality Assurance", "Training Services",
    "Documentation", "Cloud Infrastructure", "Security Audit"
]


def generate_abn():
    """Generate a valid-looking ABN (11 digits)."""
    return f"{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"


def generate_address():
    """Generate a random Australian business address."""
    level = random.choice(["Level", "Suite", "Unit"])
    level_num = random.randint(1, 20)
    street_num = random.randint(10, 500)
    street = random.choice(STREET_NAMES)
    suburb, state, postcode = random.choice(SUBURBS)
    return [f"{level} {level_num}, {street_num} {street}", f"{suburb} {state} {postcode}"]


def generate_invoice_number():
    """Generate invoice number in format INV-YYYYXXX."""
    year = datetime.now().year
    num = random.randint(1, 999)
    return f"INV-{year}{num:03d}"


def generate_date(days_ago=0):
    """Generate a date in DD/MM/YYYY format."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%d/%m/%Y")


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def generate_line_items(num_items=None, target_subtotal=None, gst_free=False):
    """Generate random line items."""
    if num_items is None:
        num_items = random.randint(2, 5)

    items = []
    if target_subtotal:
        # Distribute target amount across items
        base_amount = target_subtotal / num_items
        for i in range(num_items):
            service = random.choice(SERVICE_ITEMS)
            if gst_free:
                service += " (GST Free)"
            qty = random.randint(1, 20)
            unit_price = round_to_tenth(base_amount / qty)
            amount = round_to_tenth(qty * unit_price)
            items.append((service, str(qty), f"${unit_price:.2f}", f"${amount:.2f}"))
    else:
        # Generate random amounts
        for i in range(num_items):
            service = random.choice(SERVICE_ITEMS)
            if gst_free:
                service += " (GST Free)"
            qty = random.randint(1, 20)
            unit_price = round_to_tenth(random.uniform(50, 500))
            amount = round_to_tenth(qty * unit_price)
            items.append((service, str(qty), f"${unit_price:.2f}", f"${amount:.2f}"))

    return items


def calculate_totals(items, gst_free=False):
    """Calculate subtotal, GST, and total from line items."""
    subtotal = sum(float(item[3].replace("$", "").replace(",", "")) for item in items)
    gst = 0 if gst_free else round_to_tenth(subtotal * 0.1)
    total = round_to_tenth(subtotal + gst)
    return f"${subtotal:,.2f}", f"${gst:,.2f}", f"${total:,.2f}"


def base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("InvoiceTitle",
        fontSize=22, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_RIGHT, spaceAfter=0))
    styles.add(ParagraphStyle("SectionTitle",
        fontSize=9, fontName="Helvetica-Bold",
        textColor=NAVY, spaceAfter=3))
    styles.add(ParagraphStyle("BodyText9",
        fontSize=9, fontName="Helvetica",
        textColor=DARK_GREY, spaceAfter=2, leading=13))
    styles.add(ParagraphStyle("BodyBold9",
        fontSize=9, fontName="Helvetica-Bold",
        textColor=BLACK, spaceAfter=2))
    styles.add(ParagraphStyle("FooterText",
        fontSize=7.5, fontName="Helvetica",
        textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    styles.add(ParagraphStyle("GstBadge",
        fontSize=8, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER))
    return styles


def hr(width=None, colour=None, thickness=0.5):
    if width is None: width = USABLE_W
    if colour is None: colour = MID_GREY
    return HRFlowable(width=width, thickness=thickness, color=colour,
                      spaceAfter=4*mm, spaceBefore=2*mm)


def address_block(lines, styles):
    out = []
    for i, line in enumerate(lines):
        style = styles["BodyBold9"] if i == 0 else styles["BodyText9"]
        out.append(Paragraph(line, style))
    return out


def make_meta_table(inv_no, date, due_date, currency):
    ml = ParagraphStyle("ML", fontSize=8, fontName="Helvetica-Bold",
                         textColor=DARK_GREY, alignment=TA_RIGHT)
    mv = ParagraphStyle("MV", fontSize=9, fontName="Helvetica-Bold",
                         textColor=BLACK, alignment=TA_RIGHT)
    def row(label, value):
        return [Paragraph(label, ml), Paragraph(value, mv)]
    t = Table(
        [row("Invoice No:", inv_no), row("Date:", date),
         row("Due Date:", due_date), row("Currency:", currency)],
        colWidths=[30*mm, 38*mm])
    t.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LIGHT_GREY, WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("LINEBELOW",     (0,-1),(-1,-1), 0.5, MID_GREY)]))
    return t


def line_items_style():
    return TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),   NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [WHITE, LIGHT_GREY]),
        ("ALIGN",         (1,1),(-1,-1),  "RIGHT"),
        ("ALIGN",         (0,0),(0,-1),   "LEFT"),
        ("FONTNAME",      (0,1),(-1,-1),  "Helvetica"),
        ("FONTSIZE",      (0,1),(-1,-1),  9),
        ("TEXTCOLOR",     (0,1),(-1,-1),  DARK_GREY),
        ("TOPPADDING",    (0,0),(-1,-1),  6),
        ("BOTTOMPADDING", (0,0),(-1,-1),  6),
        ("LEFTPADDING",   (0,0),(-1,-1),  6),
        ("RIGHTPADDING",  (0,0),(-1,-1),  6),
        ("LINEBELOW",     (0,0),(-1,0),   0, NAVY),
        ("LINEBELOW",     (0,-1),(-1,-1), 1, NAVY),
        ("GRID",          (0,0),(-1,-1),  0.3, MID_GREY)])


def totals_style(gst_free=False):
    if gst_free:
        return TableStyle([
            ("ALIGN",         (0,0),(-1,-1), "RIGHT"),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("LINEABOVE",     (0,3),(-1,3),  0.5, NAVY),
            ("BACKGROUND",    (0,3),(-1,3),  NAVY),
            ("ROWBACKGROUNDS",(0,0),(-1,2),  [WHITE, LIGHT_GREY, WHITE]),
            ("TOPPADDING",    (0,2),(-1,2),  0),
            ("BOTTOMPADDING", (0,2),(-1,2),  5)])
    else:
        return TableStyle([
            ("ALIGN",         (0,0),(-1,-1), "RIGHT"),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("LINEABOVE",     (0,2),(-1,2),  0.5, NAVY),
            ("BACKGROUND",    (0,2),(-1,2),  NAVY),
            ("ROWBACKGROUNDS",(0,0),(-1,1),  [WHITE, LIGHT_GREY])])


def pay_style():
    return TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0)])


def wrapper_style():
    return TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0)])


def build_invoice(output_path, supplier_name=None, supplier_abn=None, customer_name=None,
                  subtotal=None, gst_free=False, num_items=None):
    """Build an invoice PDF with random or specified data."""
    styles = base_styles()
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        leftMargin=LEFT_M, rightMargin=RIGHT_M,
        topMargin=TOP_M, bottomMargin=BOT_M)
    story = []

    # Generate random data or use provided values
    supplier = supplier_name or random.choice(BUSINESS_NAMES)
    supplier_full = f"{supplier} Pty Ltd"
    s_abn = supplier_abn or generate_abn()
    s_address = generate_address()

    customer = customer_name or random.choice(CUSTOMER_NAMES)
    customer_full = f"{customer} Pty Ltd"
    c_abn = generate_abn()
    c_address = generate_address()

    inv_no = generate_invoice_number()
    inv_date = generate_date(0)
    due_date = generate_date(-30)

    # Generate line items
    items = generate_line_items(num_items, subtotal, gst_free)
    subtotal_str, gst_str, total_str = calculate_totals(items, gst_free)

    # Header
    vh = ParagraphStyle("VH", fontSize=13,
                         fontName="Helvetica-Bold",
                         textColor=WHITE, leading=18)

    if gst_free:
        badge = Table([[Paragraph("GST FREE", styles["GstBadge"])]],
                      colWidths=[22*mm])
        badge.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#E8A020")),
            ("TOPPADDING",    (0,0),(-1,-1), 3),
            ("BOTTOMPADDING", (0,0),(-1,-1), 3),
            ("LEFTPADDING",   (0,0),(-1,-1), 4),
            ("RIGHTPADDING",  (0,0),(-1,-1), 4)]))
        hdr_right = Table(
            [[Paragraph("TAX INVOICE", styles["InvoiceTitle"])], [badge]],
            colWidths=[USABLE_W*0.45])
        hdr_right.setStyle(TableStyle([
            ("ALIGN",         (0,0),(-1,-1), "RIGHT"),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0)]))
    else:
        hdr_right = Paragraph("TAX INVOICE", styles["InvoiceTitle"])

    hdr = Table([[
        Paragraph(f"{supplier_full}<br/>"
                  f"<font size=8>ABN {s_abn}</font>", vh),
        hdr_right,
    ]], colWidths=[USABLE_W*0.55, USABLE_W*0.45])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0),(0,0),   10),
        ("RIGHTPADDING",  (1,0),(1,0),   10),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10)]))
    story += [hdr, Spacer(1, 5*mm)]

    # Vendor address and metadata
    vendor_lines = [supplier_full] + s_address + [f"ABN {s_abn}"]
    top = Table([[address_block(vendor_lines, styles), "",
                  make_meta_table(inv_no, inv_date, due_date, "AUD")]],
                colWidths=[USABLE_W*0.40, USABLE_W*0.10, 68*mm])
    top.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0)]))
    story += [top, Spacer(1, 5*mm)]

    # Bill to section
    story.append(Paragraph("BILL TO", styles["SectionTitle"]))
    story.append(hr())
    for i, line in enumerate([customer_full] + c_address + [f"ABN {c_abn}"]):
        story.append(Paragraph(line,
            styles["BodyBold9"] if i==0 else styles["BodyText9"]))
    story.append(Spacer(1, 5*mm))

    # Line items table
    cw = [USABLE_W*0.42, USABLE_W*0.13, USABLE_W*0.20, USABLE_W*0.25]
    th  = ParagraphStyle("TH",  fontSize=8.5,
                          fontName="Helvetica-Bold", textColor=WHITE)
    thr = ParagraphStyle("THR", fontSize=8.5,
                          fontName="Helvetica-Bold", textColor=WHITE,
                          alignment=TA_RIGHT)
    rows = [
        [Paragraph("Description", th), Paragraph("Qty", thr),
         Paragraph("Unit Price", thr), Paragraph("Amount (AUD)", thr)],
    ]
    for desc, qty, price, amount in items:
        rows.append([desc, qty, price, amount])

    tbl = Table(rows, colWidths=cw, repeatRows=1)
    tbl.setStyle(line_items_style())
    story += [tbl, Spacer(1, 4*mm)]

    # Totals
    tl  = ParagraphStyle("TL",  fontSize=9,
                          fontName="Helvetica", textColor=DARK_GREY, alignment=TA_RIGHT)
    tv  = ParagraphStyle("TV",  fontSize=9,
                          fontName="Helvetica", textColor=BLACK, alignment=TA_RIGHT)
    tn  = ParagraphStyle("TN",  fontSize=8,
                          fontName="Helvetica-Oblique", textColor=DARK_GREY, alignment=TA_RIGHT)
    tlb = ParagraphStyle("TLB", fontSize=10,
                          fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    tvb = ParagraphStyle("TVB", fontSize=10,
                          fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)

    if gst_free:
        tot = Table([
            [Paragraph("Subtotal:",    tl),  Paragraph(subtotal_str, tv)],
            [Paragraph("GST:",         tl),  Paragraph(gst_str,   tv)],
            [Paragraph("(GST Free)",   tn),  Paragraph("",        tn)],
            [Paragraph("TOTAL (AUD):", tlb), Paragraph(total_str, tvb)],
        ], colWidths=[40*mm, 30*mm])
    else:
        tot = Table([
            [Paragraph("Subtotal:",    tl),  Paragraph(subtotal_str, tv)],
            [Paragraph("GST (10%):",   tl),  Paragraph(gst_str,   tv)],
            [Paragraph("TOTAL (AUD):", tlb), Paragraph(total_str, tvb)],
        ], colWidths=[40*mm, 30*mm])

    tot.setStyle(totals_style(gst_free))
    wrapper = Table([[" ", tot]], colWidths=[USABLE_W-70*mm, 70*mm])
    wrapper.setStyle(wrapper_style())
    story += [wrapper, Spacer(1, 6*mm)]

    # Payment details
    story.append(Paragraph("PAYMENT DETAILS", styles["SectionTitle"]))
    story.append(hr())
    pl = ParagraphStyle("PL", fontSize=9,
                         fontName="Helvetica-Bold", textColor=DARK_GREY)
    pv = ParagraphStyle("PV", fontSize=9,
                         fontName="Helvetica", textColor=BLACK)
    bsb = f"{random.randint(0,999):03d}-{random.randint(0,999):03d}"
    acc = f"{random.randint(100000000,999999999)}"
    pay = Table([
        [Paragraph("Bank", pl), Paragraph("BSB",        pl), Paragraph(bsb,     pv)],
        [Paragraph("",    pl), Paragraph("Account No", pl), Paragraph(acc,   pv)],
        [Paragraph("",    pl), Paragraph("Reference",  pl), Paragraph(inv_no, pv)],
    ], colWidths=[20*mm, 30*mm, 60*mm])
    pay.setStyle(pay_style())
    story += [pay, Spacer(1, 8*mm)]

    # Footer
    story.append(hr(colour=NAVY, thickness=1))
    if gst_free:
        footer_text = f"All items on this invoice are GST-free. {supplier_full} ABN {s_abn}"
    else:
        footer_text = f"{supplier_full} is registered for GST. ABN {s_abn}"
    story.append(Paragraph(footer_text, styles["FooterText"]))
    addr_line = ", ".join(s_address)
    story.append(Paragraph(
        f"{addr_line}  |  Please quote invoice number with payment.",
        styles["FooterText"]))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random invoice PDFs with optional custom data."
    )
    parser.add_argument("--supplier-name", help="Supplier business name (without 'Pty Ltd')")
    parser.add_argument("--supplier-abn", help="Supplier ABN (format: XX XXX XXX XXX)")
    parser.add_argument("--customer-name", help="Customer business name (without 'Pty Ltd')")
    parser.add_argument("--subtotal", type=float, help="Target subtotal amount (before GST)")
    parser.add_argument("--gst-free", action="store_true", help="Generate GST-free invoice")
    parser.add_argument("--num-items", type=int, help="Number of line items (default: random 2-5)")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\invoices"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    existing = [f for f in os.listdir(out_dir) if f.startswith("invoice_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[1].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"invoice_{next_n:03d}.pdf")

    build_invoice(
        path,
        supplier_name=args.supplier_name,
        supplier_abn=args.supplier_abn,
        customer_name=args.customer_name,
        subtotal=args.subtotal,
        gst_free=args.gst_free,
        num_items=args.num_items
    )

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
