import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import re


# Initialize the database
def initialize_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       product_id TEXT,
                       product_name TEXT,
                       quantity INTEGER,
                       price REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (username TEXT PRIMARY KEY,
                       password TEXT,
                       role TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       product_id TEXT,
                       quantity INTEGER,
                       total_price REAL,
                       sale_date TEXT)''')
    conn.commit()
    conn.close()


# Login screen
def login():
    username = entry_username.get()
    password = entry_password.get()

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_role = user[2]
        main_menu(user_role)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")


# GUI for Main Menu (with different user roles)
def main_menu(user_role):
    menu_window = tk.Toplevel(root)
    menu_window.title("Main Menu")

    menu_frame = tk.Frame(menu_window, padx=20, pady=20)
    menu_frame.pack(padx=20, pady=20)

    # Styling the buttons
    button_style = ttk.Style()
    button_style.configure('TButton', font=("Arial", 14), padding=10)

    if user_role == "admin":
        ttk.Button(menu_frame, text="Add Product", command=add_product).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="View Products", command=view_products).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="Edit Product", command=edit_product).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="Delete Product", command=delete_product).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="Manage Users", command=manage_users).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="Generate Sales Summary", command=sales_summary).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="View Daily Sales", command=daily_sales).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="View Monthly Sales", command=monthly_sales).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="View Annual Sales", command=annual_sales).pack(pady=10, fill=tk.X)
        ttk.Button(menu_frame, text="View Low-Stock Alerts", command=low_stock_alerts).pack(pady=10, fill=tk.X)

    ttk.Button(menu_frame, text="Log Sale", command=log_sale).pack(pady=10, fill=tk.X)
    ttk.Button(menu_frame, text="Logout", command=menu_window.destroy).pack(pady=10, fill=tk.X)


# GUI for adding a product
def add_product():
    def save_product():
        product_id = entry_product_id.get()
        product_name = entry_product_name.get()
        try:
            quantity = int(entry_quantity.get())
            price = float(entry_price.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity and price must be numeric values.")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (product_id, product_name, quantity, price) VALUES (?, ?, ?, ?)",
                       (product_id, product_name, quantity, price))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Product added successfully.")
        add_window.destroy()

    add_window = tk.Toplevel(root)
    add_window.title("Add Product")

    form_frame = tk.Frame(add_window, padx=20, pady=20)
    form_frame.pack(padx=20, pady=20)

    tk.Label(form_frame, text="Product ID:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_product_id = tk.Entry(form_frame, font=("Arial", 12))
    entry_product_id.grid(row=0, column=1, pady=5)

    tk.Label(form_frame, text="Product Name:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
    entry_product_name = tk.Entry(form_frame, font=("Arial", 12))
    entry_product_name.grid(row=1, column=1, pady=5)

    tk.Label(form_frame, text="Quantity:", font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W, pady=5)
    entry_quantity = tk.Entry(form_frame, font=("Arial", 12))
    entry_quantity.grid(row=2, column=1, pady=5)

    tk.Label(form_frame, text="Price:", font=("Arial", 12)).grid(row=3, column=0, sticky=tk.W, pady=5)
    entry_price = tk.Entry(form_frame, font=("Arial", 12))
    entry_price.grid(row=3, column=1, pady=5)

    ttk.Button(form_frame, text="Save", command=save_product).grid(row=4, columnspan=2, pady=10)

# View Products GUI
def view_products():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    view_window = tk.Toplevel(root)
    view_window.title("View Products")

    form_frame = tk.Frame(view_window, padx=20, pady=20)
    form_frame.pack(padx=20, pady=20)

    if products:
        for product in products:
            tk.Label(form_frame, text=f"Product ID: {product[1]}, Name: {product[2]}, Quantity: {product[3]}, Price: ৳{product[4]}", font=("Arial", 12)).pack(pady=5)
    else:
        tk.Label(form_frame, text="No products available.", font=("Arial", 12)).pack(pady=5)


# GUI for editing a product
def edit_product():
    def update_product():
        product_id = entry_product_id.get()
        new_quantity = entry_quantity.get()
        new_price = entry_price.get()

        try:
            if new_quantity:
                new_quantity = int(new_quantity)
            if new_price:
                new_price = float(new_price)
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity and price must be numeric values.")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        updates = []
        if new_quantity is not None:
            updates.append(f"quantity={new_quantity}")
        if new_price is not None:
            updates.append(f"price={new_price}")

        if updates:
            update_query = f"UPDATE products SET {', '.join(updates)} WHERE product_id=?"
            cursor.execute(update_query, (product_id,))
            conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Product updated successfully.")
        edit_window.destroy()

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Product")

    form_frame = tk.Frame(edit_window, padx=20, pady=20)
    form_frame.pack(padx=20, pady=20)

    tk.Label(form_frame, text="Product ID:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_product_id = tk.Entry(form_frame, font=("Arial", 12))
    entry_product_id.grid(row=0, column=1, pady=5)

    tk.Label(form_frame, text="New Quantity (Leave empty if not changing):", font=("Arial", 12)).grid(row=1, column=0,
                                                                                                      sticky=tk.W,
                                                                                                      pady=5)
    entry_quantity = tk.Entry(form_frame, font=("Arial", 12))
    entry_quantity.grid(row=1, column=1, pady=5)

    tk.Label(form_frame, text="New Price (Leave empty if not changing):", font=("Arial", 12)).grid(row=2, column=0,
                                                                                                   sticky=tk.W, pady=5)
    entry_price = tk.Entry(form_frame, font=("Arial", 12))
    entry_price.grid(row=2, column=1, pady=5)

    ttk.Button(form_frame, text="Update", command=update_product).grid(row=3, columnspan=2, pady=10)


# GUI for deleting a product
def delete_product():
    def remove_product():
        product_id = entry_product_id.get()
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id=?", (product_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Product deleted successfully.")
        delete_window.destroy()

    delete_window = tk.Toplevel(root)
    delete_window.title("Delete Product")

    form_frame = tk.Frame(delete_window, padx=20, pady=20)
    form_frame.pack(padx=20, pady=20)

    tk.Label(form_frame, text="Product ID:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_product_id = tk.Entry(form_frame, font=("Arial", 12))
    entry_product_id.grid(row=0, column=1, pady=5)

    ttk.Button(form_frame, text="Delete", command=remove_product).grid(row=1, columnspan=2, pady=10)


# Manage Users
def manage_users():
    def add_user():
        username = entry_username.get()
        password = entry_password.get()
        role = role_var.get()

        if not re.match(r"^[a-zA-Z0-9_]{3,15}$", username):
            messagebox.showerror("Invalid Input", "Username must be 3-15 alphanumeric characters.")
            return
        if len(password) < 6:
            messagebox.showerror("Invalid Input", "Password must be at least 6 characters long.")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "User added successfully.")
        manage_window.destroy()

    def view_users():
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()

        view_window = tk.Toplevel(root)
        view_window.title("View Users")

        if users:
            for user in users:
                tk.Label(view_window, text=f"Username: {user[0]}, Role: {user[2]}", font=("Arial", 12)).pack(pady=5)
        else:
            tk.Label(view_window, text="No users found.", font=("Arial", 12)).pack(pady=5)

    manage_window = tk.Toplevel(root)
    manage_window.title("Manage Users")

    form_frame = tk.Frame(manage_window, padx=20, pady=20)
    form_frame.pack(padx=20, pady=20)

    tk.Label(form_frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_username = tk.Entry(form_frame, font=("Arial", 12))
    entry_username.grid(row=0, column=1, pady=5)

    tk.Label(form_frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
    entry_password = tk.Entry(form_frame, show="*", font=("Arial", 12))
    entry_password.grid(row=1, column=1, pady=5)

    tk.Label(form_frame, text="Role:", font=("Arial", 12)).grid(row=2, column=0, sticky=tk.W, pady=5)
    role_var = tk.StringVar(value="sales")
    tk.Radiobutton(form_frame, text="Admin", variable=role_var, value="admin", font=("Arial", 12)).grid(row=2, column=1,
                                                                                                        pady=5,
                                                                                                        sticky=tk.W)
    tk.Radiobutton(form_frame, text="Sales", variable=role_var, value="sales", font=("Arial", 12)).grid(row=2, column=1,
                                                                                                        pady=5)

    ttk.Button(form_frame, text="Add User", command=add_user).grid(row=3, columnspan=2, pady=10)
    ttk.Button(form_frame, text="View Users", command=view_users).grid(row=4, columnspan=2, pady=10)


# Low-Stock Alerts
def low_stock_alerts():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity < 10")
    low_stock_items = cursor.fetchall()
    conn.close()

    alert_window = tk.Toplevel(root)
    alert_window.title("Low-Stock Alerts")

    if low_stock_items:
        for item in low_stock_items:
            tk.Label(alert_window, text=f"{item[2]} (ID: {item[1]}) has only {item[3]} units left.",
                     font=("Arial", 12)).pack(pady=5)
    else:
        tk.Label(alert_window, text="No low-stock items.", font=("Arial", 12)).pack(pady=5)


# Log a Sale
def log_sale():
    def save_sale():
        product_id = entry_sale_product_id.get()
        try:
            quantity = int(entry_sale_quantity.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be a numeric value.")
            return

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT quantity, price FROM products WHERE product_id=?", (product_id,))
        product = cursor.fetchone()

        if not product:
            messagebox.showerror("Error", "Product not found.")
            return

        stock_quantity, price = product
        if stock_quantity < quantity:
            messagebox.showerror("Error", "Not enough stock.")
            return

        new_quantity = stock_quantity - quantity
        cursor.execute("UPDATE products SET quantity=? WHERE product_id=?", (new_quantity, product_id))

        total_price = quantity * price
        cursor.execute("INSERT INTO sales (product_id, quantity, total_price, sale_date) VALUES (?, ?, ?, ?)",
                       (product_id, quantity, total_price, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Sale logged successfully.")
        sale_window.destroy()

    sale_window = tk.Toplevel(root)
    sale_window.title("Log Sale")

    form_frame = tk.Frame(sale_window, padx=20, pady=20)
    form_frame.pack(padx=20, pady=20)

    tk.Label(form_frame, text="Product ID:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
    entry_sale_product_id = tk.Entry(form_frame, font=("Arial", 12))
    entry_sale_product_id.grid(row=0, column=1, pady=5)

    tk.Label(form_frame, text="Quantity:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
    entry_sale_quantity = tk.Entry(form_frame, font=("Arial", 12))
    entry_sale_quantity.grid(row=1, column=1, pady=5)

    ttk.Button(form_frame, text="Save Sale", command=save_sale).grid(row=2, columnspan=2, pady=10)


# Sales Summary
def sales_summary():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, SUM(quantity), SUM(total_price) FROM sales GROUP BY product_id")
    sales_data = cursor.fetchall()
    conn.close()

    summary_window = tk.Toplevel(root)
    summary_window.title("Sales Summary")

    if sales_data:
        for sale in sales_data:
            tk.Label(summary_window, text=f"Product ID: {sale[0]}, Total Sold: {sale[1]}, Total Sales: ৳{sale[2]}",
                     font=("Arial", 12)).pack(pady=5)
    else:
        tk.Label(summary_window, text="No sales data found.", font=("Arial", 12)).pack(pady=5)


# Daily Sales Report
def daily_sales():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product_id, SUM(quantity), SUM(total_price) FROM sales WHERE sale_date LIKE ? GROUP BY product_id",
        (f"{today}%",))
    daily_sales_data = cursor.fetchall()
    conn.close()

    daily_sales_window = tk.Toplevel(root)
    daily_sales_window.title("Daily Sales")

    if daily_sales_data:
        for sale in daily_sales_data:
            tk.Label(daily_sales_window, text=f"Product ID: {sale[0]}, Total Sold: {sale[1]}, Total Sales: ৳{sale[2]}",
                     font=("Arial", 12)).pack(pady=5)
    else:
        tk.Label(daily_sales_window, text="No sales data for today.", font=("Arial", 12)).pack(pady=5)


# Monthly Sales Report
def monthly_sales():
    first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product_id, SUM(quantity), SUM(total_price) FROM sales WHERE sale_date BETWEEN ? AND ? GROUP BY product_id",
        (first_day, datetime.now().strftime('%Y-%m-%d')))
    monthly_sales_data = cursor.fetchall()
    conn.close()

    monthly_sales_window = tk.Toplevel(root)
    monthly_sales_window.title("Monthly Sales")

    if monthly_sales_data:
        for sale in monthly_sales_data:
            tk.Label(monthly_sales_window,
                     text=f"Product ID: {sale[0]}, Total Sold: {sale[1]}, Total Sales: ৳{sale[2]}",
                     font=("Arial", 12)).pack(pady=5)
    else:
        tk.Label(monthly_sales_window, text="No sales data for this month.", font=("Arial", 12)).pack(pady=5)


# Annual Sales Report
def annual_sales():
    first_day = datetime.now().replace(month=1, day=1).strftime('%Y-%m-%d')
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product_id, SUM(quantity), SUM(total_price) FROM sales WHERE sale_date BETWEEN ? AND ? GROUP BY product_id",
        (first_day, datetime.now().strftime('%Y-%m-%d')))
    annual_sales_data = cursor.fetchall()
    conn.close()

    annual_sales_window = tk.Toplevel(root)
    annual_sales_window.title("Annual Sales")

    if annual_sales_data:
        for sale in annual_sales_data:
            tk.Label(annual_sales_window, text=f"Product ID: {sale[0]}, Total Sold: {sale[1]}, Total Sales: ৳{sale[2]}",
                     font=("Arial", 12)).pack(pady=5)
    else:
        tk.Label(annual_sales_window, text="No sales data for this year.", font=("Arial", 12)).pack(pady=5)


# Main application
root = tk.Tk()
root.title("Inventory Management System")

initialize_db()

login_frame = tk.Frame(root, padx=20, pady=20)
login_frame.pack(padx=20, pady=20)

tk.Label(login_frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
entry_username = tk.Entry(login_frame, font=("Arial", 12))
entry_username.grid(row=0, column=1, pady=5)

tk.Label(login_frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
entry_password = tk.Entry(login_frame, show="*", font=("Arial", 12))
entry_password.grid(row=1, column=1, pady=5)

ttk.Button(login_frame, text="Login", command=login).grid(row=2, columnspan=2, pady=10)

root.mainloop()
