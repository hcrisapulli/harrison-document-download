"""
ai_instruction_parser.py
Uses Claude API to parse natural language instructions into structured parameters.
Falls back to keyword-based parsing if API key is not configured.
"""

import json
import os
from typing import Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

import instruction_parser


# Parameter schemas for each document type
PARAM_SCHEMAS = {
    "invoice": {
        "supplier_name": "string - name of the supplier/business issuing the invoice",
        "supplier_abn": "string - 11-digit ABN in format XX XXX XXX XXX",
        "customer_name": "string - name of the customer receiving the invoice",
        "subtotal": "float - subtotal amount before GST",
        "gst_free": "boolean - true if invoice should be GST-free",
        "num_items": "integer - number of line items (1-10)",
    },
    "receipt": {
        "business_name": "string - name of the business issuing the receipt",
        "business_abn": "string - 11-digit ABN in format XX XXX XXX XXX",
        "customer_name": "string - name of the customer",
        "subtotal": "float - subtotal amount before GST",
        "num_items": "integer - number of line items (1-10)",
    },
    "utility_bill": {
        "provider_name": "string - name of the utility provider",
        "provider_abn": "string - 11-digit ABN",
        "customer_name": "string - account holder name",
        "usage_amount": "float - total usage amount",
        "billing_days": "integer - number of days in billing period (default 91)",
    },
    "asic_fee": {
        "company_name": "string - name of the company",
        "acn": "string - 9-digit ACN",
        "amount_due": "float - total amount due",
    },
    "bank_statement": {
        "bank_name": "string - name of the bank",
        "account_holder": "string - name of the account holder",
        "opening_balance": "float - opening balance amount",
        "num_transactions": "integer - number of transactions to generate",
    },
    "contract_note": {
        "broker_name": "string - name of the broker",
        "broker_abn": "string - 11-digit ABN",
        "client_name": "string - name of the client",
        "security_code": "string - stock ticker code (e.g., CBA, BHP)",
        "security_name": "string - full name of the security",
        "quantity": "integer - number of shares",
        "price": "float - price per share",
        "trade_type": "string - either 'buy' or 'sell'",
    },
    "council_rate": {
        "council_name": "string - name of the council",
        "ratepayer_name": "string - name of the ratepayer",
        "property_address": "string - property address",
        "property_value": "float - capital improved value",
        "total_rates": "float - total rates amount",
    },
    "dividend": {
        "company_name": "string - name of the company paying dividend",
        "company_abn": "string - 11-digit ABN",
        "investor_name": "string - name of the investor",
        "shares": "integer - number of shares held",
        "rate_per_share": "float - dividend rate per share",
        "franking_percentage": "integer - franking percentage (0-100)",
    },
    "property_settlement": {
        "vendor_name": "string - name of the vendor",
        "purchaser_name": "string - name of the purchaser",
        "property_address": "string - property address",
        "purchase_price": "float - purchase price",
        "deposit_paid": "float - deposit amount paid",
    },
    "rental_statement": {
        "agency_name": "string - name of the property management agency",
        "agency_abn": "string - 11-digit ABN",
        "owner_name": "string - name of the property owner",
        "property_address": "string - rental property address",
        "period_from": "string - start date of period (YYYY-MM-DD)",
        "period_to": "string - end date of period (YYYY-MM-DD)",
    },
    "trial_balance": {
        "company_name": "string - name of the company",
        "company_abn": "string - 11-digit ABN",
        "balance_date": "string - balance date (YYYY-MM-DD)",
    },
}


def _parse_with_ai(instruction: str, doc_type: str, api_key: str) -> dict:
    """Use Claude API to parse natural language instruction into parameters."""
    if not ANTHROPIC_AVAILABLE:
        return {}

    schema = PARAM_SCHEMAS.get(doc_type, {})
    if not schema:
        return {}

    schema_text = "\n".join([f"- {k}: {v}" for k, v in schema.items()])

    prompt = f"""Extract parameters from this instruction for generating a {doc_type} document.

Available parameters:
{schema_text}

Instruction: {instruction}

Return ONLY a JSON object with the extracted parameters. Use null for parameters not mentioned. For example:
{{"supplier_name": "ABC Corp", "subtotal": 5000, "gst_free": true, "num_items": null}}

JSON:"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Extract JSON from response (handle cases where AI adds markdown formatting)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        params = json.loads(response_text)

        # Remove null values
        return {k: v for k, v in params.items() if v is not None}

    except Exception as e:
        print(f"AI parsing failed: {e}")
        return {}


def parse(text: str, doc_type: str = None, api_key: Optional[str] = None) -> dict:
    """
    Parse instruction text into parameters.

    If api_key is provided and doc_type is specified, uses Claude API for intelligent parsing.
    Otherwise falls back to keyword-based parsing.

    Args:
        text: Instruction text to parse
        doc_type: Document type (invoice, receipt, etc.)
        api_key: Optional Claude API key for AI-powered parsing

    Returns:
        Dictionary of extracted parameters
    """
    if not text:
        return {}

    # Try AI parsing first if API key and doc_type are provided
    if api_key and doc_type and ANTHROPIC_AVAILABLE:
        ai_params = _parse_with_ai(text, doc_type, api_key)
        if ai_params:
            return ai_params

    # Fall back to keyword-based parsing
    return instruction_parser.parse(text)


def merge(form_params: dict, instruction_params: dict) -> dict:
    """
    Merge instruction-parsed params into form params.
    Explicit form fields (non-None, non-empty) take priority over parsed values.
    """
    return instruction_parser.merge(form_params, instruction_params)
