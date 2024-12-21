import sqlite3
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class StockManagementApp:
    def __init__(self, root):
        self.tree = None
        self.root = root
        self.root.title("Stok Yönetim Sistemi")
        self.root.geometry("1200x900")

        self.current_time_label = None
        self.left_frame = self.create_left_panel()
        self.right_frame = self.create_right_panel()
        self.create_buttons()
        self.main_page()

    def create_left_panel(self):
        left_frame = tk.Frame(self.root, width=250, bg="lightgray")
        left_frame.pack(side="left", fill="y")
        left_frame.pack_propagate(False)
        return left_frame

    def create_right_panel(self):
        right_frame = tk.Frame(self.root, bg="white")
        right_frame.pack(side="right", fill="both", expand=True)
        return right_frame

    def create_buttons(self):
        buttons = [
            ("Ana Menü", self.main_page),
            ("Güncel Stok", self.current_stock),
            ("Stok Yönetimi", self.show_stock_management),
            ("Sipariş Yönetimi", self.show_order_management),
            ("Stok Uyarıları", self.show_stock_alerts),
            ("Raporlama", self.show_reporting),
            ("Tedarikçi ve Müşteri Yönetimi", self.show_supplier_customer_management),
            ("Çıkış", self.exit_app)
        ]

        for text, command in buttons:
            button = tk.Button(self.left_frame, text=text, command=command,
                               bg="lightblue", font=("Arial", 12))
            button.pack(fill="x", pady=5, padx=10)

    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def main_page(self):
        """Ana menü bilgilerini ve özet raporları gösterir."""
        self.clear_right_frame()

        header_label = tk.Label(
            self.right_frame, text="Ana Ekran", font=("Arial", 18, "bold"), bg="lightblue", fg="white"
        )
        header_label.pack(fill="x", pady=10)

        content_frame = tk.Frame(self.right_frame, bg="white", relief="groove", borderwidth=2)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_label = tk.Label(
            content_frame, text=f"Bugünün Tarihi ve Saati: {current_time}", font=("Arial", 12), bg="white", anchor="w"
        )
        time_label.pack(padx=20, pady=10, anchor="w")

        order_connection = sqlite3.connect("database/order.db")
        order_cursor = order_connection.cursor()

        stock_connection = sqlite3.connect("database/stock.db")
        stock_cursor = stock_connection.cursor()

        order_frame = tk.LabelFrame(content_frame, text="Sipariş Bilgileri", font=("Arial", 12, "bold"), bg="white")
        order_frame.pack(fill="x", padx=20, pady=10)

        order_cursor.execute("SELECT COUNT(*) FROM ordertable")
        total_orders = order_cursor.fetchone()[0]

        order_cursor.execute("SELECT COUNT(*) FROM ordertable WHERE status = 'Delivered'")
        delivered_orders = order_cursor.fetchone()[0]

        tk.Label(
            order_frame,
            text=f"Toplam Sipariş Sayısı: {total_orders}",
            font=("Arial", 12),
            bg="white",
            anchor="w",
        ).pack(padx=10, pady=5, anchor="w")

        tk.Label(
            order_frame,
            text=f"Teslim Edilen Siparişler: {delivered_orders}",
            font=("Arial", 12),
            bg="white",
            anchor="w",
        ).pack(padx=10, pady=5, anchor="w")

        stock_frame = tk.LabelFrame(content_frame, text="Stok Bilgileri", font=("Arial", 12, "bold"), bg="white")
        stock_frame.pack(fill="x", padx=20, pady=10)

        stock_cursor.execute("SELECT COUNT(*) FROM inventory")
        total_products = stock_cursor.fetchone()[0]

        stock_cursor.execute("SELECT SUM(quantity) FROM inventory")
        total_stock = stock_cursor.fetchone()[0]

        tk.Label(
            stock_frame,
            text=f"Stokta Bulunan Ürün Çeşidi: {total_products}",
            font=("Arial", 12),
            bg="white",
            anchor="w",
        ).pack(padx=10, pady=5, anchor="w")

        tk.Label(
            stock_frame,
            text=f"Toplam Ürün Adedi: {total_stock}",
            font=("Arial", 12),
            bg="white",
            anchor="w",
        ).pack(padx=10, pady=5, anchor="w")

        income_frame = tk.LabelFrame(content_frame, text="Aylık Gelir Bilgileri", font=("Arial", 12, "bold"),
                                     bg="white")
        income_frame.pack(fill="x", padx=20, pady=10)

        current_month = datetime.now().strftime("%Y-%m")
        order_cursor.execute(
            """
            SELECT product_code, SUM(quantity) 
            FROM ordertable 
            WHERE status = 'Delivered' AND strftime('%Y-%m', order_date) = ?
            GROUP BY product_code
            """,
            (current_month,),
        )
        monthly_orders = order_cursor.fetchall()

        monthly_income = 0
        for order in monthly_orders:
            product_code, quantity = order
            stock_cursor.execute("SELECT price FROM inventory WHERE product_code = ?", (product_code,))
            price = stock_cursor.fetchone()[0]
            monthly_income += quantity * price

        tk.Label(
            income_frame,
            text=f"Bu Ayki Toplam Gelir: {monthly_income:.2f} TL",
            font=("Arial", 12),
            bg="white",
            anchor="w",
        ).pack(padx=10, pady=5, anchor="w")

        order_connection.close()
        stock_connection.close()

        reminders_frame = tk.LabelFrame(content_frame, text="Hatırlatmalar ve Öneriler", font=("Arial", 12, "bold"),
                                        bg="white")
        reminders_frame.pack(fill="x", padx=20, pady=10)

        reminders_text = """- Düşük stok seviyelerini kontrol edin.\n- Yeni siparişler için durumları güncelleyin.\n- Satış performans raporlarına göz atın."""
        tk.Label(
            reminders_frame,
            text=reminders_text,
            font=("Arial", 12),
            bg="white",
            anchor="w",
            justify="left",
        ).pack(padx=10, pady=5, anchor="w")

    def current_stock(self):
        """Güncel Stok Durumu ekranı."""
        self.clear_right_frame()

        header_label = tk.Label(
            self.right_frame,
            text="Güncel Stok Durumu",
            font=("Arial", 18, "bold"),
            bg="lightblue",
            fg="white"
        )
        header_label.pack(fill="x", pady=10)

        label = tk.Label(
            self.right_frame,
            text="Aşağıdaki araçlarla güncel stok durumunu arayabilir ve inceleyebilirsiniz.",
            font=("Arial", 12),
            bg="white",
            fg="gray",
            anchor="w"
        )
        label.pack(pady=10, padx=20, anchor="w")

        self.create_search_bar()
        self.create_table()
        self.load_data()

    def create_search_bar(self):
        """Arama çubuğu oluşturur."""
        search_frame = tk.Frame(self.right_frame, bg="white")
        search_frame.pack(pady=5)

        search_label = tk.Label(search_frame, text="Ara: ", font=("Arial", 12), bg="white")
        search_label.pack(side="left", padx=5)

        search_entry = tk.Entry(search_frame, font=("Arial", 12))
        search_entry.pack(side="left", padx=5)

        search_button = tk.Button(search_frame, text="Ara", font=("Arial", 12),
                                  command=lambda: self.filter_table(search_entry.get()))
        search_button.pack(side="left", padx=5)

        info_label = tk.Label(self.right_frame,
                              text="Arama Yapılabilir Alanlar: Ürün Kodu, Ürün Adı, Kategori, Marka, Tedarikçi",
                              font=("Arial", 10, "italic"), fg="gray", bg="white")
        info_label.pack(pady=5)

    def create_table(self):
        """Veri tablosu için Treeview widget'ını oluşturur."""
        self.tree = ttk.Treeview(self.right_frame, columns=(
            "Product Code", "Product Name", "Category", "Brand", "Price", "Quantity", "Supplier"), show="headings")

        headings = ["Product Code", "Product Name", "Category", "Brand", "Price", "Quantity", "Supplier"]
        for heading in headings:
            self.tree.heading(heading, text=heading.replace("_", " ").title())
            self.tree.column(heading, anchor="center", width=120)

        self.tree.pack(fill="both", expand=True)

    def load_data(self):
        """Veritabanından tüm verileri Treeview'a yükler."""
        connection = sqlite3.connect("database/stock.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
        connection.close()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def filter_table(self, query):
        """Treeview'daki verileri arama sorgusuna göre filtreler."""
        connection = sqlite3.connect("database/stock.db")
        cursor = connection.cursor()
        cursor.execute("""
        SELECT * FROM inventory
        WHERE product_code LIKE ? OR product_name LIKE ? OR category LIKE ? OR brand LIKE ? OR supplier LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        connection.close()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def show_stock_management(self):
        """Stok Yönetimi ekranını gösterir."""
        self.clear_right_frame()

        header_label = tk.Label(
            self.right_frame,
            text="Stok Yönetim Ekranı",
            font=("Arial", 18, "bold"),
            bg="lightblue",
            fg="white"
        )
        header_label.pack(fill="x", pady=10)

        label = tk.Label(
            self.right_frame,
            text="Stok Yönetimi ekranında, ürünlerinizi kolayca yönetebilir, stok seviyelerini düzenleyebilir ve yeni ürün ekleyebilirsiniz. ",
            font=("Arial", 12),
            bg="white",
            fg="gray",
            anchor="w"
        )
        label.pack(pady=10, padx=20, anchor="w")

        top_frame = tk.Frame(self.right_frame)
        top_frame.pack(side="top", fill="x")

        button1 = tk.Button(top_frame, text="Ürün Ekleme", command=self.show_content_1)
        button1.pack(side="left")

        button2 = tk.Button(top_frame, text="Ürün Güncelleme", command=self.show_content_2)
        button2.pack(side="left")

        button3 = tk.Button(top_frame, text="Ürün Silme", command=self.show_content_3)
        button3.pack(side="left")

        button4 = tk.Button(top_frame, text="Stok Ekleme", command=self.show_content_4)
        button4.pack(side="left")

        self.content_frame = tk.Frame(self.right_frame, bg="white")
        self.content_frame.pack(side="top", fill="both", expand=True)

        self.show_content_1()

    def show_content_1(self):
        """Buton 1'e tıklanınca gösterilecek içerik (Ürün Ekleme)."""
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Ürün Ekleme", font=("Arial", 14, "bold"), bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(padx=30, pady=0, anchor="w")

        fields = [
            ("Ürün Kodu", "product_code"),
            ("Ürün Adı", "product_name"),
            ("Kategori", "category"),
            ("Marka", "brand"),
            ("Fiyat", "price"),
            ("Miktar", "quantity"),
            ("Tedarikçi", "supplier")
        ]

        self.form_entries = {}

        for label_text, field in fields:
            label = tk.Label(form_frame, text=label_text, font=("Arial", 12), bg="white", anchor="w")
            label.grid(row=fields.index((label_text, field)), column=0, pady=5,
                       sticky="w")
            entry = tk.Entry(form_frame, font=("Arial", 12))
            entry.grid(row=fields.index((label_text, field)), column=1, padx=10, pady=5,
                       sticky="w")

            self.form_entries[field] = entry

        add_button = tk.Button(self.content_frame, text="Ürünü Ekle", font=("Arial", 12), command=self.add_product)
        add_button.pack(padx=30, pady=10, anchor="w")

    def show_content_2(self):
        """Buton 2'ye tıklanınca gösterilecek içerik (Ürün Güncelleme)."""
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Ürün Güncelleme", font=("Arial", 14, "bold"), bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        self.form_frame = tk.Frame(self.content_frame, bg="white")
        self.form_frame.pack(padx=30, anchor="w")

        product_code_label = tk.Label(self.form_frame, text="Ürün Kodu", font=("Arial", 12), bg="white", anchor="w")
        self.product_code_entry = tk.Entry(self.form_frame)

        product_code_label.grid(row=1, column=0, pady=5, sticky="w")
        self.product_code_entry.grid(row=1, column=1, pady=5, sticky="w")

        search_button = tk.Button(self.form_frame, text="Ürünü Getir", font=("Arial", 12),
                                  command=self.get_product_for_update)
        search_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

        self.update_form_frame = tk.Frame(self.form_frame, bg="white")
        self.update_form_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

        self.product_name_entry = self.create_form_entry("Ürün Adı", "", 0)
        self.category_entry = self.create_form_entry("Kategori", "", 1)
        self.brand_entry = self.create_form_entry("Marka", "", 2)
        self.price_entry = self.create_form_entry("Fiyat", "", 3)
        self.quantity_entry = self.create_form_entry("Adet", "", 4)
        self.supplier_entry = self.create_form_entry("Tedarikçi", "", 5)

        self.update_button = tk.Button(self.form_frame, text="Ürünü Güncelle", font=("Arial", 12),
                                       command=self.update_product)
        self.update_button.grid(row=6, column=0, columnspan=2, sticky="w")

    def show_content_3(self):
        """Buton 3'e tıklanınca gösterilecek içerik (Ürün Silme)."""
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Ürün Silme", font=("Arial", 14, "bold"), bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        self.form_frame = tk.Frame(self.content_frame, bg="white")
        self.form_frame.pack(padx=30, pady=0, anchor="w")

        product_code_label = tk.Label(self.form_frame, text="Ürün Kodu", font=("Arial", 12), bg="white", anchor="w")
        self.product_code_entry = tk.Entry(self.form_frame)

        product_code_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.product_code_entry.grid(row=1, column=1, pady=5, sticky="w")

        delete_button = tk.Button(self.form_frame, text="Ürünü Sil", font=("Arial", 12),
                                  command=self.delete_product)
        delete_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

    def show_content_4(self):
        """Buton 4'e tıklanınca gösterilecek içerik (Stok Ekleme)."""
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Stok Ekleme", font=("Arial", 14, "bold"), bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(padx=30, pady=0, anchor="w")

        product_code_label = tk.Label(form_frame, text="Ürün Kodu", font=("Arial", 12), bg="white", anchor="w")
        product_code_label.grid(row=0, column=0, pady=5, sticky="w")
        self.product_code_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.product_code_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        quantity_label = tk.Label(form_frame, text="Eklenen Miktar", font=("Arial", 12), bg="white", anchor="w")
        quantity_label.grid(row=1, column=0, pady=5, sticky="w")
        self.quantity_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        add_stock_button = tk.Button(self.content_frame, text="Stok Ekle", font=("Arial", 12), command=self.add_stock)
        add_stock_button.pack(padx=30, pady=10, anchor="w")

    def add_stock(self):
        """Stok miktarını ekler."""
        product_code = self.product_code_entry.get()
        quantity_to_add = self.quantity_entry.get()

        if not product_code or not quantity_to_add:
            tk.messagebox.showerror("Hata", "Ürün Kodu ve Miktar alanları boş olamaz!")
            return

        try:
            quantity_to_add = int(quantity_to_add)
        except ValueError:
            tk.messagebox.showerror("Hata", "Miktar bir sayı olmalıdır!")
            return

        stock_connection = sqlite3.connect("database/stock.db")
        stock_cursor = stock_connection.cursor()

        stock_cursor.execute("""
            SELECT quantity FROM inventory WHERE product_code = ?
        """, (product_code,))
        product_data = stock_cursor.fetchone()

        if product_data:
            current_quantity = product_data[0]
            new_quantity = current_quantity + quantity_to_add

            stock_cursor.execute("""
                UPDATE inventory SET quantity = ? WHERE product_code = ?
            """, (new_quantity, product_code))
            stock_connection.commit()

            tk.messagebox.showinfo("Başarılı", f"{product_code} kodlu ürüne {quantity_to_add} adet eklendi.")
        else:
            tk.messagebox.showerror("Hata", "Bu ürün bulunamadı!")

        stock_connection.close()


    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if hasattr(self, "tree"):
            self.tree = None

    def add_product(self):
        """Yeni ürünü veritabanına ekler."""
        product_data = {
            field: entry.get() for field, entry in self.form_entries.items()
        }

        if any(value == "" for value in product_data.values()):
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return

        connection = sqlite3.connect("database/stock.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM inventory WHERE product_code = ?", (product_data["product_code"],))
        existing_product = cursor.fetchone()

        if existing_product:
            messagebox.showerror("Hata", "Bu ürün kodu zaten mevcut!")
            connection.close()
            return

        cursor.execute("""
        INSERT INTO inventory (product_code, product_name, category, brand, price, quantity, supplier)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (product_data["product_code"], product_data["product_name"], product_data["category"],
              product_data["brand"], product_data["price"], product_data["quantity"], product_data["supplier"]))
        connection.commit()
        connection.close()

        for entry in self.form_entries.values():
            entry.delete(0, tk.END)

        messagebox.showinfo("Başarı", "Ürün başarıyla eklendi!")

    def get_product_for_update(self):
        """Ürün koduna göre veriyi getirir ve formu doldurur."""
        product_code = self.product_code_entry.get()

        connection = sqlite3.connect("database/stock.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM inventory WHERE product_code = ?", (product_code,))
        product = cursor.fetchone()
        connection.close()

        if product:
            self.clear_update_form()

            fields = [
                ("Ürün Adı", product[1]),
                ("Kategori", product[2]),
                ("Marka", product[3]),
                ("Fiyat", product[4]),
                ("Adet", product[5]),
                ("Tedarikçi", product[6])
            ]

            self.product_name_entry = self.create_form_entry("Ürün Adı", product[1], 0)
            self.category_entry = self.create_form_entry("Kategori", product[2], 1)
            self.brand_entry = self.create_form_entry("Marka", product[3], 2)
            self.price_entry = self.create_form_entry("Fiyat", product[4], 3)
            self.quantity_entry = self.create_form_entry("Adet", product[5], 4)
            self.supplier_entry = self.create_form_entry("Tedarikçi", product[6], 5)

            messagebox.showinfo("Başarı", "Ürün Bilgileri Getirildi!")
        else:
            messagebox.showerror("Hata", "Ürün bulunamadı!")

    def create_form_entry(self, label_text, default_value="", row_index=0):
        """Yeni bir form alanı oluşturur ve grid ile sıralı şekilde yerleştirir."""
        label = tk.Label(self.update_form_frame, text=label_text + " ", font=("Arial", 12), bg="white", anchor="w")
        label.grid(row=row_index, column=0, pady=5, sticky="w")

        entry = tk.Entry(self.update_form_frame, font=("Arial", 12))
        entry.insert(0, default_value)
        entry.grid(row=row_index, column=1, pady=5, sticky="w")

        return entry

    def clear_update_form(self):
        """Güncelleme formunu temizler."""
        for widget in self.update_form_frame.winfo_children():
            widget.destroy()

    def update_product(self):
        """Ürünü günceller."""
        updated_data = {
            "product_code": self.product_code_entry.get(),
            "product_name": self.product_name_entry.get(),
            "category": self.category_entry.get(),
            "brand": self.brand_entry.get(),
            "price": self.price_entry.get(),
            "quantity": self.quantity_entry.get(),
            "supplier": self.supplier_entry.get()
        }

        connection = sqlite3.connect("database/stock.db")
        cursor = connection.cursor()
        cursor.execute("""
        UPDATE inventory
        SET product_name = ?, category = ?, brand = ?, price = ?, quantity = ?, supplier = ?
        WHERE product_code = ?
        """, (updated_data["product_name"], updated_data["category"], updated_data["brand"],
              updated_data["price"], updated_data["quantity"], updated_data["supplier"], updated_data["product_code"]))
        connection.commit()
        connection.close()

        messagebox.showinfo("Başarı", "Ürün başarıyla güncellendi!")

    def delete_product(self):
        """Ürünü siler."""
        product_code = self.product_code_entry.get()

        if not product_code:
            messagebox.showerror("Hata", "Lütfen ürün kodunu girin!")
            return

        connection = sqlite3.connect("database/stock.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM inventory WHERE product_code = ?", (product_code,))
        product = cursor.fetchone()

        if product:
            cursor.execute("DELETE FROM inventory WHERE product_code = ?", (product_code,))
            connection.commit()
            messagebox.showinfo("Başarı", "Ürün başarıyla silindi!")
        else:
            messagebox.showerror("Hata", "Ürün bulunamadı!")

        connection.close()

    def show_order_management(self):
        """Sipariş Yönetimi ekranını gösterir."""
        self.clear_right_frame()

        header_label = tk.Label(
            self.right_frame,
            text="Sipraiş Yönetim Ekranı",
            font=("Arial", 18, "bold"),
            bg="lightblue",
            fg="white"
        )
        header_label.pack(fill="x", pady=10)

        label = tk.Label(
            self.right_frame,
            text="Sipariş Yönetimi ekranında, siparişlerinizi takip edebilir, durumlarını güncelleyebilir veya iptal edebilirsiniz.",
            font=("Arial", 12),
            bg="white",
            fg="gray",
            anchor="w"
        )
        label.pack(pady=10, padx=20, anchor="w")

        top_frame = tk.Frame(self.right_frame)
        top_frame.pack(side="top", fill="x")

        button1 = tk.Button(top_frame, text="Siparişler", command=self.show_order_content_1)
        button1.pack(side="left")

        button2 = tk.Button(top_frame, text="Sipariş Durumu Güncelle", command=self.show_order_content_2)
        button2.pack(side="left")

        button4 = tk.Button(top_frame, text="Sipariş İptal", command=self.show_order_content_3)
        button4.pack(side="left")

        self.content_frame = tk.Frame(self.right_frame, bg="white")
        self.content_frame.pack(side="top", fill="both", expand=True)

        self.show_order_content_1()

    def show_order_content_1(self):
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Siparişler", font=("Arial", 14, "bold"), bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        self.process_orders()

        if not hasattr(self, "tree") or self.tree is None:
            self.create_table_order()

        self.load_data_order()

    def load_data_order(self):
        """Veritabanından tüm verileri Treeview'a yükler."""
        if not hasattr(self, "tree") or self.tree is None:
            print("Treeview widget'ı oluşturulmamış.")
            return

        connection = sqlite3.connect("database/order.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ordertable")
        rows = cursor.fetchall()
        connection.close()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def create_table_order(self):
        """Treeview widget'ını bir kez oluşturur."""
        self.tree = ttk.Treeview(self.content_frame, columns=(
            "order_code", "provider", "status", "order_date", "product_code", "quantity", "is_processed"), show="headings")

        headings = ["order_code", "provider", "status", "order_date", "product_code", "quantity", "is_processed"]
        for heading in headings:
            self.tree.heading(heading, text=heading.replace("_", " ").title())
            self.tree.column(heading, anchor="center", width=120)

        self.tree.pack(fill="both", expand=True)

    def process_orders(self):
        """Durumu 'Preparing' olan siparişleri işleyip stoktan düşer."""
        order_connection = sqlite3.connect("database/order.db")
        stock_connection = sqlite3.connect("database/stock.db")
        order_cursor = order_connection.cursor()
        stock_cursor = stock_connection.cursor()

        order_cursor.execute("""
            SELECT order_code, product_code, quantity 
            FROM ordertable 
            WHERE status = 'Preparing' AND is_processed = 0
        """)
        orders = order_cursor.fetchall()

        for order_code, product_code, quantity in orders:
            stock_cursor.execute("SELECT quantity FROM inventory WHERE product_code = ?", (product_code,))
            stock_data = stock_cursor.fetchone()

            if stock_data and stock_data[0] >= quantity:
                new_quantity = stock_data[0] - quantity
                stock_cursor.execute("UPDATE inventory SET quantity = ? WHERE product_code = ?",
                                     (new_quantity, product_code))
                stock_connection.commit()

                order_cursor.execute("UPDATE ordertable SET is_processed = 1 WHERE order_code = ?", (order_code,))
                order_connection.commit()

        order_connection.close()
        stock_connection.close()

    def show_order_content_2(self):
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Sipariş Durumu Güncelle", font=("Arial", 14, "bold"), bg="white",
                         anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        self.form_frame = tk.Frame(self.content_frame, bg="white")
        self.form_frame.pack(padx=30, pady=0, anchor="w")

        order_code_label = tk.Label(self.form_frame, text="Sipariş Kodu:", font=("Arial", 12), bg="white")
        order_code_label.grid(row=0, column=0, pady=10, sticky="w")

        self.order_code_entry = tk.Entry(self.form_frame, font=("Arial", 12))
        self.order_code_entry.grid(row=0, column=1, pady=10, sticky="w")

        status_label = tk.Label(self.form_frame, text="Yeni Durum:", font=("Arial", 12), bg="white")
        status_label.grid(row=1, column=0, pady=10, sticky="w")

        self.status_var = tk.StringVar()
        status_options = ["Received", "Preparing", "Delivered"]
        self.status_menu = ttk.Combobox(self.form_frame, textvariable=self.status_var, values=status_options,
                                        font=("Arial", 12), state="readonly")
        self.status_menu.grid(row=1, column=1, pady=10, sticky="w")

        update_button = tk.Button(self.form_frame, text="Durumu Güncelle", font=("Arial", 12),
                                  command=self.update_order_status)
        update_button.grid(row=2, column=0, columnspan=2, pady=20, sticky="w")

    def update_order_status(self):
        order_code = self.order_code_entry.get()
        new_status = self.status_var.get()

        if not order_code or not new_status:
            messagebox.showerror("Hata", "Lütfen sipariş kodu ve yeni durumu seçin!")
            return

        connection = sqlite3.connect("database/order.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ordertable WHERE order_code = ?", (order_code,))
        order = cursor.fetchone()

        if not order:
            messagebox.showerror("Hata", "Belirtilen sipariş kodu bulunamadı!")
        else:
            current_status = order[2]

            if new_status == "Delivered" and current_status not in ["Prepared", "Preparing"]:
                messagebox.showerror("Hata",
                                     "Sipariş 'Prepared' veya 'Preparing' durumunda olmadan 'Delivered' olarak güncellenemez!")
            else:
                cursor.execute("UPDATE ordertable SET status = ? WHERE order_code = ?", (new_status, order_code))
                connection.commit()
                messagebox.showinfo("Başarı", f"Sipariş durumu başarıyla '{new_status}' olarak güncellendi!")

        connection.close()

    def show_order_content_3(self):
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Sipariş İptal", font=("Arial", 14, "bold"), bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        self.form_frame = tk.Frame(self.content_frame, bg="white")
        self.form_frame.pack(padx=30, pady=0, anchor="w")

        order_code_label = tk.Label(self.form_frame, text="Sipariş Kodu:", font=("Arial", 12), bg="white")
        order_code_label.grid(row=0, column=0, pady=10, sticky="w")

        self.order_code_entry = tk.Entry(self.form_frame, font=("Arial", 12))
        self.order_code_entry.grid(row=0, column=1, pady=10, sticky="w")

        cancel_button = tk.Button(self.form_frame, text="Siparişi İptal Et", font=("Arial", 12),
                                  command=self.cancel_order)
        cancel_button.grid(row=1, column=0, columnspan=2, pady=20, sticky="w")

    def cancel_order(self):
        order_code = self.order_code_entry.get()

        if not order_code:
            messagebox.showerror("Hata", "Lütfen bir sipariş kodu girin!")
            return

        order_connection = sqlite3.connect("database/order.db")
        stock_connection = sqlite3.connect("database/stock.db")
        order_cursor = order_connection.cursor()
        stock_cursor = stock_connection.cursor()

        order_cursor.execute("SELECT product_code, quantity, is_processed FROM ordertable WHERE order_code = ?",
                             (order_code,))
        order = order_cursor.fetchone()

        if not order:
            messagebox.showerror("Hata", "Belirtilen sipariş kodu bulunamadı!")
            order_connection.close()
            stock_connection.close()
            return

        product_code, quantity, is_processed = order

        if is_processed == 0:
            messagebox.showerror("Hata", "Bu sipariş zaten iptal edilmiş!")
            order_connection.close()
            stock_connection.close()
            return

        order_cursor.execute("UPDATE ordertable SET status = ?, is_processed = ? WHERE order_code = ?",
                             ("Cancel", 0, order_code))
        order_connection.commit()

        stock_cursor.execute("SELECT quantity FROM inventory WHERE product_code = ?", (product_code,))
        stock_data = stock_cursor.fetchone()

        if stock_data:
            new_quantity = stock_data[0] + quantity
            stock_cursor.execute("UPDATE inventory SET quantity = ? WHERE product_code = ?",
                                 (new_quantity, product_code))
            stock_connection.commit()

        messagebox.showinfo("Başarı", "Sipariş başarıyla iptal edildi ve stok güncellendi!")

        order_connection.close()
        stock_connection.close()

    def show_stock_alerts(self):
        """Stok Uyarıları ekranını tablo şeklinde gösterir."""
        self.clear_right_frame()

        header_label = tk.Label(
            self.right_frame,
            text="Stok Uyarı Ekranı",
            font=("Arial", 18, "bold"),
            bg="lightblue",
            fg="white"
        )
        header_label.pack(fill="x", pady=10)

        label = tk.Label(
            self.right_frame,
            text="Stok Uyarı Ekranında, stok seviyeleri belirli bir eşiğin altına düştüğünde uyarılar alabilirsiniz.",
            font=("Arial", 12),
            bg="white",
            fg="gray",
            anchor="w"
        )
        label.pack(pady=10, padx=20, anchor="w")

        label = tk.Label(self.right_frame, text="Stok Uyarıları", font=("Arial", 16), bg="white")
        label.pack(pady=20)

        info_label = tk.Label(self.right_frame, text="Stoğu 20'den az olan ürünler aşşağıda listelenmiştir.",
                              font=("Arial", 10), fg="gray", bg="white")
        info_label.pack(pady=(0, 5))

        connection = sqlite3.connect("database/stock.db")
        cursor = connection.cursor()

        cursor.execute("SELECT product_name, quantity FROM inventory WHERE quantity < 20")
        low_stock_products = cursor.fetchall()

        if low_stock_products:
            tree = ttk.Treeview(self.right_frame, columns=("Product Name", "Quantity"), show="headings")
            tree.pack(pady=10, fill="both", expand=True)

            tree.heading("Product Name", text="Ürün Adı")
            tree.heading("Quantity", text="Stok Miktarı")

            tree.column("Product Name", width=200)
            tree.column("Quantity", width=100)

            for product in low_stock_products:
                tree.insert("", "end", values=product)

        else:
            no_alert_label = tk.Label(self.right_frame, text="Stok yeterli, herhangi bir uyarı yok.",
                                      font=("Arial", 12), bg="white")
            no_alert_label.pack(pady=20)

        connection.close()

    def show_reporting(self):
        """Rapor ekranını gösterir."""
        self.clear_right_frame()

        header_label = tk.Label(
            self.right_frame,
            text="Rapor Ekranı",
            font=("Arial", 18, "bold"),
            bg="lightblue",
            fg="white"
        )
        header_label.pack(fill="x", pady=10)

        label = tk.Label(
            self.right_frame,
            text="Rapor ekranı, satış performansı, gelir analizleri ve ürün bazında raporları görüntülemenizi sağlar.",
            font=("Arial", 12),
            bg="white",
            fg="gray",
            anchor="w"
        )
        label.pack(pady=10, padx=20, anchor="w")

        top_frame = tk.Frame(self.right_frame)
        top_frame.pack(side="top", fill="x")

        button1 = tk.Button(top_frame, text="En çok satan ürün", command=self.show_reporting_1)
        button1.pack(side="left")

        button2 = tk.Button(top_frame, text="Aylık Gelir", command=self.show_reporting_2)
        button2.pack(side="left")

        button3 = tk.Button(top_frame, text="Satış Performansı", command=self.show_reporting_3)
        button3.pack(side="left")

        button4 = tk.Button(top_frame, text="Kategorilere Göre Satış", command=self.show_reporting_4)
        button4.pack(side="left")

        button5 = tk.Button(top_frame, text="Zaman Dilimlerine Göre Satış Analizi", command=self.show_reporting_5)
        button5.pack(side="left")

        button6 = tk.Button(top_frame, text="Ürün Bazında Stok Değeri", command=self.show_reporting_6)
        button6.pack(side="left")


        self.content_frame = tk.Frame(self.right_frame, bg="white")
        self.content_frame.pack(side="top", fill="both", expand=True)

        self.show_reporting_1()

    def show_reporting_1(self):
        """En çok satan ürün raporunu grafik olarak gösterir."""
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="En Çok Satan Ürün Raporu", font=("Arial", 14, "bold"), bg="white",
                         anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        order_connection = sqlite3.connect("database/order.db")
        order_cursor = order_connection.cursor()

        stock_connection = sqlite3.connect("database/stock.db")
        stock_cursor = stock_connection.cursor()

        order_cursor.execute("""
            SELECT product_code, SUM(quantity) AS total_sales
            FROM ordertable
            WHERE status = 'Delivered'
            GROUP BY product_code
            ORDER BY total_sales DESC
        """)
        sold_products = order_cursor.fetchall()

        product_details = []
        for product in sold_products:
            product_code = product[0]

            stock_cursor.execute("""
                SELECT product_name FROM inventory
                WHERE product_code = ?
            """, (product_code,))
            product_info = stock_cursor.fetchone()

            if product_info:
                product_name = product_info[0]
                total_sales = product[1]
                product_details.append((product_name, total_sales))

        order_connection.close()
        stock_connection.close()

        product_names = [x[0] for x in product_details]
        total_sales = [x[1] for x in product_details]

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.barh(product_names, total_sales, color='skyblue')
        ax.set_xlabel("Satılan Adet")
        ax.set_ylabel("Ürün Adı")
        ax.set_title("En Çok Satan Ürün Raporu")

        canvas = FigureCanvasTkAgg(fig, self.content_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.content_frame.update_idletasks()
        canvas.draw()

        plt.close(fig)

    def show_reporting_2(self):
        """Bu ay satılan ürün raporunu ve toplam geliri çizer."""
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Bu Ay Satılan Ürünler Raporu", font=("Arial", 14, "bold"),
                         bg="white",
                         anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        current_month = datetime.now().strftime("%Y-%m")

        order_connection = sqlite3.connect("database/order.db")
        order_cursor = order_connection.cursor()

        stock_connection = sqlite3.connect("database/stock.db")
        stock_cursor = stock_connection.cursor()

        order_cursor.execute("""
            SELECT product_code, SUM(quantity) AS total_quantity
            FROM ordertable
            WHERE status = 'Delivered' AND strftime('%Y-%m', order_date) = ?
            GROUP BY product_code
        """, (current_month,))
        sold_products = order_cursor.fetchall()

        product_details = []
        total_quantity = 0
        total_income = 0

        for product in sold_products:
            product_code, quantity_sold = product

            stock_cursor.execute("""
                SELECT product_name, price FROM inventory
                WHERE product_code = ?
            """, (product_code,))
            product_info = stock_cursor.fetchone()

            if product_info:
                product_name, price = product_info
                income = quantity_sold * price
                total_quantity += quantity_sold
                total_income += income
                product_details.append((product_name, quantity_sold, income))

        order_connection.close()
        stock_connection.close()

        product_names = [x[0] for x in product_details]
        quantities = [x[1] for x in product_details]
        revenues = [x[2] for x in product_details]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(product_names, revenues, color='skyblue')
        ax.set_title(f"Bu Ay Satılan Ürünler - {current_month}", fontsize=16)
        ax.set_xlabel("Gelir (TL)", fontsize=12)
        ax.set_ylabel("Ürün Adı", fontsize=12)

        canvas = FigureCanvasTkAgg(fig, self.content_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
        plt.close(fig)

        summary_label = tk.Label(
            self.content_frame,
            text=f"Toplam Satılan Adet: {total_quantity}, Toplam Gelir: {total_income:.2f} TL",
            font=("Arial", 12, "bold"), bg="white", anchor="w"
        )
        summary_label.pack(padx=30, pady=20, anchor="w")

    def show_reporting_3(self):
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Satış Performansı Raporu", font=("Arial", 14, "bold"), bg="white",
                         anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        order_connection = sqlite3.connect("database/order.db")
        order_cursor = order_connection.cursor()

        stock_connection = sqlite3.connect("database/stock.db")
        stock_cursor = stock_connection.cursor()

        order_cursor.execute("""
            SELECT product_code, SUM(quantity) AS total_quantity
            FROM ordertable
            WHERE status = 'Delivered'
            GROUP BY product_code
        """)
        sold_products = order_cursor.fetchall()

        product_sales = []
        for product in sold_products:
            product_code = product[0]
            quantity_sold = product[1]

            stock_cursor.execute("""
                SELECT product_name, price FROM inventory
                WHERE product_code = ?
            """, (product_code,))
            product_info = stock_cursor.fetchone()

            if product_info:
                product_name, price = product_info
                total_revenue = quantity_sold * price
                product_sales.append((product_name, total_revenue))

        order_connection.close()
        stock_connection.close()

        product_sales.sort(key=lambda x: x[1], reverse=True)

        product_names = [x[0] for x in product_sales]
        revenues = [x[1] for x in product_sales]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(product_names, revenues, color='skyblue')
        ax.set_xlabel("Gelir (TL)")
        ax.set_ylabel("Ürün Adı")
        ax.set_title("Satış Performansı Raporu")

        canvas = FigureCanvasTkAgg(fig, self.content_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
        plt.close(fig)

    def show_reporting_4(self):
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Kategorilere Göre Satış Raporu", font=("Arial", 14, "bold"),
                         bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        order_connection = sqlite3.connect("database/order.db")
        order_cursor = order_connection.cursor()

        stock_connection = sqlite3.connect("database/stock.db")
        stock_cursor = stock_connection.cursor()

        order_cursor.execute("""
            SELECT product_code, SUM(quantity) AS total_quantity
            FROM ordertable
            WHERE status = 'Delivered'
            GROUP BY product_code
        """)
        sold_products = order_cursor.fetchall()

        category_sales = {}
        for product in sold_products:
            product_code = product[0]
            quantity_sold = product[1]

            stock_cursor.execute("""
                SELECT product_name, price, category FROM inventory
                WHERE product_code = ?
            """, (product_code,))
            product_info = stock_cursor.fetchone()

            if product_info:
                product_name, price, category = product_info
                total_revenue = quantity_sold * price

                if category not in category_sales:
                    category_sales[category] = 0
                category_sales[category] += total_revenue

        order_connection.close()
        stock_connection.close()

        categories = list(category_sales.keys())
        revenues = list(category_sales.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(categories, revenues, color='lightcoral')
        ax.set_xlabel("Gelir (TL)")
        ax.set_ylabel("Kategori")
        ax.set_title("Kategorilere Göre Satış Raporu")

        canvas = FigureCanvasTkAgg(fig, self.content_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
        plt.close(fig)

    def show_reporting_5(self):
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Zaman Dilimlerine Göre Satış Analizi", font=("Arial", 14, "bold"),
                         bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        order_connection = sqlite3.connect("database/order.db")
        order_cursor = order_connection.cursor()

        stock_connection = sqlite3.connect("database/stock.db")
        stock_cursor = stock_connection.cursor()

        order_cursor.execute("""
            SELECT order_date, product_code, quantity
            FROM ordertable
            WHERE status = 'Delivered'
        """)
        orders = order_cursor.fetchall()

        monthly_sales = {}

        for order in orders:
            order_date = order[0]  # sipariş tarihi
            product_code = order[1]  # ürün kodu
            quantity = order[2]  # satılan miktar

            order_month = datetime.strptime(order_date, "%Y-%m-%d").strftime("%Y-%m")

            stock_cursor.execute("""
                SELECT price FROM inventory
                WHERE product_code = ?
            """, (product_code,))
            product_price = stock_cursor.fetchone()

            if product_price:
                total_revenue = quantity * product_price[0]

                if order_month not in monthly_sales:
                    monthly_sales[order_month] = 0
                monthly_sales[order_month] += total_revenue

        order_connection.close()
        stock_connection.close()

        months = list(monthly_sales.keys())
        revenues = list(monthly_sales.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(months, revenues, marker='o', color='skyblue', linestyle='-', linewidth=2, markersize=6)
        ax.set_xlabel("Ay")
        ax.set_ylabel("Gelir (TL)")
        ax.set_title("Zaman Dilimlerine Göre Satış Analizi")

        canvas = FigureCanvasTkAgg(fig, self.content_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
        plt.close(fig)

    def show_reporting_6(self):
        self.clear_content_frame()

        label = tk.Label(self.content_frame, text="Ürün Bazında Stok Değeri Raporu", font=("Arial", 14, "bold"),
                         bg="white", anchor="w")
        label.pack(padx=30, pady=20, anchor="w")

        stock_connection = sqlite3.connect("database/stock.db")
        stock_cursor = stock_connection.cursor()

        stock_cursor.execute("""
            SELECT product_name, price, quantity
            FROM inventory
        """)
        products = stock_cursor.fetchall()

        product_names = []
        stock_values = []

        for product in products:
            product_name = product[0]
            price_str = product[1]
            quantity_str = product[2]

            try:
                price = float(price_str) if price_str else 0
            except ValueError:
                price = 0

            try:
                quantity = int(quantity_str) if quantity_str else 0
            except ValueError:
                quantity = 0

            stock_value = price * quantity

            product_names.append(product_name)
            stock_values.append(stock_value)

        stock_connection.close()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(product_names, stock_values, color='lightblue')
        ax.set_xlabel("Stok Değeri (TL)")
        ax.set_ylabel("Ürün Adı")
        ax.set_title("Ürün Bazında Stok Değeri Raporu")

        canvas = FigureCanvasTkAgg(fig, self.content_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()
        plt.close(fig)

    def show_supplier_customer_management(self):
        """Tedarikçi ve Müşteri Yönetimi ekranını gösterir."""
        self.clear_right_frame()

        header_label = tk.Label(
            self.right_frame, text="Tedarikçi ve Müşteri Yönetimi", font=("Arial", 18, "bold"), bg="lightblue",
            fg="white"
        )
        header_label.pack(fill="x", pady=10)

        content_frame = tk.Frame(self.right_frame, bg="white", relief="groove", borderwidth=2)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        supplier_frame = tk.LabelFrame(content_frame, text="Tedarikçi Bilgileri", font=("Arial", 12, "bold"),
                                       bg="white")
        supplier_frame.pack(fill="x", padx=20, pady=10)

        connection = sqlite3.connect("database/stock.db")
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT supplier FROM inventory")
        suppliers = cursor.fetchall()

        supplier_listbox = tk.Listbox(supplier_frame, height=5, font=("Arial", 12))
        supplier_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for supplier in suppliers:
            supplier_listbox.insert(tk.END, supplier[0])

        customer_frame = tk.LabelFrame(content_frame, text="Müşteri Bilgileri", font=("Arial", 12, "bold"), bg="white")
        customer_frame.pack(fill="x", padx=20, pady=10)

        example_customers = [
            ("Müşteri Adı: Ali Veli", "Telefon: 123-456-7890"),
            ("Müşteri Adı: Ayşe Fatma", "Telefon: 987-654-3210"),
        ]

        customer_listbox = tk.Listbox(customer_frame, height=5, font=("Arial", 12))
        customer_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for customer in example_customers:
            customer_listbox.insert(tk.END, f"{customer[0]} | {customer[1]}")

        add_supplier_frame = tk.LabelFrame(content_frame, text="Yeni Tedarikçi Ekle", font=("Arial", 12, "bold"),
                                           bg="white")
        add_supplier_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(add_supplier_frame, text="Tedarikçi Adı:", font=("Arial", 12), bg="white").pack(anchor="w", padx=10,
                                                                                                 pady=5)
        supplier_name_entry = tk.Entry(add_supplier_frame, font=("Arial", 12))
        supplier_name_entry.pack(fill="x", padx=10, pady=5)

        tk.Button(
            add_supplier_frame,
            text="Ekle",
            font=("Arial", 12, "bold"),
            command=lambda: self.add_supplier(supplier_name_entry.get()),
        ).pack(pady=10)

        add_customer_frame = tk.LabelFrame(content_frame, text="Yeni Müşteri Ekle", font=("Arial", 12, "bold"),
                                           bg="white")
        add_customer_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(add_customer_frame, text="Müşteri Adı:", font=("Arial", 12), bg="white").pack(anchor="w", padx=10,
                                                                                               pady=5)
        customer_name_entry = tk.Entry(add_customer_frame, font=("Arial", 12))
        customer_name_entry.pack(fill="x", padx=10, pady=5)

        tk.Label(add_customer_frame, text="Telefon:", font=("Arial", 12), bg="white").pack(anchor="w", padx=10, pady=5)
        customer_phone_entry = tk.Entry(add_customer_frame, font=("Arial", 12))
        customer_phone_entry.pack(fill="x", padx=10, pady=5)

        tk.Button(
            add_customer_frame,
            text="Ekle",
            font=("Arial", 12, "bold"),
            command=lambda: self.add_customer(customer_name_entry.get(), customer_phone_entry.get()),
        ).pack(pady=10)

        connection.close()

    def add_supplier(self, supplier_name):
        """Yeni bir tedarikçi ekler."""
        if supplier_name.strip():
            connection = sqlite3.connect("database/stock.db")
            cursor = connection.cursor()
            cursor.execute("INSERT INTO inventory (supplier) VALUES (?)", (supplier_name,))
            connection.commit()
            connection.close()
            messagebox.showinfo("Başarılı", "Yeni tedarikçi başarıyla eklendi!")
        else:
            messagebox.showerror("Hata", "Tedarikçi adı boş bırakılamaz!")

    def add_customer(self, customer_name, customer_phone):
        """Yeni bir müşteri ekler (örnek veritabanıyla entegre edilebilir)."""
        if customer_name.strip() and customer_phone.strip():
            messagebox.showinfo("Başarılı", "Yeni müşteri başarıyla eklendi!")
        else:
            messagebox.showerror("Hata", "Müşteri adı ve telefon boş bırakılamaz!")

    def exit_app(self):
        """Uygulamadan çıkış yapar."""
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = StockManagementApp(root)
    root.mainloop()
