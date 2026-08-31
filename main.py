import os
from typing import Optional
import numpy as np
import pandas as pd
from typing import List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise ValueError("Missing Supabase credentials in environment variables.")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)

app = FastAPI(title="Sales & Inventory Analytics API")


# --- Pydantic Schemas ---

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    reorder_threshold: int = Field(ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    reorder_threshold: Optional[int] = Field(default=None, ge=0)


# --- Endpoints ---

@app.get("/")
def home():
    return {
        "message": "Sales & Inventory API is running"
    }


@app.get("/products")
def get_products():
    response = supabase.table("products").select("*").execute()
    return response.data


@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
    response = supabase.table("products").select(
        "*").eq("id", product_id).execute()

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    return response.data[0]


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    response = (
        supabase
        .table("products")
        .insert(product.model_dump())
        .execute()
    )
    return response.data


@app.put("/products/{product_id}")
def update_product_full(product_id: int, product: ProductCreate):
    # First verify product exists
    existing = supabase.table("products").select(
        "*").eq("id", product_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    response = (
        supabase
        .table("products")
        .update(product.model_dump())
        .eq("id", product_id)
        .execute()
    )
    return response.data


@app.patch("/products/{product_id}")
def update_product_partial(product_id: int, product: ProductUpdate):
    # Exclude unset fields so omitted attributes aren't overwritten with None
    update_data = product.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    existing = supabase.table("products").select(
        "*").eq("id", product_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    response = (
        supabase
        .table("products")
        .update(update_data)
        .eq("id", product_id)
        .execute()
    )
    return response.data


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    existing = supabase.table("products").select(
        "*").eq("id", product_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    supabase.table("products").delete().eq("id", product_id).execute()
    return {"message": f"Product with ID {product_id} successfully deleted"}


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


# --- Order Endpoints ---

@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate):
    total_order_value = 0.0
    items_to_process = []

    # Step 1: Validate stock for all requested items
    for item in order.items:
        prod_resp = supabase.table("products").select(
            "*").eq("id", item.product_id).execute()

        if not prod_resp.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )

        product = prod_resp.data[0]

        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product['name']}'. Available: {product['stock']}, Requested: {item.quantity}"
            )

        item_total = product["price"] * item.quantity
        total_order_value += item_total

        items_to_process.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product["price"],
            "subtotal": item_total
        })

    # Step 2: Create the main order record
    order_resp = supabase.table("orders").insert({
        "total_value": total_order_value
    }).execute()

    created_order = order_resp.data[0]
    order_id = created_order["id"]

    # Step 3: Insert order items & update product stock
    for item in items_to_process:
        # Insert into order_items
        supabase.table("order_items").insert({
            "order_id": order_id,
            "product_id": item["product"]["id"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"]
        }).execute()

        # Decrement stock in products table
        new_stock = item["product"]["stock"] - item["quantity"]
        supabase.table("products").update({
            "stock": new_stock
        }).eq("id", item["product"]["id"]).execute()

    return {
        "message": "Order created successfully",
        "order_id": order_id,
        "total_amount": total_order_value
    }


# orders get orders endpoints


@app.get("/orders")
def get_orders_all():
    response = supabase.table("orders").select("*").execute()
    return response.data


@app.get("/orders")
def get_orders():
    # Retrieve all orders ordered by latest first
    response = supabase.table("orders").select(
        "*").order("created_at", desc=True).execute()
    return response.data


@app.get("/orders/{order_id}")
def get_order_by_id(order_id: int):
    # Fetch main order details
    order_resp = supabase.table("orders").select(
        "*").eq("id", order_id).execute()

    if not order_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )

    # Fetch associated line items with product details
    items_resp = (
        supabase
        .table("order_items")
        .select("*, products(name, category)")
        .eq("order_id", order_id)
        .execute()
    )

    order_data = order_resp.data[0]
    order_data["items"] = items_resp.data
    return order_data


# stock alert logic endpoints


# --- Stock Alerts Endpoint (NumPy Vectorized Logic) ---


@app.get("/analytics/stock-alerts")
def get_stock_alerts():
    # Fetch all product records from Supabase
    response = supabase.table("products").select("*").execute()
    products = response.data

    if not products:
        return {"alerts": [], "total_alerts": 0}

    # Convert data into a pandas DataFrame for structured extraction
    df = pd.DataFrame(products)

    # Extract relevant columns into 1D NumPy arrays
    product_ids = df["id"].to_numpy()
    names = df["name"].to_numpy()
    stock = df["stock"].to_numpy(dtype=int)
    thresholds = df["reorder_threshold"].fillna(0).to_numpy(dtype=int)

    # Vectorized NumPy evaluation: boolean mask for products at or below threshold
    needs_reorder_mask = stock <= thresholds

    # Filter arrays using the boolean mask
    alert_ids = product_ids[needs_reorder_mask]
    alert_names = names[needs_reorder_mask]
    alert_stocks = stock[needs_reorder_mask]
    alert_thresholds = thresholds[needs_reorder_mask]

    # Vectorized categorization using np.where: Flag out-of-stock vs low-stock
    statuses = np.where(alert_stocks == 0, "OUT_OF_STOCK", "LOW_STOCK")

    # Build response payload
    alert_list = []
    for i in range(len(alert_ids)):
        alert_list.append({
            "product_id": int(alert_ids[i]),
            "name": str(alert_names[i]),
            "current_stock": int(alert_stocks[i]),
            "reorder_threshold": int(alert_thresholds[i]),
            "status": str(statuses[i])
        })

    return {
        "total_alerts": len(alert_list),
        "alerts": alert_list
    }


# --- Multi-Table Analytics Endpoint (Pandas pd.merge) ---
@app.get("/analytics/top-products")
def get_top_products():
    try:
        # 1. Fetch data from Supabase
        prod_resp = supabase.table("products").select("*").execute()
        items_resp = supabase.table("order_items").select("*").execute()

        products_data = prod_resp.data
        items_data = items_resp.data

        if not products_data:
            return {"top_products": []}

        df_products = pd.DataFrame(products_data)
        df_items = pd.DataFrame(items_data)

        # Handle empty order_items
        if df_items.empty:
            df_products["total_units_sold"] = 0
            df_products["total_revenue"] = 0.0
            result = df_products[["id", "name", "category",
                                  "total_units_sold", "total_revenue"]]
            return {"top_products": result.to_dict(orient="records")}

        # 2. Determine price column and line revenue
        price_col = "unit_price" if "unit_price" in df_items.columns else "price"
        df_items["item_revenue"] = df_items["quantity"] * df_items[price_col]

        # 3. Rename product id to prevent duplicate column conflict during merge
        df_products = df_products.rename(columns={"id": "product_id_pk"})

        # 4. Merge products and order_items
        df_merged = pd.merge(
            df_products,
            df_items,
            left_on="product_id_pk",
            right_on="product_id",
            how="inner"
        )

        # 5. Fill unpurchased product rows with zeros
        df_merged["quantity"] = df_merged["quantity"].fillna(0)
        df_merged["item_revenue"] = df_merged["item_revenue"].fillna(0.0)

        # 6. Group by renamed product ID
        df_grouped = (
            df_merged.groupby(
                ["product_id_pk", "name", "category"], as_index=False)
            .agg(
                total_units_sold=("quantity", "sum"),
                total_revenue=("item_revenue", "sum")
            )
        )

        # 7. Restore original column name 'id' and convert types
        df_grouped = df_grouped.rename(columns={"product_id_pk": "id"})
        df_grouped["total_units_sold"] = df_grouped["total_units_sold"].astype(
            int)
        df_grouped["total_revenue"] = df_grouped["total_revenue"].astype(float)

        # 8. Sort and slice
        df_sorted = df_grouped.sort_values(
            by="total_revenue", ascending=False)

        return {"top_products": df_sorted.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics calculation error: {str(e)}"
        )







# --- Time-Based Revenue Analytics Endpoint (Pandas Resampling / Groupby) ---

@app.get("/analytics/revenue")
def get_revenue_analytics(period: str = "daily"):
    """
    Returns revenue aggregated over time periods.
    Accepted period values: 'daily', 'weekly', 'monthly'
    """
    valid_periods = ["daily", "weekly", "monthly"]
    if period not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period '{period}'. Must be one of {valid_periods}"
        )

    try:
        # Fetch order records containing total_value and created_at timestamps
        response = supabase.table("orders").select("*").execute()
        orders_data = response.data

        if not orders_data:
            return {"period": period, "revenue_data": []}

        df_orders = pd.DataFrame(orders_data)

        # Convert created_at column to pandas datetime objects
        df_orders["created_at"] = pd.to_datetime(df_orders["created_at"])
        
        # Ensure total_value is float
        df_orders["total_value"] = df_orders["total_value"].astype(float)

        # Map API period parameters to pandas resampling frequency strings
        freq_map = {
            "daily": "D",
            "weekly": "W",
            "monthly": "ME"
        }
        resample_freq = freq_map[period]

        # Resample data by period and calculate sum of total_value and total orders
        df_resampled = (
            df_orders.set_index("created_at")
            .resample(resample_freq)
            .agg(
                total_revenue=("total_value", "sum"),
                total_orders=("id", "count")
            )
            .reset_index()
        )

        # Format datetime column to string for clean JSON output
        date_format_map = {
            "daily": "%Y-%m-%d",
            "weekly": "%Y-%W",
            "monthly": "%Y-%m"
        }
        df_resampled["date"] = df_resampled["created_at"].dt.strftime(date_format_map[period])

        # Filter out periods with 0 revenue/orders if desired, or keep to show full timeline
        df_result = df_resampled[["date", "total_revenue", "total_orders"]]

        return {
            "period": period,
            "revenue_data": df_result.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Revenue analytics calculation error: {str(e)}"
        )
    





# --- Simple Demand Forecasting Endpoint (NumPy Moving Average) ---

@app.get("/analytics/forecast")
def get_demand_forecast(window_days: int = 7):
    """
    Predicts next-period demand for products using a NumPy moving average.
    Default window size: 7 days.
    """
    if window_days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Window size must be greater than 0"
        )

    try:
        # 1. Fetch order items and products data
        items_resp = supabase.table("order_items").select("*").execute()
        prod_resp = supabase.table("products").select("*").execute()

        items_data = items_resp.data
        prod_data = prod_resp.data

        if not prod_data:
            return {"forecast_window_days": window_days, "forecasts": []}

        df_products = pd.DataFrame(prod_data)

        if not items_data:
            # If no orders exist, forecast 0 units for all products
            df_products["predicted_daily_demand"] = 0.0
            df_products["predicted_period_demand"] = 0.0
            result = df_products[["id", "name", "category", "stock", "predicted_daily_demand", "predicted_period_demand"]]
            return {"forecast_window_days": window_days, "forecasts": result.to_dict(orient="records")}

        df_items = pd.DataFrame(items_data)

        # 2. Parse timestamps and sort by date
        df_items["created_at"] = pd.to_datetime(df_items["created_at"])
        
        # Determine analysis date range
        max_date = df_items["created_at"].max()
        start_date = max_date - pd.Timedelta(days=window_days)

        # 3. Filter orders within the selected rolling window
        df_window = df_items[df_items["created_at"] >= start_date]

        forecasts = []

        # 4. Calculate moving average per product using NumPy
        for _, product in df_products.iterrows():
            p_id = product["id"]
            p_name = product["name"]
            p_category = product["category"]
            p_stock = product["stock"]

            # Filter sales for this specific product in the time window
            p_sales = df_window[df_window["product_id"] == p_id]["quantity"].to_numpy()

            if len(p_sales) == 0:
                avg_daily_demand = 0.0
            else:
                # Total sales in window divided by window size (NumPy vectorized mean)
                avg_daily_demand = float(np.sum(p_sales) / window_days)

            predicted_period_demand = round(avg_daily_demand * window_days, 2)
            avg_daily_demand = round(avg_daily_demand, 2)

            forecasts.append({
                "product_id": int(p_id),
                "name": str(p_name),
                "category": str(p_category),
                "current_stock": int(p_stock),
                "avg_daily_demand": avg_daily_demand,
                "predicted_period_demand": predicted_period_demand,
                "reorder_suggested": bool(p_stock < predicted_period_demand)
            })

        return {
            "forecast_window_days": window_days,
            "forecasts": forecasts
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Demand forecasting error: {str(e)}"
        )






