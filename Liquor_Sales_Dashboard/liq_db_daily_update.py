import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# Initialize Faker for timestamps
fake = Faker()

# Database connection
DATABASE_URL = "postgresql://jim:HGxcoyUGmxkmRJcqoA0fsleiTDZmRwN7@dpg-cuh7201u0jms73fvj8j0-a.virginia-postgres.render.com/liquor_db"
engine = create_engine(DATABASE_URL)

# Define transaction volume per day of the week (higher on Fri/Sat, lower on Mon)
day_transaction_ranges = {
    "Monday": (400, 500),    # Least transactions
    "Tuesday": (400, 500),
    "Wednesday": (400, 500),
    "Thursday": (600, 700),
    "Friday": (900, 1000),  # Most transactions
    "Saturday": (900, 1000),  # Most transactions
    "Sunday": (700, 800)
}

def generate_daily_transactions(date):
    """
    Generates transactions for a single day with dynamic counts based on the day of the week.
    """
    with engine.connect() as conn:
        # Fetch product IDs and prices from the database
        products = pd.read_sql("SELECT product_id, product_price FROM dim_products", conn)

        # Convert date string to datetime object and get the day of the week
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")  # Get weekday name (e.g., "Monday", "Tuesday")

        # Get the range for the number of transactions based on the day of the week
        min_orders, max_orders = day_transaction_ranges.get(day_name, (600, 800))
        num_orders = random.randint(min_orders, max_orders)

        sales_data = []

        for _ in range(num_orders):
            # Generate a random time within the day
            random_time = timedelta(
                hours=random.randint(9, 22),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            transaction_time = date_obj + random_time
            transaction_id = int(transaction_time.timestamp() * 1000)  # Unix timestamp (milliseconds)

            num_items = random.randint(1, 5)  # 1-5 items per order
            selected_products = products.sample(num_items)  # Pick random products

            for _, row in selected_products.iterrows():
                product_id = row["product_id"]
                unit_price = row["product_price"]
                sale_quantity = random.randint(1, 3)  # 1-3 units per product
                total_price = round(sale_quantity * unit_price, 2)

                # 10% chance of being a refund
                transaction_type = "refund" if random.random() < 0.1 else "purchase"
                if transaction_type == "refund":
                    sale_quantity *= -1
                    total_price *= -1

                sales_data.append({
                    "trans_id": transaction_id,
                    "product_id": product_id,
                    "transaction_date": transaction_time,  # ✅ Includes full timestamp
                    "sale_quantity": sale_quantity,
                    "total_price": total_price,
                    "transaction_type": transaction_type
                })

        # Convert to DataFrame and upload to PostgreSQL
        sales_df = pd.DataFrame(sales_data)
        sales_df.to_sql("fact_sales", engine, if_exists="append", index=False)
        print(f"✅ Inserted {num_orders} transactions for {date} ({day_name})")

# Example usage: Generate transactions for a single day (e.g., "2024-02-09")
generate_daily_transactions(datetime.now().strftime("%Y-%m-%d"))