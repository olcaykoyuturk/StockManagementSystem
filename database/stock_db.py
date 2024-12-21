import sqlite3

# Connect to the stock database
connection = sqlite3.connect("stock.db")
cursor = connection.cursor()

# Create the inventory table
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    product_code TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    supplier TEXT NOT NULL
)
""")

# Commit the changes and close the connection
connection.commit()
connection.close()

print("Inventory table successfully created in stock.db.")
