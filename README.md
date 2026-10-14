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
- `inventory.csv` is the starting stock list. It is loaded only when the database has no stock yet, or after **Reset everything**.
- Sales, stock, the cash drawer, uploaded photos and reset backups live in a database:
  - **Locally**: `golden_affair.db` (SQLite, created on first run, not committed).
  - **Hosted**: a Postgres database (e.g. Supabase), used whenever the `database_url` secret is set.
- Photos uploaded in **Inventory → Photos** are stored in the database. Files placed in `images/` as `<SKU>.jpg` also work.
- Times are recorded in Indian time (Asia/Kolkata), also on cloud servers.

## Deploying on Streamlit Community Cloud
The cloud server's disk is wiped whenever the app restarts, sleeps or is redeployed, so a hosted copy needs an online database.

1. **Create a free Supabase project** at supabase.com. Pick a region near you (e.g. Mumbai) and note the database password.
2. In Supabase, click **Connect** and copy the **Session pooler** connection string (the direct connection does not work from Streamlit Cloud). It looks like
   `postgresql://postgres.abcdefgh:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres`.
   Replace `[YOUR-PASSWORD]` with your database password.
3. On share.streamlit.io, create the app from this repo with `app.py` as the main file.
4. In the app's **Settings → Secrets**, add:
   ```toml
   database_url = "postgresql://postgres.abcdefgh:your-password@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"
   app_password = "choose-a-password"
   ```
   `app_password` is optional but recommended: without it, anyone with the link can see profits and edit or reset data.
5. Open the app. On first load it creates its tables in Supabase and fills the stock list from `inventory.csv`.

Free Supabase projects pause after a week with no activity; restore it from the Supabase dashboard if the app cannot connect.
