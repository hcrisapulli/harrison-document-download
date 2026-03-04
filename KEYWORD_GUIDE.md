# Keyword-Based Instruction Guide

This guide shows all supported keywords for each document type. Keywords can be combined with commas, semicolons, or spaces.

## General Format Rules

- Use `=` or `:` to assign values: `supplier=ABC Corp` or `supplier: ABC Corp`
- Use quotes for multi-word values: `supplier="ABC Corporation Pty Ltd"`
- Dollar signs are optional: `subtotal=$5000` or `subtotal=5000`
- Commas in numbers are optional: `balance=15,000` or `balance=15000`

## Invoice Keywords

```
supplier=ABC Corp
supplier_name="ABC Corporation"
customer=John Smith
customer_name="John Smith"
abn=12 345 678 901
supplier_abn=12345678901
subtotal=5000
subtotal=$5,000
gst free (or "no gst")
3 items (or "3 line items")
```

**Example:**
```
supplier=Tech Solutions, customer=John Smith, subtotal=5000, gst free, 3 items
```

## Receipt Keywords

```
business=Corner Store
business_name="Corner Store Pty Ltd"
business_abn=12 345 678 901
customer=Sarah Williams
customer_name="Sarah Williams"
subtotal=350
subtotal=$350.00
4 items
```

**Example:**
```
business=Corner Store, customer=Michael Brown, subtotal=450, 3 items
```

## Utility Bill Keywords

```
provider=Energy Australia
provider_name="Energy Australia"
provider_abn=12 345 678 901
customer=John Smith
customer_name="John Smith"
usage=500
usage_amount=500.50
billing_days=91
91 days
```

**Example:**
```
provider=Energy Australia, customer=Sarah Williams, usage=450, 91 days
```

## ASIC Fee Keywords

```
company=ABC Pty Ltd
company_name="ABC Corporation Pty Ltd"
acn=123 456 789
amount_due=1200
amount=1200
due=1200
```

**Example:**
```
company=Tech Solutions Pty Ltd, acn=123 456 789, amount=1500
```

## Bank Statement Keywords

```
bank=Commonwealth Bank
bank_name="Commonwealth Bank"
account_holder=John Smith
holder=John Smith
balance=15000
opening_balance=15,000
20 transactions
num_transactions=20
```

**Example:**
```
bank=Commonwealth Bank, holder=Sarah Williams, balance=25000, 15 transactions
```

## Contract Note Keywords

```
broker=CommSec
broker_name="CommSec"
broker_abn=12 345 678 901
client=Sarah Williams
client_name="Sarah Williams"
security_code=CBA
code=CBA
ticker=BHP
security_name="Commonwealth Bank"
security="Commonwealth Bank"
quantity=500
qty=500
500 shares
price=42.50
price=$42.50
$42.50 per share
buy (or "sell")
```

**Example Buy:**
```
broker=CommSec, client=John Smith, buy, 500 shares, code=CBA, price=95.50
```

**Example Sell:**
```
broker=CommSec, client=Sarah Brown, sell, qty=300, ticker=BHP, price=42.75
```

## Council Rate Keywords

```
council=Melbourne City Council
council_name="Melbourne City Council"
ratepayer=John Smith
ratepayer_name="John Smith"
property=123 Main St, Melbourne VIC 3000
address="123 Main Street"
property_address="123 Main St"
property_value=750000
value=750000
total_rates=3500
rates=3500
```

**Example:**
```
council=Melbourne City Council, ratepayer=John Smith, address="123 Main St", value=800000, rates=3800
```

## Dividend Keywords

```
company=Commonwealth Bank
company_name="Commonwealth Bank"
company_abn=12 345 678 901
investor=Sarah Williams
investor_name="Sarah Williams"
500 shares
rate=0.50
rate_per_share=0.50
$0.50 per share
franking=100
100% franked
```

**Example:**
```
company=BHP Group, investor=Michael Brown, 1000 shares, rate=0.75, franking=100
```

## Property Settlement Keywords

```
vendor=John Smith
vendor_name="John Smith"
purchaser=Sarah Williams
buyer="Sarah Williams"
purchaser_name="Sarah Williams"
property=123 Main St, Melbourne VIC 3000
address="123 Main Street"
property_address="123 Main St"
purchase_price=850000
price=850000
deposit=85000
deposit_paid=85000
```

**Example:**
```
vendor=Michael Brown, purchaser=Emma Wilson, address="456 High St", price=920000, deposit=92000
```

## Rental Statement Keywords

```
agency=First National
agency_name="First National Real Estate"
agency_abn=12 345 678 901
owner=John Smith
owner_name="John Smith"
property=123 Main St, Melbourne VIC 3000
address="123 Main Street"
property_address="123 Main St"
period_from=2025-07-01
from=2025-07-01
period_to=2026-06-30
to=2026-06-30
```

**Example:**
```
agency=First National, owner=Sarah Williams, address="789 Park Ave", from=2025-07-01, to=2026-06-30
```

## Trial Balance Keywords

```
company=ABC Pty Ltd
company_name="ABC Corporation Pty Ltd"
company_abn=12 345 678 901
balance_date=2025-06-30
date=2025-06-30
```

**Example:**
```
company=Tech Solutions Pty Ltd, company_abn=12 345 678 901, date=2025-06-30
```

## Tips

1. **Combine multiple keywords** in one instruction:
   ```
   supplier=Tech Solutions, customer=John Smith, subtotal=8000, 4 items
   ```

2. **Use quotes for multi-word names**:
   ```
   company="ABC Corporation Pty Ltd", investor="Sarah Jane Williams"
   ```

3. **Order doesn't matter**:
   ```
   subtotal=5000, supplier=ABC Corp, 3 items, gst free
   ```
   is the same as:
   ```
   gst free, 3 items, subtotal=5000, supplier=ABC Corp
   ```

4. **ABN formatting is flexible**:
   - `abn=12345678901` → formatted as `12 345 678 901`
   - `abn=12 345 678 901` → kept as is
   - Must be exactly 11 digits

5. **Date format**: Use `YYYY-MM-DD` format for dates:
   - ✅ `date=2025-06-30`
   - ❌ `date=30/06/2025`
