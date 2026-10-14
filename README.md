# The Golden Affair — Exhibition Billing

A Streamlit app for running the exhibition counter: one-tap billing, a cash drawer with change suggestions, sales history with product photos, stock editing, and cost / profit reports by date.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Pages
- **Billing**: product grid, cart, discount, payment method. For cash, enter the notes received to see the change and which notes to give back.
- **Cash Drawer**: count the notes and coins you hold; cash sales update it automatically.
- **Sales**: every order with product photos, filterable by date, payment and product.
- **Inventory**: stock value, edit stock and prices, add products, upload photos.
- **Profit & Reports**: gross / net sales, discounts, cost of goods, profit by category, best sellers, day-wise summary, CSV export.
- **Settings**: clear test sales, cancel a sale, or reset everything back to `inventory.csv`.

## Data
- `inventory.csv` is the starting stock list. It is loaded only when the app has no stock yet, or after **Reset everything**.
- Sales, stock and the cash drawer live in `golden_affair.db` (SQLite, created on first run, not committed).
- Product photos are stored in `images/` as `<SKU>.jpg`; upload them from **Inventory → Photos**.

## Deploying on Streamlit Community Cloud
1. Create the app from this repo with `app.py` as the main file.
2. Optional: in the app's **Settings → Secrets**, add `app_password = "your-password"` to require a password.
3. The cloud filesystem is temporary: the database and uploaded photos are wiped whenever the app restarts, sleeps or is redeployed. Download the CSVs from **Profit & Reports → Export** after every exhibition day.
