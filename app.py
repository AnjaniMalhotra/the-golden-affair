
import streamlit as st
import pandas as pd
import sqlite3
import base64, html, io, re, shutil
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageOps
import uuid

APP_DIR = Path(__file__).parent
CSV_PATH = APP_DIR / "inventory.csv"
DB_PATH = APP_DIR / "golden_affair.db"
IMG_DIR = APP_DIR / "images"
PAYMENTS = ["UPI","Cash","Card","Other"]
LOW_STOCK = 2
DENOMS = [500,200,100,50,20,10,5,2,1]
PAGES = ["🛒  Billing","💵  Cash Drawer","🧾  Sales","📦  Inventory","📈  Profit & Reports","⚙️  Settings"]

st.set_page_config(page_title="The Golden Affair | Exhibition", page_icon="✨", layout="wide")

st.markdown("""
<style>
:root { --ink:#3b2a20; --brown:#5a3928; --muted:#8a6b55; --line:#e7dac9; --card:#fffdf9;
        --gold:#b08a4f; --green:#2f7d57; --red:#b54b36; }
.stApp { background:#f7f3ed; }
.block-container { padding-top:1.6rem; padding-bottom:3rem; max-width:1500px; }
#MainMenu, footer { visibility:hidden; }

/* header */
.topbar { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid var(--line); padding-bottom:12px; margin-bottom:16px; }
.brand { font-family:Georgia,'Times New Roman',serif; font-size:32px; font-weight:700; color:var(--brown); letter-spacing:.3px; line-height:1.1; }
.sub { color:var(--muted); font-size:12px; letter-spacing:2.2px; text-transform:uppercase; margin-top:4px; }
.today { color:var(--muted); font-size:13px; text-align:right; }
.today b { color:var(--brown); font-size:15px; display:block; }
.section { font-family:Georgia,serif; font-size:19px; font-weight:700; color:var(--brown); margin:14px 0 6px; }

/* metrics */
[data-testid="stMetric"] { background:var(--card); border:1px solid var(--line); border-left:4px solid var(--gold); padding:12px 16px; border-radius:12px; box-shadow:0 1px 6px rgba(70,45,25,.04); }
[data-testid="stMetricLabel"] p { color:var(--muted); font-size:11.5px; letter-spacing:1.1px; text-transform:uppercase; font-weight:600; }
[data-testid="stMetricValue"] { color:var(--brown); font-weight:700; font-size:26px; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap:4px; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"] { padding:10px 20px; border-radius:10px 10px 0 0; color:var(--muted); }
.stTabs [data-baseweb="tab"] p { font-size:15px; font-weight:600; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background:var(--card); color:var(--brown); border:1px solid var(--line); border-bottom:none; }
.stTabs [data-baseweb="tab-panel"] { padding-top:18px; }

/* product cards */
div[class*="st-key-pc_"] { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:10px; box-shadow:0 2px 10px rgba(70,45,25,.04); margin-bottom:6px; gap:.5rem; }
.pimg { width:100%; aspect-ratio:1/1; border-radius:10px; overflow:hidden; background:#efe6d8; display:flex; align-items:center; justify-content:center; color:#b39b82; font-size:11px; letter-spacing:1.5px; position:relative; }
.pimg img { width:100%; height:100%; object-fit:cover; display:block; }
.pnew { position:absolute; top:8px; left:8px; background:var(--brown); color:#fff; font-size:10px; font-weight:700; letter-spacing:1px; padding:2px 7px; border-radius:20px; }
.pname { font-weight:650; color:var(--ink); font-size:14.5px; line-height:1.25; margin-top:9px; height:2.5em; overflow:hidden; text-transform:capitalize; }
.pmeta { font-size:11.5px; color:var(--muted); margin-top:2px; }
.prow { display:flex; justify-content:space-between; align-items:baseline; margin-top:6px; }
.price { font-size:20px; font-weight:750; color:var(--brown); }
.stock { font-size:12px; color:var(--muted); }
.low { color:var(--red); font-weight:700; }

/* bill panel */
.st-key-billpanel { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:18px 18px 20px; box-shadow:0 2px 14px rgba(70,45,25,.06); }
.cname { font-weight:600; color:var(--ink); font-size:14px; line-height:1.25; text-transform:capitalize; }
.cmeta { font-size:12px; color:var(--muted); }
.cqty { text-align:center; font-weight:700; padding-top:7px; }
.cline { text-align:right; font-weight:700; color:var(--brown); padding-top:7px; }
.totrow { display:flex; justify-content:space-between; color:var(--muted); font-size:13.5px; margin:3px 0; }
.totrow.grand { color:var(--brown); font-size:28px; font-weight:800; border-top:1px dashed var(--line); padding-top:8px; margin-top:8px; align-items:baseline; }
.totrow.grand span:first-child { font-size:13px; letter-spacing:1.5px; text-transform:uppercase; font-weight:600; color:var(--muted); }

/* order cards */
.order { background:var(--card); border:1px solid var(--line); border-radius:14px; margin-bottom:12px; overflow:hidden; box-shadow:0 1px 6px rgba(70,45,25,.04); }
.ohead { display:flex; justify-content:space-between; align-items:center; padding:10px 16px; background:#f3ebdf; border-bottom:1px solid var(--line); }
.oid { font-weight:700; color:var(--brown); font-family:ui-monospace,Menlo,monospace; font-size:13.5px; }
.otime { color:var(--muted); font-size:12.5px; margin-left:10px; }
.pay { font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; padding:3px 10px; border-radius:20px; background:#e9ddce; color:var(--brown); }
.pay-upi { background:#e2ecf7; color:#2b5c8f; } .pay-cash { background:#e1f0e7; color:var(--green); } .pay-card { background:#efe4f5; color:#6d3f8c; }
.oitem { display:flex; align-items:center; gap:14px; padding:10px 16px; border-bottom:1px solid #f1e8db; }
.othumb { width:58px; height:58px; flex:none; border-radius:9px; overflow:hidden; background:#efe6d8; display:flex; align-items:center; justify-content:center; color:#b39b82; font-size:8.5px; letter-spacing:.8px; text-align:center; }
.othumb img { width:100%; height:100%; object-fit:cover; display:block; }
.oname { flex:1; font-weight:650; color:var(--ink); font-size:14.5px; text-transform:capitalize; }
.oname small { display:block; font-weight:400; color:var(--muted); font-size:12px; text-transform:none; }
.oqty { color:var(--muted); font-size:13px; white-space:nowrap; }
.oline { width:90px; text-align:right; font-weight:700; color:var(--brown); }
.ofoot { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:6px 22px; padding:10px 16px; font-size:13px; color:var(--muted); }
.ofoot b { color:var(--brown); font-size:15px; }
.ofoot .profit { color:var(--green); font-weight:700; }

/* sidebar menu */
[data-testid="stSidebar"] { background:#efe6d8; border-right:1px solid var(--line); }
.sbrand { font-family:Georgia,serif; font-size:23px; font-weight:700; color:var(--brown); line-height:1.15; }
.shead { color:var(--muted); font-size:11px; letter-spacing:1.6px; text-transform:uppercase; font-weight:700; margin:6px 0 2px; }
.st-key-page [role="radiogroup"] { gap:5px; }
.st-key-page [role="radiogroup"] label { width:100%; padding:10px 14px; border-radius:10px; margin:0; cursor:pointer; border:1px solid transparent; }
.st-key-page [role="radiogroup"] label > div:first-child { display:none; }
.st-key-page [role="radiogroup"] label p { font-size:15.5px; font-weight:600; color:var(--muted); }
.st-key-page [role="radiogroup"] label:hover { background:#e6d9c5; }
.st-key-page [role="radiogroup"] label:has(input:checked) { background:var(--card); border-color:var(--line); box-shadow:0 1px 6px rgba(70,45,25,.06); }
.st-key-page [role="radiogroup"] label:has(input:checked) p { color:var(--brown); }

/* cash */
.changebox { background:#e1f0e7; border:1px solid #bfdccb; border-radius:12px; padding:10px 14px; margin:8px 0; color:var(--green); }
.changebox .lbl { font-size:11.5px; letter-spacing:1.4px; text-transform:uppercase; font-weight:700; }
.changebox .amt { font-size:28px; font-weight:800; line-height:1.15; }
.changebox.short { background:#f8e6e1; border-color:#e8c4ba; color:var(--red); }

div.stButton > button, div.stDownloadButton > button { border-radius:10px; min-height:38px; font-weight:600; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

def app_password():
    try: return st.secrets.get("app_password")
    except Exception: return None   # no secrets file when running locally

# Optional lock for a hosted copy: set app_password in the Streamlit Cloud secrets to require it.
if app_password() and not st.session_state.get("unlocked"):
    st.markdown('<div class="brand" style="margin-top:40px">The Golden Affair</div>'
                '<div class="sub">Exhibition counter</div>',unsafe_allow_html=True)
    with st.form("login",border=False):
        pw=st.text_input("Password",type="password")
        if st.form_submit_button("Unlock",type="primary"):
            if pw==app_password():
                st.session_state.unlocked=True
                st.rerun()
            st.error("Wrong password")
    st.stop()

def connect():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.execute("""CREATE TABLE IF NOT EXISTS inventory(
        sku TEXT PRIMARY KEY, product TEXT, category TEXT, qty INTEGER,
        buy_price REAL, sell_price REAL, image TEXT, new INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS sales(
        order_id TEXT PRIMARY KEY, created_at TEXT, payment_method TEXT,
        subtotal REAL, discount REAL, total REAL, cost REAL, profit REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS sale_items(
        order_id TEXT, sku TEXT, product TEXT, qty INTEGER,
        sell_price REAL, buy_price REAL, line_total REAL, line_profit REAL)""")
    c.execute("CREATE TABLE IF NOT EXISTS cash_drawer(denom INTEGER PRIMARY KEY, count INTEGER NOT NULL DEFAULT 0)")
    # one row per denomination moved in a sale: delta > 0 received from customer, delta < 0 given as change
    c.execute("CREATE TABLE IF NOT EXISTS cash_moves(order_id TEXT, denom INTEGER, delta INTEGER)")
    c.commit()
    return c

conn = connect()

def seed_if_empty():
    if conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] == 0:
        d = pd.read_csv(CSV_PATH)
        for _, r in d.iterrows():
            conn.execute("""INSERT INTO inventory
                (sku,product,category,qty,buy_price,sell_price,image,new)
                VALUES (?,?,?,?,?,?,?,?)""",
                (r.sku,r['product'],r.category,int(r.qty),float(r.buy_price),
                 float(r.sell_price),r.image,int(r.new)))
        conn.commit()
seed_if_empty()

if "cart" not in st.session_state:
    st.session_state.cart = {}

def money(v):
    return f"₹{float(v):,.0f}"

def pct(part, whole):
    return f"{(part/whole*100 if whole else 0):.0f}%"

@st.cache_data(show_spinner=False)
def _thumb(path, mtime, size):
    im = ImageOps.exif_transpose(Image.open(path))
    im.thumbnail((size,size))
    buf = io.BytesIO()
    im.convert("RGB").save(buf,"JPEG",quality=82)
    return "data:image/jpeg;base64,"+base64.b64encode(buf.getvalue()).decode()

def thumb(rel, size=160):
    """Small data-URI version of a product photo, or None if there is no photo yet."""
    if rel is None or pd.isna(rel) or not str(rel): return None
    p = APP_DIR/str(rel)
    if not p.exists():
        for ext in (".jpg",".jpeg",".png",".webp",".JPG",".JPEG",".PNG"):
            if p.with_suffix(ext).exists(): p = p.with_suffix(ext); break
        else: return None
    try: return _thumb(str(p),p.stat().st_mtime,size)
    except Exception: return None

def img_tag(rel, size=160, placeholder="NO PHOTO"):
    src = thumb(rel,size)
    return f'<img src="{src}">' if src else placeholder

def drawer():
    d=dict(conn.execute("SELECT denom,count FROM cash_drawer").fetchall())
    return {k:int(d.get(k,0)) for k in DENOMS}

def bump_drawer(denom, n):
    conn.execute("""INSERT INTO cash_drawer(denom,count) VALUES(?,?)
                    ON CONFLICT(denom) DO UPDATE SET count=MAX(0,count+?)""",(denom,max(0,n),n))

def set_drawer(counts):
    for k,v in counts.items():
        conn.execute("INSERT OR REPLACE INTO cash_drawer(denom,count) VALUES(?,?)",(k,int(v)))
    conn.commit()

def cash_value(counts):
    return sum(k*v for k,v in counts.items())

def describe(counts):
    return "  +  ".join(f"₹{k} × {counts[k]}" for k in DENOMS if counts.get(k)) or "nothing"

def _reach(amount, avail):
    """Every amount up to `amount` the drawer can make, each with its fewest-pieces combination."""
    best={0:{}}
    for d in DENOMS:
        n=avail.get(d,0)
        if n<=0: continue
        nxt=dict(best)
        for a,combo in best.items():
            for k in range(1,n+1):
                b=a+d*k
                if b>amount: break
                if b not in nxt or sum(combo.values())+k<sum(nxt[b].values()):
                    nxt[b]={**combo,d:k}
        best=nxt
    return best

def change_options(amount, avail):
    """Ways to give `amount` from the drawer, fewest notes first. If it cannot be made exactly,
    the amount returned is the closest lower one that can."""
    reach=_reach(amount,avail)
    target=max(reach)
    opts=[reach[target]]
    for d in list(opts[0]):
        alt=_reach(target,{**avail,d:opts[0][d]-1}).get(target)
        if alt is not None and alt not in opts: opts.append(alt)
    return target, [opts[0]]+sorted(opts[1:],key=lambda o: sum(o.values()))[:2]

def inv():
    return pd.read_sql_query("SELECT * FROM inventory ORDER BY CAST(substr(sku,5) AS INTEGER)", conn)

def add(sku):
    stock = conn.execute("SELECT qty FROM inventory WHERE sku=?", (sku,)).fetchone()
    if not stock or stock[0] <= st.session_state.cart.get(sku,0):
        st.toast("No more stock available")
        return
    st.session_state.cart[sku] = st.session_state.cart.get(sku,0) + 1

def cart_df():
    d = inv().set_index("sku")
    out=[]
    for sku,q in st.session_state.cart.items():
        if sku in d.index:
            r=d.loc[sku]
            out.append({
                "sku":sku,"product":r['product'],"qty":q,
                "sell_price":float(r.sell_price),"buy_price":float(r.buy_price),
                "line_total":q*float(r.sell_price),
                "line_profit":q*(float(r.sell_price)-float(r.buy_price))
            })
    return pd.DataFrame(out)

def finish_sale(payment, discount, cash_in=None, cash_out=None):
    c = cart_df()
    if c.empty: return False, "Cart is empty"
    for _,r in c.iterrows():
        stock=conn.execute("SELECT qty FROM inventory WHERE sku=?",(r.sku,)).fetchone()[0]
        if r.qty > stock: return False, f"Only {stock} left for {r['product']}"
    subtotal=float(c.line_total.sum())
    discount=min(max(float(discount),0),subtotal)
    total=subtotal-discount
    cost=float((c.qty*c.buy_price).sum())
    profit=total-cost
    oid="TGA-"+datetime.now().strftime("%y%m%d")+"-"+uuid.uuid4().hex[:4].upper()
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO sales VALUES(?,?,?,?,?,?,?,?)",(oid,now,payment,subtotal,discount,total,cost,profit))
    for _,r in c.iterrows():
        conn.execute("INSERT INTO sale_items VALUES(?,?,?,?,?,?,?,?)",
            (oid,r.sku,r['product'],int(r.qty),r.sell_price,r.buy_price,r.line_total,r.line_profit))
        conn.execute("UPDATE inventory SET qty=qty-? WHERE sku=?",(int(r.qty),r.sku))
    for sign,counts in ((1,cash_in or {}),(-1,cash_out or {})):
        for dn,n in counts.items():
            if n:
                bump_drawer(dn,sign*n)
                conn.execute("INSERT INTO cash_moves VALUES(?,?,?)",(oid,dn,sign*n))
    conn.commit()
    st.session_state.cart={}
    return True,oid

EDIT_COLS=["sku","product","category","qty","buy_price","sell_price","new"]

def save_inventory(old, edited):
    e=edited.copy()
    for col in ["sku","product","category"]:
        e[col]=e[col].map(lambda v: "" if pd.isna(v) else str(v).strip())
    e=e[(e["sku"]!="") | (e["product"]!="")].reset_index(drop=True)
    if (e["product"]=="").any(): return False, "Every row needs a product name"
    e.loc[e["category"]=="","category"]="Other"
    for col in ["qty","buy_price","sell_price"]:
        e[col]=pd.to_numeric(e[col],errors="coerce")
    if e[["qty","buy_price","sell_price"]].isna().any().any():
        return False, "Fill in qty, buy price and sell price for every row"
    if (e[["qty","buy_price","sell_price"]]<0).any().any():
        return False, "Qty and prices cannot be negative"
    e["new"]=e["new"].map(lambda v: bool(v) if pd.notna(v) else False)
    # blank SKUs on new rows get the next free TGA number
    nums=pd.concat([old["sku"],e["sku"]]).str.extract(r"^TGA-(\d+)$")[0].dropna().astype(int)
    nxt=(int(nums.max()) if len(nums) else 0)+1
    for i in e.index[e["sku"]==""]:
        e.at[i,"sku"]=f"TGA-{nxt:03d}"; nxt+=1
    if e["sku"].duplicated().any():
        return False, "Duplicate SKU: "+", ".join(sorted(e["sku"][e["sku"].duplicated()].unique()))
    existing=set(old["sku"])
    removed=existing-set(e["sku"])
    added=0
    for _,r in e.iterrows():
        vals=(r['product'],r.category,int(r.qty),float(r.buy_price),float(r.sell_price),int(r.new))
        if r.sku in existing:
            conn.execute("""UPDATE inventory SET product=?,category=?,qty=?,buy_price=?,
                            sell_price=?,new=? WHERE sku=?""",vals+(r.sku,))
        else:
            conn.execute("""INSERT INTO inventory
                (product,category,qty,buy_price,sell_price,new,sku,image)
                VALUES (?,?,?,?,?,?,?,?)""",vals+(r.sku,f"images/{r.sku}.jpg"))
            added+=1
    for sku in removed:
        conn.execute("DELETE FROM inventory WHERE sku=?",(sku,))
        st.session_state.cart.pop(sku,None)
    conn.commit()
    return True, f"Saved • {added} added • {len(removed)} removed • {len(e)} products in stock list"

def save_photo(sku, file):
    """Store an uploaded photo as images/<SKU>.jpg and point the product at it."""
    im=ImageOps.exif_transpose(Image.open(file))
    im.thumbnail((1400,1400))
    IMG_DIR.mkdir(exist_ok=True)
    rel=f"images/{re.sub(r'[^A-Za-z0-9_-]','_',sku)}.jpg"
    im.convert("RGB").save(APP_DIR/rel,"JPEG",quality=88)
    conn.execute("UPDATE inventory SET image=? WHERE sku=?",(rel,sku))
    conn.commit()

def backup_db():
    conn.commit()
    d=APP_DIR/"backups"; d.mkdir(exist_ok=True)
    dest=d/f"golden_affair_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DB_PATH,dest)
    return dest.name

def cancel_orders(order_ids):
    """Delete these sales and put the sold quantities back into stock."""
    for oid in order_ids:
        for sku,q in conn.execute("SELECT sku,qty FROM sale_items WHERE order_id=?",(oid,)).fetchall():
            conn.execute("UPDATE inventory SET qty=qty+? WHERE sku=?",(q,sku))
        for dn,n in conn.execute("SELECT denom,delta FROM cash_moves WHERE order_id=?",(oid,)).fetchall():
            bump_drawer(dn,-n)
        conn.execute("DELETE FROM cash_moves WHERE order_id=?",(oid,))
        conn.execute("DELETE FROM sale_items WHERE order_id=?",(oid,))
        conn.execute("DELETE FROM sales WHERE order_id=?",(oid,))
    conn.commit()

def reset_everything():
    """Fresh start: no sales, stock list back to the original sheet."""
    for dn,n in conn.execute("SELECT denom,delta FROM cash_moves").fetchall():
        bump_drawer(dn,-n)
    conn.execute("DELETE FROM cash_moves")
    conn.execute("DELETE FROM sale_items")
    conn.execute("DELETE FROM sales")
    conn.execute("DELETE FROM inventory")
    conn.commit()
    seed_if_empty()

def order_card(s, lines, cash=None):
    when=datetime.strptime(s.created_at,"%Y-%m-%d %H:%M:%S").strftime("%d %b %Y, %I:%M %p")
    rows=""
    for _,r in lines.iterrows():
        cat="" if pd.isna(r.category) else f" • {html.escape(str(r.category))}"
        rows+=(f'<div class="oitem"><div class="othumb">{img_tag(r.image,140)}</div>'
               f'<div class="oname">{html.escape(str(r["product"]))}<small>{html.escape(str(r.sku))}{cat}</small></div>'
               f'<div class="oqty">{int(r.qty)} × {money(r.sell_price)}</div>'
               f'<div class="oline">{money(r.line_total)}</div></div>')
    disc=f'<span>Discount −{money(s.discount)}</span>' if s.discount else ''
    if cash: disc+=f'<span>Received {money(cash[0])}</span><span>Change {money(cash[1])}</span>'
    return (f'<div class="order"><div class="ohead"><div><span class="oid">{html.escape(s.order_id)}</span>'
            f'<span class="otime">{when}</span></div>'
            f'<span class="pay pay-{html.escape(str(s.payment_method).lower())}">{html.escape(str(s.payment_method))}</span></div>'
            f'{rows}<div class="ofoot"><span>Subtotal {money(s.subtotal)}</span>{disc}'
            f'<span>Cost {money(s.cost)}</span><span class="profit">Profit {money(s.profit)}</span>'
            f'<span>Total <b>{money(s.total)}</b></span></div></div>')

RUPEE=dict(format="₹%.0f")

# Header
now=datetime.now()
today=now.strftime("%Y-%m-%d")
st.markdown('<div class="topbar"><div><div class="brand">The Golden Affair</div>'
            '<div class="sub">Exhibition • Billing, Stock &amp; Profit</div></div>'
            f'<div class="today"><b>{now.strftime("%A, %d %B %Y")}</b>Exhibition counter</div></div>',
            unsafe_allow_html=True)

sales_df=pd.read_sql_query("SELECT * FROM sales ORDER BY created_at DESC",conn)
items_df=pd.read_sql_query("""SELECT si.rowid AS line_no, si.*, s.created_at, s.payment_method, i.image, i.category
                              FROM sale_items si JOIN sales s ON s.order_id=si.order_id
                              LEFT JOIN inventory i ON i.sku=si.sku ORDER BY si.rowid DESC""",conn)
sales_df["day"]=sales_df.created_at.str[:10]
items_df["day"]=items_df.created_at.str[:10]
items_df["line_cost"]=items_df.qty*items_df.buy_price

cash_df=pd.read_sql_query("SELECT * FROM cash_moves",conn)
cash_df["amount"]=cash_df.denom*cash_df.delta
cash_info={k:(int(g.amount[g.delta>0].sum()),int(-g.amount[g.delta<0].sum())) for k,g in cash_df.groupby("order_id")}

# sidebar: page menu, then one period selector that drives the figures on every page
with st.sidebar:
    st.markdown('<div class="sbrand">The Golden Affair</div><div class="sub">Exhibition counter</div>',unsafe_allow_html=True)
    st.markdown('<div class="shead" style="margin-top:18px">Menu</div>',unsafe_allow_html=True)
    page=st.radio("Menu",PAGES,key="page",label_visibility="collapsed")
    st.divider()
    period=st.radio("Show figures for",["Today","All days","Choose dates"],key="period")
    if period=="Today":
        d_from=d_to=now.date(); period_label="today"
    elif period=="All days":
        d_from=d_to=None; period_label="all days"
    else:
        picked=st.date_input("Exhibition dates (one day, or start and end)",value=(now.date(),now.date()),
                             max_value=now.date(),format="DD/MM/YYYY",key="period_dates")
        picked=list(picked) if isinstance(picked,(list,tuple)) else [picked]
        d_from,d_to=picked[0],picked[-1]
        period_label=(d_from.strftime("%d %b %Y") if d_from==d_to
                      else f"{d_from.strftime('%d %b')} – {d_to.strftime('%d %b %Y')}")
    st.divider()
    st.markdown(f'<div class="shead">Cash in drawer</div><div class="price">{money(cash_value(drawer()))}</div>',unsafe_allow_html=True)
if d_from is None:
    S=sales_df
else:
    S=sales_df[(sales_df.day>=d_from.isoformat())&(sales_df.day<=d_to.isoformat())]
IT=items_df[items_df.order_id.isin(S.order_id)]

ts=S
a,b,c,d,e=st.columns(5)
a.metric("Net Sales",money(ts.total.sum()))
b.metric("Orders",len(ts))
c.metric("Items Sold",int(IT.qty.sum()))
d.metric("Cost of Goods",money(ts.cost.sum()))
e.metric("Profit",money(ts.profit.sum()),pct(ts.profit.sum(),ts.total.sum())+" margin" if len(ts) else None,delta_color="off")

st.markdown(f'<div class="section" style="margin-top:20px">{page.split("  ")[1]}</div>',unsafe_allow_html=True)

# ───────────────────────── Billing
if page==PAGES[0]:
    products, bill = st.columns([2.15,1], gap="large")

    with products:
        x,y,z=st.columns([2,1,1])
        with x:
            search=st.text_input("Search",placeholder="Search product or SKU…",label_visibility="collapsed")
        data=inv()
        cats=["All"]+sorted(data.category.unique().tolist())
        with y:
            selected=st.selectbox("Category",cats,label_visibility="collapsed")
        with z:
            if st.button("↻ Refresh",use_container_width=True):
                st.rerun()

        if selected!="All": data=data[data.category==selected]
        if search:
            q=search.lower().strip()
            data=data[data['product'].str.lower().str.contains(q,na=False,regex=False) | data.sku.str.lower().str.contains(q,na=False,regex=False)]

        st.caption(f"{len(data)} products")
        grid=st.columns(4)
        for i,(_,r) in enumerate(data.iterrows()):
            with grid[i%4]:
                with st.container(key="pc_"+r.sku):
                    badge='<span class="pnew">NEW</span>' if int(r.new) else ''
                    cls="low" if r.qty<=LOW_STOCK else ""
                    stock=f"{int(r.qty)} in stock" if r.qty>0 else "Out of stock"
                    st.markdown(
                        f'<div class="pimg">{img_tag(r.image,420,"ADD IMAGE")}{badge}</div>'
                        f'<div class="pname">{html.escape(str(r["product"]))}</div>'
                        f'<div class="pmeta">{html.escape(r.sku)} • {html.escape(str(r.category))}</div>'
                        f'<div class="prow"><span class="price">{money(r.sell_price) if r.sell_price>0 else "No price"}</span>'
                        f'<span class="stock {cls}">{stock}</span></div>',unsafe_allow_html=True)
                    if r.sell_price<=0:
                        st.button("SET PRICE FIRST",key="noprice_"+r.sku,disabled=True,use_container_width=True,
                                  help="Add a selling price in Inventory → Edit stock & prices")
                    elif r.qty>0:
                        if st.button("＋ ADD",key="add_"+r.sku,use_container_width=True):
                            add(r.sku); st.rerun()
                    else:
                        st.button("SOLD OUT",key="out_"+r.sku,disabled=True,use_container_width=True)

    with bill:
        with st.container(key="billpanel"):
            st.markdown('<div class="section" style="margin-top:0">Current Sale</div>',unsafe_allow_html=True)
            if st.session_state.get("sale_msg"):
                st.success(st.session_state.pop("sale_msg"))
            c=cart_df()
            if c.empty:
                st.info("Tap **＋ ADD** on products to start billing.")
            else:
                for _,r in c.iterrows():
                    p,m,q,pl,t=st.columns([3,1,.7,1,1.6],vertical_alignment="center")
                    p.markdown(f'<div class="cname">{html.escape(str(r["product"]))}</div>'
                               f'<div class="cmeta">{money(r.sell_price)} each</div>',unsafe_allow_html=True)
                    if m.button("−",key="minus_"+r.sku,use_container_width=True):
                        if st.session_state.cart[r.sku]<=1: del st.session_state.cart[r.sku]
                        else: st.session_state.cart[r.sku]-=1
                        st.rerun()
                    q.markdown(f'<div class="cqty" style="padding-top:0">{int(r.qty)}</div>',unsafe_allow_html=True)
                    if pl.button("+",key="plus_"+r.sku,use_container_width=True):
                        add(r.sku); st.rerun()
                    t.markdown(f'<div class="cline" style="padding-top:0">{money(r.line_total)}</div>',unsafe_allow_html=True)
                st.divider()
                subtotal=float(c.line_total.sum())
                discount=st.number_input("Discount ₹",0.0,subtotal,0.0,10.0)
                total=subtotal-discount
                st.markdown(
                    f'<div class="totrow"><span>Subtotal ({int(c.qty.sum())} items)</span><span>{money(subtotal)}</span></div>'
                    f'<div class="totrow"><span>Discount</span><span>−{money(discount)}</span></div>'
                    f'<div class="totrow grand"><span>Total</span><span>{money(total)}</span></div>',
                    unsafe_allow_html=True)
                payment=st.radio("Payment",PAYMENTS,horizontal=True)
                cash_in=cash_out=None; block=None; note=""
                tv=st.session_state.get("tender_v",0)
                if payment=="Cash":
                    due=int(round(total))
                    st.markdown('<div class="shead" style="margin-top:10px">Cash the customer gave — number of each note / coin</div>',unsafe_allow_html=True)
                    given={}
                    cols=st.columns(3)
                    for n,dn in enumerate(DENOMS):
                        given[dn]=int(cols[n%3].number_input(f"₹{dn}",0,None,0,1,key=f"tender_{dn}_{tv}"))
                    received=cash_value(given)
                    if received==0:
                        st.caption("Enter what the customer hands over to see the change to give back. "
                                   "If you leave this empty the sale is still saved, but the cash drawer is not updated.")
                    elif received<due:
                        st.markdown(f'<div class="changebox short"><div class="lbl">Received {money(received)} • still to collect</div>'
                                    f'<div class="amt">{money(due-received)}</div></div>',unsafe_allow_html=True)
                        block=f"Cash received is {money(due-received)} less than the total"
                    else:
                        change=received-due
                        cash_in=given; cash_out={}
                        st.markdown(f'<div class="changebox"><div class="lbl">Received {money(received)} • change to give back</div>'
                                    f'<div class="amt">{money(change)}</div></div>',unsafe_allow_html=True)
                        if change:
                            target,opts=change_options(change,drawer())
                            if target<change:
                                st.warning(f"Your drawer cannot make {money(change)} exactly. The closest it can give is "
                                           f"{money(target)}, which is {money(change-target)} short.")
                            if target:
                                labels={describe(o):o for o in opts}
                                pick=st.radio("Give the change as" if len(opts)>1 else "Give the change as (only way from your drawer)",
                                              list(labels),key=f"change_pick_{tv}")
                                cash_out=labels[pick]
                                note=f" • change {money(target)}: {pick}"
                            else:
                                st.caption("Nothing in the drawer can be given as change. Set your change in the Cash Drawer page.")
                if st.button("✓ COMPLETE SALE",type="primary",use_container_width=True):
                    if block: ok,msg=False,block
                    else: ok,msg=finish_sale(payment,discount,cash_in,cash_out)
                    if ok:
                        st.session_state.sale_msg=f"Sale complete • {msg} • {money(total)} by {payment}{note}"
                        st.session_state.tender_v=tv+1
                        st.rerun()
                    else: st.error(msg)
                if st.button("Clear cart",use_container_width=True):
                    st.session_state.cart={}; st.session_state.tender_v=tv+1; st.rerun()

# ───────────────────────── Cash Drawer
if page==PAGES[1]:
    dr=drawer()
    if st.session_state.get("drawer_msg"):
        st.success(st.session_state.pop("drawer_msg"))
    k1,k2,k3,k4=st.columns(4)
    k1.metric("Cash in Drawer",money(cash_value(dr)))
    k2.metric("Notes & Coins",sum(dr.values()))
    k3.metric(f"Cash Received ({period_label})",money(sum(v[0] for k,v in cash_info.items() if k in set(S.order_id))))
    k4.metric(f"Change Given ({period_label})",money(sum(v[1] for k,v in cash_info.items() if k in set(S.order_id))))

    left,right=st.columns([1.3,1],gap="large")
    with left:
        st.markdown('<div class="section">Count your change</div>',unsafe_allow_html=True)
        st.caption("Enter how many of each note and coin you have right now, then save. Cash sales update these "
                   "counts automatically: what the customer gives is added and the change you give is taken out.")
        with st.form("drawer_form",border=False):
            cols=st.columns(3)
            counted={}
            for n,dn in enumerate(DENOMS):
                # the current count is part of the key so the box refreshes after a sale changes it
                counted[dn]=int(cols[n%3].number_input(f"₹{dn}",0,None,dr[dn],1,key=f"dr_{dn}_{dr[dn]}"))
            if st.form_submit_button("💾 Save drawer",type="primary"):
                set_drawer(counted)
                st.session_state.drawer_msg=f"Drawer saved • {money(cash_value(counted))} in {sum(counted.values())} notes and coins"
                st.rerun()
    with right:
        st.markdown('<div class="section">In the drawer now</div>',unsafe_allow_html=True)
        dd=pd.DataFrame({"denom":DENOMS,"count":[dr[k] for k in DENOMS]})
        dd["value"]=dd.denom*dd["count"]
        st.dataframe(dd,use_container_width=True,hide_index=True,column_config={
            "denom":st.column_config.NumberColumn("Note / coin",**RUPEE),
            "count":st.column_config.NumberColumn("How many",format="%d"),
            "value":st.column_config.NumberColumn("Value",**RUPEE)})

    st.markdown(f'<div class="section">Cash sales for {period_label}</div>',unsafe_allow_html=True)
    cm=cash_df[cash_df.order_id.isin(S.order_id)]
    if cm.empty:
        st.info("No cash sales with notes entered in this period.")
    else:
        rows=[]
        for o in S[S.order_id.isin(cm.order_id)].itertuples():
            g=cm[cm.order_id==o.order_id]
            rows.append({"time":pd.to_datetime(o.created_at).strftime("%d %b, %I:%M %p"),"order_id":o.order_id,"total":o.total,
                         "received":cash_info[o.order_id][0],"change":cash_info[o.order_id][1],
                         "notes_in":describe({r.denom:r.delta for r in g[g.delta>0].itertuples()}),
                         "notes_out":describe({r.denom:-r.delta for r in g[g.delta<0].itertuples()})})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True,column_config={
            "time":"Sold at","order_id":"Order no.","total":st.column_config.NumberColumn("Bill",**RUPEE),
            "received":st.column_config.NumberColumn("Received",**RUPEE),
            "change":st.column_config.NumberColumn("Change given",**RUPEE),
            "notes_in":"Customer gave","notes_out":"You gave back"})

# ───────────────────────── Sales
if page==PAGES[2]:
    f2,f3,f4=st.columns([1,2.4,1.5])
    pay=f2.selectbox("Payment",["All"]+PAYMENTS,key="sales_pay")
    find=f3.text_input("Find",placeholder="Search product, SKU or order no…",key="sales_find")
    view=f4.radio("View",["Orders","Items table"],horizontal=True,key="sales_view")

    s=S
    if pay!="All": s=s[s.payment_method==pay]
    lines=items_df[items_df.order_id.isin(s.order_id)]
    hits=lines
    if find:
        q=find.lower().strip()
        hits=lines[lines['product'].str.lower().str.contains(q,na=False,regex=False)
                   | lines.sku.str.lower().str.contains(q,na=False,regex=False)
                   | lines.order_id.str.lower().str.contains(q,na=False,regex=False)]
        s=s[s.order_id.isin(hits.order_id)]
        lines=lines[lines.order_id.isin(s.order_id)]

    if s.empty:
        st.info(f"No sales for {period_label} match this view. Change the period in the side menu to see other dates.")
    elif view=="Orders":
        MAX_ORDERS=60
        st.caption(f"{len(s)} orders for {period_label} • {int(lines.qty.sum())} items • {money(s.total.sum())} • "
                   f"showing {min(len(s),MAX_ORDERS)}, newest first")
        st.markdown("".join(order_card(o,lines[lines.order_id==o.order_id].sort_values("line_no"),cash_info.get(o.order_id))
                            for o in s.head(MAX_ORDERS).itertuples()),unsafe_allow_html=True)
    else:
        t=hits.copy()
        t["photo"]=t.image.map(lambda v: thumb(v,140))
        t["time"]=pd.to_datetime(t.created_at).dt.strftime("%d %b, %I:%M %p")
        st.dataframe(
            t[["photo","product","sku","category","qty","sell_price","line_total","line_cost","line_profit","payment_method","time","order_id"]],
            use_container_width=True,hide_index=True,row_height=56,
            column_config={
                "photo":st.column_config.ImageColumn("Photo",width="small"),
                "product":"Product","sku":"SKU","category":"Category",
                "qty":st.column_config.NumberColumn("Qty",format="%d"),
                "sell_price":st.column_config.NumberColumn("Price",**RUPEE),
                "line_total":st.column_config.NumberColumn("Amount",**RUPEE),
                "line_cost":st.column_config.NumberColumn("Cost",**RUPEE),
                "line_profit":st.column_config.NumberColumn("Profit",**RUPEE),
                "payment_method":"Payment","time":"Sold at","order_id":"Order no.",
            })

# ───────────────────────── Inventory
if page==PAGES[3]:
    i=inv()
    i["stock_cost"]=i.qty*i.buy_price
    i["stock_retail"]=i.qty*i.sell_price
    i["margin"]=i.sell_price-i.buy_price
    i["margin_pct"]=(i.margin/i.sell_price.where(i.sell_price>0)*100).fillna(0)
    i["photo"]=i.image.map(lambda v: thumb(v,140))
    low=i[i.qty<=0]
    k1,k2,k3,k4,k5,k6=st.columns(6)
    k1.metric("Products",len(i))
    k2.metric("Units in Stock",int(i.qty.sum()))
    k3.metric("Stock at Cost",money(i.stock_cost.sum()))
    k4.metric("Stock at Selling Price",money(i.stock_retail.sum()))
    k5.metric("Potential Profit",money(i.stock_retail.sum()-i.stock_cost.sum()))
    k6.metric("Sold Out",len(low))

    STOCK_COLS={
        "photo":st.column_config.ImageColumn("Photo",width="small"),
        "sku":"SKU","product":"Product","category":"Category",
        "qty":st.column_config.NumberColumn("Qty",format="%d"),
        "buy_price":st.column_config.NumberColumn("Buy price",**RUPEE),
        "sell_price":st.column_config.NumberColumn("Sell price",**RUPEE),
        "margin":st.column_config.NumberColumn("Profit / unit",**RUPEE),
        "margin_pct":st.column_config.NumberColumn("Margin",format="%.0f%%"),
        "stock_cost":st.column_config.NumberColumn("Stock at cost",**RUPEE),
        "stock_retail":st.column_config.NumberColumn("Stock at sell",**RUPEE),
    }
    SHOW=["photo","sku","product","category","qty","buy_price","sell_price","margin","margin_pct","stock_cost","stock_retail"]

    i1,i2,i4,i3=st.tabs(["Stock list","✏️ Edit stock & prices","📷 Photos",f"Sold out ({len(low)})"])
    with i1:
        cat=st.selectbox("Category",["All"]+sorted(i.category.unique().tolist()),key="inv_cat")
        view_i=i if cat=="All" else i[i.category==cat]
        st.dataframe(view_i[SHOW],use_container_width=True,hide_index=True,column_config=STOCK_COLS,height=560)
        by=i.groupby("category",as_index=False).agg(products=("sku","count"),units=("qty","sum"),
                stock_cost=("stock_cost","sum"),stock_retail=("stock_retail","sum"))
        by["potential"]=by.stock_retail-by.stock_cost
        st.markdown('<div class="section">Stock value by category</div>',unsafe_allow_html=True)
        st.dataframe(by,use_container_width=True,hide_index=True,column_config={
            "category":"Category","products":"Products","units":"Units",
            "stock_cost":st.column_config.NumberColumn("Stock at cost",**RUPEE),
            "stock_retail":st.column_config.NumberColumn("Stock at sell",**RUPEE),
            "potential":st.column_config.NumberColumn("Potential profit",**RUPEE)})
    with i2:
        st.caption("Edit any cell to change stock or pricing. Use the ＋ row at the bottom to add a product "
                   "(leave SKU blank to auto-assign). Nothing is saved until you press Save changes.")
        if "editor_v" not in st.session_state: st.session_state.editor_v=0
        if st.session_state.get("stock_msg"):
            st.success(st.session_state.pop("stock_msg"))
        cur=inv()[EDIT_COLS]
        cur["new"]=cur["new"].astype(bool)
        edited=st.data_editor(cur,num_rows="dynamic",use_container_width=True,hide_index=True,height=560,
            key=f"stock_editor_{st.session_state.editor_v}",
            column_config={
                "sku":st.column_config.TextColumn("SKU"),
                "product":st.column_config.TextColumn("Product"),
                "category":st.column_config.TextColumn("Category"),
                "qty":st.column_config.NumberColumn("Qty",min_value=0,step=1,format="%d"),
                "buy_price":st.column_config.NumberColumn("Buy ₹",min_value=0.0,format="%.0f"),
                "sell_price":st.column_config.NumberColumn("Sell ₹",min_value=0.0,format="%.0f"),
                "new":st.column_config.CheckboxColumn("New",default=False),
            })
        s1,s2,_=st.columns([1,1,2])
        if s1.button("💾 Save changes",type="primary",use_container_width=True):
            ok,msg=save_inventory(cur,edited)
            if ok:
                st.session_state.stock_msg=msg
                st.session_state.editor_v+=1
                st.rerun()
            else: st.error(msg)
        if s2.button("Discard edits",use_container_width=True):
            st.session_state.editor_v+=1; st.rerun()
    with i4:
        IMG_TYPES=["jpg","jpeg","png","webp"]
        if "photo_v" not in st.session_state: st.session_state.photo_v=0
        pv=st.session_state.photo_v
        if st.session_state.get("photo_msg"):
            st.success(st.session_state.pop("photo_msg"))
        has=i.photo.notna()
        st.caption(f"{int(has.sum())} of {len(i)} products have a photo.")
        u1,u2=st.columns(2,gap="large")
        with u1:
            st.markdown('<div class="section">One product</div>',unsafe_allow_html=True)
            only_missing=st.checkbox("Only list products without a photo",value=True,key="photo_missing")
            opts=i[~has] if only_missing and (~has).any() else i
            names=i.set_index("sku")["product"]
            psku=st.selectbox("Product",opts.sku.tolist(),format_func=lambda k: f"{k} — {names[k]}",key="photo_sku")
            if psku:
                st.markdown(f'<div class="pimg" style="width:150px">{img_tag(i.set_index("sku").image[psku],300,"NO PHOTO YET")}</div>',
                            unsafe_allow_html=True)
                up=st.file_uploader("Choose a photo",type=IMG_TYPES,key=f"photo_one_{pv}")
                if st.toggle("Take a photo with the camera instead",key="photo_cam"):
                    up=st.camera_input("Take photo",key=f"photo_shot_{pv}") or up
                if up is not None and st.button("💾 Save photo",type="primary",key="photo_save"):
                    try:
                        save_photo(psku,up)
                        st.session_state.photo_msg=f"Photo saved for {psku} — {names[psku]}"
                        st.session_state.photo_v+=1
                        st.rerun()
                    except Exception:
                        st.error("That file could not be read as an image. Use a JPG, PNG or WebP photo.")
        with u2:
            st.markdown('<div class="section">Many at once</div>',unsafe_allow_html=True)
            st.caption("Name each file by its SKU, for example TGA-001.jpg, and upload them together.")
            ups=st.file_uploader("Choose photos",type=IMG_TYPES,accept_multiple_files=True,key=f"photo_many_{pv}")
            if ups and st.button(f"💾 Save {len(ups)} photos",type="primary",key="photo_save_many"):
                by_upper={k.upper():k for k in i.sku}
                saved,skipped=0,[]
                for f in ups:
                    k=by_upper.get(Path(f.name).stem.strip().upper())
                    try:
                        if k is None: raise ValueError
                        save_photo(k,f); saved+=1
                    except Exception:
                        skipped.append(f.name)
                st.session_state.photo_msg=f"{saved} photos saved"+(f" • skipped (no matching SKU or unreadable): {', '.join(skipped)}" if skipped else "")
                st.session_state.photo_v+=1
                st.rerun()
    with i3:
        if low.empty: st.success("Nothing has sold out yet.")
        else:
            st.caption("Products with no units left")
            st.dataframe(low[SHOW[:7]],use_container_width=True,hide_index=True,column_config=STOCK_COLS)

# ───────────────────────── Profit & Reports
if page==PAGES[4]:
    st.caption(f"Figures for {period_label}. Change the period in the side menu.")
    s=S
    it=IT

    p1,p2,p3,p4,p5,p6=st.columns(6)
    p1.metric("Gross Sales",money(s.subtotal.sum()))
    p2.metric("Discounts Given",money(s.discount.sum()))
    p3.metric("Net Sales",money(s.total.sum()))
    p4.metric("Cost of Goods",money(s.cost.sum()))
    p5.metric("Net Profit",money(s.profit.sum()))
    p6.metric("Profit Margin",pct(s.profit.sum(),s.total.sum()))

    if s.empty:
        st.info(f"No sales recorded for {period_label}.")
    else:
        def summarise(keys):
            g=it.assign(category=it.category.fillna("Removed product")).groupby(keys,as_index=False).agg(
                units=("qty","sum"),revenue=("line_total","sum"),cost=("line_cost","sum"),profit=("line_profit","sum"))
            g["margin_pct"]=(g.profit/g.revenue.where(g.revenue>0)*100).fillna(0)
            return g.sort_values("revenue",ascending=False)
        REP_COLS={
            "photo":st.column_config.ImageColumn("Photo",width="small"),
            "category":"Category","product":"Product","sku":"SKU","day":"Date","payment_method":"Payment",
            "orders":st.column_config.NumberColumn("Orders",format="%d"),
            "units":st.column_config.NumberColumn("Units sold",format="%d"),
            "revenue":st.column_config.NumberColumn("Sales",**RUPEE),
            "subtotal":st.column_config.NumberColumn("Gross sales",**RUPEE),
            "discount":st.column_config.NumberColumn("Discounts",**RUPEE),
            "total":st.column_config.NumberColumn("Net sales",**RUPEE),
            "cost":st.column_config.NumberColumn("Cost",**RUPEE),
            "profit":st.column_config.NumberColumn("Profit",**RUPEE),
            "margin_pct":st.column_config.NumberColumn("Margin",format="%.0f%%"),
        }
        left,right=st.columns([1.5,1],gap="large")
        with left:
            st.markdown('<div class="section">Profit by category</div>',unsafe_allow_html=True)
            st.dataframe(summarise("category"),use_container_width=True,hide_index=True,column_config=REP_COLS)
        with right:
            st.markdown('<div class="section">Collections by payment</div>',unsafe_allow_html=True)
            bp=s.groupby("payment_method",as_index=False).agg(orders=("order_id","count"),total=("total","sum")).sort_values("total",ascending=False)
            st.dataframe(bp,use_container_width=True,hide_index=True,column_config=REP_COLS)

        st.markdown('<div class="section">Best sellers</div>',unsafe_allow_html=True)
        best=summarise(["sku","product"])
        imgs=items_df.drop_duplicates("sku").set_index("sku").image
        best.insert(0,"photo",best.sku.map(lambda k: thumb(imgs.get(k),140)))
        st.dataframe(best,use_container_width=True,hide_index=True,column_config=REP_COLS,row_height=56)

        st.markdown('<div class="section">Day-wise summary</div>',unsafe_allow_html=True)
        days=s.groupby("day",as_index=False).agg(orders=("order_id","count"),subtotal=("subtotal","sum"),
                discount=("discount","sum"),total=("total","sum"),cost=("cost","sum"),profit=("profit","sum")).sort_values("day",ascending=False)
        days["margin_pct"]=(days.profit/days.total.where(days.total>0)*100).fillna(0)
        st.dataframe(days,use_container_width=True,hide_index=True,column_config=REP_COLS)
        st.caption("Category and product profit is before order-level discounts; the totals at the top are after discounts.")

    st.markdown('<div class="section">Export</div>',unsafe_allow_html=True)
    e1,e2,e3,_=st.columns([1,1,1,1])
    e1.download_button("⬇ Sales CSV",sales_df.drop(columns="day").to_csv(index=False).encode(),"sales.csv","text/csv",use_container_width=True)
    e2.download_button("⬇ Sale items CSV",items_df[["order_id","created_at","payment_method","sku","product","category","qty","sell_price","buy_price","line_total","line_profit"]].to_csv(index=False).encode(),"sale_items.csv","text/csv",use_container_width=True)
    e3.download_button("⬇ Inventory CSV",inv().to_csv(index=False).encode(),"inventory.csv","text/csv",use_container_width=True)

# ───────────────────────── Settings
if page==PAGES[5]:
    if st.session_state.get("reset_msg"):
        st.success(st.session_state.pop("reset_msg"))
    st.caption("Use these to clean up after testing. A backup copy of the data is saved in the backups folder before anything is removed.")
    c0,c1,c2=st.columns(3,gap="large")
    with c0:
        st.markdown('<div class="section">Reset everything</div>',unsafe_allow_html=True)
        st.write(f"A fresh start after testing: deletes **all {len(sales_df)} sales**, so every figure goes back to zero, "
                 "and puts the stock list back to the original sheet (inventory.csv). "
                 "Stock and price edits and products added in the app are lost. Photos are kept. "
                 "Cash from those sales is taken back out of the drawer count.")
        sure0=st.checkbox("Yes, reset everything",key="resetall_sure")
        if st.button("♻️ Reset sales & stock",type="primary",disabled=not sure0,use_container_width=True,key="resetall_go"):
            b=backup_db()
            reset_everything()
            st.session_state.cart={}
            st.session_state.reset_msg=f"Everything reset: no sales, original stock list • backup saved as backups/{b}"
            st.session_state.pop("resetall_sure",None)
            st.rerun()
    with c1:
        st.markdown('<div class="section">Clear sales only</div>',unsafe_allow_html=True)
        scope=st.radio("Which sales",[f"Only {period_label} ({len(S)} orders)",f"All sales ever ({len(sales_df)} orders)"],key="reset_scope")
        target=sales_df if scope.startswith("All") else S
        st.write(f"Removes **{len(target)} orders** worth {money(target.total.sum())} and puts the sold items back into stock. Your stock and price edits are kept, and the cash drawer is put back too.")
        sure=st.checkbox("Yes, remove these sales",key="reset_sure")
        if st.button("🗑 Clear sales & restore stock",disabled=not sure or target.empty,use_container_width=True,key="reset_go"):
            b=backup_db()
            cancel_orders(target.order_id.tolist())
            st.session_state.reset_msg=f"{len(target)} orders removed and their stock restored • backup saved as backups/{b}"
            st.session_state.pop("reset_sure",None)
            st.rerun()
    with c2:
        st.markdown('<div class="section">Cancel one sale</div>',unsafe_allow_html=True)
        if sales_df.empty:
            st.write("No sales recorded.")
        else:
            what=items_df.sort_values("line_no").groupby("order_id")["product"].agg(", ".join)
            info=sales_df.set_index("order_id")
            oid=st.selectbox("Order",sales_df.order_id.tolist(),key="cancel_oid",
                format_func=lambda k: f"{k} • {info.created_at[k][5:16]} • {money(info.total[k])} • {what.get(k,'')}"[:90])
            st.write("Removes this order and puts its items back into stock.")
            sure1=st.checkbox("Yes, cancel this sale",key="cancel_sure")
            if st.button("Cancel this sale",disabled=not sure1,use_container_width=True,key="cancel_go"):
                b=backup_db()
                cancel_orders([oid])
                st.session_state.reset_msg=f"Order {oid} cancelled and its stock restored • backup saved as backups/{b}"
                st.session_state.pop("cancel_sure",None)
                st.rerun()
