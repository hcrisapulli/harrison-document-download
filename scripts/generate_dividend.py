"""
Dividend Statement generator.
Generates random dividend statements with command-line argument support.
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
LGREY = colors.HexColor("#F4F4F4")
MGREY = colors.HexColor("#CCCCCC")
DGREY = colors.HexColor("#555555")
WHITE = colors.white
BLACK = colors.black


# Data pools for random generation
COMPANIES = [
    ("BHP GROUP LIMITED", "49 004 028 077"),
    ("COMMONWEALTH BANK OF AUSTRALIA", "48 123 123 124"),
    ("TELSTRA CORPORATION LIMITED", "33 051 775 556"),
    ("WESFARMERS LIMITED", "28 008 984 049"),
    ("WOOLWORTHS GROUP LIMITED", "88 000 014 675"),
    ("NATIONAL AUSTRALIA BANK LIMITED", "12 004 044 937"),
]

INVESTOR_NAMES = [
    "MR LYN TEST <LYN DOC V2 TEST SMSF A/C>",
    "MS SARAH CHEN <CHEN SUPER FUND A/C>",
    "MR & MRS JOHNSON <JOHNSON FAMILY TRUST A/C>",
    "BGL CORP <CORPORATE INVESTMENT A/C>",
    "SMITH FAMILY SUPER FUND PTY LTD",
    "WILSON HOLDINGS <WILSON SUPER FUND A/C>",
]

REGISTRARS = [
    ("Link Market Services Limited", "Locked Bag A14, Sydney South, NSW, 1235", "1300 554 474"),
    ("Computershare Investor Services Pty Ltd", "GPO Box 2975, Melbourne VIC 3001", "1300 656 780"),
    ("Boardroom Pty Limited", "GPO Box 3993, Sydney NSW 2001", "1300 737 760"),
]

BANKS = [
    ("COMMONWEALTH BANK OF AUSTRALIA", "067-167"),
    ("WESTPAC BANKING CORPORATION", "032-001"),
    ("NATIONAL AUSTRALIA BANK", "083-004"),
    ("AUSTRALIA AND NEW ZEALAND BANKING GROUP", "013-006"),
]

SUBURBS = [
    ("BRIGHTON EAST", "VIC", "3187"), ("MELBOURNE", "VIC", "3000"),
    ("SYDNEY", "NSW", "2000"), ("BRISBANE", "QLD", "4000"),
    ("HAWTHORN", "VIC", "3122"), ("FITZROY", "VIC", "3065")
]

STREET_NAMES = [
    "HAWTHORN RD", "COLLINS STREET", "GEORGE STREET", "KING STREET",
    "QUEEN STREET", "BOURKE STREET", "ELIZABETH STREET"
]


def generate_date(days_ago=0):
    """Generate a date in DD Month YYYY format."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%d %B %Y")


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def generate_address():
    """Generate a random Australian address."""
    unit = random.choice([f"{random.randint(1,20)}/{random.randint(100,999)}", str(random.randint(1,500))])
    street = random.choice(STREET_NAMES)
    suburb, state, postcode = random.choice(SUBURBS)
    return [f"{unit} {street}", suburb, f"{state} {postcode}"]


def p(text, size=9, font="Helvetica", color=BLACK, align=TA_LEFT, leading=13):
    return Paragraph(text, ParagraphStyle("_", fontSize=size, fontName=font,
                     textColor=color, alignment=align, leading=leading))


def hr(c=MGREY, t=0.5):
    return HRFlowable(width=UW, thickness=t, color=c, spaceAfter=3*mm, spaceBefore=2*mm)


def build(output_path, company_name=None, company_abn=None, investor_name=None,
          shares=None, rate_per_share=None, franking_percentage=None):
    """Build a dividend statement PDF with random or specified data."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    # Generate or use provided data
    if company_name:
        comp_name = company_name
        comp_abn = company_abn or f"{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"
    else:
        comp_name, comp_abn = random.choice(COMPANIES)

    holder_name = investor_name or random.choice(INVESTOR_NAMES)
    holder_address = generate_address()

    reg_name, reg_address, reg_phone = random.choice(REGISTRARS)
    asx_code = "".join([c for c in comp_name.split()[0] if c.isalpha()])[:3].upper()

    registrar_lines = [
        f"C/- {reg_name}",
        reg_address,
        f"Telephone: {reg_phone}",
        f"ASX Code: {asx_code}",
        f"Email: registrars@{reg_name.split()[0].lower()}.com.au",
    ]

    ref_no = f"X********{random.randint(1000,9999)}"
    payment_date = generate_date(random.randint(0, 30))
    record_date = generate_date(random.randint(15, 45))

    # Calculate dividend amounts
    num_shares = shares or random.randint(1000, 10000)
    rate = rate_per_share or round_to_tenth(random.uniform(0.10, 1.00))
    frank_pct = franking_percentage if franking_percentage is not None else 100

    # Determine franked vs unfranked split
    if frank_pct == 100:
        franked_amount = round_to_tenth(num_shares * rate)
        unfranked_amount = 0.00
    elif frank_pct == 0:
        franked_amount = 0.00
        unfranked_amount = round_to_tenth(num_shares * rate)
    else:
        total = round_to_tenth(num_shares * rate)
        franked_amount = round_to_tenth(total * frank_pct / 100)
        unfranked_amount = round_to_tenth(total - franked_amount)

    total_payment = round_to_tenth(franked_amount + unfranked_amount)

    # Franking credit calculation
    if franked_amount > 0:
        franking_credit = round_to_tenth(franked_amount * 0.30 / 0.70)  # 30% company tax rate
    else:
        franking_credit = 0.00

    # Withholding tax (typically on unfranked portion for foreign investors)
    withholding_tax = round_to_tenth(unfranked_amount * random.uniform(0.15, 0.30)) if unfranked_amount > 0 else 0.00
    net_amount = round_to_tenth(total_payment - withholding_tax)

    # Banking details
    bank_name, bank_bsb = random.choice(BANKS)
    bank_account_name = holder_name.split("<")[0].strip()
    bank_account = f"*****{random.randint(1000,9999)}"
    bank_ref = str(random.randint(1000000000, 9999999999))

    # Tax information
    cfi_amount = round_to_tenth(unfranked_amount * random.uniform(0, 0.3)) if unfranked_amount > 0 else 0.00
    nil_cfi = round_to_tenth(unfranked_amount - cfi_amount) if unfranked_amount > 0 else 0.00

    # ── Header ────────────────────────────────────────────────────────
    hdr = Table([[
        p(comp_name, 14, "Helvetica-Bold", WHITE),
        p(f"ABN: {comp_abn}", 9, color=colors.HexColor("#CCDDEE"), align=TA_RIGHT),
    ]], colWidths=[UW * 0.6, UW * 0.4])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(0,0),   10),
        ("RIGHTPADDING",  (-1,0),(-1,0), 10),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    # ── Addressee (left) + Registrar (right) ──────────────────────────
    addr_rows = [[p(holder_name, 9, "Helvetica-Bold", BLACK)]]
    for line in holder_address:
        addr_rows.append([p(line, 9, color=DGREY)])
    addr_tbl = Table(addr_rows, colWidths=[UW * 0.5])
    addr_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 1),
        ("BOTTOMPADDING", (0,0),(-1,-1), 1),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    reg_rows = [[p("All Registry communications to:", 9, "Helvetica-Bold", BLACK)]]
    for line in registrar_lines:
        reg_rows.append([p(line, 9, color=DGREY)])
    reg_tbl = Table(reg_rows, colWidths=[UW * 0.5])
    reg_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 1),
        ("BOTTOMPADDING", (0,0),(-1,-1), 1),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    top = Table([[addr_tbl, reg_tbl]], colWidths=[UW * 0.5, UW * 0.5])
    top.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    story += [top, Spacer(1, 6*mm)]

    # ── Statement heading + meta ───────────────────────────────────────
    story.append(p("DIVIDEND STATEMENT", 14, "Helvetica-Bold", NAVY))
    story.append(Spacer(1, 3*mm))

    meta_rows = [
        ["Reference No.:",    ref_no],
        ["Payment Date:",     payment_date],
        ["Record Date:",      record_date],
    ]
    meta_tbl = Table(
        [[p(r[0], 8, "Helvetica-Bold", DGREY, TA_RIGHT), p(r[1], 9, "Helvetica-Bold", BLACK)]
         for r in meta_rows],
        colWidths=[35*mm, 60*mm])
    meta_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
    ]))
    story += [meta_tbl, Spacer(1, 5*mm)]

    # ── Dividend detail table ──────────────────────────────────────────
    th  = ParagraphStyle("TH",  fontSize=8, fontName="Helvetica-Bold", textColor=WHITE)
    thr = ParagraphStyle("THR", fontSize=8, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td  = ParagraphStyle("TD",  fontSize=8.5, fontName="Helvetica",      textColor=DGREY)
    tdr = ParagraphStyle("TDR", fontSize=8.5, fontName="Helvetica",      textColor=DGREY, alignment=TA_RIGHT)

    div_cw = [UW*0.28, 18*mm, 20*mm, 22*mm, 22*mm, 22*mm, 22*mm]
    div_hdr = [
        Paragraph("Security Description", th),
        Paragraph("Rate per Share", thr),
        Paragraph("Participating Shares", thr),
        Paragraph("Unfranked Amount", thr),
        Paragraph("Franked Amount", thr),
        Paragraph("Total Payment", thr),
        Paragraph("Franking Credit", thr),
    ]
    div_data_rows = [[
        Paragraph(f"{asx_code} - ORDINARY FULLY PAID SHARES", td),
        Paragraph(f"${rate:.2f}", tdr),
        Paragraph(f"{num_shares:,}", tdr),
        Paragraph(f"${unfranked_amount:.2f}", tdr),
        Paragraph(f"${franked_amount:.2f}", tdr),
        Paragraph(f"${total_payment:.2f}", tdr),
        Paragraph(f"${franking_credit:.2f}", tdr),
    ]]

    div_tbl = Table([div_hdr] + div_data_rows, colWidths=div_cw, repeatRows=1)
    div_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),   NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [WHITE, LGREY]),
        ("TOPPADDING",    (0,0),(-1,-1),  5),
        ("BOTTOMPADDING", (0,0),(-1,-1),  5),
        ("LEFTPADDING",   (0,0),(-1,-1),  4),
        ("RIGHTPADDING",  (0,0),(-1,-1),  4),
        ("GRID",          (0,0),(-1,-1),  0.3, MGREY),
        ("LINEBELOW",     (0,-1),(-1,-1), 1, NAVY),
    ]))
    story += [div_tbl, Spacer(1, 4*mm)]

    # ── Net amount ─────────────────────────────────────────────────────
    net_rows = [
        [p("Less Resident Withholding Tax", 9, color=DGREY),
         p(f"${withholding_tax:.2f}", 9, "Helvetica-Bold", BLACK, TA_RIGHT)],
        [p("Net Amount AUD", 9, "Helvetica-Bold", BLACK),
         p(f"${net_amount:.2f}", 9, "Helvetica-Bold", BLACK, TA_RIGHT)],
        [p(f"Represented By: Direct Credit amount AUD", 9, color=DGREY),
         p(f"${net_amount:.2f}", 9, color=DGREY, align=TA_RIGHT)],
    ]
    net_tbl = Table(net_rows, colWidths=[UW * 0.7, UW * 0.3])
    net_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, LGREY, WHITE]),
        ("LINEABOVE",      (0,1),(-1,1),  0.5, NAVY),
        ("TOPPADDING",     (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 4),
        ("LEFTPADDING",    (0,0),(-1,-1), 4),
        ("RIGHTPADDING",   (0,0),(-1,-1), 4),
    ]))
    story += [net_tbl, Spacer(1, 5*mm)]

    # ── Banking instructions ───────────────────────────────────────────
    story.append(p("BANKING INSTRUCTIONS", 10, "Helvetica-Bold", NAVY))
    story.append(hr())
    story.append(p(f"The amount of AUD ${net_amount:.2f} was deposited to the bank account detailed below:",
                   9, color=DGREY))
    story.append(Spacer(1, 2*mm))

    banking_rows = [
        ["Bank:",                 bank_name],
        ["Account Name:",         bank_account_name],
        ["BSB:",                  bank_bsb],
        ["Account:",              bank_account],
        ["Direct Credit Ref No.:", bank_ref],
    ]
    bank_tbl = Table(
        [[p(r[0], 9, "Helvetica-Bold", BLACK), p(r[1], 9, color=DGREY)]
         for r in banking_rows],
        colWidths=[45*mm, UW - 45*mm])
    bank_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, LGREY]),
    ]))
    story += [bank_tbl, Spacer(1, 5*mm)]

    # ── Franking + tax information ─────────────────────────────────────
    story.append(p("FRANKING INFORMATION", 10, "Helvetica-Bold", NAVY))
    story.append(hr())

    frank_rate = f"${rate * frank_pct / 100:.2f}" if frank_pct > 0 else "$0.00"
    frank_rows = [
        ["Franked Rate per Share",  frank_rate],
        ["Franking Percentage",     f"{frank_pct}%"],
        ["Company Tax Rate",        "30%"],
    ]
    frank_left = Table(
        [[p(r[0], 9, color=DGREY), p(r[1], 9, "Helvetica-Bold", BLACK)]
         for r in frank_rows],
        colWidths=[50*mm, 30*mm])
    frank_left.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, LGREY, WHITE]),
    ]))

    th2  = ParagraphStyle("TH2",  fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr2 = ParagraphStyle("THR2", fontSize=8.5, fontName="Helvetica-Bold",
                           textColor=WHITE, alignment=TA_RIGHT)
    tax_items = [
        ["Conduit Foreign Income (CFI)",  f"${cfi_amount:.2f}"],
        ["Nil CFI",                       f"${nil_cfi:.2f}"],
        ["Total unfranked Income",        f"${unfranked_amount:.2f}"],
    ]
    tax_rows = [["Income Description", "Amount"]] + tax_items
    tax_tbl = Table(
        [[Paragraph(tax_rows[0][0], th2), Paragraph(tax_rows[0][1], thr2)]] +
        [[p(r[0], 9, color=DGREY), p(r[1], 9, align=TA_RIGHT, color=DGREY)]
         for r in tax_rows[1:]],
        colWidths=[62*mm, 30*mm])
    tax_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),   NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [WHITE, LGREY, WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1),  4),
        ("BOTTOMPADDING", (0,0),(-1,-1),  4),
        ("LEFTPADDING",   (0,0),(-1,-1),  4),
        ("RIGHTPADDING",  (0,0),(-1,-1),  4),
        ("GRID",          (0,0),(-1,-1),  0.3, MGREY),
        ("LINEBELOW",     (0,-1),(-1,-1), 1, NAVY),
    ]))

    tax_section = Table([[frank_left, tax_tbl]],
                         colWidths=[UW * 0.45, UW * 0.55])
    tax_section.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    story += [tax_section, Spacer(1, 4*mm)]

    story.append(p(
        "Withholding tax is not payable by non-residents on the Conduit Foreign Income portion "
        "of the unfranked dividend amount. The total amount together with the franking credit (if any) "
        "should be disclosed as assessable income in your Australian tax return.",
        8, "Helvetica-Oblique", DGREY, leading=12))
    story.append(Spacer(1, 8*mm))

    # ── Footer ─────────────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    story.append(p(
        "Note: You may require this statement for taxation purposes. "
        "All investors should seek independent advice relevant to their own particular circumstances.",
        7.5, color=DGREY, align=TA_CENTER, leading=11))
    story.append(p(
        "Please ensure your details are current by viewing and updating via the online service centre.",
        7.5, color=DGREY, align=TA_CENTER, leading=11))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random dividend statement PDFs with optional custom data."
    )
    parser.add_argument("--company-name", help="Company name")
    parser.add_argument("--company-abn", help="Company ABN (format: XX XXX XXX XXX)")
    parser.add_argument("--investor-name", help="Investor/shareholder name")
    parser.add_argument("--shares", type=int, help="Number of shares held")
    parser.add_argument("--rate-per-share", type=float, help="Dividend rate per share")
    parser.add_argument("--franking-percentage", type=int, default=100,
                        help="Franking percentage (0-100, default: 100)")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\dividends"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    existing = [f for f in os.listdir(out_dir) if f.startswith("dividend_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[1].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"dividend_{next_n:03d}.pdf")

    build(
        path,
        company_name=args.company_name,
        company_abn=args.company_abn,
        investor_name=args.investor_name,
        shares=args.shares,
        rate_per_share=args.rate_per_share,
        franking_percentage=args.franking_percentage
    )

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
