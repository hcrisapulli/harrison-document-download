"""
generators.py
Adapter layer: maps doc-type names + param dicts to the correct script build() calls.
Imports each script by file path using importlib so the existing scripts are never modified.
"""

import importlib.util
import os
import sys

# Resolve the scripts directory relative to this file
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "scripts")
)


def _load_module(script_name: str):
    """Import a script from the scripts/ directory by filename."""
    path = os.path.join(_SCRIPTS_DIR, script_name)
    spec = importlib.util.spec_from_file_location(script_name[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    # Add scripts dir to sys.path so intra-script imports work
    if _SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, _SCRIPTS_DIR)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Individual dispatch functions (one per doc type)
# ---------------------------------------------------------------------------

def _gen_invoice(params: dict, output_path: str):
    mod = _load_module("generate_invoices.py")
    mod.build_invoice(
        output_path,
        supplier_name=params.get("supplier_name") or None,
        supplier_abn=params.get("supplier_abn") or None,
        customer_name=params.get("customer_name") or None,
        subtotal=params.get("subtotal") or None,
        gst_free=bool(params.get("gst_free", False)),
        num_items=params.get("num_items") or None,
    )


def _gen_receipt(params: dict, output_path: str):
    mod = _load_module("generate_receipts.py")
    mod.build_receipt(
        output_path,
        business_name=params.get("business_name") or None,
        business_abn=params.get("business_abn") or None,
        customer_name=params.get("customer_name") or None,
        subtotal=params.get("subtotal") or None,
        num_items=params.get("num_items") or None,
    )


def _gen_utility_bill(params: dict, output_path: str):
    mod = _load_module("generate_utility_bills.py")
    data = mod.generate_utility_data(
        provider_name=params.get("provider_name") or None,
        provider_abn=params.get("provider_abn") or None,
        customer_name=params.get("customer_name") or None,
        usage_amount=params.get("usage_amount") or None,
        billing_days=params.get("billing_days") or 91,
    )
    mod.build_utility_bill(data, output_path)


def _gen_asic_fee(params: dict, output_path: str):
    mod = _load_module("generate_asic_fee.py")
    data = mod.generate_asic_data(
        company_name=params.get("company_name") or None,
        acn=params.get("acn") or None,
        amount_due=params.get("amount_due") or None,
    )
    mod.build(output_path, data)


def _gen_bank_statement(params: dict, output_path: str):
    mod = _load_module("generate_bank_statement.py")
    data = mod.generate_bank_statement_data(
        bank_name=params.get("bank_name") or None,
        account_holder=params.get("account_holder") or None,
        opening_balance=params.get("opening_balance") or None,
        num_transactions=params.get("num_transactions") or None,
    )
    mod.build(output_path, data)


def _gen_contract_note(params: dict, output_path: str):
    mod = _load_module("generate_contract_note.py")
    mod.build(
        output_path,
        broker_name=params.get("broker_name") or None,
        broker_abn=params.get("broker_abn") or None,
        client_name=params.get("client_name") or None,
        security_code=params.get("security_code") or None,
        security_name=params.get("security_name") or None,
        quantity=params.get("quantity") or None,
        price=params.get("price") or None,
        trade_type=params.get("trade_type") or None,
    )


def _gen_council_rate(params: dict, output_path: str):
    mod = _load_module("generate_council_rate.py")
    mod.build(
        output_path,
        council_name=params.get("council_name") or None,
        ratepayer_name=params.get("ratepayer_name") or None,
        property_address=params.get("property_address") or None,
        property_value=params.get("property_value") or None,
        total_rates=params.get("total_rates") or None,
    )


def _gen_dividend(params: dict, output_path: str):
    mod = _load_module("generate_dividend.py")
    mod.build(
        output_path,
        company_name=params.get("company_name") or None,
        company_abn=params.get("company_abn") or None,
        investor_name=params.get("investor_name") or None,
        shares=params.get("shares") or None,
        rate_per_share=params.get("rate_per_share") or None,
        franking_percentage=params.get("franking_percentage") or None,
    )


def _gen_property_settlement(params: dict, output_path: str):
    mod = _load_module("generate_property_settlement.py")
    mod.build(
        output_path,
        vendor_name=params.get("vendor_name") or None,
        purchaser_name=params.get("purchaser_name") or None,
        property_address=params.get("property_address") or None,
        purchase_price=params.get("purchase_price") or None,
        deposit_paid=params.get("deposit_paid") or None,
    )


def _gen_rental_statement(params: dict, output_path: str):
    mod = _load_module("generate_rental_statement.py")
    mod.build(
        output_path,
        agency_name=params.get("agency_name") or None,
        agency_abn=params.get("agency_abn") or None,
        owner_name=params.get("owner_name") or None,
        property_address=params.get("property_address") or None,
        period_from=params.get("period_from") or None,
        period_to=params.get("period_to") or None,
    )


def _gen_trial_balance(params: dict, output_path: str):
    mod = _load_module("generate_trial_balance.py")
    mod.build(
        output_path,
        company_name=params.get("company_name") or None,
        company_abn=params.get("company_abn") or None,
        balance_date=params.get("balance_date") or None,
    )


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_DISPATCH = {
    "invoice": _gen_invoice,
    "receipt": _gen_receipt,
    "utility_bill": _gen_utility_bill,
    "asic_fee": _gen_asic_fee,
    "bank_statement": _gen_bank_statement,
    "contract_note": _gen_contract_note,
    "council_rate": _gen_council_rate,
    "dividend": _gen_dividend,
    "property_settlement": _gen_property_settlement,
    "rental_statement": _gen_rental_statement,
    "trial_balance": _gen_trial_balance,
}

SUPPORTED_TYPES = list(_DISPATCH.keys())


def dispatch(doc_type: str, params: dict, output_path: str):
    """Generate a single PDF of the given doc_type with the given params."""
    fn = _DISPATCH.get(doc_type)
    if fn is None:
        raise ValueError(f"Unknown document type: {doc_type!r}")
    fn(params, output_path)
