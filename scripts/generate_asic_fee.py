"""
ASIC Fee / Invoice Statement generator.
Reference: ASICFEE 47.00 IssueDate_28.11.20 REDACTED.pdf
Fix: header logo rendered "ASI C" — now uses correct tight letter-spacing via
     a borderless table so the logo box and text column sit flush.
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
COMPANY_NAMES = [
    "JP & LP SUPERFUND PTY LTD", "SUNRISE HOLDINGS PTY LTD",
    "PACIFIC INVESTMENTS PTY LTD", "METRO VENTURES PTY LTD",
    "SOUTHERN CROSS FUND PTY LTD", "ZENITH CAPITAL PTY LTD",
    "AURORA ENTERPRISES PTY LTD", "NEXUS GROUP PTY LTD"
]

ADDRESS_ENTITIES = [
    "DOBBY PARTNERS", "ACCOUNTS DEPARTMENT", "FINANCIAL SERVICES",
    "INVESTMENT MANAGEMENT", "CORPORATE SERVICES"
]

STREETS = [
    "GPO BOX", "PO BOX", "LOCKED BAG"
]

SUBURBS = [
    ("NOBLE PARK", "VIC", "3174"), ("SYDNEY", "NSW", "2001"),
    ("MELBOURNE", "VIC", "3000"), ("BRISBANE", "QLD", "4000"),
    ("PERTH", "WA", "6000"), ("ADELAIDE", "SA", "5000")
]


def generate_acn():
    """Generate a valid-looking ACN (9 digits, formatted as XXX XXX XXX)."""
    return f"{random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"


def generate_reference():
    """Generate reference number in format Li XXXXXXXX."""
    return f"Li {random.randint(10000000,99999999)}"


def generate_address():
    """Generate a random Australian business address."""
    entity = random.choice(ADDRESS_ENTITIES)
    box_type = random.choice(STREETS)
    box_num = random.randint(100, 9999)
    suburb, state, postcode = random.choice(SUBURBS)
    return [entity, f"{box_type} {box_num}", f"{suburb} {state} {postcode}"]


def generate_date(days_ago=0):
    """Generate a date in DD Mon YYYY format."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%d %b %Y")


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def generate_asic_data(company_name=None, acn=None, amount_due=None):
    """Generate random ASIC fee data."""
    company = company_name or random.choice(COMPANY_NAMES)
    company_acn = acn or generate_acn()
    address = generate_address()
    invoice_no = generate_reference()
    issue_date = generate_date(0)

    # Generate amounts
    if amount_due:
        total = round_to_tenth(float(amount_due))
    else:
        # Common ASIC fee amounts - these are already rounded to nearest 10 cents
        total = random.choice([47.00, 59.00, 279.00, 315.00, 485.00])

    # Most invoices have no outstanding balance and no payments
    balance_outstanding = "$0.00"
    new_items = f"${total:.2f}"
    payments_credits = "$0.00"
    total_due = f"${total:.2f}"
    pay_immediately = "$0.00"

    # Due date is typically 2 months from issue
    due_date_obj = datetime.now() + timedelta(days=60)
    due_date = due_date_obj.strftime("%d %b %y")

    return {
        "company_name": company,
        "address_lines": address,
        "invoice_no": invoice_no,
        "acn": company_acn,
        "issue_date": issue_date,
        "balance_outstanding": balance_outstanding,
        "new_items": new_items,
        "payments_credits": payments_credits,
        "total_due": total_due,
        "pay_immediately": pay_immediately,
        "due_date": due_date,
    }


def p(text, size=9, font="Helvetica", color=BLACK, align=TA_LEFT, leading=13):
    return Paragraph(text, ParagraphStyle("_", fontSize=size, fontName=font,
                     textColor=color, alignment=align, leading=leading))


def hr(c=MGREY, t=0.5):
    return HRFlowable(width=UW, thickness=t, color=c, spaceAfter=3*mm, spaceBefore=2*mm)


def build(output_path, d):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    # ── Header: ASIC logo box + commission name ────────────────────────
    # Use a box with a dark-blue background for the "ASIC" wordmark,
    # then a second cell for the full name. Both cells share one background row.
    logo_box = Table([
        [p("ASIC", 22, "Helvetica-Bold", WHITE, TA_CENTER)],
    ], colWidths=[22*mm])
    logo_box.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))

    hdr = Table([[
        logo_box,
        p("Australian Securities &amp; Investments Commission",
          9, color=colors.HexColor("#CCDDEE"), leading=12),
    ]], colWidths=[26*mm, UW - 26*mm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(0,0),0),
        ("LEFTPADDING",(1,0),(1,0),8),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    story += [hdr, Spacer(1, 5*mm)]

    story.append(p("page 1 of 2", 8, color=DGREY, align=TA_RIGHT))
    story.append(Spacer(1, 2*mm))

    # ── Addressee (left) + Invoice No (right) ─────────────────────────
    meta = Table([
        [p("Invoice No:", 8, "Helvetica-Bold", DGREY, TA_RIGHT),
         p(d["invoice_no"], 9, "Helvetica-Bold", BLACK, TA_RIGHT)],
    ], colWidths=[28*mm, 42*mm])
    meta.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))

    addr_rows = [[p(d["company_name"], 9, "Helvetica-Bold", BLACK)]]
    for line in d["address_lines"]:
        addr_rows.append([p(line, 9, color=DGREY)])
    addr_tbl = Table(addr_rows, colWidths=[UW * 0.55])
    addr_tbl.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))

    top = Table([[addr_tbl, meta]], colWidths=[UW * 0.55, UW * 0.45])
    top.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    story += [top, Spacer(1, 5*mm)]

    # ── Invoice Statement heading ──────────────────────────────────────
    story.append(p("INVOICE STATEMENT", 16, "Helvetica-Bold", NAVY))
    story.append(Spacer(1, 2*mm))
    story.append(p(f"Issue date {d['issue_date']}", 9, color=DGREY))
    story.append(p(d["company_name"], 9, color=DGREY))
    story.append(Spacer(1, 3*mm))
    story.append(p(f"ACN  {d['acn']}", 9, color=DGREY))
    story.append(p(f"Account No.  {d['invoice_no']}", 9, color=DGREY))
    story.append(Spacer(1, 5*mm))

    # ── Summary ───────────────────────────────────────────────────────
    story.append(p("Summary", 14, "Helvetica-Bold", NAVY))
    story.append(hr())

    sum_rows = [
        ("Balance outstanding",    d["balance_outstanding"]),
        ("New items",              d["new_items"]),
        ("Payments &amp; credits", d["payments_credits"]),
    ]
    rows = [[p(lbl, 9, color=DGREY),
             p(val, 9, "Helvetica-Bold", BLACK, TA_RIGHT)] for lbl, val in sum_rows]
    rows.append([p("TOTAL DUE", 10, "Helvetica-Bold", NAVY),
                 p(d["total_due"], 10, "Helvetica-Bold", NAVY, TA_RIGHT)])
    smry = Table(rows, colWidths=[UW * 0.6, UW * 0.4])
    smry.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,2),[WHITE, LGREY, WHITE]),
        ("LINEABOVE",(0,3),(-1,3),1,NAVY),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    story += [smry, Spacer(1, 5*mm)]

    # ── Notes ─────────────────────────────────────────────────────────
    for note in [
        "Amounts are not subject to GST. (Treasurer's determination – asic registry fees, fees and charges).",
        "Payment of your annual review fee will maintain your registration as an Australian company.",
        "Transaction details are listed on the back of this page.",
    ]:
        story.append(p(f"•  {note}", 9, color=DGREY, leading=13))
    story.append(Spacer(1, 6*mm))

    # ── Please pay ────────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    story.append(p("Please pay", 14, "Helvetica-Bold", NAVY))
    pay_rows = [
        [p("Immediately",      9, color=DGREY), p(d["pay_immediately"], 20, "Helvetica-Bold", NAVY, TA_RIGHT)],
        [p(f"By {d['due_date']}", 9, color=DGREY), p(d["total_due"],   20, "Helvetica-Bold", NAVY, TA_RIGHT)],
    ]
    pt = Table(pay_rows, colWidths=[UW * 0.5, UW * 0.5])
    pt.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LINEBELOW",(0,0),(-1,0),0.5,MGREY),
    ]))
    story += [pt, Spacer(1, 4*mm)]

    story.append(p("If you have already paid please ignore this invoice statement.", 9, color=DGREY))
    story.append(Spacer(1, 3*mm))
    story.append(p("Late fees will apply if you do NOT:", 9, color=DGREY))
    for item in [
        "tell us about a change during the period that ASIC may charge a fee",
        "bring your company or scheme details up to date within 28 days of the date of issue of the annual statement, or",
        "pay your review fee within 2 months of the annual review date.",
    ]:
        story.append(p(f"  – {item}", 9, color=DGREY, leading=13))
    story.append(Spacer(1, 3*mm))
    story.append(p("Information on late fees can be found on the ASIC website.", 9, color=DGREY))
    story.append(Spacer(1, 8*mm))

    # ── Footer ────────────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    story.append(p("Australian Securities &amp; Investments Commission  |  asic.gov.au  |  1300 300 630",
                   7.5, color=DGREY, align=TA_CENTER, leading=11))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random ASIC fee PDFs with optional custom data."
    )
    parser.add_argument("--company-name", help="Company name")
    parser.add_argument("--acn", help="ACN (format: XXX XXX XXX)")
    parser.add_argument("--amount-due", type=float, help="Amount due (e.g., 47.00)")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\asic_fees"
    os.makedirs(out_dir, exist_ok=True)
    existing = [f for f in os.listdir(out_dir) if f.startswith("asic_fee_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[2].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"asic_fee_{next_n:03d}.pdf")

    data = generate_asic_data(
        company_name=args.company_name,
        acn=args.acn,
        amount_due=args.amount_due
    )

    build(path, data)

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
