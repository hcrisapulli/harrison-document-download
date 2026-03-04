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

## AI-Powered Instructions

When the Claude API key is configured, you can use natural language instructions like:

- "Make the supplier ABC Corp with subtotal of $5000"
- "GST free invoice with 5 items"
- "Bank statement for John Smith with opening balance $10,000 and 20 transactions"
- "Buy 500 shares of CBA at $95 per share"

Without the API key, the app falls back to keyword-based parsing (e.g., "gst free", "subtotal=5000", "5 items")

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

## Requirements

- Python 3.7+
- Flask
- ReportLab
