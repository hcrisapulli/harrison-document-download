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

## Usage

Run the Flask application:
```bash
python app.py
```

Then open your browser and navigate to `http://localhost:5000`

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
