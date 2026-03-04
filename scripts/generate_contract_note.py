"""
Contract Note (Buy/Sell Confirmation) generator.
Generates random contract notes with command-line argument support.
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
GOLD  = colors.HexColor("#D4A017")
LGREY = colors.HexColor("#F4F4F4")
MGREY = colors.HexColor("#CCCCCC")
DGREY = colors.HexColor("#555555")
WHITE = colors.white
BLACK = colors.black


# Data pools for random generation
BROKER_NAMES = [
    ("nabtrade", "nabtrade Securities Limited", "83 089 718 249", "312 686"),
    ("CommSec", "Commonwealth Securities Limited", "60 067 254 399", "238 814"),
    ("SelfWealth", "SelfWealth Ltd", "52 154 324 428", "421 789"),
]

CLIENT_NAMES = [
    "BGL CORP SUPER FUND", "CHEN FAMILY SUPER FUND", "JOHNSON INVESTMENT TRUST",
    "SMITH HOLDINGS PTY LTD", "WILSON FAMILY FUND", "TAYLOR SUPER FUND"
]

SUBURBS = [
    ("Sydney", "NSW", "2000"), ("Melbourne", "VIC", "3000"),
    ("Brisbane", "QLD", "4000"), ("Perth", "WA", "6000"),
    ("Adelaide", "SA", "5000"), ("Canberra", "ACT", "2600")
]

STREET_NAMES = [
    "Collins Street", "Queen Street", "George Street", "Bourke Street",
    "Elizabeth Street", "Market Street", "King Street", "Pitt Street"
]

SECURITIES_ASX = [
    ("BHP", "BHP GROUP LIMITED ORD"),
    ("CBA", "COMMONWEALTH BANK OF AUSTRALIA ORD"),
    ("CSL", "CSL LIMITED ORD"),
    ("WBC", "WESTPAC BANKING CORPORATION ORD"),
    ("NAB", "NATIONAL AUSTRALIA BANK LTD ORD"),
    ("ANZ", "AUSTRALIA AND NEW ZEALAND BANKING GROUP LTD ORD"),
    ("WES", "WESFARMERS LIMITED ORD"),
    ("MQG", "MACQUARIE GROUP LIMITED ORD"),
]

SECURITIES_US = [
    ("AAPL NAS", "APPLE INC ORD Common Stock"),
    ("MSFT NAS", "MICROSOFT CORP ORD Common Stock"),
    ("GOOGL NAS", "ALPHABET INC CLASS A ORD Common Stock"),
    ("AMZN NAS", "AMAZON.COM INC ORD Common Stock"),
    ("TSLA NAS", "TESLA INC ORD Common Stock"),
]


def generate_date(days_ago=0):
    """Generate a date in DD/MM/YYYY format."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%d/%m/%Y")


def round_to_tenth(amount):
    """Round amount to nearest 10 cents (e.g., 123.47 -> 123.50)."""
    return round(amount * 10) / 10


def generate_address():
    """Generate a random Australian address."""
    street_num = random.randint(1, 500)
    street = random.choice(STREET_NAMES)
    suburb, state, postcode = random.choice(SUBURBS)
    return [f"{street_num} {street.upper()}", f"{suburb.upper()} {state} {postcode}"]


def p(text, size=9, font="Helvetica", color=BLACK, align=TA_LEFT, leading=13):
    return Paragraph(text, ParagraphStyle("_", fontSize=size, fontName=font,
                     textColor=color, alignment=align, leading=leading))


def hr(c=MGREY, t=0.5):
    return HRFlowable(width=UW, thickness=t, color=c, spaceAfter=4*mm, spaceBefore=2*mm)


def build(output_path, broker_name=None, broker_abn=None, client_name=None,
          security_code=None, security_name=None, quantity=None, price=None,
          trade_type=None):
    """Build a contract note PDF with random or specified data."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)
    story = []

    td   = ParagraphStyle("TD",   fontSize=9, fontName="Helvetica",      textColor=DGREY, leading=13)
    td_r = ParagraphStyle("TDR",  fontSize=9, fontName="Helvetica",      textColor=DGREY, alignment=TA_RIGHT)
    td_b = ParagraphStyle("TDB",  fontSize=9, fontName="Helvetica-Bold", textColor=BLACK)
    td_br= ParagraphStyle("TDBR", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)
    th   = ParagraphStyle("TH",   fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr  = ParagraphStyle("THR",  fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)

    # Generate or use provided data
    if broker_name:
        b_name = broker_name
        b_legal = f"{broker_name} Securities Limited"
        b_abn = broker_abn or f"{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)} {random.randint(100,999)}"
        b_afsl = f"{random.randint(100,999)} {random.randint(100,999)}"
    else:
        b_name, b_legal, b_abn, b_afsl = random.choice(BROKER_NAMES)

    b_address = "GPO Box 4545, Melbourne VIC 3001"
    b_website = f"{b_name.lower().replace(' ', '')}.com.au"

    client = client_name or random.choice(CLIENT_NAMES)
    client_address = generate_address()

    trade_date = generate_date(random.randint(0, 30))
    settlement_date = generate_date(random.randint(-7, -2))
    conf_num = str(random.randint(100000000, 999999999))
    account_num = f"{chr(random.randint(65,90))}{chr(random.randint(65,90))}{random.randint(1000000,9999999)}-{random.randint(100,999)}"

    # Determine trade type
    if trade_type is None:
        trade_type = random.choice(["buy", "sell"])

    # Determine security
    is_international = security_code and "NAS" in security_code
    if not is_international:
        is_international = random.choice([True, False]) if not security_code else False

    if security_code:
        sec_code = security_code
        sec_name = security_name or f"{security_code} ORDINARY SHARES"
    elif is_international:
        sec_code, sec_name = random.choice(SECURITIES_US)
    else:
        sec_code, sec_name = random.choice(SECURITIES_ASX)

    exchange = "NAS" if "NAS" in sec_code else "ASX"

    # Generate quantities and prices
    qty = quantity or random.randint(100, 1000)
    if price:
        share_price = round_to_tenth(price)
    else:
        if is_international:
            share_price = round_to_tenth(random.uniform(50, 300))
        else:
            share_price = round_to_tenth(random.uniform(10, 100))

    consideration = round_to_tenth(qty * share_price)

    # Calculate brokerage
    if consideration < 1000:
        brokerage = round_to_tenth(5.00)
    elif consideration < 10000:
        brokerage = round_to_tenth(consideration * 0.01)
    else:
        brokerage = round_to_tenth(consideration * 0.005)
    brokerage = max(brokerage, round_to_tenth(10.00))

    # Build trade items
    if is_international:
        # International trade with FX
        fx_rate = round(random.uniform(0.6, 0.8), 4)
        aud_consideration = round_to_tenth(consideration / fx_rate)

        price_str = f"USD ${share_price:.2f}"
        consid_str = f"USD ${consideration:,.2f}"

        total_payable = round_to_tenth(aud_consideration + brokerage)
        trade_items = [
            (str(qty), sec_code, sec_name, price_str, consid_str),
            ("", "", "Total Value", "", f"1 AUD : {fx_rate:.4f} USD"),
            ("", "", "Brokerage", "", f"${brokerage:.2f}"),
            ("", "", "Total amount payable", "", f"${total_payable:,.2f}"),
        ]

        fx_items = [
            [str(random.randint(100000, 999999)), trade_date, settlement_date, "Base currency", "USD"],
            ["", "", "", "Client exchange rate", f"1 AUD : {fx_rate:.4f} USD"],
            ["", "", "", "Base currency amount", consid_str],
            ["", "", "", "Exchange currency amount", f"${aud_consideration:,.2f}"],
        ]
    else:
        # Domestic trade
        price_str = f"${share_price:.2f}"
        consid_str = f"${consideration:,.2f}"
        gst = round_to_tenth(brokerage * 0.1)
        total = round_to_tenth(consideration + brokerage + gst) if trade_type == "buy" else round_to_tenth(consideration - brokerage - gst)

        trade_items = [
            (str(qty), sec_code, sec_name, price_str, consid_str),
            ("", "", "Brokerage", "", f"${brokerage:.2f}"),
            ("", "", "GST on Brokerage", "", f"${gst:.2f}"),
            ("", "", "Total amount payable", "", f"${abs(total):,.2f}"),
        ]

        fx_items = None

    confirmation_title = "Buy confirmation" if trade_type == "buy" else "Sell confirmation"

    # ── Header ────────────────────────────────────────────────────────────
    hdr = Table([[
        p(b_name, 20, "Helvetica-Bold", GOLD),
        p(f"{b_legal}  ABN {b_abn}  AFSL {b_afsl}<br/>"
          f"{b_address}  |  {b_website}",
          7.5, color=DGREY, leading=11),
    ]], colWidths=[40*mm, UW - 40*mm])
    hdr.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ("LINEBELOW",     (0,0),(-1,0), 1.5, GOLD),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    # ── Title ──────────────────────────────────────────────────────────────
    story.append(p(confirmation_title, 18, "Helvetica-Bold", NAVY))
    story.append(Spacer(1, 3*mm))
    story.append(p("Tax Invoice - please retain for tax purposes.", 9, color=DGREY))
    story.append(Spacer(1, 5*mm))

    # ── Client (left) + trade meta (right) ────────────────────────────────
    client_rows = [[p(client, 9, "Helvetica-Bold", BLACK)]]
    for line in client_address:
        client_rows.append([p(line, 9, color=DGREY)])
    client_tbl = Table(client_rows, colWidths=[UW * 0.45])
    client_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0),(-1,-1), 2),
        ("BOTTOMPADDING", (0,0),(-1,-1), 2),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 0),
    ]))

    ml = ParagraphStyle("ML", fontSize=8.5, fontName="Helvetica-Bold",
                         textColor=DGREY, alignment=TA_RIGHT)
    mv = ParagraphStyle("MV", fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK)

    trade_meta = [
        ("Trade date:", trade_date),
        ("As at date:", trade_date),
        ("Settlement date:", settlement_date),
        ("Confirmation number:", conf_num),
        ("Account number:", account_num),
        ("Exchange:", exchange),
        ("Registration type:", random.choice(["Own Name", "Third Party"])),
    ]

    meta_tbl = Table(
        [[Paragraph(r[0], ml), Paragraph(r[1], mv)] for r in trade_meta],
        colWidths=[42*mm, 50*mm])
    meta_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [WHITE, LGREY]),
        ("TOPPADDING",     (0,0),(-1,-1), 3),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 3),
        ("LEFTPADDING",    (0,0),(-1,-1), 4),
        ("RIGHTPADDING",   (0,0),(-1,-1), 4),
    ]))

    top = Table([[client_tbl, meta_tbl]], colWidths=[UW * 0.45, UW * 0.55])
    top.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    story += [top, Spacer(1, 6*mm)]

    # ── Trade details table ────────────────────────────────────────────────
    story.append(p("Trade Details", 10, "Helvetica-Bold", NAVY))
    story.append(Spacer(1, 2*mm))

    trade_cw = [20*mm, 22*mm, UW * 0.35, 36*mm, 36*mm]
    trade_hdr = [
        Paragraph("Quantity", th),
        Paragraph("Code", th),
        Paragraph("Security Description", th),
        Paragraph("Avg Price per Share", thr),
        Paragraph("Consideration", thr),
    ]
    trade_data = [trade_hdr]
    for row in trade_items:
        is_summary = row[0] == "" and row[2] in ("Total Value", "Brokerage",
                                                   "Total amount payable", "GST on Brokerage")
        trade_data.append([
            Paragraph(row[0], td),
            Paragraph(row[1], td),
            Paragraph(row[2], td_b if is_summary else td),
            Paragraph(row[3], td_r),
            Paragraph(row[4], td_br if row[2] == "Total amount payable" else td_r),
        ])

    trade_tbl = Table(trade_data, colWidths=trade_cw, repeatRows=1)
    trade_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),   NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [WHITE, LGREY, WHITE, LGREY, WHITE]),
        ("ALIGN",         (3,1),(-1,-1),  "RIGHT"),
        ("TOPPADDING",    (0,0),(-1,-1),  5),
        ("BOTTOMPADDING", (0,0),(-1,-1),  5),
        ("LEFTPADDING",   (0,0),(-1,-1),  5),
        ("RIGHTPADDING",  (0,0),(-1,-1),  5),
        ("GRID",          (0,0),(-1,-1),  0.3, MGREY),
        ("LINEBELOW",     (0,-1),(-1,-1), 1, NAVY),
        ("LINEABOVE",     (0,-1),(-1,-1), 0.5, NAVY),
        ("BACKGROUND",    (0,-1),(-1,-1), colors.HexColor("#E8F0FB")),
    ]))
    story += [trade_tbl, Spacer(1, 5*mm)]

    # ── Confirmation details ───────────────────────────────────────────────
    story.append(p("Confirmation Details", 10, "Helvetica-Bold", NAVY))
    story.append(Spacer(1, 2*mm))
    conf_cw = [30*mm, 22*mm, 28*mm, UW * 0.35, 28*mm]
    conf_hdr = [
        Paragraph("Conf number", th),
        Paragraph("Total quantity", th),
        Paragraph("Price", th),
        Paragraph("Basis of quotation", th),
        Paragraph("Condition Code", th),
    ]
    conf_data = [conf_hdr] + [
        [Paragraph(str(c), td) for c in [conf_num, qty, price_str, "Market price", ""]]
    ]
    conf_tbl = Table(conf_data, colWidths=conf_cw, repeatRows=1)
    conf_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),   NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [LGREY]),
        ("TOPPADDING",    (0,0),(-1,-1),  5),
        ("BOTTOMPADDING", (0,0),(-1,-1),  5),
        ("LEFTPADDING",   (0,0),(-1,-1),  5),
        ("RIGHTPADDING",  (0,0),(-1,-1),  5),
        ("GRID",          (0,0),(-1,-1),  0.3, MGREY),
    ]))
    story += [conf_tbl, Spacer(1, 5*mm)]

    # ── FX details (if present) ────────────────────────────────────────────
    if fx_items:
        story.append(p("FX Details", 10, "Helvetica-Bold", NAVY))
        story.append(Spacer(1, 2*mm))
        fx_cw = [18*mm, 30*mm, 30*mm, UW * 0.35, 30*mm]
        fx_hdr = [
            Paragraph("FX ID", th),
            Paragraph("Transaction date", th),
            Paragraph("Settlement date", th),
            Paragraph("Description", th),
            Paragraph("Consideration", thr),
        ]
        fx_data = [fx_hdr]
        for row in fx_items:
            fx_data.append([Paragraph(str(c), td) for c in row[:-1]] +
                           [Paragraph(str(row[-1]), td_r)])
        fx_tbl = Table(fx_data, colWidths=fx_cw, repeatRows=1)
        fx_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),   NAVY),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),  [WHITE, LGREY, WHITE, LGREY]),
            ("ALIGN",         (4,1),(-1,-1),  "RIGHT"),
            ("TOPPADDING",    (0,0),(-1,-1),  5),
            ("BOTTOMPADDING", (0,0),(-1,-1),  5),
            ("LEFTPADDING",   (0,0),(-1,-1),  5),
            ("RIGHTPADDING",  (0,0),(-1,-1),  5),
            ("GRID",          (0,0),(-1,-1),  0.3, MGREY),
            ("LINEBELOW",     (0,-1),(-1,-1), 1, NAVY),
            ("BACKGROUND",    (0,-1),(-1,-1), colors.HexColor("#E8F0FB")),
        ]))
        story += [fx_tbl, Spacer(1, 4*mm)]

    # ── Notes ──────────────────────────────────────────────────────────────
    story.append(p(
        "If this confirmation does not correspond with your records please contact us within 48 hours.",
        8, "Helvetica-Oblique", DGREY, leading=12))
    story.append(p("Payment options:", 9, color=DGREY))
    story.append(p(
        "All proceeds must be received by 9am on the above settlement date. "
        "This transaction will be settled in accordance with your instructions.",
        9, color=DGREY))
    story.append(Spacer(1, 8*mm))

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(hr(NAVY, 1))
    story.append(p(
        f"The {b_name} service is provided by {b_legal} "
        f"ABN {b_abn} AFSL {b_afsl}. "
        f"{b_name} is a Market Participant under the ASX Market Integrity Rules.",
        7.5, color=DGREY, align=TA_CENTER, leading=11))

    doc.build(story)
    print(f"Created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate random contract note PDFs with optional custom data."
    )
    parser.add_argument("--broker-name", help="Broker name (e.g., nabtrade)")
    parser.add_argument("--broker-abn", help="Broker ABN (format: XX XXX XXX XXX)")
    parser.add_argument("--client-name", help="Client name")
    parser.add_argument("--security-code", help="Security code (e.g., BHP, AAPL NAS)")
    parser.add_argument("--security-name", help="Security description")
    parser.add_argument("--quantity", type=int, help="Number of shares")
    parser.add_argument("--price", type=float, help="Price per share")
    parser.add_argument("--trade-type", choices=["buy", "sell"], help="Buy or sell (default: random)")

    args = parser.parse_args()

    out_dir = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents\contract_notes"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    existing = [f for f in os.listdir(out_dir) if f.startswith("contract_note_") and f.endswith(".pdf")]
    next_n = max([int(f.split("_")[2].split(".")[0]) for f in existing], default=0) + 1

    path = os.path.join(out_dir, f"contract_note_{next_n:03d}.pdf")

    build(
        path,
        broker_name=args.broker_name,
        broker_abn=args.broker_abn,
        client_name=args.client_name,
        security_code=args.security_code,
        security_name=args.security_name,
        quantity=args.quantity,
        price=args.price,
        trade_type=args.trade_type
    )

    size = os.path.getsize(path)
    print(f"  {os.path.basename(path)}: {size:,} bytes ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
