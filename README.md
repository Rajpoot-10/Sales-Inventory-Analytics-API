Sales & Inventory Analytics API
A robust RESTful API built with FastAPI, Supabase (PostgreSQL), Pandas, and NumPy to manage e-commerce product catalogs, process orders with automatic stock tracking, and run business intelligence analytics.

Features
1. Product Management (CRUD)
Full CRUD support (GET, POST, PUT, PATCH, DELETE) for products.

Enforces data validation using Pydantic models (e.g., price and stock bounds).

2. Order Processing & Automated Inventory
POST /orders: Validates cart items against database stock levels before confirming purchases.

Automatically decrements product inventory upon order completion.

Transactional records link orders and line items in order_items via foreign key constraints.

3. Business Intelligence & Analytics
Stock Alerts (NumPy): Evaluates product stock against reorder thresholds using vectorized NumPy logic to flag low-stock or out-of-stock items without slow loops.

Best-Sellers Ranking (Pandas): Merges products and order_items tables via pd.merge() to compute revenue and units sold per product.

Time-Series Revenue Analytics (Pandas): Aggregates total sales revenue over custom time intervals (daily, weekly, monthly) using datetime resampling.

Demand Forecasting (NumPy): Calculates rolling moving averages of product sales over customizable time windows (e.g., 7 or 30 days) to project upcoming demand and suggest stock reorders.

🛠️ Tech Stack
Backend Framework: FastAPI

Database: Supabase (PostgreSQL)

Data Processing & Analytics: Pandas, NumPy

Data Validation: Pydantic (v2)

Server: Uvicorn

📁 Project Structure
Plaintext
sales_inventory_api/
│
├── main.py              # Core API endpoints & logic
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (git-ignored)
└── README.md            # Documentation
⚙️ Installation & Setup
1. Clone or Open Project
Bash
cd E:\sales_inventory_api
2. Create & Activate Virtual Environment
Bash
# Windows
python -m venv venv
venv\Scripts\activate
3. Install Dependencies
Bash
pip install -r requirements.txt
4. Environment Configuration
Create a .env file in the root directory:

Code snippet
SUPABASE_URL=your_supabase_project_url
SUPABASE_SECRET_KEY=your_supabase_secret_key
5. Run the Server
Bash
uvicorn main:app --reload
The API will start running at [http://127.0.0.1:8000](http://127.0.0.1:8000).

📌 API Endpoints Overview
Products
GET /products — Fetch all products

GET /products/{id} — Fetch product by ID

POST /products — Create a new product

PUT /products/{id} — Full update of product details

PATCH /products/{id} — Partial update of product fields

DELETE /products/{id} — Remove product from catalog

Orders
POST /orders — Place an order (validates stock & decrements inventory)

GET /orders — Fetch complete order history

GET /orders/{id} — Fetch single order with detailed line items

Analytics
GET /analytics/stock-alerts — Vectorized inventory check (LOW_STOCK, OUT_OF_STOCK)

GET /analytics/top-products?limit=5 — Ranked products by revenue & units sold

GET /analytics/revenue?period=daily — Time-series revenue (daily, weekly, monthly)

GET /analytics/forecast?window_days=7 — Moving average demand prediction & reorder flags

📖 API Documentation & Testing
FastAPI automatically generates interactive documentation. Once the app is running, visit:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

## Streamlit dashboard

The Nexus dashboard provides an overview of revenue and inventory, product search
and category filters, revenue trends, demand forecasts, and CSV exports.

Start the API and dashboard in separate terminals:

```powershell
python -m uvicorn main:app --reload
python -m streamlit run dashboard.py
```

The dashboard connects to `http://127.0.0.1:8000` by default. Set the `API_URL`
environment variable to use another API address. The dashboard theme is configured
in `.streamlit/config.toml`.

Keep your Supabase project active and configure its Project URL and secret key
in the local `.env` file. Never commit this file.

## Streamlit Community Cloud

Deploy `dashboard.py` from the `main` branch. The root `requirements.txt`
contains only the packages used by this project and excludes Windows-only tools.

The dashboard and FastAPI are separate processes. Community Cloud starts the
Streamlit dashboard; it does not start `uvicorn main:app` automatically. Deploy
the backend separately, then add this setting in the Streamlit app's Secrets:

```toml
API_URL = "https://your-deployed-api.example.com"
```

Replace the example with your actual backend URL. Configure `SUPABASE_URL` and
`SUPABASE_SECRET_KEY` in the backend host's environment. A localhost API address
cannot connect from Community Cloud to your personal computer.

For local secrets, `.streamlit/secrets.toml` is ignored by Git. Never commit keys.

### Standalone cloud mode (no separate API hosting)

In the Streamlit app's Secrets settings, add:

```toml
DATA_BACKEND = "supabase"
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_SECRET_KEY = "your-project-secret-key"
```

Use your real credentials only in Secrets, never in GitHub or chat. This mode
reuses the existing read-only analytics functions directly without an HTTP
server. Local use defaults to API mode; set `DATA_BACKEND = "api"` and `API_URL`
if you prefer a separately hosted backend. Restart after changing credentials.

Anyone who can access the dashboard can view the displayed business data.
Restrict app access if the data should remain private.
