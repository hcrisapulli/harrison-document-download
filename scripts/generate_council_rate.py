"""
Council Rate generator.
Generates random council rate notices with command-line argument support.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, HRFlowable, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
import os
import random
import argparse
from datetime import datetime, timedelta

PAGE_W, PAGE_H = A4
LM = RM = 18 * mm
TM = BM = 18 * mm
UW = PAGE_W - LM - RM

GREEN       = colors.HexColor("#2E6B3E")
LIGHT_GREEN = colors.HexColor("#EAF4EC")
GOLD        = colors.HexColor("#C8901A")
LGREY       = colors.HexColor("#F5F5F5")
MGREY       = colors.HexColor("#CCCCCC")
DGREY       = colors.HexColor("#555555")
WHITE       = colors.white
BLACK       = colors.black


# Data pools for random generation
COUNCILS = [
    ("BOROONDARA", "City of harmony"),
    ("YARRA CITY COUNCIL", "Inner Melbourne"),
    ("PORT PHILLIP", "City by the bay"),
    ("STONNINGTON", "Premier community"),
    ("MELBOURNE", "Capital city"),
    ("DAREBIN", "Thriving community"),
]

OWNER_NAMES = [
    "H & P Hogwarts Superannuation Fund", "BGL Corp Super Fund",
    "Chen Family Trust", "Johnson Investment Holdings",
    "Smith Property Fund Pty Ltd", "Wilson Holdings Trust"
]

PROPERTY_ADDRESSES = [
    ("47 Kent Street", "SEBASTOPOL", "VIC", "2356"),
    ("15 Smith Street", "FITZROY", "VIC", "3065"),
    ("22 Beach Road", "SANDRINGHAM", "VIC", "3191"),
    ("8 High Street", "KEW", "VIC", "3101"),
    ("35 Chapel Street", "WINDSOR", "VIC", "3181"),
]

WARDS = ["Junction", "Fitzroy", "Gardenvale", "Studley", "Windsor"]


def generate_abn():
    """Generate a valid-looking ABN."""
    return f"{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"


def generate_date(days_ago=0):
    """Generate a date in DD/MM/YYYY format."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%d/%m/%Y")


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def p(text, size=9, font="Helvetica", color=BLACK, align=TA_LEFT, leading=13):
    return Paragraph(text, ParagraphStyle("_", fontSize=size, fontName=font,
                     textColor=color, alignment=align, leading=leading))


def hr(c=MGREY, t=0.5):
    return HRFlowable(width=UW, thickness=t, color=c, spaceAfter=3*mm, spaceBefore=2*mm)


def build(output_path, council_name=None, ratepayer_name=None, property_address=None,
          property_value=None, total_rates=None):
    """Build a council rate notice PDF with random or specified data."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    # Generate or use provided data
    if council_name:
        c_name = council_name
        c_sub = "Local Government Area"
    else:
        c_name, c_sub = random.choice(COUNCILS)

    abn = generate_abn()
    period = "1 July 2024 to 30 June 2025"

    owner_name = ratepayer_name or random.choice(OWNER_NAMES)
    owner_address = [f"PO Box {random.randint(1000, 9999)}",
                     f"BALLARAT VIC {random.randint(3300, 3500)}"]

    # Property details
    if property_address:
        prop_address = property_address
    else:
        street, suburb, state, postcode = random.choice(PROPERTY_ADDRESSES)
        prop_address = f"{street}, {suburb} {state} {postcode}"

    prop_num = str(random.randint(100000, 999999))
    issue_date = generate_date(random.randint(30, 90))
    ref_num = str(random.randint(10000000, 99999999))
    declared_date = generate_date(random.randint(150, 200))

    # Property values
    if property_value:
        civ = property_value
    else:
        civ = random.randint(400000, 1500000)

    site_value = int(civ * random.uniform(0.15, 0.25))
    nav = int(civ * random.uniform(0.04, 0.06))

    ward = random.choice(WARDS)

    # Calculate rates
    if total_rates:
        total = round_to_tenth(total_rates)
    else:
        total = round_to_tenth(civ * random.uniform(0.0008, 0.0015))

    waste_levy = round_to_tenth(random.uniform(100, 200))
    general_rate = round_to_tenth(total * random.uniform(0.75, 0.85))
    council_subtotal = round_to_tenth(waste_levy + general_rate)

    # Fire services levy
    fire_fixed = round_to_tenth(random.uniform(110, 125))
    fire_variable = round_to_tenth(civ * random.uniform(0.00004, 0.00008))
    fire_subtotal_current = round_to_tenth(fire_fixed + fire_variable)
    fire_subtotal_prior = round_to_tenth(fire_subtotal_current * random.uniform(0.95, 1.05))

    total_due = round_to_tenth(council_subtotal + fire_subtotal_current)
    due_date_obj = datetime.now() + timedelta(days=random.randint(180, 240))
    due_date = due_date_obj.strftime("%d.%m.%Y")

    property_meta = [
        ("Property number",       prop_num),
        ("Issue date",            issue_date),
        ("Reference number",      ref_num),
        ("Date rates declared",   declared_date),
        ("Capital improved value",f"${civ:,}"),
        ("Site value",            f"${site_value:,}"),
        ("Net annual value",      f"${nav:,}"),
        ("Ward",                  ward),
    ]

    council_charges = [
        ("Waste Environment Levy", f"${waste_levy:.2f}"),
        ("General Rate",           f"${general_rate:.2f}"),
    ]

    fire_charges = [
        ("Fire Service Levy Residential Fixed Charge",
         f"${fire_fixed:.2f}", f"${fire_fixed * 0.98:.2f}"),
        ("Fire Service Levy Residential Variable Rate 1.345678 X CIV",
         f"${fire_variable:.2f}", f"${fire_variable * 0.95:.2f}"),
    ]

    # ── Header banner ─────────────────────────────────────────────────
    name_block = Table([
        [p(c_name, 16, "Helvetica-Bold", WHITE)],
        [p(c_sub,   8, "Helvetica-Oblique", colors.HexColor("#AADDAA"), leading=10)],
    ], colWidths=[58*mm], style=TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    hdr = Table([[name_block,
                  p("Annual valuation and rate notice", 16, "Helvetica-Bold", WHITE, TA_RIGHT)]],
                colWidths=[62*mm, UW - 62*mm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),GREEN),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(0,0),10),("RIGHTPADDING",(-1,0),(-1,0),10),
        ("LEFTPADDING",(1,0),(1,0),4),
    ]))
    story += [hdr, Spacer(1, 3*mm)]
    story.append(p(f"ABN {abn}  |  {period}", 8, color=DGREY))
    story.append(Spacer(1, 5*mm))

    # ── Three-column layout: address | property meta | due panel ──────
    # Address block
    addr_rows = [[p(owner_name, 9, "Helvetica-Bold", BLACK)]]
    for line in owner_address:
        addr_rows.append([p(line, 9, color=DGREY)])
    addr_tbl = Table(addr_rows, colWidths=[UW * 0.27], style=TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))

    # Property meta
    ml = ParagraphStyle("ML", fontSize=8.5, fontName="Helvetica",      textColor=DGREY)
    mv = ParagraphStyle("MV", fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)
    meta_rows = [[Paragraph(r[0], ml), Paragraph(r[1], mv)] for r in property_meta]
    meta_tbl = Table(meta_rows, colWidths=[UW * 0.28, UW * 0.20])
    meta_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE, LGREY]),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("GRID",(0,0),(-1,-1),0.3,MGREY),
    ]))

    # Due panel
    due_tbl = Table([
        [p("Total amount due", 9, "Helvetica-Bold", GREEN, TA_RIGHT)],
        [p(f"${total_due:,.2f}",    20, "Helvetica-Bold", GOLD,  TA_RIGHT)],
        [p(f"by {due_date}", 10, "Helvetica-Bold", GREEN, TA_RIGHT)],
    ], colWidths=[UW * 0.25])
    due_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT_GREEN),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("BOX",(0,0),(-1,-1),1,GREEN),
    ]))

    row = Table([[addr_tbl, meta_tbl, due_tbl]],
                colWidths=[UW * 0.27, UW * 0.48, UW * 0.25])
    row.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(1,0),(1,0),6),
    ]))
    story += [row, Spacer(1, 6*mm)]

    # ── Property location ─────────────────────────────────────────────
    story.append(p("Property location", 10, "Helvetica-Bold", GREEN))
    story.append(hr(GREEN))
    story.append(p(prop_address, 9, "Helvetica-Bold", BLACK))
    story.append(p("AVPCC - 125-Strata Unit or Flat  Residential", 9, color=DGREY))
    story.append(Spacer(1, 5*mm))

    # ── Council charges table ─────────────────────────────────────────
    story.append(p("Details of Council rates and charges", 10, "Helvetica-Bold", GREEN))
    story.append(Spacer(1, 2*mm))

    th   = ParagraphStyle("TH",  fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr  = ParagraphStyle("THR", fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td   = ParagraphStyle("TD",  fontSize=9,   fontName="Helvetica",      textColor=DGREY)
    tdr  = ParagraphStyle("TDR", fontSize=9,   fontName="Helvetica",      textColor=DGREY, alignment=TA_RIGHT)
    tdb  = ParagraphStyle("TDB", fontSize=9,   fontName="Helvetica-Bold", textColor=BLACK)
    tdbr = ParagraphStyle("TDBR",fontSize=9,   fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)

    crows = [[Paragraph("Charge", th), Paragraph("Amount", thr)]]
    for charge, amt in council_charges:
        crows.append([Paragraph(charge, td), Paragraph(amt, tdr)])
    crows.append([Paragraph("SUB TOTAL", tdb), Paragraph(f"${council_subtotal:.2f}", tdbr)])
    ct = Table(crows, colWidths=[UW * 0.72, UW * 0.28])
    ct.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),GREEN),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[WHITE, LGREY]),
        ("LINEABOVE",(0,-1),(-1,-1),0.5,GREEN),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("GRID",(0,1),(-1,-2),0.3,MGREY),
    ]))
    story += [ct, Spacer(1, 5*mm)]

    # ── Fire services levy table ──────────────────────────────────────
    story.append(p("Details of State Government Fire Services Property Levy",
                   10, "Helvetica-Bold", GREEN))
    story.append(Spacer(1, 2*mm))
    frows = [[Paragraph("Charge", th),
              Paragraph("2025", thr),
              Paragraph("2024", thr)]]
    for charge, cur, pri in fire_charges:
        frows.append([Paragraph(charge, td), Paragraph(cur, tdr), Paragraph(pri, tdr)])
    frows.append([Paragraph("SUB TOTAL", tdb),
                  Paragraph(f"${fire_subtotal_current:.2f}", tdbr),
                  Paragraph(f"${fire_subtotal_prior:.2f}",   tdbr)])
    ft = Table(frows, colWidths=[UW * 0.58, UW * 0.21, UW * 0.21])
    ft.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),GREEN),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[WHITE, LGREY]),
        ("LINEABOVE",(0,-1),(-1,-1),0.5,GREEN),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("GRID",(0,1),(-1,-2),0.3,MGREY),
        ("ALIGN",(1,0),(-1,-1),"RIGHT"),
    ]))
    story += [ft, Spacer(1, 5*mm)]

    # ── Total ─────────────────────────────────────────────────────────
    story.append(hr(GREEN, 1))
    tot = Table([[
        p("TOTAL AMOUNT DUE:", 12, "Helvetica-Bold", GREEN),
        p(f"${total_due:,.2f}",      14, "Helvetica-Bold", GOLD,  TA_RIGHT),
    ]], colWidths=[UW * 0.6, UW * 0.4])
    tot.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    story += [tot, Spacer(1, 6*mm)]

    # Payment Options - Four Quarterly Installments (wrapped in KeepTogether)
    payment_section = []
    payment_section.append(p("Payment options", 10, "Helvetica-Bold", GREEN))
    payment_section.append(hr(GREEN))
    payment_section.append(p("Pay your rates in 4 installments throughout the year. Each installment is due on the following dates:", 9, color=DGREY))
    payment_section.append(Spacer(1, 3*mm))

    # Calculate 4 equal installments (25% each)
    installment_amount = round_to_tenth(total_due / 4)

    # Standard Victorian council installment due dates
    current_year = datetime.now().year
    next_year = current_year + 1

    # Determine which year to use based on current date
    if datetime.now().month < 6:
        # Before June - use previous year's rating period
        base_year = current_year - 1
    else:
        # After June - use current year's rating period
        base_year = current_year

    installment_dates = [
        datetime(base_year, 9, 30),      # 1st: 30 September
        datetime(base_year, 11, 30),     # 2nd: 30 November
        datetime(base_year + 1, 2, 28),  # 3rd: 28 February (or 29 in leap year)
        datetime(base_year + 1, 5, 31),  # 4th: 31 May
    ]

    # Adjust for leap year
    if (base_year + 1) % 4 == 0 and ((base_year + 1) % 100 != 0 or (base_year + 1) % 400 == 0):
        installment_dates[2] = datetime(base_year + 1, 2, 29)

    installments = []
    for i, inst_date in enumerate(installment_dates):
        installments.append({
            "number": i + 1,
            "date": inst_date.strftime("%d.%m.%Y"),
            "amount": installment_amount
        })

    # Adjust last installment to ensure total matches exactly (handle rounding)
    total_installments = round_to_tenth(installment_amount * 4)
    if total_installments != total_due:
        installments[3]["amount"] = round_to_tenth(installment_amount + (total_due - total_installments))

    # Create installments table
    inst_th = ParagraphStyle("ITH", fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    inst_thc = ParagraphStyle("ITHC", fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    inst_thr = ParagraphStyle("ITHR", fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    inst_td = ParagraphStyle("ITD", fontSize=9, fontName="Helvetica", textColor=DGREY)
    inst_tdc = ParagraphStyle("ITDC", fontSize=9, fontName="Helvetica", textColor=DGREY, alignment=TA_CENTER)
    inst_tdr = ParagraphStyle("ITDR", fontSize=9, fontName="Helvetica", textColor=DGREY, alignment=TA_RIGHT)

    inst_rows = [[Paragraph("Installment", inst_th),
                  Paragraph("Due Date", inst_thc),
                  Paragraph("Amount", inst_thr)]]

    for inst in installments:
        inst_rows.append([
            Paragraph(f"Installment {inst['number']}", inst_td),
            Paragraph(inst['date'], inst_tdc),
            Paragraph(f"${inst['amount']:.2f}", inst_tdr)
        ])

    inst_table = Table(inst_rows, colWidths=[UW * 0.30, UW * 0.35, UW * 0.35], repeatRows=1)
    inst_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GREEN),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LGREY]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("GRID", (0,0), (-1,-1), 0.3, MGREY),
    ]))
    inst_table.hAlign = "LEFT"

    payment_section.append(inst_table)
    payment_section.append(Spacer(1, 4*mm))

    # Payment reminder note
    payment_section.append(p("<b>Important:</b> You must pay by the due date to avoid interest and collection costs.",
                   8, color=DGREY, leading=11))
    payment_section.append(Spacer(1, 6*mm))

    # Add entire payment section as KeepTogether to prevent page breaks
    story.append(KeepTogether(payment_section))

    # ── Footer ────────────────────────────────────────────────────────
    story.append(hr(GREEN, 1))
    story.append(p(f"{c_name}  |  ABN {abn}  |  council.vic.gov.au  |  9278 4444",
                   7.5, color=DGREY, align=TA_CENTER, leading=11))
    story.append(p("47 Camberwell Road, Hawthorn East VIC 3123", 7.5, color=DGREY, align=TA_CENTER, leading=11))
    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random council rate PDFs with optional custom data."
    )
    parser.add_argument("--council-name", help="Council name (e.g., BOROONDARA)")
    parser.add_argument("--ratepayer-name", help="Ratepayer name")
    parser.add_argument("--property-address", help="Property address")
    parser.add_argument("--property-value", type=int, help="Capital improved value")
    parser.add_argument("--total-rates", type=float, help="Total rates amount")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\council_rates"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    existing = [f for f in os.listdir(out_dir) if f.startswith("council_rate_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[2].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"council_rate_{next_n:03d}.pdf")

    build(
        path,
        council_name=args.council_name,
        ratepayer_name=args.ratepayer_name,
        property_address=args.property_address,
        property_value=args.property_value,
        total_rates=args.total_rates
    )

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
