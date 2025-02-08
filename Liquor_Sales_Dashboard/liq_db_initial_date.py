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

# Define transaction distribution with variation
transaction_counts = {
    "2025-02-01": random.randint(900, 1000),  # Max 1000, random range 900-1000
    "2025-02-02": random.randint(650, 750),   # Max 850, range 750-850
    "2025-02-03": random.randint(450, 550),   # Max 700, range 650-750
    "2025-02-04": random.randint(550, 650),   # Max 700, range 650-750
    "2025-02-05": random.randint(550, 650),   # Max 700, range 650-750
    "2025-02-06": random.randint(650, 750),
    "2025-02-07": random.randint(800, 900),   # Max 700, range 650-750    
}

def generate_daily_transactions(date, num_orders):
    """
    Generates up to `num_orders` transactions for a specific date with full timestamps.
    """
    with engine.connect() as conn:
        # Fetch product IDs and prices from the database
        products = pd.read_sql("SELECT product_id, product_price FROM dim_products", conn)
        
        sales_data = []
        date_obj = datetime.strptime(date, "%Y-%m-%d")  # Convert date string to datetime

        for _ in range(num_orders):
            # Generate a random timestamp within the day
            random_time = timedelta(
                hours=random.randint(9, 22),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            # Combine the date with the random time
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
        print(f"✅ Inserted {num_orders} transactions for {date} with varied count!")

# Generate transactions for each day with randomized counts
for date, num_orders in transaction_counts.items():
    generate_daily_transactions(date, num_orders)

print("🎉 Transactions successfully inserted for 2/1 - 2/7 with varied counts!")