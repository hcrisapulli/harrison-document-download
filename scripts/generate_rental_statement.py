"""
Rental Property Statement generator.
Generates random rental statements with command-line argument support.
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
TM = BM = 18 * mm
UW = PAGE_W - LM - RM

NAVY  = colors.HexColor("#1B2A4A")
LGREY = colors.HexColor("#F5F5F5")
MGREY = colors.HexColor("#CCCCCC")
DGREY = colors.HexColor("#555555")
WHITE = colors.white
BLACK = colors.black


# Data pools for random generation
AGENCY_NAMES = [
    "ABC Rentals", "Prestige Property Management", "Elite Rental Services",
    "Premium Property Group", "First National Real Estate", "Ray White Property Management"
]

OWNER_NAMES = [
    "Lyn Test", "Sarah Chen", "John Smith", "Maria Garcia",
    "David Wilson", "Emma Thompson"
]

PROPERTY_ADDRESSES = [
    ("1 Sample St", "Wantirna South", "VIC"),
    ("8 Hawthorn Ave", "Hawthorn", "VIC"),
    ("15 Beach Road", "Brighton", "VIC"),
    ("22 High Street", "Kew", "VIC"),
    ("35 Park Lane", "Richmond", "VIC"),
    ("42 Chapel Street", "Windsor", "VIC"),
]

EXPENSE_TYPES = [
    "Plumbing", "Plumbing repairs", "Electrical work", "Advertising",
    "General Repairs and Maintenance", "Painting", "Carpet cleaning",
    "Garden maintenance", "Pest control"
]


def generate_abn():
    """Generate a valid-looking ABN."""
    return f"{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"


def generate_date(format_str="%d/%m/%Y", days_ago=0):
    """Generate a date in specified format."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime(format_str)


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def p(text, size=9, font="Helvetica", color=BLACK, align=TA_LEFT, leading=13):
    return Paragraph(text, ParagraphStyle("_", fontSize=size, fontName=font,
                     textColor=color, alignment=align, leading=leading))


def hr(c=MGREY, t=0.5):
    return HRFlowable(width=UW, thickness=t, color=c, spaceAfter=3*mm, spaceBefore=2*mm)


def build(output_path, agency_name=None, agency_abn=None, owner_name=None,
          property_address=None, period_from=None, period_to=None):
    """Build a rental statement PDF with random or specified data."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    # Generate or use provided data
    agency = agency_name or random.choice(AGENCY_NAMES)
    agency_abn_str = agency_abn or generate_abn()
    agency_phone = f"03 9{random.randint(100,999)} {random.randint(1000,9999)}"
    agency_email = f"{agency.lower().replace(' ', '')}@{agency.split()[0].lower()}.com.au"
    agency_address = f"{random.randint(1,200)} {random.choice(['Collins St', 'Queen St', 'King St'])}, Melbourne VIC 3000"

    owner = owner_name or random.choice(OWNER_NAMES)

    folio = f"{agency.split()[0][:3].upper()}-{datetime.now().year}-{random.randint(100,999)}"
    date_from = period_from or "1/07/2024"
    date_to = period_to or "30/06/2025"
    created = generate_date()

    # Property details
    if property_address:
        prop_address = property_address
    else:
        street, suburb, state = random.choice(PROPERTY_ADDRESSES)
        street_num = random.randint(1, 200)
        prop_address = f"{street_num} {street}, {suburb} {state}"

    # Generate financial data
    monthly_rent = round_to_tenth(random.uniform(1500, 3500))
    months = 12
    total_rent = round_to_tenth(monthly_rent * months)

    # Generate expenses
    expenses = []
    total_expenses = 0.0
    num_expenses = random.randint(4, 7)

    for i in range(num_expenses):
        expense_type = random.choice(EXPENSE_TYPES)
        # Ensure unique expense types
        while any(e[0] == expense_type for e in expenses):
            expense_type = random.choice(EXPENSE_TYPES)

        amount = round_to_tenth(random.uniform(50, 500))
        gst = round_to_tenth(amount * 0.1)
        total_with_gst = round_to_tenth(amount + gst)

        expenses.append((expense_type, f"${gst:.2f}", f"${total_with_gst:.2f}", ""))
        total_expenses = round_to_tenth(total_expenses + total_with_gst)

    # Management fees
    mgmt_fee = round_to_tenth(total_rent * random.uniform(0.065, 0.085))
    mgmt_gst = round_to_tenth(mgmt_fee * 0.1)
    mgmt_total = round_to_tenth(mgmt_fee + mgmt_gst)
    expenses.append(("Residential Management Fee", f"${mgmt_gst:.2f}", f"${mgmt_total:.2f}", ""))
    total_expenses = round_to_tenth(total_expenses + mgmt_total)

    # Letting fee (one-off)
    letting_fee = round_to_tenth(monthly_rent * random.uniform(0.6, 1.0))
    letting_gst = round_to_tenth(letting_fee * 0.1)
    letting_total = round_to_tenth(letting_fee + letting_gst)
    expenses.append(("Letting Fee", f"${letting_gst:.2f}", f"${letting_total:.2f}", ""))
    total_expenses = round_to_tenth(total_expenses + letting_total)

    balance = round_to_tenth(total_rent - total_expenses)

    # Calculate total GST
    total_gst = sum([float(e[1].replace("$", "").replace(",", "")) for e in expenses])

    money_in = f"${total_rent:,.2f}"
    money_out = f"${total_expenses:,.2f}"
    balance_str = f"${balance:,.2f}"

    # ── Header ────────────────────────────────────────────────────────
    contact_rows = [
        [p(f"(w) {agency_phone}", 8, color=colors.HexColor("#CCDDEE"), align=TA_RIGHT)],
        [p(agency_email,          8, color=colors.HexColor("#CCDDEE"), align=TA_RIGHT)],
        [p(agency_address,        8, color=colors.HexColor("#CCDDEE"), align=TA_RIGHT)],
        [p(f"ABN: {agency_abn_str}",  8, color=colors.HexColor("#CCDDEE"), align=TA_RIGHT)],
    ]
    contact_tbl = Table(contact_rows, colWidths=[UW * 0.42])
    contact_tbl.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))

    hdr = Table([[
        p(agency, 20, "Helvetica-Bold", WHITE),
        contact_tbl,
    ]], colWidths=[UW * 0.58, UW * 0.42])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(0,0),12),("RIGHTPADDING",(0,0),(-1,-1),8),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    # ── Owner + folio ─────────────────────────────────────────────────
    folio_rows = [
        [p("Folio:",    8, "Helvetica-Bold", DGREY, TA_RIGHT), p(folio,      9, "Helvetica-Bold", BLACK)],
        [p("From:",     8, "Helvetica-Bold", DGREY, TA_RIGHT), p(date_from,  9, "Helvetica-Bold", BLACK)],
        [p("To:",       8, "Helvetica-Bold", DGREY, TA_RIGHT), p(date_to,    9, "Helvetica-Bold", BLACK)],
        [p("Created:",  8, "Helvetica-Bold", DGREY, TA_RIGHT), p(created,    9, "Helvetica-Bold", BLACK)],
    ]
    folio_tbl = Table(folio_rows, colWidths=[22*mm, 48*mm])
    folio_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE, LGREY]),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))

    folio_section = Table([
        [p("Folio Summary", 11, "Helvetica-Bold", NAVY, TA_RIGHT)],
        [folio_tbl],
    ], colWidths=[UW * 0.45])
    folio_section.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))

    owner_block = Table([[p(owner, 9, "Helvetica-Bold", BLACK)]],
                         colWidths=[UW * 0.55])
    owner_block.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))

    top = Table([[owner_block, folio_section]], colWidths=[UW * 0.55, UW * 0.45])
    top.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    story += [top, Spacer(1, 6*mm)]

    # ── Summary panels ────────────────────────────────────────────────
    panels = []
    for label, value, bg in [
        ("Money In",  money_in,     colors.HexColor("#F5F5F5")),
        ("Money Out", money_out,    colors.HexColor("#F5F5F5")),
        ("Balance",   balance_str,  colors.HexColor("#F5F5F5")),
    ]:
        c = Table([
            [p(label, 9, "Helvetica-Bold", DGREY, TA_CENTER)],
            [p(value, 13, "Helvetica-Bold", BLACK, TA_CENTER)],
        ], colWidths=[(UW / 3) - 4*mm])
        c.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),bg),
            ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
            ("BOX",(0,0),(-1,-1),0.5,MGREY),
        ]))
        panels.append(c)

    panel_row = Table([panels], colWidths=[(UW / 3)] * 3)
    panel_row.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    story += [panel_row, Spacer(1, 5*mm)]

    # ── Transactions table ────────────────────────────────────────────
    cw = [UW * 0.42, 28*mm, 30*mm, 30*mm]

    th_s  = ParagraphStyle("TH",  fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr_s = ParagraphStyle("THR", fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE,  alignment=TA_RIGHT)
    td_s  = ParagraphStyle("TD",  fontSize=9,   fontName="Helvetica",      textColor=DGREY)
    tdr_s = ParagraphStyle("TDR", fontSize=9,   fontName="Helvetica",      textColor=DGREY,  alignment=TA_RIGHT)
    tdb_s = ParagraphStyle("TDB", fontSize=9,   fontName="Helvetica-Bold", textColor=BLACK)
    tdbr_s= ParagraphStyle("TDBR",fontSize=9,   fontName="Helvetica-Bold", textColor=BLACK,  alignment=TA_RIGHT)
    prop_s= ParagraphStyle("PROP",fontSize=9,   fontName="Helvetica-Bold", textColor=BLACK)

    rows = [[
        Paragraph("Account",      th_s),
        Paragraph("Included Tax", thr_s),
        Paragraph("Money Out",    thr_s),
        Paragraph("Money In",     thr_s),
    ]]

    # Property address row
    rows.append([
        Paragraph(prop_address, prop_s),
        Paragraph("", td_s),
        Paragraph("", td_s),
        Paragraph("", td_s),
    ])

    # Rent income
    rows.append([
        Paragraph("Rent", td_s),
        Paragraph("", tdr_s),
        Paragraph("", tdr_s),
        Paragraph(money_in, tdr_s),
    ])

    # Expenses
    for expense in expenses:
        rows.append([
            Paragraph(expense[0], td_s),
            Paragraph(expense[1], tdr_s),
            Paragraph(expense[2], tdr_s),
            Paragraph(expense[3], tdr_s),
        ])

    # Subtotal row
    rows.append([
        Paragraph("Subtotal", tdb_s),
        Paragraph("", tdbr_s),
        Paragraph(money_out, tdbr_s),
        Paragraph(money_in,  tdbr_s),
    ])

    tbl = Table(rows, colWidths=cw, repeatRows=1)

    # Property row index
    prop_row_idx = 1

    style_cmds = [
        ("BACKGROUND",(0,0),(-1,0),NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, LGREY]),
        ("ALIGN",(1,1),(-1,-1),"RIGHT"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("GRID",(0,0),(-1,-1),0.3,MGREY),
        ("LINEABOVE",(0,-1),(-1,-1),1,NAVY),
        ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#E8F0FB")),
        ("BACKGROUND",(0,prop_row_idx),(-1,prop_row_idx),colors.HexColor("#D8E8FF")),
        ("FONTNAME",(0,prop_row_idx),(-1,prop_row_idx),"Helvetica-Bold"),
    ]

    tbl.setStyle(TableStyle(style_cmds))
    story += [tbl, Spacer(1, 5*mm)]

    # ── Total row ─────────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    tot_tbl = Table([[
        p("Total", 9, "Helvetica-Bold", BLACK),
        p("", tdbr_s.alignment),
        p(money_out, 9, "Helvetica-Bold", BLACK, TA_RIGHT),
        p(money_in,  9, "Helvetica-Bold", BLACK, TA_RIGHT),
    ]], colWidths=cw)
    tot_tbl.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
    ]))
    story += [tot_tbl,
              p(f"Total Tax on Money Out: ${total_gst:.2f}", 9, color=DGREY),
              Spacer(1, 8*mm)]

    # ── Footer ────────────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    story.append(p(f"{agency}  |  ABN {agency_abn_str}  |  {agency_address}",
                   7.5, color=DGREY, align=TA_CENTER, leading=11))
    story.append(p("This statement is produced for the financial year specified above and is for the owner's records.",
                   7.5, color=DGREY, align=TA_CENTER, leading=11))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random rental statement PDFs with optional custom data."
    )
    parser.add_argument("--agency-name", help="Property management agency name")
    parser.add_argument("--agency-abn", help="Agency ABN (format: XX XXX XXX XXX)")
    parser.add_argument("--owner-name", help="Property owner name")
    parser.add_argument("--property-address", help="Rental property address")
    parser.add_argument("--period-from", help="Period start date (DD/MM/YYYY)")
    parser.add_argument("--period-to", help="Period end date (DD/MM/YYYY)")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\rental_statements"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    existing = [f for f in os.listdir(out_dir) if f.startswith("rental_statement_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[2].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"rental_statement_{next_n:03d}.pdf")

    build(
        path,
        agency_name=args.agency_name,
        agency_abn=args.agency_abn,
        owner_name=args.owner_name,
        property_address=args.property_address,
        period_from=args.period_from,
        period_to=args.period_to
    )

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
