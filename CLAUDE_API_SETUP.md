# How to Get a Free Claude API Key

Follow these steps to get your free Claude API key for AI-powered instruction parsing:

## Step 1: Create an Anthropic Account

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Click "Sign Up" (top right)
3. Create an account using:
   - Email address
   - Google account
   - Or GitHub account

## Step 2: Get Your API Key

1. Once logged in, click on your profile/account icon (top right)
2. Select "API Keys" from the menu
   - Or go directly to: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
3. Click "Create Key" button
4. Give your key a name (e.g., "Document Download App")
5. Copy the API key immediately (you won't be able to see it again!)

## Step 3: Add API Key to Your Application

### Option A: Create a .env file (Recommended)

1. In the `webapp` folder, create a file named `.env` (note the dot at the start)
2. Add this line to the file:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```
3. Save the file
4. The key will be loaded automatically when you start the app

### Option B: Set Environment Variable

#### Windows Command Prompt:
```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
python app.py
```

#### Windows PowerShell:
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-api03-your-actual-key-here"
python app.py
```

## Step 4: Verify It's Working

1. Start the application
2. Select a document type (e.g., Invoice)
3. In the Instructions field, type something like:
   ```
   Make the supplier ABC Corporation with customer John Smith and subtotal $5000
   ```
4. Generate the document
5. Check the PDF - it should have "ABC Corporation" as the supplier and "John Smith" as the customer

## Free Tier Information

Anthropic provides free credits for new accounts:
- You get $5 in free credits when you sign up
- This is enough for thousands of instruction parsing requests
- The app uses Claude 3.5 Haiku, which is very cost-effective (only $0.001 per request typically)
- After free credits are used, you can add a payment method or the app will fall back to keyword-based parsing

## Troubleshooting

### "Module 'anthropic' not found"
Run: `pip install -r requirements.txt`

### "Authentication error"
- Check that your API key is correct (starts with `sk-ant-api03-`)
- Make sure there are no extra spaces or quotes around the key in the .env file
- Verify the key is still active in the Anthropic console

### Instructions not being parsed correctly
- Make sure the `.env` file is in the `webapp` folder (same folder as `app.py`)
- Restart the application after adding the API key
- Check the command window for any error messages

## Security Notes

- **Never commit your `.env` file to GitHub** (it's already in `.gitignore`)
- Keep your API key private
- If you accidentally expose your key, delete it in the Anthropic console and create a new one
