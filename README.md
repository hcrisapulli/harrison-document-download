# Harrison Document Download

A Flask web application for generating and downloading sample Australian financial documents.

## Features

- Generate various types of Australian financial documents (invoices, receipts, utility bills, etc.)
- Download documents as PDFs
- Simple web interface for document generation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hcrisapulli/harrison-document-download.git
cd harrison-document-download
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up AI-powered instruction parsing:
   - Get a free Claude API key from [console.anthropic.com](https://console.anthropic.com/settings/keys)
   - Set the environment variable:
     ```bash
     # Windows Command Prompt
     set ANTHROPIC_API_KEY=your_api_key_here

     # Windows PowerShell
     $env:ANTHROPIC_API_KEY="your_api_key_here"

     # Linux/Mac
     export ANTHROPIC_API_KEY=your_api_key_here
     ```
   - Alternatively, create a `.env` file in the webapp directory with:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```

## Usage

### Windows (Easy Method)
Double-click the "Document Download" desktop shortcut created during setup.

### Manual Method
Run the Flask application:
```bash
python app.py
```

Then open your browser and navigate to `http://localhost:5000`

## Using Instructions

The app supports comprehensive keyword-based instruction parsing. You can customize document parameters using simple keywords.

### Quick Examples

**Invoice:**
```
supplier=Tech Solutions, customer=John Smith, subtotal=8000, 4 items
```

**Bank Statement:**
```
bank=Commonwealth Bank, holder=Sarah Williams, balance=25000, 15 transactions
```

**Contract Note (Buy):**
```
buy, 500 shares, code=CBA, price=95.50, client=Michael Brown
```

**Receipt:**
```
business=Corner Store, customer=Emma Wilson, subtotal=350, 3 items
```

### Comprehensive Keyword Guide

See [KEYWORD_GUIDE.md](KEYWORD_GUIDE.md) for the complete list of supported keywords for all document types.

**Key Features:**
- Use `=` or `:` to assign values
- Use quotes for multi-word text: `supplier="ABC Corporation Pty Ltd"`
- Flexible number formats: `$5,000` or `5000`
- ABN auto-formatting: `12345678901` → `12 345 678 901`
- Order doesn't matter - combine keywords however you like

## Document Types Supported

- Invoices
- Receipts
- Utility Bills
- ASIC Fees
- Bank Statements
- Contract Notes
- Council Rates
- Dividends
- Property Settlement Statements
- Rental Property Statements
- Trial Balances

## Project Structure

```
harrison-document-download/
├── app.py                      # Main Flask application
├── generators.py               # Document generation dispatcher
├── ai_instruction_parser.py    # AI-powered instruction parser
├── instruction_parser.py       # Fallback keyword-based parser
├── requirements.txt            # Python dependencies
├── start_webapp.bat            # Windows launcher script
├── create_shortcut.ps1         # Desktop shortcut creator
├── scripts/                    # PDF generation scripts
│   ├── generate_invoices.py
│   ├── generate_receipts.py
│   ├── generate_utility_bills.py
│   ├── generate_asic_fee.py
│   ├── generate_bank_statement.py
│   ├── generate_contract_note.py
│   ├── generate_council_rate.py
│   ├── generate_dividend.py
│   ├── generate_property_settlement.py
│   ├── generate_rental_statement.py
│   └── generate_trial_balance.py
├── static/                     # CSS and JavaScript
│   ├── css/style.css
│   └── js/app.js
└── templates/                  # HTML templates
    └── index.html
```

## Requirements

- Python 3.7+
- Flask
- ReportLab
- Anthropic (optional, for AI-powered parsing)
