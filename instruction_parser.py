"""
instruction_parser.py
Parses free-text instructions into a dict of keyword params.
Comprehensive keyword support for all document types.
"""

import re


def _clean_number(s: str) -> float:
    """Strip commas/spaces/$ from a numeric string and return float."""
    return float(s.replace(",", "").replace(" ", "").replace("$", ""))


def _extract_quoted_text(pattern: str, text: str) -> str:
    """Extract text within quotes or after a keyword."""
    # Try quoted text first: supplier="ABC Corp" or supplier='ABC Corp'
    m = re.search(pattern + r'[=:]\s*["\']([^"\']+)["\']', text, re.IGNORECASE)
    if m:
        return m.group(1)

    # Try unquoted text: supplier=ABC Corp (up to comma, semicolon, or end)
    m = re.search(pattern + r'[=:]\s*([^,;\n]+)', text, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    return None


def parse(text: str) -> dict:
    """
    Extract known param keywords from free-text instruction string.
    Returns a dict of recognised params (unrecognised text is silently ignored).

    Supported formats:
    - supplier_name="ABC Corp" or supplier="ABC Corp"
    - subtotal=5000 or subtotal:5000 or subtotal $5000
    - gst free or no gst
    - 5 items or 5 line items
    - buy/sell (for contract notes)

    Examples:
    - "supplier=ABC Corp, customer=John Smith, subtotal=5000, gst free, 3 items"
    - "bank=Commonwealth Bank, account_holder=Sarah Williams, balance=15000, 20 transactions"
    - "buy 500 shares, price=42.50"
    """
    if not text:
        return {}

    params = {}
    t = text.lower()

    # ========== COMMON PARAMETERS ==========

    # gst_free
    if re.search(r"gst[- ]?free|no[- ]?gst", t):
        params["gst_free"] = True

    # num_items — "3 items", "3 line items", "3 lines"
    m = re.search(r"(\d+)\s*(?:line\s*)?items?|(\d+)\s*lines?", t)
    if m:
        n = m.group(1) or m.group(2)
        params["num_items"] = int(n)

    # num_transactions — "5 transactions"
    m = re.search(r"(\d+)\s*transactions?", t)
    if m:
        params["num_transactions"] = int(m.group(1))

    # subtotal — "subtotal=5000", "subtotal: $5,000", "subtotal 5000"
    m = re.search(r"subtotal\s*[=:\s]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["subtotal"] = _clean_number(m.group(1))

    # ========== INVOICE PARAMETERS ==========

    # supplier_name — "supplier=ABC Corp" or "supplier_name=ABC Corp"
    supplier = _extract_quoted_text(r"supplier(?:_name)?", text)
    if supplier:
        params["supplier_name"] = supplier

    # supplier_abn — "supplier_abn=12 345 678 901" or "abn=12345678901"
    m = re.search(r"(?:supplier[_\s])?abn\s*[=:]\s*([\d\s]+)", t)
    if m:
        abn = re.sub(r'\s+', '', m.group(1))
        if len(abn) == 11:
            params["supplier_abn"] = f"{abn[0:2]} {abn[2:5]} {abn[5:8]} {abn[8:11]}"

    # customer_name — "customer=John Smith" or "customer_name=John Smith"
    customer = _extract_quoted_text(r"customer(?:_name)?", text)
    if customer:
        params["customer_name"] = customer

    # ========== RECEIPT PARAMETERS ==========

    # business_name — "business=Corner Store" or "business_name=Corner Store"
    business = _extract_quoted_text(r"business(?:_name)?", text)
    if business:
        params["business_name"] = business

    # business_abn — "business_abn=12 345 678 901"
    m = re.search(r"business[_\s]abn\s*[=:]\s*([\d\s]+)", t)
    if m:
        abn = re.sub(r'\s+', '', m.group(1))
        if len(abn) == 11:
            params["business_abn"] = f"{abn[0:2]} {abn[2:5]} {abn[5:8]} {abn[8:11]}"

    # ========== UTILITY BILL PARAMETERS ==========

    # provider_name — "provider=Energy Australia"
    provider = _extract_quoted_text(r"provider(?:_name)?", text)
    if provider:
        params["provider_name"] = provider

    # provider_abn
    m = re.search(r"provider[_\s]abn\s*[=:]\s*([\d\s]+)", t)
    if m:
        abn = re.sub(r'\s+', '', m.group(1))
        if len(abn) == 11:
            params["provider_abn"] = f"{abn[0:2]} {abn[2:5]} {abn[5:8]} {abn[8:11]}"

    # usage_amount — "usage=500" or "usage_amount=500"
    m = re.search(r"usage(?:_amount)?\s*[=:]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["usage_amount"] = _clean_number(m.group(1))

    # billing_days — "billing_days=91" or "91 days"
    m = re.search(r"(?:billing[_\s])?(\d+)\s*days?", t)
    if m:
        params["billing_days"] = int(m.group(1))

    # ========== ASIC FEE PARAMETERS ==========

    # company_name — "company=ABC Pty Ltd"
    company = _extract_quoted_text(r"company(?:_name)?", text)
    if company:
        params["company_name"] = company

    # acn — "acn=123 456 789" (9 digits)
    m = re.search(r"acn\s*[=:]\s*([\d\s]+)", t)
    if m:
        acn = re.sub(r'\s+', '', m.group(1))
        if len(acn) == 9:
            params["acn"] = f"{acn[0:3]} {acn[3:6]} {acn[6:9]}"

    # amount_due — "amount_due=1200" or "amount=1200" or "due=1200"
    m = re.search(r"(?:amount[_\s])?due\s*[=:]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["amount_due"] = _clean_number(m.group(1))
    elif not params.get("subtotal"):  # Use "amount=" if amount_due not found
        m = re.search(r"\bamount\s*[=:]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
        if m:
            params["amount_due"] = _clean_number(m.group(1))

    # ========== BANK STATEMENT PARAMETERS ==========

    # financial_year — "FY2025", "FY 2025", "Financial Year 2025", "financial_year=2025"
    m = re.search(r"(?:financial[_\s]?year|fy)[_\s=:]?\s*(\d{4})", t)
    if m:
        params["financial_year"] = int(m.group(1))

    # bank_name — "bank=Commonwealth Bank"
    bank = _extract_quoted_text(r"bank(?:_name)?", text)
    if bank:
        params["bank_name"] = bank

    # account_holder — "account_holder=John Smith" or "holder=John Smith"
    holder = _extract_quoted_text(r"(?:account[_\s])?holder", text)
    if holder:
        params["account_holder"] = holder

    # show_balance — "no running balance", "no balance", "hide balance"
    if re.search(r"no\s+running\s+balance|no\s+balance|hide\s+balance|without\s+balance", t):
        params["show_balance"] = True

    # opening_balance — "balance=10000", "opening_balance=10000"
    m = re.search(r"(?:opening[_\s])?balance\s*[=:]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["opening_balance"] = _clean_number(m.group(1))

    # ========== CONTRACT NOTE PARAMETERS ==========

    # broker_name — "broker=CommSec"
    broker = _extract_quoted_text(r"broker(?:_name)?", text)
    if broker:
        params["broker_name"] = broker

    # broker_abn
    m = re.search(r"broker[_\s]abn\s*[=:]\s*([\d\s]+)", t)
    if m:
        abn = re.sub(r'\s+', '', m.group(1))
        if len(abn) == 11:
            params["broker_abn"] = f"{abn[0:2]} {abn[2:5]} {abn[5:8]} {abn[8:11]}"

    # client_name — "client=Sarah Williams"
    client = _extract_quoted_text(r"client(?:_name)?", text)
    if client:
        params["client_name"] = client

    # security_code — "security_code=CBA" or "code=CBA" or "ticker=CBA"
    m = re.search(r"(?:security[_\s])?(?:code|ticker)\s*[=:]\s*([A-Z]{3,4})", text, re.IGNORECASE)
    if m:
        params["security_code"] = m.group(1).upper()

    # security_name — "security_name=Commonwealth Bank" or "security=Commonwealth Bank"
    security = _extract_quoted_text(r"security(?:_name)?", text)
    if security:
        params["security_name"] = security

    # quantity — "quantity=500" or "qty=500" or "500 shares"
    m = re.search(r"(?:quantity|qty)\s*[=:]\s*([\d,]+)", t)
    if m:
        params["quantity"] = int(_clean_number(m.group(1)))
    elif "shares" not in params:  # Don't override if shares already found
        m = re.search(r"(\d[\d,]*)\s*shares?", t)
        if m:
            params["quantity"] = int(_clean_number(m.group(1)))

    # price — "price=42.50" or "$42.50 per share"
    m = re.search(r"price\s*[=:]\s*\$?\s*([\d,]+\.\d+)", t)
    if m:
        params["price"] = _clean_number(m.group(1))
    elif not params.get("price"):
        m = re.search(r"\$\s*([\d,]+\.\d+)\s*(?:per|/)\s*share", t)
        if m:
            params["price"] = _clean_number(m.group(1))

    # trade_type — "buy" or "sell"
    if re.search(r"\bbuy\b", t):
        params["trade_type"] = "buy"
    elif re.search(r"\bsell\b", t):
        params["trade_type"] = "sell"

    # shares (for dividends) — "500 shares"
    m = re.search(r"(\d[\d,]*)\s*shares?", t)
    if m:
        params["shares"] = int(_clean_number(m.group(1)))

    # ========== COUNCIL RATE PARAMETERS ==========

    # council_name — "council=Melbourne City Council"
    council = _extract_quoted_text(r"council(?:_name)?", text)
    if council:
        params["council_name"] = council

    # ratepayer_name — "ratepayer=John Smith"
    ratepayer = _extract_quoted_text(r"ratepayer(?:_name)?", text)
    if ratepayer:
        params["ratepayer_name"] = ratepayer

    # property_address — "property=123 Main St" or "address=123 Main St"
    prop_addr = _extract_quoted_text(r"(?:property[_\s])?address", text)
    if prop_addr:
        params["property_address"] = prop_addr
    elif not params.get("property_address"):
        prop_addr = _extract_quoted_text(r"property", text)
        if prop_addr:
            params["property_address"] = prop_addr

    # property_value — "property_value=500000" or "value=500000"
    m = re.search(r"(?:property[_\s])?value\s*[=:]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["property_value"] = _clean_number(m.group(1))

    # total_rates — "total_rates=3500" or "rates=3500"
    m = re.search(r"(?:total[_\s])?rates\s*[=:]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["total_rates"] = _clean_number(m.group(1))

    # ========== DIVIDEND PARAMETERS ==========

    # company_abn (for dividends)
    m = re.search(r"company[_\s]abn\s*[=:]\s*([\d\s]+)", t)
    if m:
        abn = re.sub(r'\s+', '', m.group(1))
        if len(abn) == 11:
            params["company_abn"] = f"{abn[0:2]} {abn[2:5]} {abn[5:8]} {abn[8:11]}"

    # investor_name — "investor=Sarah Williams"
    investor = _extract_quoted_text(r"investor(?:_name)?", text)
    if investor:
        params["investor_name"] = investor

    # rate_per_share — "rate=0.50" or "rate_per_share=0.50" or "$0.50 per share"
    m = re.search(r"rate(?:_per_share)?\s*[=:]\s*\$?\s*([\d,]+\.\d+)", t)
    if m:
        params["rate_per_share"] = _clean_number(m.group(1))
    elif not params.get("rate_per_share"):
        m = re.search(r"\$\s*([\d,]+\.\d+)\s*(?:per|/)\s*share", t)
        if m:
            params["rate_per_share"] = _clean_number(m.group(1))

    # franking_percentage — "franking=100" or "100% franked"
    m = re.search(r"franking\s*[=:]\s*(\d+)", t)
    if m:
        params["franking_percentage"] = int(m.group(1))
    elif not params.get("franking_percentage"):
        m = re.search(r"(\d+)%?\s*franked", t)
        if m:
            params["franking_percentage"] = int(m.group(1))

    # ========== PROPERTY SETTLEMENT PARAMETERS ==========

    # vendor_name — "vendor=John Smith"
    vendor = _extract_quoted_text(r"vendor(?:_name)?", text)
    if vendor:
        params["vendor_name"] = vendor

    # purchaser_name — "purchaser=Sarah Williams" or "buyer=Sarah Williams"
    purchaser = _extract_quoted_text(r"(?:purchaser|buyer)(?:_name)?", text)
    if purchaser:
        params["purchaser_name"] = purchaser

    # purchase_price — "purchase_price=850000" or "price=850000"
    m = re.search(r"(?:purchase[_\s])?price\s*[=:]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["purchase_price"] = _clean_number(m.group(1))

    # deposit_paid — "deposit=85000" or "deposit_paid=85000"
    m = re.search(r"deposit(?:_paid)?\s*[=:]\s*\$?\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["deposit_paid"] = _clean_number(m.group(1))

    # ========== RENTAL STATEMENT PARAMETERS ==========

    # agency_name — "agency=First National"
    agency = _extract_quoted_text(r"agency(?:_name)?", text)
    if agency:
        params["agency_name"] = agency

    # agency_abn
    m = re.search(r"agency[_\s]abn\s*[=:]\s*([\d\s]+)", t)
    if m:
        abn = re.sub(r'\s+', '', m.group(1))
        if len(abn) == 11:
            params["agency_abn"] = f"{abn[0:2]} {abn[2:5]} {abn[5:8]} {abn[8:11]}"

    # owner_name — "owner=Michael Brown"
    owner = _extract_quoted_text(r"owner(?:_name)?", text)
    if owner:
        params["owner_name"] = owner

    # period_from — "period_from=2025-07-01" or "from=2025-07-01"
    m = re.search(r"(?:period[_\s])?from\s*[=:]\s*([\d-]+)", t)
    if m:
        params["period_from"] = m.group(1)

    # period_to — "period_to=2026-06-30" or "to=2026-06-30"
    m = re.search(r"(?:period[_\s])?to\s*[=:]\s*([\d-]+)", t)
    if m:
        params["period_to"] = m.group(1)

    # ========== TRIAL BALANCE PARAMETERS ==========

    # balance_date — "balance_date=2025-06-30" or "date=2025-06-30"
    m = re.search(r"(?:balance[_\s])?date\s*[=:]\s*([\d-]+)", t)
    if m:
        params["balance_date"] = m.group(1)

    return params


def merge(form_params: dict, instruction_params: dict) -> dict:
    """
    Merge instruction-parsed params into form params.
    Explicit form fields (non-None, non-empty string) take priority over parsed values.
    Note: 0 is a valid value and is not treated as empty.
    """
    merged = dict(instruction_params)
    for key, value in form_params.items():
        if value is not None and value != "":
            merged[key] = value
    return merged
