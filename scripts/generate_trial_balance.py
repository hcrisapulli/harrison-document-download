"""
Trial Balance generator - comparative format.
Generates random trial balances with command-line argument support.
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
COMPANY_NAMES = [
    "Earth SQL Pty Ltd", "Sunrise Consulting Pty Ltd", "Tech Solutions Australia Pty Ltd",
    "Green Energy Co Pty Ltd", "Metro Design Studio Pty Ltd", "Apex Financial Services Pty Ltd"
]

INCOME_ACCOUNTS = [
    ("0510", "Sales"), ("0510", "Consulting Revenue"), ("0510", "Service Revenue"),
    ("0520", "Interest Income"), ("0530", "Other Income")
]

EXPENSE_ACCOUNTS = [
    ("1510", "Accountancy"), ("1523", "Annual leave (provision)"),
    ("1540", "Bad debts"), ("1545", "Bank fees & charges"),
    ("1617", "Depreciation - Temporary expensing"), ("1660", "Entertainment"),
    ("1675", "Fees & charges"), ("1685", "Filing fees"),
    ("1690", "Fines"), ("1715", "General expenses"),
    ("1755", "Insurance"), ("1838", "Office Expenses"),
    ("1840", "Printing & stationery"), ("1855", "Rent on land & buildings"),
    ("1865", "Repairs & maintenance"), ("1871", "Software with GST"),
    ("1880", "Salaries - Ordinary"), ("1885", "Salaries - Associated persons"),
    ("1915", "Staff amenities"), ("1925", "Memberships & Subscriptions"),
    ("1935", "Superannuation"), ("1936", "Superannuation - Associated persons"),
    ("1940", "Telephone"), ("1950", "Travel, accommodation & conference"),
    ("1966", "WorkCover")
]

CURRENT_ASSET_ACCOUNTS = [
    ("2000", "Cash at bank"), ("2050", "Cash on hand"), ("2101", "Trade debtors")
]

NON_CURRENT_ASSET_ACCOUNTS = [
    ("2870", "Office equipment"), ("2875", "Less: Accumulated depreciation")
]

CURRENT_LIABILITY_ACCOUNTS = [
    ("3325", "Provision for Income Tax"), ("3330", "ATO PAYG Instalments Payable"),
    ("3350", "Superannuation Payable"), ("3380", "GST payable control account"),
    ("3385", "GST on Accruals"), ("3392", "Wages Payable"),
    ("3394", "Amounts withheld from salary & wages")
]

NON_CURRENT_LIABILITY_ACCOUNTS = [
    ("3751", "Provision for Annual Leave")
]

EQUITY_ACCOUNTS = [
    ("4110", "Income tax expense/income"), ("4160", "Dividends provided for or paid"),
    ("4199", "Retained Profits"), ("4200", "Issued & paid up capital"),
    ("4390", "Cashflow Boost Reserve")
]


def generate_abn():
    """Generate a valid-looking ABN."""
    return f"{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"


def parse_date(date_str):
    """Parse DD/MM/YYYY date string."""
    return datetime.strptime(date_str, "%d/%m/%Y")


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def format_amount(amount):
    """Format amount with commas."""
    if amount == 0:
        return ""
    return f"{amount:,.2f}"


def p(text, size=9, font="Helvetica", color=BLACK, align=TA_LEFT, leading=13):
    return Paragraph(text, ParagraphStyle("_", fontSize=size, fontName=font,
                     textColor=color, alignment=align, leading=leading))


def hr(c=MGREY, t=0.5):
    return HRFlowable(width=UW, thickness=t, color=c, spaceAfter=3*mm, spaceBefore=2*mm)


def build(output_path, company_name=None, company_abn=None, balance_date=None):
    """Build a trial balance PDF with random or specified data."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    # Generate or use provided data
    comp_name = company_name or random.choice(COMPANY_NAMES)
    comp_abn = company_abn or generate_abn()

    if balance_date:
        date_obj = parse_date(balance_date)
    else:
        date_obj = datetime(datetime.now().year, 6, 30)

    report_title = f"Comparative Trial Balance as at {date_obj.strftime('%d %B %Y')}"
    year1 = str(date_obj.year)
    year2 = str(date_obj.year - 1)

    # Generate trial balance data - ensuring it balances!
    entries = []

    # Track running totals for current year
    current_dr_total = 0.0
    current_cr_total = 0.0

    # Track running totals for prior year
    prior_dr_total = 0.0
    prior_cr_total = 0.0

    # Income section (CREDIT balance)
    entries.append(("SECTION", "Income"))
    income_total = round_to_tenth(random.uniform(500000, 1500000))
    income_prior = round_to_tenth(income_total * random.uniform(0.8, 0.95))
    num_income = random.randint(1, 3)
    income_accounts = random.sample(INCOME_ACCOUNTS, min(num_income, len(INCOME_ACCOUNTS)))

    for i, (code, name) in enumerate(income_accounts):
        if i == 0:
            amount_current = income_total
            amount_prior = income_prior
        else:
            amount_current = round_to_tenth(random.uniform(1000, 50000))
            amount_prior = round_to_tenth(amount_current * random.uniform(0.8, 0.95))
        entries.append(("ROW", code, name, "", format_amount(amount_current), "", format_amount(amount_prior)))
        current_cr_total += amount_current
        prior_cr_total += amount_prior

    # Expenses section (DEBIT balance)
    entries.append(("SECTION", "Expenses"))
    num_expenses = random.randint(10, 20)
    expense_accounts = random.sample(EXPENSE_ACCOUNTS, min(num_expenses, len(EXPENSE_ACCOUNTS)))
    total_expenses = 0.0
    total_expenses_prior = 0.0

    for code, name in expense_accounts:
        amount = round_to_tenth(random.uniform(100, 100000))
        amount_prior = round_to_tenth(amount * random.uniform(0.8, 0.95))
        total_expenses += amount
        total_expenses_prior += amount_prior
        entries.append(("ROW", code, name, format_amount(amount), "", format_amount(amount_prior), ""))
        current_dr_total += amount
        prior_dr_total += amount_prior

    # Current Assets section (DEBIT balance)
    entries.append(("SECTION", "Current Assets"))
    cash_balance = round_to_tenth(random.uniform(100000, 500000))
    cash_prior = round_to_tenth(cash_balance * random.uniform(0.7, 0.9))
    debtors = round_to_tenth(random.uniform(50000, 200000))
    debtors_prior = round_to_tenth(debtors * random.uniform(0.8, 0.95))

    entries.append(("ROW", "2000", "Cash at bank", format_amount(cash_balance), "", format_amount(cash_prior), ""))
    current_dr_total += cash_balance
    prior_dr_total += cash_prior

    cash_hand = 12.0
    entries.append(("ROW", "2050", "Cash on hand", format_amount(cash_hand), "", format_amount(cash_hand), ""))
    current_dr_total += cash_hand
    prior_dr_total += cash_hand

    entries.append(("ROW", "2101", "Trade debtors", format_amount(debtors), "", format_amount(debtors_prior), ""))
    current_dr_total += debtors
    prior_dr_total += debtors_prior

    # Non Current Assets section
    entries.append(("SECTION", "Non Current Assets"))
    equipment_cost = round_to_tenth(random.uniform(2000, 10000))
    accumulated_dep = round_to_tenth(equipment_cost * random.uniform(0.4, 0.8))  # Partially depreciated
    accumulated_dep_prior = round_to_tenth(accumulated_dep * random.uniform(0.6, 0.9))

    entries.append(("ROW", "2870", "Office equipment", format_amount(equipment_cost), "", format_amount(equipment_cost), ""))
    current_dr_total += equipment_cost
    prior_dr_total += equipment_cost

    entries.append(("ROW", "2875", "Less: Accumulated depreciation", "", format_amount(accumulated_dep), "", format_amount(accumulated_dep_prior)))
    current_cr_total += accumulated_dep
    prior_cr_total += accumulated_dep_prior

    # Current Liabilities section (CREDIT balance)
    entries.append(("SECTION", "Current Liabilities"))
    income_tax_provision = round_to_tenth(random.uniform(10000, 100000))
    income_tax_prior = round_to_tenth(income_tax_provision * random.uniform(0.8, 0.95))
    payg_instalments = round_to_tenth(random.uniform(20000, 80000))
    payg_prior = round_to_tenth(payg_instalments * random.uniform(0.8, 0.95))
    super_payable = round_to_tenth(random.uniform(3000, 10000))
    super_prior = round_to_tenth(super_payable * random.uniform(0.8, 0.95))
    gst_payable = round_to_tenth(random.uniform(15000, 50000))
    gst_prior = round_to_tenth(gst_payable * random.uniform(0.8, 0.95))
    gst_accruals = round_to_tenth(random.uniform(5000, 20000))
    gst_accruals_prior = round_to_tenth(gst_accruals * random.uniform(0.8, 0.95))
    wages_payable = round_to_tenth(random.uniform(20000, 60000))
    wages_prior = round_to_tenth(wages_payable * random.uniform(0.8, 0.95))
    withholding = round_to_tenth(random.uniform(10000, 20000))
    withholding_prior = round_to_tenth(withholding * random.uniform(0.8, 0.95))

    entries.append(("ROW", "3325", "Provision for Income Tax", "", format_amount(income_tax_provision), "", format_amount(income_tax_prior)))
    current_cr_total += income_tax_provision
    prior_cr_total += income_tax_prior

    entries.append(("ROW", "3330", "ATO PAYG Instalments Payable", "", format_amount(payg_instalments), "", format_amount(payg_prior)))
    current_cr_total += payg_instalments
    prior_cr_total += payg_prior

    entries.append(("ROW", "3350", "Superannuation Payable", "", format_amount(super_payable), "", format_amount(super_prior)))
    current_cr_total += super_payable
    prior_cr_total += super_prior

    entries.append(("ROW", "3380", "GST payable control account", "", format_amount(gst_payable), "", format_amount(gst_prior)))
    current_cr_total += gst_payable
    prior_cr_total += gst_prior

    entries.append(("ROW", "3385", "GST on Accruals", "", format_amount(gst_accruals), "", format_amount(gst_accruals_prior)))
    current_cr_total += gst_accruals
    prior_cr_total += gst_accruals_prior

    entries.append(("ROW", "3392", "Wages Payable", "", format_amount(wages_payable), "", format_amount(wages_prior)))
    current_cr_total += wages_payable
    prior_cr_total += wages_prior

    entries.append(("ROW", "3394", "Amounts withheld from salary & wages", "", format_amount(withholding), "", format_amount(withholding_prior)))
    current_cr_total += withholding
    prior_cr_total += withholding_prior

    # Non Current Liabilities section (CREDIT balance)
    entries.append(("SECTION", "Non Current Liabilities"))
    annual_leave = round_to_tenth(random.uniform(30000, 70000))
    annual_leave_prior = round_to_tenth(annual_leave * random.uniform(0.8, 0.95))
    entries.append(("ROW", "3751", "Provision for Annual Leave", "", format_amount(annual_leave), "", format_amount(annual_leave_prior)))
    current_cr_total += annual_leave
    prior_cr_total += annual_leave_prior

    # Equity section
    entries.append(("SECTION", "Equity"))

    # Income tax expense (DEBIT)
    entries.append(("ROW", "4110", "Income tax expense/income", format_amount(income_tax_provision), "", format_amount(income_tax_prior), ""))
    current_dr_total += income_tax_provision
    prior_dr_total += income_tax_prior

    # Dividends (DEBIT)
    dividends = round_to_tenth(random.uniform(50000, 250000))
    dividends_prior = round_to_tenth(dividends * random.uniform(0.8, 0.95))
    entries.append(("ROW", "4160", "Dividends provided for or paid", format_amount(dividends), "", format_amount(dividends_prior), ""))
    current_dr_total += dividends
    prior_dr_total += dividends_prior

    # Issued capital (CREDIT) - fixed amount
    capital = 12.0

    # Cashflow boost (CREDIT)
    cashflow_boost = round_to_tenth(random.uniform(50000, 100000))

    # Calculate balancing figure for Retained Profits (CREDIT)
    # Retained Profits must balance: Total DR = Total CR
    # We need to account for capital and cashflow boost that will be added
    retained_profits = round_to_tenth(current_dr_total - current_cr_total - capital - cashflow_boost)
    retained_profits_prior = round_to_tenth(prior_dr_total - prior_cr_total - capital - cashflow_boost)

    entries.append(("ROW", "4199", "Retained Profits", "", format_amount(retained_profits), "", format_amount(retained_profits_prior)))
    current_cr_total += retained_profits
    prior_cr_total += retained_profits_prior

    entries.append(("ROW", "4200", "Issued & paid up capital", "", format_amount(capital), "", format_amount(capital)))
    current_cr_total += capital
    prior_cr_total += capital

    entries.append(("ROW", "4390", "Cashflow Boost Reserve", "", format_amount(cashflow_boost), "", format_amount(cashflow_boost)))
    current_cr_total += cashflow_boost
    prior_cr_total += cashflow_boost

    # Round totals to ensure they're clean
    total_dr_current = round_to_tenth(current_dr_total)
    total_cr_current = round_to_tenth(current_cr_total)
    total_dr_prior = round_to_tenth(prior_dr_total)
    total_cr_prior = round_to_tenth(prior_cr_total)

    entries.append(("TOTAL", format_amount(total_dr_current), format_amount(total_cr_current),
                    format_amount(total_dr_prior), format_amount(total_cr_prior)))

    # Net profit
    net_profit = round_to_tenth(income_total - total_expenses - income_tax_provision)
    entries.append(("NET", "Net Profit", format_amount(net_profit), "", "", ""))

    # ── Header ────────────────────────────────────────────────────────
    hdr = Table([[
        p(comp_name, 14, "Helvetica-Bold", WHITE),
        p(f"ABN {comp_abn}", 9, color=colors.HexColor("#CCDDEE"), align=TA_RIGHT),
    ]], colWidths=[UW * 0.6, UW * 0.4])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(0,0),   10),
        ("RIGHTPADDING",  (-1,0),(-1,0), 10),
    ]))
    story += [hdr, Spacer(1, 4*mm)]

    story.append(p(report_title, 12, "Helvetica-Bold", NAVY))
    story.append(Spacer(1, 4*mm))

    # ── Trial balance table ────────────────────────────────────────────
    cw = [14*mm, UW*0.38, 26*mm, 26*mm, 26*mm, 26*mm]

    th  = ParagraphStyle("TH",   fontSize=7.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr = ParagraphStyle("THR",  fontSize=7.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td  = ParagraphStyle("TD",   fontSize=7.5, fontName="Helvetica",      textColor=DGREY)
    tdr = ParagraphStyle("TDR",  fontSize=7.5, fontName="Helvetica",      textColor=DGREY, alignment=TA_RIGHT)
    tdb = ParagraphStyle("TDB",  fontSize=7.5, fontName="Helvetica-Bold", textColor=BLACK)
    tdbr= ParagraphStyle("TDBR", fontSize=7.5, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)
    sec = ParagraphStyle("SecH", fontSize=7.5, fontName="Helvetica-Bold", textColor=NAVY)

    header_row = [
        Paragraph("", th),
        Paragraph("", th),
        Paragraph(f"{year1}\n$ Dr", thr),
        Paragraph(f"{year1}\n$ Cr", thr),
        Paragraph(f"{year2}\n$ Dr", thr),
        Paragraph(f"{year2}\n$ Cr", thr),
    ]

    rows = [header_row]
    section_indices = []

    for entry in entries:
        if entry[0] == "SECTION":
            section_indices.append(len(rows))
            rows.append([Paragraph(entry[1], sec), "", "", "", "", ""])
        elif entry[0] == "TOTAL":
            rows.append([
                Paragraph("", tdb),
                Paragraph("", tdb),
                Paragraph(entry[1], tdbr),
                Paragraph(entry[2], tdbr),
                Paragraph(entry[3], tdbr),
                Paragraph(entry[4], tdbr),
            ])
        elif entry[0] == "NET":
            rows.append([
                Paragraph("", td),
                Paragraph(entry[1], tdb),
                Paragraph(entry[2], tdbr),
                Paragraph("", tdr),
                Paragraph("", tdr),
                Paragraph("", tdr),
            ])
        else:
            # ("ROW", code, name, dr1, cr1, dr2, cr2)
            rows.append([
                Paragraph(entry[1], td),
                Paragraph(entry[2], td),
                Paragraph(entry[3], tdr),
                Paragraph(entry[4], tdr),
                Paragraph(entry[5], tdr),
                Paragraph(entry[6], tdr),
            ])

    tbl = Table(rows, colWidths=cw, repeatRows=1)

    style_cmds = [
        ("BACKGROUND",    (0,0),(-1,0),   NAVY),
        ("TOPPADDING",    (0,0),(-1,-1),  2),
        ("BOTTOMPADDING", (0,0),(-1,-1),  2),
        ("LEFTPADDING",   (0,0),(-1,-1),  3),
        ("RIGHTPADDING",  (0,0),(-1,-1),  3),
        ("GRID",          (0,0),(-1,-1),  0.2, MGREY),
        ("LINEBELOW",     (0,-2),(-1,-2), 1, NAVY),
        ("LINEBELOW",     (0,-1),(-1,-1), 0.5, MGREY),
    ]
    for idx in section_indices:
        style_cmds += [
            ("BACKGROUND", (0,idx),(-1,idx), colors.HexColor("#E8F0FB")),
            ("SPAN",       (0,idx),(-1,idx)),
            ("FONTNAME",   (0,idx),(-1,idx), "Helvetica-Bold"),
        ]

    # Alternating backgrounds for non-section data rows
    data_indices = [i for i in range(1, len(rows)) if i not in section_indices]
    for j, idx in enumerate(data_indices):
        bg = WHITE if j % 2 == 0 else LGREY
        style_cmds.append(("ROWBACKGROUNDS", (0,idx),(-1,idx), [bg]))

    tbl.setStyle(TableStyle(style_cmds))
    story += [tbl, Spacer(1, 5*mm)]

    # ── Auditor note ───────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    story.append(p(
        "These financial statements are unaudited. They must be read in conjunction with the attached "
        "Accountant's Compilation Report and Notes which form part of these financial statements.",
        8, "Helvetica-Oblique", DGREY, leading=12))
    story.append(Spacer(1, 4*mm))
    story.append(p(
        f"{comp_name}  |  ABN {comp_abn}  |  {report_title}",
        7.5, color=DGREY, align=TA_CENTER, leading=11))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random trial balance PDFs with optional custom data."
    )
    parser.add_argument("--company-name", help="Company name")
    parser.add_argument("--company-abn", help="Company ABN (format: XX XXX XXX XXX)")
    parser.add_argument("--balance-date", help="Balance date (format: DD/MM/YYYY)")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\trial_balances"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    existing = [f for f in os.listdir(out_dir) if f.startswith("trial_balance_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[2].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"trial_balance_{next_n:03d}.pdf")

    build(
        path,
        company_name=args.company_name,
        company_abn=args.company_abn,
        balance_date=args.balance_date
    )

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
