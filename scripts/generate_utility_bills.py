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
BLUE       = colors.HexColor("#1565C0")
WHITE      = colors.white
BLACK      = colors.black
PAGE_W, PAGE_H = A4
LEFT_M = RIGHT_M = 18 * mm
TOP_M  = 20 * mm
BOT_M  = 20 * mm
USABLE_W = PAGE_W - LEFT_M - RIGHT_M

# Data pools for random generation
UTILITY_PROVIDERS = [
    ("ELECTRICITY BILL", "PowerFlow Energy", "Electricity", "kWh", "$0.28"),
    ("ELECTRICITY BILL", "AusGrid Services", "Electricity", "kWh", "$0.30"),
    ("ELECTRICITY BILL", "EnergyStar Australia", "Electricity", "kWh", "$0.27"),
    ("GAS BILL", "MetroGas Services", "Gas", "MJ", "$0.032"),
    ("GAS BILL", "CityGas Australia", "Gas", "MJ", "$0.035"),
    ("GAS BILL", "AusGas Supply", "Gas", "MJ", "$0.030"),
    ("WATER BILL", "Sydney Water", "Water", "kL", "$2.35"),
    ("WATER BILL", "Melbourne Water", "Water", "kL", "$2.50"),
    ("WATER BILL", "AquaSafe Services", "Water", "kL", "$2.40"),
]

CUSTOMER_NAMES = [
    "Jennifer Collins", "Robert Harris", "Michael Chen", "Sarah Wilson",
    "David Thompson", "Emma Johnson", "James Anderson", "Olivia Martinez"
]

STREETS = [
    "Willow Street", "Oak Drive", "Maple Avenue", "Cedar Road",
    "Pine Street", "Elm Avenue", "Birch Street", "Ash Lane"
]

SUBURBS = [
    ("Sydney", "NSW", "2000"), ("Melbourne", "VIC", "3000"),
    ("Brisbane", "QLD", "4000"), ("Perth", "WA", "6000"),
    ("Adelaide", "SA", "5000"), ("Canberra", "ACT", "2600")
]


def base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("BillTitle",
        fontSize=20, fontName="Helvetica-Bold",
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
    styles.add(ParagraphStyle("BillType",
        fontSize=11, fontName="Helvetica-Bold",
        textColor=BLUE, spaceAfter=4))
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


def make_meta_table(bill_no, account_no, bill_date, due_date):
    ml = ParagraphStyle("ML", fontSize=8, fontName="Helvetica-Bold",
                         textColor=DARK_GREY, alignment=TA_LEFT)
    mv = ParagraphStyle("MV", fontSize=9, fontName="Helvetica-Bold",
                         textColor=BLACK, alignment=TA_LEFT)
    def row(label, value):
        return [Paragraph(label, ml), Paragraph(value, mv)]
    t = Table(
        [row("Bill Number:", bill_no),
         row("Account Number:", account_no),
         row("Bill Date:", bill_date),
         row("Due Date:", due_date)],
        colWidths=[35*mm, 40*mm])
    t.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LIGHT_GREY, WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("LINEBELOW",     (0,-1),(-1,-1), 0.5, MID_GREY)]))
    return t


def meter_info_style():
    return TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),   NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [LIGHT_GREY]),
        ("ALIGN",         (1,1),(-1,-1),  "CENTER"),
        ("FONTNAME",      (0,1),(-1,-1),  "Helvetica"),
        ("FONTSIZE",      (0,1),(-1,-1),  9),
        ("TEXTCOLOR",     (0,1),(-1,-1),  BLACK),
        ("TOPPADDING",    (0,0),(-1,-1),  6),
        ("BOTTOMPADDING", (0,0),(-1,-1),  6),
        ("LEFTPADDING",   (0,0),(-1,-1),  6),
        ("RIGHTPADDING",  (0,0),(-1,-1),  6),
        ("GRID",          (0,0),(-1,-1),  0.5, MID_GREY)])


def charges_style():
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


def totals_style():
    return TableStyle([
        ("ALIGN",         (0,0),(-1,-1), "RIGHT"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("LINEABOVE",     (0,2),(-1,2),  0.5, NAVY),
        ("BACKGROUND",    (0,2),(-1,2),  NAVY),
        ("ROWBACKGROUNDS",(0,0),(-1,1),  [WHITE, LIGHT_GREY])])


def wrapper_style():
    return TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0)])


def generate_abn():
    """Generate a valid-looking ABN (11 digits)."""
    return f"{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"


def generate_address():
    """Generate a random Australian address."""
    street_num = random.randint(10, 200)
    street = random.choice(STREETS)
    suburb, state, postcode = random.choice(SUBURBS)
    return [f"{street_num} {street}", f"{suburb} {state} {postcode}"]


def generate_date(days_ago=0):
    """Generate a date in DD/MM/YYYY format."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%d/%m/%Y")


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def generate_bill_number():
    """Generate bill number in format B-XXXXXX."""
    return f"B-{random.randint(100000,999999)}"


def generate_account_number():
    """Generate account number (10 digits)."""
    return f"{random.randint(3000000000,4999999999)}"


def generate_utility_data(provider_name=None, provider_abn=None, customer_name=None,
                         usage_amount=None, billing_days=91):
    """Generate random utility bill data."""
    # Select utility type and provider
    if provider_name:
        # Find matching provider in data pools
        provider_data = next((p for p in UTILITY_PROVIDERS if provider_name.lower() in p[1].lower()), None)
        if not provider_data:
            provider_data = random.choice(UTILITY_PROVIDERS)
    else:
        provider_data = random.choice(UTILITY_PROVIDERS)

    utility_type, provider, service_type, unit, rate_str = provider_data
    rate = float(rate_str.replace("$", ""))

    provider_full = f"{provider} Pty Ltd"
    abn = provider_abn or generate_abn()
    address = generate_address()

    bill_no = generate_bill_number()
    account_no = generate_account_number()

    # Generate bill date and due date
    bill_date = generate_date(random.randint(0, 5))  # Bill issued 0-5 days ago
    due_date = generate_date(-21)  # Due 21 days from now

    customer = customer_name or random.choice(CUSTOMER_NAMES)
    customer_address = generate_address()

    # Meter information
    meter_prefix = {"Electricity": "EL", "Gas": "GS", "Water": "WM"}[service_type]
    meter_no = f"{meter_prefix}{random.randint(100000000,999999999)}"

    opening_read = random.randint(10000, 50000)
    if usage_amount:
        usage = int(usage_amount)
    else:
        # Generate realistic usage based on utility type
        if service_type == "Electricity":
            usage = random.randint(1500, 2500)
        elif service_type == "Gas":
            usage = random.randint(3000, 5000)
        else:  # Water
            usage = random.randint(150, 300)

    closing_read = opening_read + usage
    usage_str = f"{usage:,} {unit}"

    # Calculate charges
    usage_charge = round_to_tenth(usage * rate)
    if service_type == "Electricity":
        daily_rate = round_to_tenth(random.uniform(1.10, 1.25))
        supply_charge = round_to_tenth(billing_days * daily_rate)
        charges = [
            ("Usage Charge", f"{usage:,} {unit} @ {rate_str}/{unit}", f"${usage_charge:.2f}"),
            ("Daily Supply Charge", f"{billing_days} days @ ${daily_rate:.2f}/day", f"${supply_charge:.2f}"),
        ]
    elif service_type == "Gas":
        daily_rate = round_to_tenth(random.uniform(0.80, 1.00))
        supply_charge = round_to_tenth(billing_days * daily_rate)
        charges = [
            ("Usage Charge", f"{usage:,} {unit} @ {rate_str}/{unit}", f"${usage_charge:.2f}"),
            ("Daily Supply Charge", f"{billing_days} days @ ${daily_rate:.2f}/day", f"${supply_charge:.2f}"),
        ]
    else:  # Water
        service_charge = round_to_tenth(random.uniform(70, 100))
        charges = [
            ("Usage Charge", f"{usage:,} {unit} @ {rate_str}/{unit}", f"${usage_charge:.2f}"),
            ("Service Charge", f"Quarterly", f"${service_charge:.2f}"),
        ]
        supply_charge = service_charge

    subtotal = round_to_tenth(usage_charge + supply_charge)
    gst = round_to_tenth(subtotal * 0.1)
    total = round_to_tenth(subtotal + gst)

    tariff_type = "Single Rate" if service_type != "Water" else "Residential"

    return {
        "utility_type": utility_type,
        "provider_name": provider_full,
        "abn": abn,
        "address": address,
        "bill_no": bill_no,
        "account_no": account_no,
        "bill_date": bill_date,
        "due_date": due_date,
        "customer_name": customer,
        "customer_address": customer_address,
        "meter_no": meter_no,
        "opening_read": f"{opening_read:,}",
        "closing_read": f"{closing_read:,}",
        "usage": usage_str,
        "charges": charges,
        "subtotal": f"${subtotal:,.2f}",
        "gst": f"${gst:,.2f}",
        "total": f"${total:,.2f}",
        "tariff_type": tariff_type,
        "rate": f"{rate_str}/{unit}"
    }


def build_utility_bill(data, output_path):
    """Build a utility bill PDF with provided data."""
    styles = base_styles()
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        leftMargin=LEFT_M, rightMargin=RIGHT_M,
        topMargin=TOP_M, bottomMargin=BOT_M)
    story = []

    # Header
    vh = ParagraphStyle("VH", fontSize=13,
                         fontName="Helvetica-Bold",
                         textColor=WHITE, leading=18)
    hdr = Table([[
        Paragraph(f"{data['provider_name']}<br/>"
                  f"<font size=8>ABN {data['abn']}</font>", vh),
        Paragraph(data['utility_type'], styles["BillTitle"]),
    ]], colWidths=[USABLE_W*0.55, USABLE_W*0.45])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (0,0),(0,0),   10),
        ("RIGHTPADDING",  (1,0),(1,0),   10),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10)]))
    story += [hdr, Spacer(1, 5*mm)]

    # Provider address and metadata
    provider_lines = [data['provider_name']] + data['address'] + [f"ABN {data['abn']}"]
    top = Table([[address_block(provider_lines, styles), "",
                  make_meta_table(
                      data['bill_no'], data['account_no'],
                      data['bill_date'], data['due_date'])]],
                colWidths=[USABLE_W*0.38, USABLE_W*0.10, 75*mm])
    top.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0)]))
    story += [top, Spacer(1, 5*mm)]

    # Account holder section
    story.append(Paragraph("ACCOUNT HOLDER", styles["SectionTitle"]))
    story.append(hr())
    for i, line in enumerate([data['customer_name']] + data['customer_address']):
        story.append(Paragraph(line,
            styles["BodyBold9"] if i==0 else styles["BodyText9"]))
    story.append(Spacer(1, 5*mm))

    # Meter information
    story.append(Paragraph("METER INFORMATION", styles["SectionTitle"]))
    story.append(hr())
    th  = ParagraphStyle("TH",  fontSize=8.5,
                          fontName="Helvetica-Bold", textColor=WHITE,
                          alignment=TA_CENTER)
    meter_rows = [
        [Paragraph("Meter Number", th), Paragraph("Opening Read", th),
         Paragraph("Closing Read", th), Paragraph("Usage", th)],
        [data['meter_no'], data['opening_read'], data['closing_read'], data['usage']],
    ]
    meter_tbl = Table(meter_rows, colWidths=[USABLE_W*0.25]*4)
    meter_tbl.setStyle(meter_info_style())
    story += [meter_tbl, Spacer(1, 5*mm)]

    # Charges
    story.append(Paragraph("CHARGES", styles["SectionTitle"]))
    story.append(hr())
    cw = [USABLE_W*0.35, USABLE_W*0.40, USABLE_W*0.25]
    th_left  = ParagraphStyle("THL",  fontSize=8.5,
                          fontName="Helvetica-Bold", textColor=WHITE)
    thr = ParagraphStyle("THR", fontSize=8.5,
                          fontName="Helvetica-Bold", textColor=WHITE,
                          alignment=TA_RIGHT)
    charge_rows = [
        [Paragraph("Charge Type", th_left), Paragraph("Description", th_left),
         Paragraph("Amount (AUD)", thr)],
    ]
    for charge_type, description, amount in data['charges']:
        charge_rows.append([charge_type, description, amount])

    charge_tbl = Table(charge_rows, colWidths=cw, repeatRows=1)
    charge_tbl.setStyle(charges_style())
    story += [charge_tbl, Spacer(1, 4*mm)]

    # Totals
    tl  = ParagraphStyle("TL",  fontSize=9,
                          fontName="Helvetica", textColor=DARK_GREY, alignment=TA_RIGHT)
    tv  = ParagraphStyle("TV",  fontSize=9,
                          fontName="Helvetica", textColor=BLACK, alignment=TA_RIGHT)
    tlb = ParagraphStyle("TLB", fontSize=10,
                          fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    tvb = ParagraphStyle("TVB", fontSize=10,
                          fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    tot = Table([
        [Paragraph("Subtotal:",      tl),  Paragraph(data['subtotal'], tv)],
        [Paragraph("GST (10%):",     tl),  Paragraph(data['gst'],   tv)],
        [Paragraph("AMOUNT DUE:", tlb), Paragraph(data['total'], tvb)],
    ], colWidths=[40*mm, 30*mm])
    tot.setStyle(totals_style())
    wrapper = Table([[" ", tot]], colWidths=[USABLE_W-70*mm, 70*mm])
    wrapper.setStyle(wrapper_style())
    story += [wrapper, Spacer(1, 6*mm)]

    # Tariff information
    story.append(Paragraph("TARIFF INFORMATION", styles["SectionTitle"]))
    story.append(hr())
    story.append(Paragraph(f"Tariff Type: <b>{data['tariff_type']}</b>", styles["BodyText9"]))
    story.append(Paragraph(f"Rate: <b>{data['rate']}</b>", styles["BodyText9"]))
    story.append(Spacer(1, 6*mm))

    # Footer
    story.append(hr(colour=NAVY, thickness=1))
    story.append(Paragraph(
        f"{data['provider_name']} is registered for GST. ABN {data['abn']}",
        styles["FooterText"]))
    addr_line = ", ".join(data['address'])
    story.append(Paragraph(
        f"{addr_line}  |  Payment due by {data['due_date']}",
        styles["FooterText"]))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random utility bill PDFs with optional custom data."
    )
    parser.add_argument("--provider-name", help="Utility provider name (e.g., 'PowerFlow Energy')")
    parser.add_argument("--provider-abn", help="Provider ABN (format: XX XXX XXX XXX)")
    parser.add_argument("--customer-name", help="Customer name")
    parser.add_argument("--usage-amount", type=float, help="Usage amount (e.g., 1950 for electricity in kWh)")
    parser.add_argument("--billing-days", type=int, default=91, help="Number of billing days (default: 91)")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\utility_bills"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    existing = [f for f in os.listdir(out_dir) if f.startswith("utility_bill_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[2].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"utility_bill_{next_n:03d}.pdf")

    data = generate_utility_data(
        provider_name=args.provider_name,
        provider_abn=args.provider_abn,
        customer_name=args.customer_name,
        usage_amount=args.usage_amount,
        billing_days=args.billing_days
    )

    build_utility_bill(data, path)

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
