"""
Property Settlement / Statement of Adjustments generator.
Generates random property settlement statements with command-line argument support.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, HRFlowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
import os
import random
import argparse
from datetime import datetime, timedelta

PAGE_W, PAGE_H = A4
LM = RM = 18 * mm
TM = BM = 20 * mm
UW = PAGE_W - LM - RM

NAVY  = colors.HexColor("#1B2A4A")
NAVY2 = colors.HexColor("#2E5090")
LGREY = colors.HexColor("#F4F4F4")
MGREY = colors.HexColor("#CCCCCC")
DGREY = colors.HexColor("#555555")
WHITE = colors.white
BLACK = colors.black


# Data pools for random generation
SURNAMES = [
    "YANG", "CHEN", "NGUYEN", "PATEL", "SMITH", "JONES",
    "WILLIAMS", "BROWN", "WILSON", "TAYLOR", "ANDERSON"
]

PROPERTY_STREETS = [
    ("Jean Street", "Cheltenham"), ("Maple Grove", "Box Hill"),
    ("Kent Road", "Pascoe Vale"), ("High Street", "Glen Iris"),
    ("Park Avenue", "Brighton"), ("Beach Road", "Sandringham"),
    ("Station Street", "Oakleigh"), ("Main Road", "Eltham")
]

COUNCILS = [
    "Kingston City Council", "Whitehorse City Council", "Moreland City Council",
    "Boroondara City Council", "Bayside City Council", "Glen Eira City Council"
]

WATER_AUTHORITIES = [
    "South East Water", "Yarra Valley Water", "City West Water"
]


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
    return HRFlowable(width=UW, thickness=t, color=c, spaceAfter=4*mm, spaceBefore=2*mm)


def build(output_path, vendor_name=None, purchaser_name=None, property_address=None,
          purchase_price=None, deposit_paid=None):
    """Build a property settlement statement PDF with random or specified data."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    td   = ParagraphStyle("TD",   fontSize=9, fontName="Helvetica",      textColor=DGREY, leading=13)
    td_r = ParagraphStyle("TDR",  fontSize=9, fontName="Helvetica",      textColor=DGREY, alignment=TA_RIGHT)
    td_b = ParagraphStyle("TDB",  fontSize=9, fontName="Helvetica-Bold", textColor=BLACK)
    td_br= ParagraphStyle("TDBR", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)

    # Generate or use provided data
    vendor = vendor_name or random.choice(SURNAMES)
    purchaser = purchaser_name or random.choice([s for s in SURNAMES if s != vendor])
    parties = f"{purchaser} FROM {vendor}"

    if property_address:
        prop_address = property_address
    else:
        street, suburb = random.choice(PROPERTY_STREETS)
        street_num = random.randint(1, 150)
        prop_address = f"{street_num} {street}, {suburb}, Victoria"

    settlement_date = generate_date(random.randint(0, 30))
    adjustment_date = settlement_date

    # Financial details
    if purchase_price:
        price = purchase_price
    else:
        price = random.randint(500000, 1500000)
        price = round(price / 1000) * 1000  # Round to nearest thousand

    if deposit_paid:
        deposit = deposit_paid
    else:
        deposit = round(price * 0.10)  # 10% deposit

    balance = price - deposit

    # Generate adjustments
    council = random.choice(COUNCILS)
    council_annual = round_to_tenth(random.uniform(1200, 2500))
    council_days = random.randint(10, 30)
    council_adj = round_to_tenth(council_annual * council_days / 365)

    water_auth = random.choice(WATER_AUTHORITIES)
    adjustments = []

    # Council rates adjustment
    adjustments.append((
        f"{council} - Rates, Charges & Levies\n"
        f"${council_annual:,.2f} Annually, paid to 30/06/{datetime.now().year + 1}\n"
        f"Vendor allows {council_days} days",
        f"${council_adj:.2f}", ""
    ))

    # Water charges
    num_water_charges = random.randint(2, 4)
    total_purchaser_adj = 0.0

    for i in range(num_water_charges):
        charge_type = random.choice(["Parks & Gardens", "Drainage", "Water Service Charge", "Sewerage Service Charge"])
        charge_annual = round_to_tenth(random.uniform(20, 100))
        charge_days = random.randint(60, 90)
        charge_adj = round_to_tenth(charge_annual * charge_days / 365)
        total_purchaser_adj = round_to_tenth(total_purchaser_adj + charge_adj)

        adjustments.append((
            f"{water_auth} - {charge_type} ${charge_annual:.2f} Quarterly, paid to 30/09/{datetime.now().year}\n"
            f"Purchaser allows {charge_days} days",
            "", f"${charge_adj:.2f}"
        ))

    # Owners corporation (random chance)
    if random.choice([True, False]):
        oc_monthly = round_to_tenth(random.uniform(400, 800))
        oc_days = random.randint(60, 90)
        oc_adj = round_to_tenth(oc_monthly * oc_days / 30)
        total_purchaser_adj = round_to_tenth(total_purchaser_adj + oc_adj)

        adjustments.append((
            f"Owners Corporation Fees on Plan No. {random.randint(100000, 999999)}T\n"
            f"${oc_monthly:.2f} Monthly, paid to 30/09/{datetime.now().year}\n"
            f"Purchaser allows {oc_days} days",
            "", f"${oc_adj:.2f}"
        ))

    # Mortgage discharge
    mortgage_discharge = round_to_tenth(114.40)
    adjustments.append(("Discharge of Mortgage - Electronic", f"${mortgage_discharge:.2f}", ""))

    # Calculate totals
    vendor_total = round_to_tenth(council_adj + mortgage_discharge)
    purchaser_total = round_to_tenth(total_purchaser_adj)
    net_adjustment = round_to_tenth(vendor_total - purchaser_total)

    balance_due = round_to_tenth(balance + net_adjustment)

    # Settlement cheques
    cheques = []
    if total_purchaser_adj > 0:
        cheques.append((water_auth, f"${total_purchaser_adj:.2f}"))

    if "Owners Corporation" in str(adjustments):
        for adj in adjustments:
            if "Owners Corporation" in adj[0]:
                # Extract the monthly amount
                oc_line = adj[0]
                import re
                match = re.search(r'\$([0-9,.]+) Monthly', oc_line)
                if match:
                    oc_amount = match.group(1)
                    cheques.append(("Owners Corporation", f"${oc_amount}"))

    # Remaining balance to vendor
    cheques_total = round_to_tenth(sum([float(c[1].replace("$", "").replace(",", "")) for c in cheques]))
    vendor_cheque = round_to_tenth(balance_due - cheques_total)
    cheques.append(("As directed by Vendor", f"${vendor_cheque:,.2f}"))

    # ── Header ────────────────────────────────────────────────────────
    hdr = Table([[
        p("STATEMENT OF ADJUSTMENTS", 16, "Helvetica-Bold", WHITE, TA_CENTER),
    ]], colWidths=[UW])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 12),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
    ]))
    story += [hdr, Spacer(1, 4*mm)]

    # ── Property + dates ───────────────────────────────────────────────
    story.append(p(parties, 11, "Helvetica-Bold", NAVY))
    story.append(p(f"Property: {prop_address}", 9, color=DGREY))
    story.append(p(f"Date of Adjustment: {adjustment_date}", 9, color=DGREY))
    story.append(p(f"Date of Settlement: {settlement_date}", 9, color=DGREY))
    story.append(Spacer(1, 4*mm))

    # ── Adjustments table ──────────────────────────────────────────────
    col_w = [UW * 0.60, UW * 0.20, UW * 0.20]

    # Column header row
    adj_hdr = Table([[
        p("", 9, "Helvetica-Bold", BLACK),
        p("Vendor", 9, "Helvetica-Bold", WHITE, TA_CENTER),
        p("Purchaser", 9, "Helvetica-Bold", WHITE, TA_CENTER),
    ]], colWidths=col_w)
    adj_hdr.setStyle(TableStyle([
        ("BACKGROUND",    (1,0),(1,0), NAVY),
        ("BACKGROUND",    (2,0),(2,0), NAVY2),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
    ]))
    story.append(adj_hdr)

    # Adjustment rows
    adj_data = []
    for item in adjustments:
        adj_data.append([
            Paragraph(item[0], td),
            Paragraph(item[1], td_r),
            Paragraph(item[2], td_r),
        ])
    # Totals row
    adj_data.append([
        Paragraph("Less Vendor's Proportion", td_b),
        Paragraph(f"${vendor_total:.2f}", td_br),
        Paragraph(f"${purchaser_total:.2f}", td_br),
    ])

    adj_tbl = Table(adj_data, colWidths=col_w)
    cmds = [
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("GRID",          (0,0),(-1,-1), 0.3, MGREY),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ("LINEABOVE",     (0,-1),(-1,-1), 1, NAVY),
        ("BACKGROUND",    (0,-1),(-1,-1), colors.HexColor("#E8F0FB")),
    ]
    for i in range(len(adj_data) - 1):
        bg = WHITE if i % 2 == 0 else LGREY
        cmds.append(("BACKGROUND", (0,i),(-1,i), bg))
    adj_tbl.setStyle(TableStyle(cmds))
    story.append(adj_tbl)
    story.append(Spacer(1, 4*mm))

    # Net adjustment box
    net_row = Table([[
        p("PURCHASER TO PAY VENDOR",
          11, "Helvetica-Bold", NAVY),
        p(f"${net_adjustment:,.2f}",
          13, "Helvetica-Bold", NAVY, TA_RIGHT),
    ]], colWidths=[UW * 0.6, UW * 0.4])
    net_row.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#D8E8FF")),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
        ("BOX",           (0,0),(-1,-1), 1, NAVY),
    ]))
    story += [net_row, Spacer(1, 4*mm)]

    # ── Settlement statement ───────────────────────────────────────────
    story.append(p("SETTLEMENT STATEMENT", 11, "Helvetica-Bold", NAVY))
    story.append(hr(NAVY))

    settle_rows = [
        ["Purchase Price",     f"${price:,.2f}"],
        ["Less Deposit Paid",  f"${deposit:,.2f}"],
        ["Balance",            f"${balance:,.2f}"],
        ["Plus adjustments",   f"${net_adjustment:,.2f}"],
    ]
    settle_tbl = Table(
        [[p(r[0], 9, color=DGREY), p(r[1], 9, "Helvetica-Bold", BLACK, TA_RIGHT)]
         for r in settle_rows],
        colWidths=[UW * 0.65, UW * 0.35])
    settle_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, LGREY, WHITE, LGREY]),
        ("LINEABOVE",      (0,2),(-1,2),  0.5, MGREY),
        ("TOPPADDING",     (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 4),
        ("LEFTPADDING",    (0,0),(-1,-1), 4),
        ("RIGHTPADDING",   (0,0),(-1,-1), 4),
    ]))

    balance_due_tbl = Table([[
        p("BALANCE DUE TO VENDOR",  11, "Helvetica-Bold", WHITE),
        p(f"${balance_due:,.2f}", 13, "Helvetica-Bold", WHITE, TA_RIGHT),
    ]], colWidths=[UW * 0.65, UW * 0.35])
    balance_due_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
    ]))
    story += [settle_tbl, Spacer(1, 3*mm), balance_due_tbl, Spacer(1, 4*mm)]

    # ── Settlement cheques ─────────────────────────────────────────────
    story.append(p("SETTLEMENT CHEQUES", 11, "Helvetica-Bold", NAVY))
    story.append(hr(NAVY))

    cheque_tbl = Table(
        [[p(r[0], 9, color=DGREY), p(r[1], 9, "Helvetica-Bold", BLACK, TA_RIGHT)]
         for r in cheques],
        colWidths=[UW * 0.65, UW * 0.35])
    cheque_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, LGREY]),
        ("TOPPADDING",     (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 4),
        ("LEFTPADDING",    (0,0),(-1,-1), 4),
        ("RIGHTPADDING",   (0,0),(-1,-1), 4),
        ("GRID",           (0,0),(-1,-1), 0.3, MGREY),
    ]))

    total_cheques = Table([[
        p("TOTAL CHEQUES", 10, "Helvetica-Bold", WHITE),
        p(f"${balance_due:,.2f}", 11, "Helvetica-Bold", WHITE, TA_RIGHT),
    ]], colWidths=[UW * 0.65, UW * 0.35])
    total_cheques.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("RIGHTPADDING",  (0,0),(-1,-1), 8),
    ]))
    story += [cheque_tbl, Spacer(1, 3*mm), total_cheques, Spacer(1, 4*mm)]

    # ── Footer ─────────────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    story.append(p(
        "This statement of adjustments is prepared for settlement purposes only "
        "and does not constitute legal advice.",
        7.5, color=DGREY, align=TA_CENTER, leading=11))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random property settlement PDFs with optional custom data."
    )
    parser.add_argument("--vendor-name", help="Vendor surname")
    parser.add_argument("--purchaser-name", help="Purchaser surname")
    parser.add_argument("--property-address", help="Property address")
    parser.add_argument("--purchase-price", type=int, help="Purchase price")
    parser.add_argument("--deposit-paid", type=int, help="Deposit paid")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\property_settlements"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    existing = [f for f in os.listdir(out_dir) if f.startswith("property_settlement_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[2].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"property_settlement_{next_n:03d}.pdf")

    build(
        path,
        vendor_name=args.vendor_name,
        purchaser_name=args.purchaser_name,
        property_address=args.property_address,
        purchase_price=args.purchase_price,
        deposit_paid=args.deposit_paid
    )

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
