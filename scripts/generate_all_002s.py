"""
Generates a _002 sample PDF for every new document type, saved into the correct subfolder.
Each _002 uses different fictitious data from _001 to provide variety.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
import os, importlib.util, sys

# ── Shared constants ───────────────────────────────────────────────────────────
NAVY       = colors.HexColor("#1B2A4A")
GOLD       = colors.HexColor("#C8901A")
GREEN      = colors.HexColor("#2E6B3E")
LIGHT_GREEN = colors.HexColor("#E8F4EB")
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

BASE = r"C:\Users\hcrisapulli\Downloads\claudecode\sample_documents"


def doc(path):
    return SimpleDocTemplate(path, pagesize=A4,
        leftMargin=LEFT_M, rightMargin=RIGHT_M,
        topMargin=TOP_M, bottomMargin=BOT_M)


def hr(colour=MID_GREY, thickness=0.5):
    return HRFlowable(width=USABLE_W, thickness=thickness, color=colour,
                      spaceAfter=4*mm, spaceBefore=2*mm)


def p(text, **kw):
    defaults = dict(fontSize=9, fontName="Helvetica", textColor=DARK_GREY, leading=13)
    defaults.update(kw)
    return Paragraph(text, ParagraphStyle("_", **defaults))


def tbl_style(header_bg=NAVY, alternate=True):
    cmds = [
        ("BACKGROUND",    (0,0),(-1,0),  header_bg),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("GRID",          (0,0),(-1,-1), 0.3, MID_GREY),
        ("LINEBELOW",     (0,-1),(-1,-1), 1, header_bg),
    ]
    if alternate:
        cmds.append(("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, LIGHT_GREY]))
    return TableStyle(cmds)


# ══════════════════════════════════════════════════════════════════════════════
# ASIC Fee 002
# ══════════════════════════════════════════════════════════════════════════════
def build_asic_fee_002(out):
    d = doc(out)
    story = []

    hdr = Table([[
        p("ASIC", fontSize=28, fontName="Helvetica-Bold", textColor=WHITE),
        p("Australian Securities &amp; Investments Commission",
          fontSize=8, textColor=colors.HexColor("#CCDDEE"), leading=11),
    ]], colWidths=[30*mm, USABLE_W - 30*mm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), NAVY),
        ("VALIGN",     (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 10), ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",(0,0),(0,0),   10), ("RIGHTPADDING",  (0,0),(-1,-1), 10),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    story.append(p("page 1 of 2", fontSize=8, textColor=DARK_GREY, alignment=TA_RIGHT))
    story.append(Spacer(1, 2*mm))

    meta = Table([[p("Invoice No:", fontSize=8, fontName="Helvetica-Bold",
                      textColor=DARK_GREY, alignment=TA_RIGHT),
                   p("Li 98765432", fontSize=9, fontName="Helvetica-Bold",
                      textColor=BLACK, alignment=TA_RIGHT)]],
                 colWidths=[30*mm, 40*mm])
    meta.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                               ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)]))

    addr = Table([[p(l, fontSize=9,
                     fontName="Helvetica-Bold" if i==0 else "Helvetica", textColor=BLACK if i==0 else DARK_GREY)]
                  for i, l in enumerate([
                      "SUNRISE HOLDINGS PTY LTD", "ACCOUNTS DEPARTMENT",
                      "GPO BOX 4422", "SYDNEY NSW 2001"])],
                 colWidths=[USABLE_W * 0.55])
    addr.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                               ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))

    top = Table([[addr, meta]], colWidths=[USABLE_W*0.55, USABLE_W*0.45])
    top.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                              ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    story += [top, Spacer(1, 5*mm)]

    story.append(p("INVOICE STATEMENT", fontSize=16, fontName="Helvetica-Bold", textColor=NAVY, spaceAfter=2))
    story.append(p("Issue date 15 Jan 2025", fontSize=9, textColor=DARK_GREY))
    story.append(p("SUNRISE HOLDINGS PTY LTD", fontSize=9, textColor=DARK_GREY))
    story.append(Spacer(1, 3*mm))
    story.append(p("ACN  987 654 321", fontSize=9, textColor=DARK_GREY))
    story.append(p("Account No.  Li 98765432", fontSize=9, textColor=DARK_GREY))
    story.append(Spacer(1, 4*mm))

    story.append(p("Summary", fontSize=14, fontName="Helvetica-Bold", textColor=NAVY, spaceAfter=3))
    story.append(hr())

    sum_rows = [
        ["Balance outstanding", "$0.00"],
        ["New items",           "$59.00"],
        ["Payments &amp; credits", "$0.00"],
    ]
    rows = [[p(r[0], fontSize=9, textColor=DARK_GREY),
             p(r[1], fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)]
            for r in sum_rows]
    rows.append([p("TOTAL DUE", fontSize=10, fontName="Helvetica-Bold", textColor=NAVY),
                 p("$59.00", fontSize=10, fontName="Helvetica-Bold", textColor=NAVY, alignment=TA_RIGHT)])
    smry = Table(rows, colWidths=[USABLE_W*0.6, USABLE_W*0.4])
    smry.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,2),[WHITE,LIGHT_GREY,WHITE]),
        ("LINEABOVE",(0,3),(-1,3),1,NAVY),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    story += [smry, Spacer(1, 5*mm)]

    for note in [
        "Amounts are not subject to GST. (Treasurer's determination – ASIC registry fees, fees and charges).",
        "Payment of your annual review fee will maintain your registration as an Australian company.",
        "Transaction details are listed on the back of this page.",
    ]:
        story.append(p(f"\u2022  {note}", fontSize=9, textColor=DARK_GREY, leading=13))
    story.append(Spacer(1, 6*mm))

    story.append(hr(colour=NAVY, thickness=1))
    story.append(p("Please pay", fontSize=14, fontName="Helvetica-Bold", textColor=NAVY, spaceAfter=4))
    pay_rows = [
        [p("Immediately",  fontSize=9, textColor=DARK_GREY), p("$0.00",  fontSize=20, fontName="Helvetica-Bold", textColor=NAVY, alignment=TA_RIGHT)],
        [p("By 14 Mar 25", fontSize=9, textColor=DARK_GREY), p("$59.00", fontSize=20, fontName="Helvetica-Bold", textColor=NAVY, alignment=TA_RIGHT)],
    ]
    pt = Table(pay_rows, colWidths=[USABLE_W*0.5, USABLE_W*0.5])
    pt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                             ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
                             ("LINEBELOW",(0,0),(-1,0),0.5,MID_GREY)]))
    story += [pt, Spacer(1, 8*mm)]
    story.append(hr(colour=NAVY, thickness=1))
    story.append(p("Australian Securities &amp; Investments Commission  |  asic.gov.au  |  1300 300 630",
                   fontSize=7.5, textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    d.build(story)
    print("Created:", out)


# ══════════════════════════════════════════════════════════════════════════════
# Bank Statement 002
# ══════════════════════════════════════════════════════════════════════════════
def build_bank_statement_002(out):
    d = doc(out)
    story = []

    hdr = Table([[
        p("ANZ", fontSize=22, fontName="Helvetica-Bold", textColor=WHITE),
        p("Australia and New Zealand Banking Group Limited  ABN 11 005 357 522",
          fontSize=8, textColor=colors.HexColor("#CCDDEE")),
        p("Your Statement", fontSize=13, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT),
    ]], colWidths=[22*mm, USABLE_W*0.5, USABLE_W*0.35])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#007DBA")),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(0,0),10),("RIGHTPADDING",(-1,0),(-1,0),10),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    meta = Table([
        [p("Statement 8 (Page 1 of 1)", fontSize=8, fontName="Helvetica-Bold", textColor=DARK_GREY, alignment=TA_RIGHT)],
        [p("Account Number  01 2345 67890123", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)],
        [p("Statement Period  1 Jul 2023 – 30 Jun 2024", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)],
        [p("Closing Balance  $14,238.90 CR", fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#007DBA"), alignment=TA_RIGHT)],
        [p("Enquiries  13 13 14", fontSize=8, fontName="Helvetica-Bold", textColor=DARK_GREY, alignment=TA_RIGHT)],
    ], colWidths=[USABLE_W*0.55])
    meta.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                               ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))

    addr = Table([[p(l, fontSize=9, fontName="Helvetica-Bold" if i==0 else "Helvetica",
                      textColor=BLACK if i==0 else DARK_GREY)]
                  for i, l in enumerate(["GREENFIELD SUPER FUND","C/O GREENFIELD ADVISORY","PO BOX 889","PARRAMATTA NSW 2150"])],
                 colWidths=[USABLE_W*0.45])
    addr.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                               ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))

    story += [Table([[addr, meta]], colWidths=[USABLE_W*0.45, USABLE_W*0.55],
                     style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                       ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])),
              Spacer(1, 5*mm)]

    story.append(p("ANZ Access Advantage", fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#007DBA")))
    story.append(p("Name: MICHAEL CHEN  ATF GREENFIELD SUPER FUND", fontSize=9, textColor=DARK_GREY))
    story.append(Spacer(1, 5*mm))

    th  = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td  = lambda t: p(t, fontSize=8.5, textColor=DARK_GREY)
    tdr = lambda t: p(t, fontSize=8.5, textColor=DARK_GREY, alignment=TA_RIGHT)
    tdb = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK)
    tdbr= lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)

    cw = [22*mm, USABLE_W*0.40, 28*mm, 28*mm, 36*mm]
    rows = [
        [th("Date"), th("Transaction"), thr("Debit"), thr("Credit"), thr("Balance")],
        [tdb("01 Jul 2023"), tdb("OPENING BALANCE"), tdbr(""), tdbr(""), tdbr("$8,500.00 CR")],
        [td("15 Jul"),  td("Woolworths Supermarkets – groceries"),  tdr("$312.40"), tdr(""), tdr("$8,187.60 CR")],
        [td("22 Jul"),  td("Direct Credit – employer super contribution"), tdr(""), tdr("$5,000.00"), tdr("$13,187.60 CR")],
        [td("03 Aug"),  td("BPAY – council rates payment"),          tdr("$623.75"), tdr(""), tdr("$12,563.85 CR")],
        [td("19 Sep"),  td("Direct Credit – rental income"),         tdr(""), tdr("$2,200.00"), tdr("$14,763.85 CR")],
        [td("30 Sep"),  td("Credit Interest"),                       tdr(""), tdr("$12.18"),    tdr("$14,776.03 CR")],
        [td("12 Nov"),  td("BPay – AGL electricity"),                tdr("$284.60"), tdr(""),   tdr("$14,491.43 CR")],
        [td("07 Jan"),  td("BUY VAS units – ETF purchase"),          tdr("$3,500.00"), tdr(""), tdr("$10,991.43 CR")],
        [td("14 Mar"),  td("Direct Credit – dividend income"),       tdr(""), tdr("$247.00"),   tdr("$11,238.43 CR")],
        [td("28 Apr"),  td("ANZ monthly account fee"),               tdr("$6.00"),   tdr(""),   tdr("$11,232.43 CR")],
        [td("30 Jun"),  td("Credit Interest"),                       tdr(""), tdr("$9.47"),     tdr("$11,241.90 CR")],
        [tdb("30 Jun 2024"), tdb("CLOSING BALANCE"), tdbr(""), tdbr(""), tdbr("$14,238.90 CR")],
    ]
    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#007DBA")),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[WHITE,LIGHT_GREY]),
        ("BACKGROUND",(0,1),(-1,1),colors.HexColor("#E0F0FF")),
        ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#E0F0FF")),
        ("ALIGN",(2,1),(-1,-1),"RIGHT"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("GRID",(0,0),(-1,-1),0.3,MID_GREY),
        ("LINEBELOW",(0,-1),(-1,-1),1,colors.HexColor("#007DBA")),
    ]))
    story += [t, Spacer(1, 5*mm)]

    story.append(hr())
    story.append(p("Opening balance  −  Total debits  +  Total credits  =  Closing balance",
                   fontSize=8, fontName="Helvetica-Oblique", textColor=DARK_GREY))
    smry = Table([[p(v, fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK)
                   for v in ["$8,500.00 CR", "$4,726.75", "$7,468.65", "$14,238.90 CR"]]],
                 colWidths=[USABLE_W*0.25]*4)
    smry.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT_GREY),
        ("GRID",(0,0),(-1,-1),0.3,MID_GREY),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    story += [smry, Spacer(1, 8*mm)]

    story.append(hr(colour=colors.HexColor("#007DBA"), thickness=1))
    story.append(p("Australia and New Zealand Banking Group Limited  ABN 11 005 357 522  |  anz.com.au  |  13 13 14",
                   fontSize=7.5, textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    d.build(story)
    print("Created:", out)


# ══════════════════════════════════════════════════════════════════════════════
# Contract Note 002  (Sell confirmation)
# ══════════════════════════════════════════════════════════════════════════════
def build_contract_note_002(out):
    d = doc(out)
    story = []

    COMMSEC_ORANGE = colors.HexColor("#FF6600")

    hdr = Table([[
        p("CommSec", fontSize=20, fontName="Helvetica-Bold", textColor=COMMSEC_ORANGE),
        p("Commonwealth Securities Limited  ABN 60 067 254 399  AFSL 238814<br/>"
          "GPO Box 3280, Sydney NSW 2001  |  commsec.com.au",
          fontSize=7.5, textColor=DARK_GREY, leading=11),
    ]], colWidths=[40*mm, USABLE_W-40*mm])
    hdr.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("LINEBELOW",(0,0),(-1,0),1.5,COMMSEC_ORANGE),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    story.append(p("Sell confirmation", fontSize=18, fontName="Helvetica-Bold", textColor=NAVY, spaceAfter=4))
    story.append(p("Tax Invoice – please retain for tax purposes.", fontSize=9, textColor=DARK_GREY))
    story.append(Spacer(1, 5*mm))

    meta_rows = [
        ["Trade date:",        "15/11/2024"],
        ["As at date:",        "15/11/2024"],
        ["Settlement date:",   "19/11/2024"],
        ["Confirmation number:", "987654321"],
        ["Account number:",    "XY9876543-001"],
        ["Exchange:",          "ASX"],
        ["Registration type:", "Direct"],
    ]
    meta_tbl = Table(
        [[p(r[0], fontSize=8.5, fontName="Helvetica-Bold", textColor=DARK_GREY, alignment=TA_RIGHT),
          p(r[1], fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK)] for r in meta_rows],
        colWidths=[42*mm, 50*mm])
    meta_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LIGHT_GREY]),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))

    client_tbl = Table([[p(l, fontSize=9,
                            fontName="Helvetica-Bold" if i==0 else "Helvetica",
                            textColor=BLACK if i==0 else DARK_GREY)]
                         for i, l in enumerate(["SARAH NGUYEN","12 PARKVIEW DRIVE","CHATSWOOD NSW 2067"])],
                        colWidths=[USABLE_W*0.45])
    client_tbl.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                                     ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))

    story += [Table([[client_tbl, meta_tbl]], colWidths=[USABLE_W*0.45, USABLE_W*0.55],
                     style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                       ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])),
              Spacer(1, 6*mm)]

    story.append(p("Trade Details", fontSize=10, fontName="Helvetica-Bold", textColor=NAVY))
    story.append(Spacer(1, 2*mm))

    th  = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td  = lambda t: p(t, fontSize=9, textColor=DARK_GREY)
    tdb = lambda t: p(t, fontSize=9, fontName="Helvetica-Bold", textColor=BLACK)
    tdr = lambda t: p(t, fontSize=9, textColor=DARK_GREY, alignment=TA_RIGHT)
    tdbr= lambda t: p(t, fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)

    cw = [20*mm, 22*mm, USABLE_W*0.35, 36*mm, 36*mm]
    trade_rows = [
        [th("Quantity"), th("Code"), th("Security Description"), thr("Avg Price per Share"), thr("Consideration")],
        [td("500"), td("CBA"), td("Commonwealth Bank of Australia ORD"), tdr("$135.42"), tdr("$67,710.00")],
        [td(""),    td(""),    tdb("Total Value"),                       tdr(""),        tdr("$67,710.00")],
        [td(""),    td(""),    tdb("Brokerage"),                         tdr(""),        tdr("$19.95")],
        [td(""),    td(""),    tdb("Total proceeds received"),           tdr(""),        tdbr("$67,690.05")],
    ]
    tt = Table(trade_rows, colWidths=cw, repeatRows=1)
    tt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,LIGHT_GREY,WHITE,LIGHT_GREY]),
        ("ALIGN",(3,1),(-1,-1),"RIGHT"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("GRID",(0,0),(-1,-1),0.3,MID_GREY),
        ("LINEBELOW",(0,-1),(-1,-1),1,NAVY),
        ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#E8F0FB")),
    ]))
    story += [tt, Spacer(1, 8*mm)]
    story.append(hr(colour=NAVY, thickness=1))
    story.append(p("Commonwealth Securities Limited ABN 60 067 254 399 AFSL 238814  |  commsec.com.au  |  13 15 19",
                   fontSize=7.5, textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    d.build(story)
    print("Created:", out)


# ══════════════════════════════════════════════════════════════════════════════
# Council Rate 002
# ══════════════════════════════════════════════════════════════════════════════
def build_council_rate_002(out):
    d = doc(out)
    story = []

    COUNCIL_BLUE = colors.HexColor("#1A5276")
    LIGHT_BLUE   = colors.HexColor("#EAF2FF")

    hdr = Table([[
        Table([
            [p("YARRA", fontSize=16, fontName="Helvetica-Bold", textColor=WHITE)],
            [p("City of Melbourne's north", fontSize=8, fontName="Helvetica-Oblique",
               textColor=colors.HexColor("#AACCEE"))],
        ], colWidths=[50*mm]),
        p("Annual valuation and rate notice",
          fontSize=16, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT),
    ]], colWidths=[55*mm, USABLE_W-55*mm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),COUNCIL_BLUE),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(0,0),10),("RIGHTPADDING",(-1,0),(-1,0),10),
    ]))
    story += [hdr, Spacer(1, 4*mm)]

    story.append(p("ABN 36 238 272 659  |  1 July 2023 to 30 June 2024",
                   fontSize=8, textColor=DARK_GREY))
    story.append(Spacer(1, 5*mm))

    prop_rows = [
        ["Property number",       "7654321"],
        ["Issue date",            "28/07/2023"],
        ["Reference number",      "87654321"],
        ["Date rates declared",   "21/06/2023"],
        ["Capital improved value","$1,250,000"],
        ["Site value",            "$820,000"],
        ["Net annual value",      "$62,500"],
        ["Ward",                  "Fitzroy"],
    ]
    meta_tbl = Table(
        [[p(r[0], fontSize=8.5, fontName="Helvetica-Bold", textColor=DARK_GREY),
          p(r[1], fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)]
         for r in prop_rows], colWidths=[50*mm, 35*mm])
    meta_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LIGHT_GREY]),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("GRID",(0,0),(-1,-1),0.3,MID_GREY),
    ]))

    addr = Table([[p(l, fontSize=9, fontName="Helvetica-Bold" if i==0 else "Helvetica",
                      textColor=BLACK if i==0 else DARK_GREY)]
                  for i, l in enumerate(["PARKVIEW SUPER FUND PTY LTD","PO BOX 2244","FITZROY VIC 3065"])],
                 colWidths=[USABLE_W*0.28])
    addr.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                               ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))

    due_panel = Table([
        [p("Total amount due", fontSize=9, fontName="Helvetica-Bold", textColor=COUNCIL_BLUE, alignment=TA_RIGHT)],
        [p("$2,184.50", fontSize=18, fontName="Helvetica-Bold", textColor=GOLD, alignment=TA_RIGHT)],
        [p("by 15.02.2024", fontSize=10, fontName="Helvetica-Bold", textColor=COUNCIL_BLUE, alignment=TA_RIGHT)],
    ], colWidths=[USABLE_W*0.35])
    due_panel.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT_BLUE),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("BOX",(0,0),(-1,-1),1,COUNCIL_BLUE),
    ]))

    story += [Table([[addr, meta_tbl, due_panel]],
                     colWidths=[USABLE_W*0.28, USABLE_W*0.37, USABLE_W*0.35],
                     style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                       ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(1,0),(1,0),6),
                                       ("RIGHTPADDING",(0,0),(0,0),0),("RIGHTPADDING",(2,0),(2,0),0)])),
              Spacer(1, 6*mm)]

    story.append(p("Property location", fontSize=10, fontName="Helvetica-Bold", textColor=COUNCIL_BLUE))
    story.append(hr(colour=COUNCIL_BLUE))
    story.append(p("15 Smith Street, FITZROY VIC 3065", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK))
    story.append(p("AVPCC – Residential  Commercial Unit", fontSize=9, textColor=DARK_GREY))
    story.append(Spacer(1, 5*mm))

    story.append(p("Details of Council rates and charges", fontSize=10, fontName="Helvetica-Bold", textColor=COUNCIL_BLUE))
    story.append(Spacer(1, 2*mm))
    charges = [["Waste Management Levy", "$185.00"], ["General Rate", "$1,742.00"]]
    rate_rows = [
        [p("Charge", fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE),
         p("Amount", fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)],
    ] + [[p(r[0], fontSize=9, textColor=DARK_GREY), p(r[1], fontSize=9, textColor=DARK_GREY, alignment=TA_RIGHT)]
         for r in charges] + [
        [p("SUB TOTAL", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK),
         p("$1,927.00", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)],
    ]
    rt = Table(rate_rows, colWidths=[USABLE_W*0.7, USABLE_W*0.3])
    rt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),COUNCIL_BLUE),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[WHITE,LIGHT_GREY]),
        ("LINEABOVE",(0,-1),(-1,-1),0.5,COUNCIL_BLUE),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("GRID",(0,0),(-1,-2),0.3,MID_GREY),
    ]))
    story += [rt, Spacer(1, 5*mm)]

    story.append(hr(colour=COUNCIL_BLUE, thickness=1))
    story.append(Table([[
        p("TOTAL AMOUNT DUE:", fontSize=12, fontName="Helvetica-Bold", textColor=COUNCIL_BLUE),
        p("$2,184.50", fontSize=14, fontName="Helvetica-Bold", textColor=GOLD, alignment=TA_RIGHT),
    ]], colWidths=[USABLE_W*0.6, USABLE_W*0.4]))
    story.append(Spacer(1, 8*mm))
    story.append(hr(colour=COUNCIL_BLUE, thickness=1))
    story.append(p("Yarra City Council  |  ABN 36 238 272 659  |  yarracity.vic.gov.au  |  9205 5555",
                   fontSize=7.5, textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    d.build(story)
    print("Created:", out)


# ══════════════════════════════════════════════════════════════════════════════
# Dividend 002
# ══════════════════════════════════════════════════════════════════════════════
def build_dividend_002(out):
    d = doc(out)
    story = []

    hdr = Table([[
        p("BHP GROUP LIMITED", fontSize=14, fontName="Helvetica-Bold", textColor=WHITE),
        p("ABN: 49 004 028 077", fontSize=9, textColor=colors.HexColor("#CCDDEE"), alignment=TA_RIGHT),
    ]], colWidths=[USABLE_W*0.6, USABLE_W*0.4])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(0,0),10),("RIGHTPADDING",(-1,0),(-1,0),10),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    addr = Table([[p(l, fontSize=9, fontName="Helvetica-Bold" if i==0 else "Helvetica",
                      textColor=BLACK if i==0 else DARK_GREY)]
                  for i, l in enumerate(["MR JAMES ROBERTSON <ROBERTSON SMSF A/C>",
                                          "UNIT 4, 88 PACIFIC HWY", "NORTH SYDNEY NSW 2060"])],
                 colWidths=[USABLE_W*0.5])
    addr.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
                               ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))

    reg = Table([[p(l, fontSize=9, fontName="Helvetica-Bold" if i==0 else "Helvetica",
                     textColor=DARK_GREY)]
                  for i, l in enumerate(["All Registry communications to:",
                                          "C/- Computershare Investor Services",
                                          "GPO Box 2975, Melbourne VIC 3001",
                                          "Telephone: 1300 855 998",
                                          "ASX Code: BHP"])],
                colWidths=[USABLE_W*0.5])
    reg.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
                               ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))

    story += [Table([[addr, reg]], colWidths=[USABLE_W*0.5, USABLE_W*0.5],
                     style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                       ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])),
              Spacer(1, 6*mm)]

    story.append(p("DIVIDEND STATEMENT", fontSize=14, fontName="Helvetica-Bold", textColor=NAVY, spaceAfter=3))
    meta_tbl = Table(
        [[p(r[0], fontSize=8, fontName="Helvetica-Bold", textColor=DARK_GREY, alignment=TA_RIGHT),
          p(r[1], fontSize=9, fontName="Helvetica-Bold", textColor=BLACK)]
         for r in [["Reference No.:","Y****5544"],["Payment Date:","14 September 2024"],["Record Date:","19 August 2024"]]],
        colWidths=[35*mm, 60*mm])
    meta_tbl.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                                   ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4)]))
    story += [meta_tbl, Spacer(1, 5*mm)]

    th  = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td  = lambda t: p(t, fontSize=9, textColor=DARK_GREY)
    tdr = lambda t: p(t, fontSize=9, textColor=DARK_GREY, alignment=TA_RIGHT)
    tdb = lambda t: p(t, fontSize=9, fontName="Helvetica-Bold", textColor=BLACK)
    tdbr= lambda t: p(t, fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)

    cw = [24*mm, 22*mm, 22*mm, 24*mm, 24*mm, 26*mm, 26*mm]
    dt = Table([
        [th("Security Description"), th("Dividend Rate per Share"), thr("Participating Shares"),
         thr("Unfranked Amount"), thr("Franked Amount"), thr("Total Payment"), thr("Franking Credit")],
        [td("BHP – ORDINARY FULLY PAID SHARES"), td("$0.95"), td("2,500"),
         td("$0.00"), td("$2,375.00"), td("$2,375.00"), td("$1,017.86")],
    ], colWidths=cw, repeatRows=1)
    dt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[LIGHT_GREY]),
        ("ALIGN",(2,1),(-1,-1),"RIGHT"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("GRID",(0,0),(-1,-1),0.3,MID_GREY),
        ("LINEBELOW",(0,-1),(-1,-1),1,NAVY),
    ]))
    story += [dt, Spacer(1, 4*mm)]

    net = Table([
        [tdb("Less Resident Withholding Tax"), tdbr("$0.00")],
        [tdb("Net Amount AUD"),                tdbr("$2,375.00")],
        [td("Represented By: Direct Credit amount AUD"), tdr("$2,375.00")],
    ], colWidths=[USABLE_W*0.7, USABLE_W*0.3])
    net.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LIGHT_GREY,WHITE]),
        ("LINEABOVE",(0,1),(-1,1),0.5,NAVY),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    story += [net, Spacer(1, 5*mm)]

    story.append(p("BANKING INSTRUCTIONS", fontSize=10, fontName="Helvetica-Bold", textColor=NAVY))
    story.append(hr())
    story.append(p("The amount of AUD $2,375.00 was deposited to the bank account detailed below:", fontSize=9, textColor=DARK_GREY))
    story.append(Spacer(1, 2*mm))
    bank_rows = [["Bank:","WESTPAC BANKING CORPORATION"],["Account Name:","ROBERTSON SMSF"],
                 ["BSB:","032-010"],["Account:","*****7890"],["Direct Credit Ref No.:","4492817633"]]
    bt = Table([[p(r[0], fontSize=9, fontName="Helvetica-Bold", textColor=BLACK),
                  p(r[1], fontSize=9, textColor=DARK_GREY)] for r in bank_rows],
               colWidths=[45*mm, USABLE_W-45*mm])
    bt.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LIGHT_GREY]),
    ]))
    story += [bt, Spacer(1, 8*mm)]
    story.append(hr(colour=NAVY, thickness=1))
    story.append(p("Note: You may require this statement for taxation purposes. "
                   "All investors should seek independent advice relevant to their own particular circumstances.",
                   fontSize=7.5, textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    d.build(story)
    print("Created:", out)


# ══════════════════════════════════════════════════════════════════════════════
# Property Settlement 002
# ══════════════════════════════════════════════════════════════════════════════
def build_property_settlement_002(out):
    d = doc(out)
    story = []

    hdr = Table([[p("STATEMENT OF ADJUSTMENTS", fontSize=16, fontName="Helvetica-Bold", textColor=WHITE)]],
                colWidths=[USABLE_W])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NAVY),("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    story += [hdr, Spacer(1, 5*mm)]

    story.append(p("PATEL FROM MORGAN", fontSize=11, fontName="Helvetica-Bold", textColor=NAVY))
    for line in ["Property: 14 Riverview Terrace, Richmond, Victoria",
                 "Date of Adjustment: 22/03/2024", "Date of Settlement: 22/03/2024"]:
        story.append(p(line, fontSize=9, textColor=DARK_GREY))
    story.append(Spacer(1, 6*mm))

    vendor_s   = p("Vendor",    fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    purchaser_s = p("Purchaser", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)
    col_hdr = Table([[p("", fontSize=9), vendor_s, purchaser_s]],
                     colWidths=[USABLE_W*0.60, USABLE_W*0.20, USABLE_W*0.20])
    col_hdr.setStyle(TableStyle([
        ("BACKGROUND",(1,0),(1,0),NAVY),("BACKGROUND",(2,0),(2,0),colors.HexColor("#2E5090")),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    story.append(col_hdr)

    adjs = [
        ("Yarra City Council – General Rate $3,420.00 Annually, paid to 30/06/2024\nVendor allows 101 days", "$948.49", ""),
        ("Yarra City Council – Waste Levy $185.00 Annually, paid to 30/06/2024\nVendor allows 101 days",     "$51.37",  ""),
        ("South East Water – Water Service Charge $24.80 Quarterly, paid to 30/09/2024\nPurchaser allows 92 days", "", "$24.80"),
        ("South East Water – Sewerage Charge $109.40 Quarterly, paid to 30/09/2024\nPurchaser allows 92 days",     "", "$109.40"),
        ("Discharge of Mortgage – Electronic",                                                                "$114.40", ""),
    ]
    for i, (desc, v, pu) in enumerate(adjs):
        r = Table([[p(desc, fontSize=9, textColor=DARK_GREY),
                    p(v, fontSize=9, textColor=DARK_GREY, alignment=TA_RIGHT),
                    p(pu, fontSize=9, textColor=DARK_GREY, alignment=TA_RIGHT)]],
                   colWidths=[USABLE_W*0.60, USABLE_W*0.20, USABLE_W*0.20])
        r.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),LIGHT_GREY if i%2==1 else WHITE),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
            ("GRID",(0,0),(-1,-1),0.3,MID_GREY),
        ]))
        story.append(r)

    tot_r = Table([[p("Less Vendor's Proportion", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK),
                    p("$1,114.26", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT),
                    p("$134.20",   fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)]],
                   colWidths=[USABLE_W*0.60, USABLE_W*0.20, USABLE_W*0.20])
    tot_r.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#E8F0FB")),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("LINEABOVE",(0,0),(-1,0),1,NAVY),("GRID",(0,0),(-1,-1),0.3,MID_GREY),
    ]))
    story += [tot_r, Spacer(1, 4*mm)]

    net_r = Table([[
        p("PURCHASER TO PAY VENDOR", fontSize=11, fontName="Helvetica-Bold", textColor=NAVY),
        p("$980.06", fontSize=13, fontName="Helvetica-Bold", textColor=NAVY, alignment=TA_RIGHT),
    ]], colWidths=[USABLE_W*0.6, USABLE_W*0.4])
    net_r.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#D8E8FF")),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("BOX",(0,0),(-1,-1),1,NAVY),
    ]))
    story += [net_r, Spacer(1, 6*mm)]

    story.append(p("SETTLEMENT STATEMENT", fontSize=11, fontName="Helvetica-Bold", textColor=NAVY))
    story.append(hr(colour=NAVY))

    settle_rows = [
        ["Purchase Price", "$1,280,000.00"],
        ["Less Deposit Paid", "$128,000.00"],
        ["Balance", "$1,152,000.00"],
        ["Plus adjustments", "$980.06"],
    ]
    st = Table([[p(r[0], fontSize=9, textColor=DARK_GREY),
                  p(r[1], fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)]
                for r in settle_rows],
               colWidths=[USABLE_W*0.65, USABLE_W*0.35])
    st.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LIGHT_GREY,WHITE,LIGHT_GREY]),
        ("LINEABOVE",(0,2),(-1,2),0.5,MID_GREY),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    bal_due = Table([[
        p("BALANCE DUE TO VENDOR", fontSize=11, fontName="Helvetica-Bold", textColor=WHITE),
        p("$1,152,980.06", fontSize=13, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT),
    ]], colWidths=[USABLE_W*0.65, USABLE_W*0.35])
    bal_due.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
    ]))
    story += [st, Spacer(1, 3*mm), bal_due, Spacer(1, 8*mm)]

    story.append(hr(colour=NAVY, thickness=1))
    story.append(p("This statement of adjustments is prepared for settlement purposes only and does not constitute legal advice.",
                   fontSize=7.5, textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    d.build(story)
    print("Created:", out)


# ══════════════════════════════════════════════════════════════════════════════
# Rental Statement 002
# ══════════════════════════════════════════════════════════════════════════════
def build_rental_statement_002(out):
    d = doc(out)
    story = []

    TEAL = colors.HexColor("#1A6B5A")

    hdr = Table([[
        p("Prestige Property Management", fontSize=14, fontName="Helvetica-Bold", textColor=WHITE),
        Table([
            [p("(t) 03 9555 1234", fontSize=8, textColor=colors.HexColor("#CCEECC"), alignment=TA_RIGHT)],
            [p("info@prestigepm.com.au", fontSize=8, textColor=colors.HexColor("#CCEECC"), alignment=TA_RIGHT)],
            [p("Level 2, 200 Collins St, Melbourne VIC 3000", fontSize=8, textColor=colors.HexColor("#CCEECC"), alignment=TA_RIGHT)],
            [p("ABN: 44 555 666 777", fontSize=8, textColor=colors.HexColor("#CCEECC"), alignment=TA_RIGHT)],
        ], colWidths=[USABLE_W*0.45]),
    ]], colWidths=[USABLE_W*0.55, USABLE_W*0.45])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),TEAL),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(0,0),10),("RIGHTPADDING",(-1,0),(-1,0),10),
    ]))
    story += [hdr, Spacer(1, 6*mm)]

    folio_rows = [["Folio:","PPM-2024-447"],["From:","1/07/2023"],["To:","30/06/2024"],["Created:","3/07/2024"]]
    folio_tbl = Table(
        [[p(r[0], fontSize=8, fontName="Helvetica-Bold", textColor=DARK_GREY, alignment=TA_RIGHT),
          p(r[1], fontSize=9, fontName="Helvetica-Bold", textColor=BLACK)] for r in folio_rows],
        colWidths=[25*mm, 45*mm])
    folio_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,LIGHT_GREY]),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))
    owner = Table([[p("Sarah Chen", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK)]],
                   colWidths=[USABLE_W*0.50])
    owner.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
                                ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    story += [Table([[owner, folio_tbl]], colWidths=[USABLE_W*0.50, USABLE_W*0.50],
                     style=TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                       ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])),
              Spacer(1, 6*mm)]

    summary_items = [("Money In","$36,400.00",colors.HexColor("#E8F4EB")),
                     ("Money Out","$4,218.30",colors.HexColor("#FFF4E8")),
                     ("Balance","$32,181.70",colors.HexColor("#E8F0FB"))]
    cells = []
    for lbl, val, bg in summary_items:
        c = Table([[p(lbl, fontSize=9, fontName="Helvetica-Bold", textColor=DARK_GREY, alignment=TA_CENTER)],
                   [p(val, fontSize=13, fontName="Helvetica-Bold", textColor=NAVY, alignment=TA_CENTER)]],
                   colWidths=[(USABLE_W/3)-4*mm])
        c.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),
                                ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                                ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
                                ("BOX",(0,0),(-1,-1),0.5,MID_GREY)]))
        cells.append(c)
    story += [Table([cells], colWidths=[(USABLE_W/3)]*3,
                     style=TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)])),
              Spacer(1, 2*mm)]
    story.append(p("Total Tax on Money Out: $383.48", fontSize=9, textColor=DARK_GREY))
    story.append(Spacer(1, 5*mm))

    story.append(p("Account Transactions", fontSize=10, fontName="Helvetica-Bold", textColor=TEAL))
    story.append(Spacer(1, 2*mm))

    th  = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE)
    thr = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td  = lambda t: p(t, fontSize=9, textColor=DARK_GREY)
    tdr = lambda t: p(t, fontSize=9, textColor=DARK_GREY, alignment=TA_RIGHT)
    tdb = lambda t: p(t, fontSize=9, fontName="Helvetica-Bold", textColor=BLACK)
    tdbr= lambda t: p(t, fontSize=9, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)

    cw = [USABLE_W*0.40, 25*mm, 28*mm, 28*mm]
    rows = [
        [th("Account"), thr("Included Tax"), thr("Money Out"), thr("Money In")],
        [p("8 Hawthorn Ave, Hawthorn VIC 3122", fontSize=9, fontName="Helvetica-Bold", textColor=BLACK), p(""), p(""), p("")],
        [td("Rent"), tdr(""), tdr(""), tdr("$36,400.00")],
        [td("Plumbing repairs"), tdr("$35.00"), tdr("$385.00"), tdr("")],
        [td("Advertising"), tdr("$22.73"), tdr("$250.00"), tdr("")],
        [td("General Repairs and Maintenance"), tdr("$54.55"), tdr("$600.00"), tdr("")],
        [td("Residential Management Fee"), tdr("$254.55"), tdr("$2,800.00"), tdr("")],
        [td("Letting Fee"), tdr("$16.65"), tdr("$183.30"), tdr("")],
        [tdb("Subtotal"), tdbr(""), tdbr("$4,218.30"), tdbr("$36,400.00")],
    ]
    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),TEAL),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[WHITE,LIGHT_GREY]),
        ("ALIGN",(1,1),(-1,-1),"RIGHT"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("GRID",(0,0),(-1,-2),0.3,MID_GREY),
        ("LINEABOVE",(0,-1),(-1,-1),1,TEAL),
        ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#E8F0FB")),
        ("SPAN",(0,1),(-1,1)),("BACKGROUND",(0,1),(-1,1),colors.HexColor("#D8E8FF")),
    ]))
    story += [t, Spacer(1, 8*mm)]
    story.append(hr(colour=TEAL, thickness=1))
    story.append(p("Prestige Property Management  |  ABN 44 555 666 777  |  Level 2, 200 Collins St, Melbourne VIC 3000",
                   fontSize=7.5, textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    d.build(story)
    print("Created:", out)


# ══════════════════════════════════════════════════════════════════════════════
# Trial Balance 002
# ══════════════════════════════════════════════════════════════════════════════
def build_trial_balance_002(out):
    d = doc(out)
    story = []

    hdr = Table([[
        p("Blue River Advisory Pty Ltd", fontSize=14, fontName="Helvetica-Bold", textColor=WHITE),
        p("ABN 55 812 334 901", fontSize=9, textColor=colors.HexColor("#CCDDEE"), alignment=TA_RIGHT),
    ]], colWidths=[USABLE_W*0.6, USABLE_W*0.4])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LEFTPADDING",(0,0),(0,0),10),("RIGHTPADDING",(-1,0),(-1,0),10),
    ]))
    story += [hdr, Spacer(1, 4*mm)]
    story.append(p("Comparative Trial Balance as at 30 June 2025",
                   fontSize=12, fontName="Helvetica-Bold", textColor=NAVY, spaceAfter=2))
    story.append(Spacer(1, 4*mm))

    th  = lambda t: p(t, fontSize=8, fontName="Helvetica-Bold", textColor=WHITE)
    thr = lambda t: p(t, fontSize=8, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)
    td  = lambda t: p(t, fontSize=8.5, textColor=DARK_GREY)
    tdr = lambda t: p(t, fontSize=8.5, textColor=DARK_GREY, alignment=TA_RIGHT)
    tdb = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK)
    tdbr= lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)
    sec = lambda t: p(t, fontSize=8.5, fontName="Helvetica-Bold", textColor=NAVY)

    cw = [14*mm, USABLE_W*0.38, 26*mm, 26*mm, 26*mm, 26*mm]

    def row(code, name, dr25="", cr25="", dr24="", cr24=""):
        return [td(code), td(name), tdr(dr25), tdr(cr25), tdr(dr24), tdr(cr24)]

    def section_row(name):
        return [sec(name), p(""), p(""), p(""), p(""), p("")]

    rows = [
        [th(""), th(""), thr("2025\n$ Dr"), thr("2025\n$ Cr"), thr("2024\n$ Dr"), thr("2024\n$ Cr")],
        section_row("Income"),
        row("0510", "Consulting Fees",                  "",          "2,340,880.00"),
        row("0520", "Interest Income",                  "",          "14,220.00"),
        section_row("Expenses"),
        row("1510", "Accountancy",                      "18,700.00"),
        row("1523", "Annual leave (provision)",         "22,400.00"),
        row("1545", "Bank fees & charges",              "430.00"),
        row("1660", "Entertainment",                    "3,120.00"),
        row("1715", "General expenses",                 "890.00"),
        row("1755", "Insurance",                        "9,840.00"),
        row("1855", "Rent on land & buildings",         "84,000.00"),
        row("1871", "Software with GST",                "61,200.00"),
        row("1880", "Salaries – Ordinary",              "1,120,400.00"),
        row("1885", "Salaries – Associated persons",    "210,000.00"),
        row("1935", "Superannuation",                   "143,800.00"),
        row("1940", "Telephone",                        "2,640.00"),
        row("1950", "Travel, accommodation & conference", "4,380.00"),
        row("1966", "WorkCover",                        "8,900.00"),
        section_row("Current Assets"),
        row("2000", "Cash at bank",       "628,340.00",  "628,340.00"),
        row("2101", "Trade debtors",      "198,640.00",  "198,640.00"),
        section_row("Current Liabilities"),
        row("3325", "Provision for Income Tax",          "", "189,560.00", "", "189,560.00"),
        row("3350", "Superannuation Payable",            "", "11,200.00",  "", "11,200.00"),
        row("3380", "GST payable control account",       "", "52,800.00",  "", "52,800.00"),
        row("3392", "Wages Payable",                     "", "68,000.00",  "", "68,000.00"),
        section_row("Equity"),
        row("4160", "Dividends provided for or paid",    "350,000.00"),
        row("4199", "Retained Profits",                  "", "411,050.00", "", "411,050.00"),
        row("4200", "Issued & paid up capital",          "", "100.00",     "", "100.00"),
        # Totals
        [tdb(""), tdb(""), tdbr("2,690,740.00"), tdbr("2,690,740.00"),
         tdbr(""), tdbr("")],
        [tdb(""), tdb("Net Profit"), tdbr("595,780.00"), tdbr(""), tdbr(""), tdbr("")],
    ]

    section_indices = [i for i, r in enumerate(rows) if isinstance(r[0], Paragraph)
                       and r[0].style.name == "_" and r[0].style.fontSize == 8.5
                       and r[0].style.fontName == "Helvetica-Bold" and r[0].style.textColor == NAVY]

    style_cmds = [
        ("BACKGROUND",(0,0),(-1,0),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),
        ("ALIGN",(2,1),(-1,-1),"RIGHT"),
        ("GRID",(0,0),(-1,-1),0.2,MID_GREY),
        ("LINEBELOW",(0,-2),(-1,-2),1,NAVY),
    ]
    for idx in section_indices:
        style_cmds += [
            ("BACKGROUND",(0,idx),(-1,idx),colors.HexColor("#E8F0FB")),
            ("SPAN",(0,idx),(-1,idx)),
        ]
    data_indices = [i for i in range(1, len(rows)) if i not in section_indices]
    for j, idx in enumerate(data_indices):
        style_cmds.append(("ROWBACKGROUNDS",(0,idx),(-1,idx),[WHITE if j%2==0 else LIGHT_GREY]))

    t = Table(rows, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(style_cmds))
    story += [t, Spacer(1, 5*mm)]

    story.append(hr(colour=NAVY, thickness=1))
    story.append(p("These financial statements are unaudited. They must be read in conjunction with the attached "
                   "Accountant's Compilation Report and Notes which form part of these financial statements.",
                   fontSize=8, fontName="Helvetica-Oblique", textColor=DARK_GREY, leading=11))
    story.append(Spacer(1, 4*mm))
    story.append(p("Blue River Advisory Pty Ltd  |  ABN 55 812 334 901  |  Comparative Trial Balance as at 30 June 2025",
                   fontSize=7.5, textColor=DARK_GREY, alignment=TA_CENTER, leading=11))
    d.build(story)
    print("Created:", out)


# ══════════════════════════════════════════════════════════════════════════════
# Run all
# ══════════════════════════════════════════════════════════════════════════════
tasks = [
    (build_asic_fee_002,            "asic_fees",           "asic_fee_002.pdf"),
    (build_bank_statement_002,      "bank_statements",     "bank_statement_002.pdf"),
    (build_contract_note_002,       "contract_notes",      "contract_note_002.pdf"),
    (build_council_rate_002,        "council_rates",       "council_rate_002.pdf"),
    (build_dividend_002,            "dividends",           "dividend_002.pdf"),
    (build_property_settlement_002, "property_settlements","property_settlement_002.pdf"),
    (build_rental_statement_002,    "rental_statements",   "rental_statement_002.pdf"),
    (build_trial_balance_002,       "trial_balances",      "trial_balance_002.pdf"),
]

for fn, subfolder, fname in tasks:
    path = os.path.join(BASE, subfolder, fname)
    fn(path)
    print(f"  {fname}: {os.path.getsize(path):,} bytes")

print("\nAll done.")
