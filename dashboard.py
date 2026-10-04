"""Nexus: a Streamlit workspace for sales and inventory intelligence."""
import os
from datetime import datetime
from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Nexus / Commerce intelligence", page_icon="◈", layout="wide")
def setting(name, default=None):
    value = os.getenv(name)
    if value is not None:
        return value
    try:
        return st.secrets.get(name, default)
    except FileNotFoundError:
        return default


API_URL = setting("API_URL", "http://127.0.0.1:8000").strip().rstrip("/")
DATA_BACKEND = setting("DATA_BACKEND", "api").strip().lower()
COLORS = ["#526c39", "#bbd77a", "#252d28", "#dfad65", "#929e8a", "#c9c6b8"]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --paper:#f5f5ef; --ink:#202820; --muted:#73796e; --line:#e0e3d8; --lime:#d6f395; }
.stApp { background:var(--paper); color:var(--ink); }
html,body,[class*="css"],.stApp,p,input,button { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Manrope',sans-serif!important; color:var(--ink)!important; }
header[data-testid="stHeader"] { background:rgba(245,245,239,.92); }
.block-container { padding-top:2.4rem; padding-bottom:2rem; max-width:1550px; }
section[data-testid="stSidebar"] { background:#202a24; border-right:0; }
section[data-testid="stSidebar"] * { color:#e2e8db; }
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding:1.3rem .7rem; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:12px 14px; border-radius:10px; margin-bottom:7px; transition:background .2s; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#334034; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background:#d6f395; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * { color:#202a24!important; }
section[data-testid="stSidebar"] hr { border-color:#3b453e; }
.brand { font-family:Manrope,sans-serif; font-weight:800; font-size:34px; letter-spacing:-2px; }
.brand-mark { display:inline-flex; width:39px; height:39px; align-items:center; justify-content:center; background:#d6f395; color:#202a24!important; border-radius:12px; margin-right:10px; font-size:29px; }
.brand-sub { font-size:10px; letter-spacing:2.6px; color:#a9b5a3!important; margin:10px 0 38px; }
.nav-label { color:#8e9c88!important; font-size:10px; letter-spacing:2px; margin:22px 0 14px; }
.side-note { border:1px solid #495643; border-radius:16px; padding:20px; margin-top:40px; background:linear-gradient(135deg,#34412e,#263128); }
.side-note b { color:#d6f395!important; font-size:17px; }
.side-note p { color:#b2beaa!important; font-size:12px; line-height:1.8; margin:10px 0 0; }
.eyebrow { font-size:10px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#73796e; }
.topline { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--line); padding-bottom:20px; margin-bottom:28px; gap:16px; }
.topline span { font-size:12px; color:#73796e; }
.topline b { color:#202820; }
.hero { display:flex; align-items:center; justify-content:space-between; gap:24px; margin:0 0 26px; }
.hero h1 { font-size:clamp(30px,3.3vw,49px); font-weight:800; letter-spacing:-2.3px; line-height:1.12; padding:10px 0; margin:0; }
.hero p { color:#73796e; font-size:14px; margin:3px 0; }
.hero-stamp { border:1px solid #cbd4bf; border-radius:50%; width:86px; height:86px; flex-shrink:0; display:flex; align-items:center; justify-content:center; color:#526c39; font-size:45px; background:radial-gradient(circle,#e8efdb,transparent); }
.stat { background:#fff; border:1px solid var(--line); border-radius:17px; padding:23px; min-height:160px; position:relative; overflow:hidden; margin-bottom:10px; }
.stat.featured { background:#d6f395; border-color:#c8e28d; }
.stat .number { font-family:Manrope,sans-serif; font-size:clamp(26px,2.7vw,39px); line-height:1.3; font-weight:800; letter-spacing:-1.7px; margin:13px 0 9px; }
.stat .note { color:#69735e; font-size:11px; }
.stat .glyph { position:absolute; right:20px; top:19px; color:#5d704e; font-size:19px; }
.section-head { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:8px; }
.section-head h3 { font-size:18px; font-weight:800; letter-spacing:-.5px; padding:0; margin:0; }
.section-head span { color:#828878; font-size:11px; }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-color:var(--line)!important; border-radius:18px!important; background:#fff; }
[data-testid="stWidgetLabel"] p { color:#58614f; font-size:12px; }
[data-baseweb="select"] > div, [data-baseweb="input"] { background:#fff!important; color:#202820!important; border-color:#dce1d4!important; border-radius:9px!important; }
input { color:#202820!important; }
.stButton button,.stDownloadButton button { border:1px solid #ccd5bf; border-radius:9px; background:#edf2e4; color:#293524; font-size:12px; font-weight:600; }
.stButton button:hover,.stDownloadButton button:hover { border-color:#526c39; color:#293524; background:#d6f395; }
section[data-testid="stSidebar"] .stButton button { background:#35432f; border-color:#4b5d41; }
.empty { padding:44px 24px; text-align:center; border:1px dashed #cdd6c0; background:#f0f4e9; border-radius:15px; margin:10px 0; }
.empty b { display:block; font-size:18px; margin-bottom:8px; }
.empty p { color:#73796e; font-size:13px; margin:0; }
.priority { display:flex; align-items:center; gap:12px; padding:15px 0; border-bottom:1px solid #edf0e7; }
.priority-icon { width:36px; height:36px; background:#f2eee3; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#a8793a; }
.priority-name { flex:1; min-width:0; font-size:13px; font-weight:600; overflow-wrap:anywhere; }
.priority-name small { display:block; color:#868c7f; font-size:11px; font-weight:400; margin-top:4px; }
.pill { font-size:10px; padding:5px 9px; border-radius:20px; white-space:nowrap; background:#fff1d8; color:#97611e; }
.pill.red { background:#fce6df; color:#b4533b; }
.insight { background:#253126; border-radius:14px; padding:20px 23px; color:#eaf0e2; margin:14px 0; font-size:13px; line-height:1.8; }
.insight b { color:#d6f395; }
.footer { border-top:1px solid var(--line); margin-top:30px; padding-top:18px; display:flex; justify-content:space-between; color:#8c9384; font-size:10px; letter-spacing:1px; }
@media(max-width:768px) { .block-container { padding:1.4rem 1rem; } .hero-stamp { display:none; } .hero h1 { letter-spacing:-1px; } .stat { min-height:135px; padding:18px; } .topline { flex-wrap:wrap; } }
@media(prefers-reduced-motion:reduce) { * { transition:none!important; } }
</style>
""", unsafe_allow_html=True)


def html(value):
    st.markdown(value, unsafe_allow_html=True)


def empty(title, message):
    html(f'<div class="empty"><b>{escape(title)}</b><p>{escape(message)}</p></div>')


def fetch_supabase(endpoint):
    """Reuse read-only API analytics without starting an HTTP server."""
    from urllib.parse import parse_qs, urlsplit
    import httpx
    from fastapi import HTTPException
    from postgrest.exceptions import APIError

    for name in ("SUPABASE_URL", "SUPABASE_SECRET_KEY"):
        value = setting(name)
        if not value:
            st.error(f"Add {name} to your Streamlit app Secrets to connect your database.")
            return None
        os.environ[name] = value
    try:
        import main as analytics
        url = urlsplit(endpoint)
        params = parse_qs(url.query)
        if url.path == "/products":
            return analytics.get_products()
        if url.path == "/analytics/stock-alerts":
            return analytics.get_stock_alerts()
        if url.path == "/analytics/top-products":
            return analytics.get_top_products(limit=None)
        if url.path == "/analytics/revenue":
            return analytics.get_revenue_analytics(period=params.get("period", ["daily"])[0])
        if url.path == "/analytics/forecast":
            return analytics.get_demand_forecast(window_days=int(params.get("window_days", ["7"])[0]))
        st.error("This data view is not available in standalone mode.")
    except httpx.RequestError:
        st.error("Cannot reach Supabase. Check the Project URL and confirm the project is active.")
    except APIError:
        st.error("Supabase rejected the request. Check your key, tables, and database permissions.")
    except (HTTPException, ValueError):
        st.error("Unable to load analytics. Check the database configuration and table data.")
    return None


def fetch_api(endpoint):
    if DATA_BACKEND == "supabase":
        return fetch_supabase(endpoint)
    if DATA_BACKEND != "api":
        st.error("DATA_BACKEND must be 'api' or 'supabase'.")
        return None
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=(3, 20))
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        st.error("Your data is taking longer than expected. Try refreshing in a moment.")
    except requests.ConnectionError:
        st.error("Unable to reach the API. Locally, run: python -m uvicorn main:app --reload. On Streamlit Cloud, set API_URL in app Secrets to your deployed FastAPI HTTPS address; localhost cannot reach your PC.")
    except requests.HTTPError:
        st.error(f"Data is unavailable (HTTP {response.status_code}). Check the API and Supabase connection, then refresh.")
    except (requests.RequestException, ValueError):
        st.error("The API returned an unreadable response. Please try again.")
    return None


def records(endpoint, key=None):
    data = fetch_api(endpoint)
    if data is None:
        return None
    rows = data.get(key, []) if key and isinstance(data, dict) else data
    if not isinstance(rows, list):
        st.error("The API returned an unexpected data format.")
        return None
    return pd.DataFrame(rows)


def metric(label, value, note, featured=False, glyph="↗"):
    html(f'<div class="stat {"featured" if featured else ""}"><div class="eyebrow">{escape(label)}</div><span class="glyph">{glyph}</span><div class="number">{escape(str(value))}</div><div class="note">{escape(note)}</div></div>')


def heading(title, subtitle=""):
    html(f'<div class="section-head"><h3>{escape(title)}</h3><span>{escape(subtitle)}</span></div>')


def chart(fig, height=330):
    fig.update_layout(template="plotly_white", height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans, sans-serif", color="#747c6c", size=11), margin=dict(l=10,r=10,t=25,b=15), colorway=COLORS, legend=dict(orientation="h", y=1.15, x=0, title=None), hoverlabel=dict(bgcolor="#253126",font_color="#f4f8ed"))
    fig.update_xaxes(showgrid=False, zeroline=False, title=None)
    fig.update_yaxes(gridcolor="#eef0e8", zeroline=False, title=None)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False}, theme=None)


def table(df, name):
    left, right = st.columns([4,1])
    with left:
        heading("The details", f"{len(df):,} records")
    with right:
        st.download_button("↓ Export CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"nexus_{name}.csv", mime="text/csv", use_container_width=True)
    display = df.rename(columns=lambda x: x.replace("_", " ").title())
    st.dataframe(display, use_container_width=True, hide_index=True)


def revenue_chart(df):
    fig = go.Figure(go.Scatter(x=df["date"],y=df["total_revenue"], mode="lines+markers", line=dict(color="#526c39",width=3), marker=dict(size=5,color="#526c39"),fill="tozeroy",fillcolor="rgba(187,215,122,.22)",hovertemplate="%{x}<br>Revenue: $%{y:,.2f}<extra></extra>"))
    fig.update_yaxes(tickprefix="$")
    chart(fig)


with st.sidebar:
    html('<div class="brand"><span class="brand-mark">◈</span>nexus<span style="color:#d6f395">.</span></div><div class="brand-sub">COMMERCE INTELLIGENCE</div>')
    html('<div class="nav-label">WORKSPACE / 01</div>')
    page = st.radio("Workspace", ["Overview", "Product Analytics", "Revenue Trends", "Demand Forecasting"], label_visibility="collapsed")
    st.divider()
    if st.button("↻  Refresh workspace", use_container_width=True):
        st.rerun()
    st.caption("Data is requested on each page refresh.")
    html('<div class="side-note"><b>A clearer view.<br>A smarter next move.</b><p>Your sales, stock, and demand. Connected in one thoughtful workspace.</p></div>')
    html('<div class="nav-label">NEXUS / RETAIL OPERATIONS</div>')

html(f'<div class="topline"><span><b>Workspace</b> &nbsp; / &nbsp; {escape(page)}</span><span>{datetime.now():%A, %d %B %Y} &nbsp; · &nbsp; USD</span></div>')
TITLES = {"Overview":("YOUR BUSINESS, IN FOCUS", "The bigger picture.", "A considered view of how your business is moving."), "Product Analytics":("KNOW WHAT MOVES", "Every product. A story.", "Find the standouts and understand what drives your sales."), "Revenue Trends":("FOLLOW THE MOMENTUM", "Growth, in perspective.", "See your revenue rhythm, one period at a time."), "Demand Forecasting":("STAY ONE STEP AHEAD", "Plan with perspective.", "Turn recent demand into more thoughtful inventory decisions.")}
eyebrow, title, subtitle = TITLES[page]
html(f'<div class="hero"><div><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div><div class="hero-stamp">✳</div></div>')

if page == "Overview":
    products = records("/products")
    revenue = records("/analytics/revenue?period=daily", "revenue_data")
    alerts = records("/analytics/stock-alerts", "alerts")
    cols = st.columns(4)
    total_revenue = revenue["total_revenue"].sum() if revenue is not None and not revenue.empty else 0
    for col, args in zip(cols, [
        ("Total revenue", f"${total_revenue:,.0f}" if revenue is not None else "—", "Across all recorded sales", True),
        ("Products", f"{len(products):,}" if products is not None else "—", "In your product catalog", False),
        ("Units on hand", f"{products['stock'].sum():,.0f}" if products is not None and not products.empty else ("0" if products is not None else "—"), "Available across the catalog", False),
        ("Stock alerts", f"{len(alerts):,}" if alerts is not None else "—", "Products at or below threshold", False),
    ]):
        with col:
            metric(*args)
    left, right = st.columns([1.9,1])
    with left:
        with st.container(border=True):
            heading("Revenue pulse", "Last 30 recorded daily periods")
            if revenue is not None and not revenue.empty:
                revenue_chart(revenue.tail(30))
            elif revenue is not None:
                empty("Your next chapter starts here", "Revenue will appear when your first order is recorded.")
            else:
                empty("Revenue unavailable", "Refresh after restoring your API connection.")
    with right:
        with st.container(border=True):
            heading("Inventory balance", "Product availability")
            if products is not None and not products.empty:
                stock = products["stock"]
                thresholds = products["reorder_threshold"].fillna(0)
                values = [int((stock > thresholds).sum()),int(((stock > 0)&(stock <= thresholds)).sum()),int((stock == 0).sum())]
                fig = go.Figure(go.Pie(labels=["Healthy","Low stock","Out of stock"],values=values,hole=.78,sort=False,marker=dict(colors=["#bbd77a","#dfad65","#b96550"],line=dict(color="#fff",width=5)),textinfo="none",hovertemplate="%{label}: %{value}<extra></extra>"))
                fig.add_annotation(text=f"<b>{values[0]/len(products):.0%}</b><br>healthy",x=.5,y=.5,showarrow=False,font=dict(size=25,color="#253126"))
                chart(fig)
            else:
                empty("No inventory to display" if products is not None else "Inventory unavailable", "Your product availability will appear here.")
    left, right = st.columns([1.3,1])
    with left:
        with st.container(border=True):
            heading("Needs your attention", "Stock priorities")
            if alerts is not None and not alerts.empty:
                for row in alerts.sort_values("current_stock").head(5).to_dict("records"):
                    out = row["current_stock"] == 0
                    html(f'<div class="priority"><div class="priority-icon">▦</div><div class="priority-name">{escape(str(row["name"]))}<small>{row["current_stock"]} on hand · threshold {row["reorder_threshold"]}</small></div><span class="pill {"red" if out else ""}">{"Out of stock" if out else "Low stock"}</span></div>')
                st.caption(f"Showing {min(5,len(alerts))} of {len(alerts)} alerts.")
            elif alerts is not None:
                empty("Looking good", "No products are currently at or below their reorder threshold.")
            else:
                empty("Alerts unavailable", "Reconnect to review your stock priorities.")
    with right:
        with st.container(border=True):
            heading("Your inventory, by category", "Units on hand")
            if products is not None and not products.empty:
                groups = products.groupby("category",dropna=False)["stock"].sum().reset_index().sort_values("stock",ascending=True)
                chart(px.bar(groups,x="stock",y="category",orientation="h",color_discrete_sequence=["#526c39"]),260)
            else:
                empty("Room to grow", "Add products to explore your category mix.")

elif page == "Product Analytics":
    df = records("/analytics/top-products", "top_products")
    if df is not None and not df.empty:
        a,b,c = st.columns([2,1,1])
        with a:
            search = st.text_input("Find a product", placeholder="Search your catalog…")
        with b:
            category = st.selectbox("Category", ["All categories"]+sorted(df["category"].dropna().unique().tolist()))
        with c:
            limit = st.selectbox("Show top", [5,10,20,50], index=1)
        if search:
            df = df[df["name"].str.contains(search,case=False,regex=False,na=False)]
        if category != "All categories":
            df = df[df["category"] == category]
        df = df.sort_values("total_revenue",ascending=False).head(limit)
        if df.empty:
            empty("No matching products", "Try another search or category.")
        else:
            a,b,c = st.columns(3)
            with a: metric("Revenue", f"${df['total_revenue'].sum():,.0f}", "Within the selected products", True)
            with b: metric("Units sold", f"{df['total_units_sold'].sum():,.0f}", "Within the selected products")
            with c: metric("Products shown", str(len(df)), "Ranked by revenue")
            a,b = st.columns([1.65,1])
            with a:
                with st.container(border=True):
                    heading("The revenue leaders", "Selected products")
                    fig=px.bar(df.sort_values("total_revenue"),x="total_revenue",y="name",orientation="h",color_discrete_sequence=["#526c39"],labels={"total_revenue":"Revenue","name":"Product"})
                    fig.update_xaxes(tickprefix="$")
                    chart(fig,max(330,len(df)*27))
            with b:
                with st.container(border=True):
                    heading("Sales mix", "Share of units sold")
                    if df["total_units_sold"].sum()>0:
                        chart(px.pie(df,names="name",values="total_units_sold",hole=.7,color_discrete_sequence=COLORS))
                    else: empty("The first sale is ahead", "Unit share appears after products are sold.")
            table(df,"products")
    elif df is not None:
        empty("Your catalog belongs here", "Add products to start exploring performance.")

elif page == "Revenue Trends":
    a,b = st.columns([1,3])
    with a:
        period = st.selectbox("Time interval",["daily","weekly","monthly"],format_func=str.title)
    df = records(f"/analytics/revenue?period={period}","revenue_data")
    if df is not None and not df.empty:
        with b:
            count=st.selectbox("Reporting window",["All periods","Last 7 periods","Last 30 periods","Last 90 periods"])
        if count != "All periods": df=df.tail(int(count.split()[1]))
        total=df["total_revenue"].sum()
        orders=df["total_orders"].sum()
        a,b,c=st.columns(3)
        with a: metric("Revenue",f"${total:,.2f}","Within the reporting window",True)
        with b: metric("Orders",f"{orders:,.0f}","Within the reporting window")
        with c: metric("Average order",f"${total/orders:,.2f}" if orders else "$0.00","Revenue divided by order count")
        with st.container(border=True):
            heading("The revenue rhythm",f"{period.title()} · {len(df)} periods")
            revenue_chart(df)
        with st.container(border=True):
            heading("Order activity","Volume over time")
            chart(px.bar(df,x="date",y="total_orders",color_discrete_sequence=["#bbd77a"]),240)
        table(df,"revenue")
    elif df is not None: empty("A fresh start", "Your revenue timeline will appear once orders are recorded.")

else:
    a,b=st.columns([1,2])
    with a: window=st.slider("Forecast window · days",1,60,7)
    with b: st.caption("A simple demand estimate based on the latest recorded sales window. Use it as a planning signal, alongside your own judgment.")
    df=records(f"/analytics/forecast?window_days={window}","forecasts")
    if df is not None and not df.empty:
        a,b,c=st.columns(3)
        with a: metric("Projected units",f"{df['predicted_period_demand'].sum():,.0f}",f"Over the next {window} days",True)
        with b: metric("Reorder signals",str(int(df["reorder_suggested"].sum())),"Stock below projected demand")
        with c: metric("Daily demand",f"{df['avg_daily_demand'].sum():,.1f}","Estimated units across all products")
        df["stock_gap"]=(df["predicted_period_demand"]-df["current_stock"]).clip(lower=0).round(2)
        html('<div class="insight"><b>Read the signals.</b> Products above the diagonal have projected demand greater than current stock. Prioritize those with the largest gap.</div>')
        with st.container(border=True):
            heading("Stock meets demand", "Each dot is a product")
            plot=df.assign(Priority=df["reorder_suggested"].map({True:"Review stock",False:"Covered"}))
            fig=px.scatter(plot,x="current_stock",y="predicted_period_demand",color="Priority",hover_name="name",size=("avg_daily_demand" if df["avg_daily_demand"].gt(0).any() else None),size_max=40,color_discrete_map={"Review stock":"#b96550","Covered":"#526c39"},labels={"current_stock":"Current stock","predicted_period_demand":"Projected demand"})
            # A visible minimum size keeps zero-demand products discoverable.
            fig.update_traces(marker=dict(sizemin=6,line=dict(width=1,color="#fff")))
            maximum=max(float(df["current_stock"].max()),float(df["predicted_period_demand"].max()),1)
            fig.add_shape(type="line",x0=0,y0=0,x1=maximum,y1=maximum,line=dict(color="#b7c2a8",dash="dot"))
            fig.update_xaxes(title="Current stock (units)")
            fig.update_yaxes(title="Projected demand (units)")
            chart(fig,390)
            st.caption("Horizontal axis: current stock · Vertical axis: projected demand · Dotted line: stock equals demand")
        only=st.checkbox("Show only products with a reorder signal")
        table(df[df["reorder_suggested"]] if only else df,"forecast")
    elif df is not None: empty("Build your next move", "Add products and record sales to start planning demand.")

html('<div class="footer"><span>NEXUS / CLARITY FOR COMMERCE</span><span>MADE FOR YOUR NEXT MOVE ↗</span></div>')
