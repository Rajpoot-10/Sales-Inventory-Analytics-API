import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Nexus | Retail & Inventory Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

# --- Inject Google Fonts & Font Awesome & Custom Advanced CSS ---
st.markdown("""
<!-- External Fonts & Icons -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
    /* Global Typography Reset */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Background Gradient */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(15, 18, 28) 0%, rgb(10, 12, 18) 90.2%);
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(25, 30, 46, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }

    /* Metric Card Styling */
    .kpi-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .kpi-icon {
        width: 52px;
        height: 52px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }
    
    .icon-indigo { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
    .icon-red { background: rgba(239, 68, 68, 0.15); color: #f87171; }
    .icon-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .icon-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; }

    .kpi-value {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-top: 8px;
        margin-bottom: 2px;
        color: #f8fafc;
    }

    .kpi-label {
        font-size: 13px;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0e14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Status Badges */
    .badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-success { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

    /* Custom Header Component */
    .main-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 28px;
    }
    .main-header i {
        font-size: 32px;
        color: #6366f1;
        background: rgba(99, 102, 241, 0.1);
        padding: 12px;
        border-radius: 12px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        color: #f8fafc;
    }
    .main-header p {
        margin: 0;
        font-size: 14px;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# --- API Helper ---


def fetch_api(endpoint):
    try:
        res = requests.get(f"{API_URL}{endpoint}")
        if res.status_code == 200:
            return res.json()
        st.error(f"API Error ({res.status_code}): {res.text}")
    except Exception:
        st.error("Connection Refused. Please ensure FastAPI is running on port 8000.")
    return None


# --- Sidebar Component ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0;">
            <i class="fa-solid fa-cube" style="font-size: 26px; color: #6366f1;"></i>
            <span style="font-size: 20px; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px;">NEXUS AI</span>
        </div>
    """, unsafe_allow_html=True)
    st.caption("Inventory & Revenue Command Center")
    st.divider()

    menu = st.radio(
        "NAVIGATION",
        ["Overview", "Product Analytics", "Revenue Trends", "Demand Forecasting"],
        label_visibility="collapsed"
    )

# ---------------------------------------------------------
# 1. OVERVIEW VIEW
# ---------------------------------------------------------
if menu == "Overview":
    st.markdown("""
        <div class="main-header">
            <i class="fa-solid fa-chart-line"></i>
            <div>
                <h1>Executive Inventory Command</h1>
                <p>Real-time telemetry on stock thresholds and order exceptions.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    alerts_data = fetch_api("/analytics/stock-alerts")

    if alerts_data:
        alerts = alerts_data.get("alerts", [])
        total_alerts = len(alerts)
        out_of_stock = sum(1 for a in alerts if a["status"] == "OUT_OF_STOCK")
        low_stock = sum(1 for a in alerts if a["status"] == "LOW_STOCK")

        # HTML KPI Cards with Font Awesome Icons
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-container">
                        <div>
                            <div class="kpi-label">Active Alerts</div>
                            <div class="kpi-value">{total_alerts}</div>
                        </div>
                        <div class="kpi-icon icon-indigo"><i class="fa-solid fa-bell"></i></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-container">
                        <div>
                            <div class="kpi-label">Out of Stock</div>
                            <div class="kpi-value">{out_of_stock}</div>
                        </div>
                        <div class="kpi-icon icon-red"><i class="fa-solid fa-triangle-exclamation"></i></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-container">
                        <div>
                            <div class="kpi-label">Low Stock Warning</div>
                            <div class="kpi-value">{low_stock}</div>
                        </div>
                        <div class="kpi-icon icon-amber"><i class="fa-solid fa-box-open"></i></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(
            "<h3 style='color: #f8fafc; margin-top: 10px;'>Threshold Distribution</h3>", unsafe_allow_html=True)

        if alerts:
            df_alerts = pd.DataFrame(alerts)

            fig = px.bar(
                df_alerts,
                x="name",
                y=["current_stock", "reorder_threshold"],
                barmode="group",
                title="Stock Level vs Reorder Threshold",
                color_discrete_sequence=["#6366f1", "#f59e0b"],
                labels={"value": "Units",
                        "variable": "Metric", "name": "Product"}
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter", "color": "#94a3b8"},
                height=380,
                legend={"orientation": "h", "y": 1.15}
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_alerts, use_container_width=True, hide_index=True)
        else:
            st.markdown("""
                <div class="glass-card" style="text-align: center;">
                    <i class="fa-solid fa-circle-check" style="font-size: 40px; color: #34d399; margin-bottom: 10px;"></i>
                    <h4 style="color: #f8fafc; margin: 0;">Optimal Inventory Health</h4>
                    <p style="color: #64748b; margin: 0;">No items currently fall below critical reorder limits.</p>
                </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PRODUCT ANALYTICS VIEW
# ---------------------------------------------------------
elif menu == "Product Analytics":
    st.markdown("""
        <div class="main-header">
            <i class="fa-solid fa-trophy"></i>
            <div>
                <h1>Product Performance & Ranking</h1>
                <p>Vectorized multi-table joins analyzing top performers by volume and revenue.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    limit = st.slider("Select Top N Products", 1, 20, 5)
    data = fetch_api(f"/analytics/top-products?limit={limit}")

    if data and data.get("top_products"):
        df = pd.DataFrame(data["top_products"])

        col1, col2 = st.columns([1.3, 1])
        with col1:
            fig = px.bar(
                df,
                x="total_revenue",
                y="name",
                orientation="h",
                color="total_revenue",
                color_continuous_scale="Viridis",
                title="Total Revenue ($)",
                text_auto=".2s"
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter", "color": "#94a3b8"},
                yaxis={"categoryorder": "total ascending"},
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig_pie = px.pie(
                df,
                names="name",
                values="total_units_sold",
                hole=0.6,
                title="Units Sold Share",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter", "color": "#94a3b8"},
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 3. REVENUE TRENDS VIEW
# ---------------------------------------------------------
elif menu == "Revenue Trends":
    st.markdown("""
        <div class="main-header">
            <i class="fa-solid fa-arrow-trend-up"></i>
            <div>
                <h1>Time-Series Revenue Analytics</h1>
                <p>Pandas resampling over configurable temporal granularities.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    period = st.selectbox("Granularity", ["daily", "weekly", "monthly"])
    data = fetch_api(f"/analytics/revenue?period={period}")

    if data and data.get("revenue_data"):
        df = pd.DataFrame(data["revenue_data"])

        fig = px.area(
            df,
            x="date",
            y="total_revenue",
            title=f"Gross Revenue ({period.capitalize()})",
            markers=True
        )
        fig.update_traces(line_color="#818cf8",
                          fillcolor="rgba(99, 102, 241, 0.15)")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter", "color": "#94a3b8"},
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 4. DEMAND FORECASTING VIEW
# ---------------------------------------------------------
elif menu == "Demand Forecasting":
    st.markdown("""
        <div class="main-header">
            <i class="fa-solid fa-wand-magic-sparkles"></i>
            <div>
                <h1>Predictive Demand Forecasting</h1>
                <p>NumPy moving-average model estimating stock depletion velocity.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    window = st.slider("Rolling Window (Days)", 1, 60, 7)
    data = fetch_api(f"/analytics/forecast?window_days={window}")

    if data and data.get("forecasts"):
        df = pd.DataFrame(data["forecasts"])

        fig = px.scatter(
            df,
            x="current_stock",
            y="predicted_period_demand",
            size="avg_daily_demand",
            color="reorder_suggested",
            hover_name="name",
            title="Current Stock vs Projected Demand",
            color_discrete_map={True: "#ef4444", False: "#10b981"}
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter", "color": "#94a3b8"},
            height=420
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
