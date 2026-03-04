"""
instruction_parser.py
Parses free-text instructions into a dict of keyword params.
Parsed values only fill in blank params — explicit form fields take priority.
"""

import re


def _clean_number(s: str) -> float:
    """Strip commas/spaces from a numeric string and return float."""
    return float(s.replace(",", "").replace(" ", ""))


def parse(text: str) -> dict:
    """
    Extract known param keywords from free-text instruction string.
    Returns a dict of recognised params (unrecognised text is silently ignored).
    """
    if not text:
        return {}

    params = {}
    t = text.lower()

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

    # subtotal — "subtotal=5000", "subtotal: 5000", "subtotal 5000"
    m = re.search(r"subtotal\s*[=:\s]\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["subtotal"] = _clean_number(m.group(1))

    # opening_balance — "balance=10000", "balance: 10000", "balance 10000"
    m = re.search(r"(?:opening[_\s])?balance\s*[=:\s]\s*([\d,]+(?:\.\d+)?)", t)
    if m:
        params["opening_balance"] = _clean_number(m.group(1))

    # trade_type
    if re.search(r"\bbuy\b", t):
        params["trade_type"] = "buy"
    elif re.search(r"\bsell\b", t):
        params["trade_type"] = "sell"

    # shares — "500 shares"
    m = re.search(r"(\d[\d,]*)\s*shares?", t)
    if m:
        params["shares"] = int(_clean_number(m.group(1)))

    # franking_percentage — "franking=100", "franking: 50"
    m = re.search(r"franking\s*[=:\s]\s*(\d+)", t)
    if m:
        params["franking_percentage"] = int(m.group(1))

    return params


def merge(form_params: dict, instruction_params: dict) -> dict:
    """
    Merge instruction-parsed params into form params.
    Explicit form fields (non-None, non-empty) take priority over parsed values.
    """
    merged = dict(instruction_params)
    for key, value in form_params.items():
        if value is not None and value != "" and value != 0:
            merged[key] = value
    return merged
