import random
import sqlite3

def generate_unique_order_code(cursor):
    while True:
        # Generate a unique 6-digit order code
        order_code = str(random.randint(100000, 999999))

        # Check if the order code exists in the ordertable
        cursor.execute("SELECT 1 FROM ordertable WHERE order_code = ?", (order_code,))
        if not cursor.fetchone():  # If the order code doesn't exist
            return order_code  # Return the unique code

# Connect to the order database
connection = sqlite3.connect("order.db")
cursor = connection.cursor()

# Drop the existing table if it exists
cursor.execute("DROP TABLE IF EXISTS ordertable")

# Create the ordertable
cursor.execute("""
CREATE TABLE IF NOT EXISTS ordertable (
    order_code TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT "Received",
    order_date TEXT NOT NULL,
    product_code TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    is_processed INTEGER NOT NULL DEFAULT 0
)
""")

# Sample orders to be added
orders = [
    ('Trendyol', '2024-07-19', '100001', 2),
    ('Trendyol', '2024-07-19', '100002', 3),
    ('Trendyol', '2024-07-19', '100003', 1),
    ('Hepsiburada', '2024-07-20', '100004', 1),
    ('Hepsiburada', '2024-07-21', '100005', 2),
    ('Trendyol', '2024-08-15', '100006', 1),
    ('Amazon', '2024-08-17', '100007', 4),
    ('Hepsiburada', '2024-08-20', '100008', 3),
    ('Amazon', '2024-09-01', '100009', 5),
    ('Trendyol', '2024-09-10', '100010', 1),
    ('Trendyol', '2024-09-15', '100011', 2),
    ('Hepsiburada', '2024-09-20', '100012', 1),
    ('Trendyol', '2024-10-05', '100013', 3),
    ('Hepsiburada', '2024-10-07', '100014', 2),
    ('Amazon', '2024-10-15', '100015', 1),
    ('Hepsiburada', '2024-10-20', '100016', 2),
    ('Trendyol', '2024-10-25', '100017', 3),
    ('Trendyol', '2024-11-02', '100018', 2),
    ('Amazon', '2024-11-05', '100019', 1),
    ('Trendyol', '2024-11-10', '100020', 1),
    ('Hepsiburada', '2024-11-12', '100001', 4),
    ('Amazon', '2024-11-15', '100002', 2),
    ('Trendyol', '2024-12-05', '100003', 3),
    ('Hepsiburada', '2024-12-06', '100004', 1),
    ('Amazon', '2024-12-10', '100005', 1),
    ('Trendyol', '2024-12-12', '100006', 2),
    ('Trendyol', '2024-12-15', '100007', 5),
    ('Hepsiburada', '2024-12-18', '100008', 3),
    ('Amazon', '2024-12-19', '100009', 2),
    ('Trendyol', '2024-12-19', '100010', 1),
    ('Trendyol', '2024-12-20', '100011', 2),
    ('Hepsiburada', '2024-12-21', '100012', 1),
    ('Amazon', '2024-12-21', '100013', 1),
    ('Trendyol', '2024-12-22', '100014', 3),
    ('Hepsiburada', '2024-12-23', '100015', 2),
    ('Amazon', '2024-12-23', '100016', 4),
    ('Trendyol', '2024-12-24', '100017', 2),
    ('Hepsiburada', '2024-12-25', '100018', 5),
    ('Amazon', '2024-12-25', '100019', 2),
    ('Trendyol', '2024-12-25', '100020', 3)
]


# Insert each order into the ordertable
for order in orders:
    # Generate unique order code
    order_code = generate_unique_order_code(cursor)

    # Insert the order into the table (status will default to 'Received')
    cursor.execute("""
    INSERT INTO ordertable (order_code, provider, order_date, product_code, quantity)
    VALUES (?, ?, ?, ?, ?)
    """, (order_code, *order))

# Commit the changes and close the connection
connection.commit()
connection.close()

print("Table successfully created and new orders added to order.db.")
