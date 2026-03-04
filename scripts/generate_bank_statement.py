"""
Bank Statement generator — CBA Accelerator Cash Account style.
Data-driven with random generation and command-line arguments.
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
LGREY = colors.HexColor("#F4F4F4")
MGREY = colors.HexColor("#CCCCCC")
DGREY = colors.HexColor("#555555")
WHITE = colors.white
BLACK = colors.black

# Data pools for random generation
BANK_NAMES = [
    ("CBA", "Commonwealth Bank of Australia", "48 123 123 124", "commbank.com.au", "13 2221"),
    ("NAB", "National Australia Bank Limited", "12 004 044 937", "nab.com.au", "13 22 65"),
    ("ANZ", "Australia and New Zealand Banking Group", "11 005 357 522", "anz.com.au", "13 13 14"),
    ("WBC", "Westpac Banking Corporation", "33 007 457 141", "westpac.com.au", "13 20 32"),
]

ACCOUNT_HOLDERS = [
    "REGTECH UAT FUND TEST", "CHEN FAMILY SUPER FUND", "PARKVIEW SUPER FUND",
    "SMITH FAMILY TRUST", "JONES INVESTMENT FUND", "TAYLOR SUPER FUND"
]

ACCOUNT_TYPES = [
    "Accelerator Cash Account", "Business Transaction Account",
    "Premium Cash Account", "Everyday Saver Account"
]

STREETS = [
    "Hawthorn Rd", "Collins Street", "Bridge Road", "Smith Street",
    "Queen Street", "George Street", "Elizabeth Street"
]

SUBURBS = [
    ("BRIGHTON EAST", "VIC", "3187"), ("MELBOURNE", "VIC", "3000"),
    ("SYDNEY", "NSW", "2000"), ("BRISBANE", "QLD", "4000"),
    ("PERTH", "WA", "6000"), ("ADELAIDE", "SA", "5000")
]

TRANSACTIONS = [
    ("Credit Interest", "credit"),
    ("Direct Credit {} Dividend", "credit"),
    ("Direct Credit - Rental Income", "credit"),
    ("Bunnings – property expense", "debit"),
    ("SYDNEY WATER BPAY – water, property expense", "debit"),
    ("BPAY {} Acc – Accounting fee", "debit"),
    ("Direct Credit {} DIVIDEND", "credit"),
    ("BUY {} shares purchase", "debit"),
    ("Direct Debit – Property Manager Fee", "debit"),
    ("Direct Debit – Council Rates", "debit"),
    ("BPAY – Insurance Premium", "debit"),
    ("Direct Debit – Accounting Fee", "debit"),
]

SHARE_CODES = ["PDL", "FXJ", "PGH", "BHP", "CBA", "ANZ", "TLS", "WES", "RIO"]
PAYEES = ["ABC", "XYZ", "123 Partners", "Smith & Co", "Jones Legal"]


def generate_abn():
    """Generate a valid-looking ABN with AFSL."""
    abn = f"{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"
    afsl = random.randint(200000, 400000)
    return f"ABN {abn} AFSL {afsl}"


def generate_address():
    """Generate a random Australian address."""
    level = random.choice(["", "2/", "3/", "Level 4, "])
    street_num = random.randint(100, 999)
    street = random.choice(STREETS)
    suburb, state, postcode = random.choice(SUBURBS)
    return [f"{level}{street_num} {street.upper()}", f"{suburb} {state} {postcode}"]


def generate_account_number():
    """Generate account number in format XX XXXX XXXXXXXX."""
    return f"{random.randint(6,9):02d} {random.randint(0,9999):04d} {random.randint(10000000,99999999)}"


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def generate_transactions(opening_balance, num_transactions, start_date=None, end_date=None):
    """Generate random bank transactions."""
    transactions = []
    balance = opening_balance

    if start_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=300)
    span_days = (end_date - start_date).days or 1

    dates = sorted([start_date + timedelta(days=random.randint(0, span_days))
                    for _ in range(num_transactions)])

    for i, date in enumerate(dates):
        trans_type, direction = random.choice(TRANSACTIONS)

        # Fill in placeholders
        if "{}" in trans_type:
            if "Dividend" in trans_type:
                trans_type = trans_type.format(random.choice(SHARE_CODES))
            elif "shares" in trans_type:
                trans_type = trans_type.format(random.choice(SHARE_CODES))
            else:
                trans_type = trans_type.format(random.choice(PAYEES))

        # Generate amount
        if direction == "credit":
            if "Interest" in trans_type:
                amount = round_to_tenth(random.uniform(5, 50))
            elif "Dividend" in trans_type:
                amount = round_to_tenth(random.uniform(100, 500))
            else:
                amount = round_to_tenth(random.uniform(500, 5000))
            debit = ""
            credit = f"${amount:.2f}"
            balance = round_to_tenth(balance + amount)
        else:  # debit
            if "Insurance" in trans_type or "Accounting" in trans_type:
                amount = round_to_tenth(random.uniform(1000, 3500))
            elif "shares" in trans_type:
                amount = round_to_tenth(random.uniform(2000, 5000))
            elif "Council" in trans_type:
                amount = round_to_tenth(random.uniform(1000, 2000))
            else:
                amount = round_to_tenth(random.uniform(50, 500))
            debit = f"${amount:.2f}"
            credit = ""
            balance = round_to_tenth(balance - amount)

        date_str = f"{date.day} {date.strftime('%b')}"
        if i == 0:
            date_str = f"{date.day} {date.strftime('%b %Y')}"
        elif i == len(dates) - 1:
            date_str = f"{end_date.day} {end_date.strftime('%b %Y')}"

        transactions.append((date_str, trans_type, debit, credit, f"${balance:,.2f} CR"))

    return transactions, balance


def fy_date_range(year: int):
    """Return (start_date, end_date) for the given Australian financial year.
    FY2025 = 1 Jul 2024 – 30 Jun 2025.
    """
    return datetime(year - 1, 7, 1), datetime(year, 6, 30)


def generate_bank_statement_data(bank_name=None, account_holder=None, opening_balance=None,
                                 num_transactions=None, show_balance=False, financial_year=None):
    """Generate random bank statement data."""
    # Select bank
    if bank_name:
        bank_data = next((b for b in BANK_NAMES if bank_name.lower() in b[1].lower()), None)
        if not bank_data:
            bank_data = random.choice(BANK_NAMES)
    else:
        bank_data = random.choice(BANK_NAMES)

    bank_abbrev, bank_full, abn_num, website, phone = bank_data
    bank_abn = f"ABN {abn_num} AFSL {random.randint(200000, 400000)}"

    holder = account_holder or random.choice(ACCOUNT_HOLDERS)
    holder_address = generate_address()

    statement_no = random.randint(10, 50)
    account_number = generate_account_number()

    # Period
    if financial_year:
        start_date, end_date = fy_date_range(financial_year)
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=300)
    period = f"{start_date.day} {start_date.strftime('%b %Y')} - {end_date.day} {end_date.strftime('%b %Y')}"

    account_type = random.choice(ACCOUNT_TYPES)
    account_name_full = f"{random.choice(['MARY JONES', 'SARAH CHEN', 'JOHN SMITH', 'DAVID TAYLOR'])}  ATF {holder}"

    # Generate opening balance
    if opening_balance is None:
        opening_balance = round_to_tenth(random.uniform(8000, 50000))

    # Generate transactions
    if num_transactions is None:
        num_transactions = random.randint(15, 25)

    trans_list, closing_balance = generate_transactions(opening_balance, num_transactions, start_date, end_date)

    # Add opening and closing balance rows
    if show_balance:
        transactions = [
            (f"{start_date.day} {start_date.strftime('%b %Y')}", "OPENING BALANCE", "", "", f"${opening_balance:,.2f} CR")
        ] + trans_list + [
            (f"{end_date.day} {end_date.strftime('%b %Y')}", "CLOSING BALANCE", "", "", f"${closing_balance:,.2f} CR")
        ]
    else:
        # Strip balance column (5th element) from all transaction rows
        transactions = [(t[0], t[1], t[2], t[3]) for t in trans_list]

    # Calculate totals
    total_debits = sum(float(t[2].replace("$", "").replace(",", ""))
                       for t in trans_list if t[2])
    total_credits = sum(float(t[3].replace("$", "").replace(",", ""))
                        for t in trans_list if t[3])

    return {
        "bank_abbrev": bank_abbrev,
        "bank_name": bank_full,
        "bank_abn": bank_abn,
        "bank_website": website,
        "bank_phone": phone,
        "account_holder": holder,
        "holder_address": holder_address,
        "statement_no": str(statement_no),
        "account_number": account_number,
        "period": period,
        "closing_balance": f"${closing_balance:,.2f} CR",
        "enquiries": phone,
        "account_type": account_type,
        "account_name_full": account_name_full,
        "transactions": transactions,
        "show_balance": show_balance,
        "summary_opening": f"${opening_balance:,.2f} CR",
        "summary_debits": f"${total_debits:,.2f}",
        "summary_credits": f"${total_credits:,.2f}",
        "interest_rates": [
            (f"{end_date.day} {end_date.strftime('%b')}", "$0.00 and over", f"{random.choice(['0.30', '0.35', '0.40', '0.45'])}%"),
        ],
    }


def p(text, size=9, font="Helvetica", color=BLACK, align=TA_LEFT, leading=13):
    return Paragraph(text, ParagraphStyle("_", fontSize=size, fontName=font,
                     textColor=color, alignment=align, leading=leading))


def hr(c=MGREY, t=0.5):
    return HRFlowable(width=UW, thickness=t, color=c, spaceAfter=4*mm, spaceBefore=2*mm)


def build(output_path, d):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    # ── Header ────────────────────────────────────────────────────────
    # Logo box (abbreviated bank name) + bank full name + "Your Statement"
    logo_box = Table([[p(d["bank_abbrev"], 22, "Helvetica-Bold", WHITE, TA_CENTER)]],
                     colWidths=[22*mm])
    logo_box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
    ]))

    hdr = Table([[
        logo_box,
        p(d["bank_name"], 9, color=colors.HexColor("#CCDDEE")),
        p("Your Statement", 13, "Helvetica-Bold", WHITE, TA_RIGHT),
    ]], colWidths=[26*mm, UW * 0.45, UW - 26*mm - UW * 0.45])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("LEFTPADDING",   (0,0),(0,0),   0),
        ("LEFTPADDING",   (1,0),(1,0),   8),
        ("RIGHTPADDING",  (-1,0),(-1,0), 10),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    # ── Address (left) + Statement meta (right) ────────────────────────
    addr_rows = [[p(d["account_holder"], 9, "Helvetica-Bold", BLACK)]]
    for line in d["holder_address"]:
        addr_rows.append([p(line, 9, color=DGREY)])
    addr_tbl = Table(addr_rows, colWidths=[UW * 0.45])
    addr_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    meta_rows = [
        [p(f"Statement {d['statement_no']} (Page 1 of 2)", 8, color=DGREY, align=TA_RIGHT)],
        [p(f"Account Number  {d['account_number']}", 9, "Helvetica-Bold", BLACK, TA_RIGHT)],
        [p(f"Statement Period  {d['period']}", 9, "Helvetica-Bold", BLACK, TA_RIGHT)],
        [p(f"Closing Balance  {d['closing_balance']}", 10, "Helvetica-Bold", NAVY, TA_RIGHT)],
        [p(f"Enquiries  {d['enquiries']}", 8, color=DGREY, align=TA_RIGHT)],
    ]
    meta_tbl = Table(meta_rows, colWidths=[UW * 0.55])
    meta_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    top = Table([[addr_tbl, meta_tbl]], colWidths=[UW * 0.45, UW * 0.55])
    top.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    story += [top, Spacer(1, 5*mm)]

    # ── Account name + disclaimer ──────────────────────────────────────
    story.append(p(d["account_type"], 10, "Helvetica-Bold", NAVY))
    story.append(p(f"Name: {d['account_name_full']}", 9, color=DGREY))
    story.append(Spacer(1, 2*mm))
    story.append(p(
        "Note: Have you checked your statement today? It's easy to find out more information about each "
        "of your transactions by logging on to the Bank App or Online Banking. Should you have any questions "
        "on fees or see an error please contact us on the details above. Cheque proceeds are available when cleared.",
        8, "Helvetica-Oblique", DGREY, leading=12))
    story.append(Spacer(1, 5*mm))

    # ── Transaction table ──────────────────────────────────────────────
    th  = ParagraphStyle("TH",   fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr = ParagraphStyle("THR",  fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td  = ParagraphStyle("TD",   fontSize=8.5, fontName="Helvetica",      textColor=DGREY)
    tdr = ParagraphStyle("TDR",  fontSize=8.5, fontName="Helvetica",      textColor=DGREY, alignment=TA_RIGHT)
    tdb = ParagraphStyle("TDB",  fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK)
    tdbr= ParagraphStyle("TDBR", fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)

    show_balance = d.get("show_balance", True)  # True = show balance column (default)
    if show_balance:
        cw = [22*mm, UW * 0.40, 26*mm, 26*mm, 36*mm]
        hdr_row = [
            Paragraph("Date", th),
            Paragraph("Transaction", th),
            Paragraph("Debit", thr),
            Paragraph("Credit", thr),
            Paragraph("Balance", thr),
        ]
    else:
        cw = [22*mm, UW * 0.52, 26*mm, 26*mm]
        hdr_row = [
            Paragraph("Date", th),
            Paragraph("Transaction", th),
            Paragraph("Debit", thr),
            Paragraph("Credit", thr),
        ]

    txn_rows = [hdr_row]
    for i, t in enumerate(d["transactions"]):
        if show_balance:
            is_boundary = i == 0 or i == len(d["transactions"]) - 1
            ds  = tdb  if is_boundary else td
            vsr = tdbr if is_boundary else tdr
            txn_rows.append([
                Paragraph(t[0], ds),
                Paragraph(t[1], ds),
                Paragraph(t[2], vsr),
                Paragraph(t[3], vsr),
                Paragraph(t[4], vsr),
            ])
        else:
            txn_rows.append([
                Paragraph(t[0], td),
                Paragraph(t[1], td),
                Paragraph(t[2], tdr),
                Paragraph(t[3], tdr),
            ])

    tbl = Table(txn_rows, colWidths=cw, repeatRows=1)
    cmds = [
        ("BACKGROUND",    (0,0),(-1,0),   NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [WHITE, LGREY]),
        ("TOPPADDING",    (0,0),(-1,-1),  5),
        ("BOTTOMPADDING", (0,0),(-1,-1),  5),
        ("LEFTPADDING",   (0,0),(-1,-1),  5),
        ("RIGHTPADDING",  (0,0),(-1,-1),  5),
        ("GRID",          (0,0),(-1,-1),  0.3, MGREY),
        ("LINEBELOW",     (0,-1),(-1,-1), 1, NAVY),
        ("LINEABOVE",     (0,1),(-1,1),   0.5, MGREY),
        # Highlight opening and closing rows
        ("BACKGROUND",    (0,1),(-1,1),   colors.HexColor("#E8F0FB")),
        ("BACKGROUND",    (0,-1),(-1,-1), colors.HexColor("#E8F0FB")),
    ]
    tbl.setStyle(TableStyle(cmds))
    story += [tbl, Spacer(1, 5*mm)]

    # ── Summary ────────────────────────────────────────────────────────
    story.append(hr())
    story.append(p(
        "Opening balance  −  Total debits  +  Total credits  =  Closing balance",
        8, "Helvetica-Oblique", DGREY))
    smry = Table([[
        p(d["summary_opening"],  8.5, "Helvetica-Bold", BLACK),
        p(d["summary_debits"],   8.5, "Helvetica-Bold", BLACK),
        p(d["summary_credits"],  8.5, "Helvetica-Bold", BLACK),
        p(d["closing_balance"],  8.5, "Helvetica-Bold", BLACK),
    ]], colWidths=[UW * 0.25] * 4)
    smry.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("BACKGROUND",    (0,0),(-1,-1), LGREY),
        ("GRID",          (0,0),(-1,-1), 0.3, MGREY),
    ]))
    story += [smry, Spacer(1, 5*mm)]

    # ── Interest rate table ────────────────────────────────────────────
    story.append(p("Your Credit Interest Rate Summary", 10, "Helvetica-Bold", NAVY))
    ir_th = ParagraphStyle("IRH", fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    ir_tbl = Table([
        [Paragraph("Date", ir_th),
         Paragraph("Balance", ir_th),
         Paragraph("Standard Credit Interest Rate (p.a.)", ir_th)],
    ] + [[p(r[0], 9, color=DGREY), p(r[1], 9, color=DGREY), p(r[2], 9, color=DGREY)]
         for r in d["interest_rates"]],
        colWidths=[20*mm, 60*mm, UW - 80*mm])
    ir_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LGREY, WHITE]),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("GRID",          (0,0),(-1,-1), 0.3, MGREY),
    ]))
    story += [ir_tbl, Spacer(1, 8*mm)]

    # ── Footer ─────────────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    story.append(p(
        f"{d['bank_name']} {d['bank_abn']}  |  {d['bank_website']}  |  {d['bank_phone']}",
        7.5, color=DGREY, align=TA_CENTER, leading=11))
    story.append(p(
        "Note: Interest rates are effective as at the date shown but are subject to change.",
        7.5, color=DGREY, align=TA_CENTER, leading=11))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random bank statement PDFs with optional custom data."
    )
    parser.add_argument("--bank-name", help="Bank name (e.g., 'Commonwealth Bank')")
    parser.add_argument("--account-holder", help="Account holder name")
    parser.add_argument("--opening-balance", type=float, help="Opening balance amount")
    parser.add_argument("--num-transactions", type=int, help="Number of transactions (default: random 15-25)")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\bank_statements"
    os.makedirs(out_dir, exist_ok=True)
    existing = [f for f in os.listdir(out_dir) if f.startswith("bank_statement_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[2].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"bank_statement_{next_n:03d}.pdf")

    data = generate_bank_statement_data(
        bank_name=args.bank_name,
        account_holder=args.account_holder,
        opening_balance=args.opening_balance,
        num_transactions=args.num_transactions
    )

    build(path, data)

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
