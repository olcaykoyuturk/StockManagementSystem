import sqlite3

connection = sqlite3.connect("stock.db")
cursor = connection.cursor()

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

connection.commit()
connection.close()

print("stock.db tablosu başarıyla oluşturuldu.")
