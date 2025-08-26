import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import hashlib

# Database Initialization and Setup
def create_db():
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            expiry_date TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (medicine_id) REFERENCES medicines (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
    if cursor.fetchone()[0] == 0:
        # Hash the password for security
        hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES ("admin", ?, "admin")
        ''', (hashed_password,))
    
    conn.commit()
    conn.close()

create_db()

# Global Variable for Logged-In User
logged_in_user = None

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User Authentication
class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Pharmacy Management System - Login")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.eval('tk::PlaceWindow . center')
        
        # Create main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Username
        ttk.Label(main_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_username = ttk.Entry(main_frame, width=25)
        self.entry_username.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.entry_username.focus()
        
        # Password
        ttk.Label(main_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_password = ttk.Entry(main_frame, width=25, show="*")
        self.entry_password.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Login button
        self.btn_login = ttk.Button(main_frame, text="Login", command=self.check_login)
        self.btn_login.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Bind Enter key to login
        self.entry_password.bind('<Return>', lambda event: self.check_login())
        
        self.window.mainloop()
    
    def check_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password")
            return
        
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[2] == hash_password(password):
            global logged_in_user
            logged_in_user = user
            messagebox.showinfo("Login Success", f"Welcome, {user[1]}!")
            self.window.destroy()
            MainWindow()
        else:
            messagebox.showwarning("Login Failed", "Invalid username or password")
            self.entry_password.delete(0, tk.END)

# Main Application Window
class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Pharmacy Management System")
        self.window.geometry("1000x700")
        self.window.state('zoomed')  # Start maximized
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Medicine Management Frame
        self.medicine_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.medicine_frame, text="Medicine Management")
        
        # Sales Frame
        self.sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_frame, text="Sales")
        
        # Reports Frame
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Reports")
        
        # User Management Frame (only for admin)
        if logged_in_user[3] == 'admin':
            self.users_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.users_frame, text="User Management")
            self.setup_user_management()
        
        # Setup each section
        self.setup_medicine_management()
        self.setup_sales_management()
        self.setup_reports()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set(f"Logged in as: {logged_in_user[1]} ({logged_in_user[3]})")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.window.mainloop()
    
    def setup_medicine_management(self):
        # Left frame for form
        left_frame = ttk.LabelFrame(self.medicine_frame, text="Add/Edit Medicine", padding="10")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right frame for medicine list
        right_frame = ttk.LabelFrame(self.medicine_frame, text="Medicine List", padding="10")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.medicine_frame.columnconfigure(0, weight=1)
        self.medicine_frame.columnconfigure(1, weight=2)
        self.medicine_frame.rowconfigure(0, weight=1)
        
        # Form elements
        ttk.Label(left_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_name = ttk.Entry(left_frame, width=25)
        self.entry_name.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(left_frame, text="Quantity:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_quantity = ttk.Entry(left_frame, width=25)
        self.entry_quantity.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(left_frame, text="Price:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_price = ttk.Entry(left_frame, width=25)
        self.entry_price.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(left_frame, text="Expiry Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_expiry = ttk.Entry(left_frame, width=25)
        self.entry_expiry.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Add Medicine", command=self.add_medicine).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update Medicine", command=self.update_medicine).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Medicine", command=self.delete_medicine).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_medicine_form).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.entry_search = ttk.Entry(search_frame, width=20)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_medicines).pack(side=tk.LEFT)
        
        # Medicine list with scrollbar
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('id', 'name', 'quantity', 'price', 'expiry_date')
        self.medicine_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.medicine_tree.heading('id', text='ID')
        self.medicine_tree.heading('name', text='Name')
        self.medicine_tree.heading('quantity', text='Quantity')
        self.medicine_tree.heading('price', text='Price')
        self.medicine_tree.heading('expiry_date', text='Expiry Date')
        
        # Define columns
        self.medicine_tree.column('id', width=50, anchor=tk.CENTER)
        self.medicine_tree.column('name', width=150, anchor=tk.W)
        self.medicine_tree.column('quantity', width=80, anchor=tk.CENTER)
        self.medicine_tree.column('price', width=80, anchor=tk.CENTER)
        self.medicine_tree.column('expiry_date', width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.medicine_tree.yview)
        self.medicine_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.medicine_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.medicine_tree.bind('<<TreeviewSelect>>', self.on_medicine_select)
        
        # Load medicine data
        self.load_medicines()
    
    def setup_sales_management(self):
        # Left frame for sales form
        left_frame = ttk.LabelFrame(self.sales_frame, text="Record Sale", padding="10")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right frame for sales history
        right_frame = ttk.LabelFrame(self.sales_frame, text="Sales History", padding="10")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.sales_frame.columnconfigure(0, weight=1)
        self.sales_frame.columnconfigure(1, weight=2)
        self.sales_frame.rowconfigure(0, weight=1)
        
        # Sales form elements
        ttk.Label(left_frame, text="Medicine:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sale_medicine_var = tk.StringVar()
        self.sale_medicine_combo = ttk.Combobox(left_frame, textvariable=self.sale_medicine_var, state="readonly")
        self.sale_medicine_combo.grid(row=0, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        self.sale_medicine_combo.bind('<<ComboboxSelected>>', self.on_medicine_select_sale)
        
        ttk.Label(left_frame, text="Available Quantity:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.available_qty_var = tk.StringVar()
        ttk.Label(left_frame, textvariable=self.available_qty_var).grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(left_frame, text="Price per Unit:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.unit_price_var = tk.StringVar()
        ttk.Label(left_frame, textvariable=self.unit_price_var).grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(left_frame, text="Quantity to Sell:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.sale_qty_entry = ttk.Entry(left_frame, width=25)
        self.sale_qty_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(left_frame, text="Total Amount:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.total_amount_var = tk.StringVar()
        ttk.Label(left_frame, textvariable=self.total_amount_var).grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Record Sale", command=self.record_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Calculate Total", command=self.calculate_total).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_sale_form).pack(side=tk.LEFT, padx=5)
        
        # Sales history with scrollbar
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('id', 'medicine', 'quantity', 'total_price', 'date')
        self.sales_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.sales_tree.heading('id', text='ID')
        self.sales_tree.heading('medicine', text='Medicine')
        self.sales_tree.heading('quantity', text='Quantity')
        self.sales_tree.heading('total_price', text='Total Price')
        self.sales_tree.heading('date', text='Date')
        
        # Define columns
        self.sales_tree.column('id', width=50, anchor=tk.CENTER)
        self.sales_tree.column('medicine', width=150, anchor=tk.W)
        self.sales_tree.column('quantity', width=80, anchor=tk.CENTER)
        self.sales_tree.column('total_price', width=100, anchor=tk.CENTER)
        self.sales_tree.column('date', width=120, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Load sales data
        self.load_sales()
        self.load_medicine_combo()
    
    def setup_reports(self):
        # Frame for report controls
        controls_frame = ttk.LabelFrame(self.reports_frame, text="Report Options", padding="10")
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Frame for report display
        report_frame = ttk.LabelFrame(self.reports_frame, text="Report Results", padding="10")
        report_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.reports_frame.columnconfigure(0, weight=1)
        self.reports_frame.rowconfigure(1, weight=1)
        
        # Report type selection
        ttk.Label(controls_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.report_type_var = tk.StringVar(value="sales_summary")
        report_combo = ttk.Combobox(controls_frame, textvariable=self.report_type_var, state="readonly")
        report_combo['values'] = ('sales_summary', 'inventory_status', 'expiry_alerts')
        report_combo.grid(row=0, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        
        # Period selection
        ttk.Label(controls_frame, text="Period:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.period_var = tk.StringVar(value="daily")
        period_combo = ttk.Combobox(controls_frame, textvariable=self.period_var, state="readonly")
        period_combo['values'] = ('daily', 'weekly', 'monthly')
        period_combo.grid(row=1, column=1, pady=5, padx=(10, 0), sticky=tk.W)
        
        # Generate report button
        ttk.Button(controls_frame, text="Generate Report", command=self.generate_report).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Report text area
        self.report_text = tk.Text(report_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def setup_user_management(self):
        # Only for admin users
        if logged_in_user[3] != 'admin':
            return
            
        # Left frame for user form
        left_frame = ttk.LabelFrame(self.users_frame, text="Add/Edit User", padding="10")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right frame for user list
        right_frame = ttk.LabelFrame(self.users_frame, text="User List", padding="10")
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.users_frame.columnconfigure(0, weight=1)
        self.users_frame.columnconfigure(1, weight=2)
        self.users_frame.rowconfigure(0, weight=1)
        
        # Form elements
        ttk.Label(left_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_username = ttk.Entry(left_frame, width=25)
        self.user_username.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(left_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_password = ttk.Entry(left_frame, width=25, show="*")
        self.user_password.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(left_frame, text="Role:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.user_role_var = tk.StringVar(value="staff")
        role_combo = ttk.Combobox(left_frame, textvariable=self.user_role_var, state="readonly", width=22)
        role_combo['values'] = ('admin', 'staff')
        role_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Add User", command=self.add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update User", command=self.update_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete User", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_user_form).pack(side=tk.LEFT, padx=5)
        
        # User list with scrollbar
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('id', 'username', 'role')
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Define headings
        self.user_tree.heading('id', text='ID')
        self.user_tree.heading('username', text='Username')
        self.user_tree.heading('role', text='Role')
        
        # Define columns
        self.user_tree.column('id', width=50, anchor=tk.CENTER)
        self.user_tree.column('username', width=150, anchor=tk.W)
        self.user_tree.column('role', width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.user_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # Load user data
        self.load_users()
    
    # Database operations
    def connect_db(self):
        return sqlite3.connect('pharmacy.db')
    
    # Medicine management methods
    def load_medicines(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM medicines ORDER BY name')
        medicines = cursor.fetchall()
        conn.close()
        
        # Clear existing data
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)
        
        # Add data to treeview
        for medicine in medicines:
            self.medicine_tree.insert('', 'end', values=medicine)
    
    def add_medicine(self):
        name = self.entry_name.get()
        quantity = self.entry_quantity.get()
        price = self.entry_price.get()
        expiry_date = self.entry_expiry.get()
        
        if not all([name, quantity, price, expiry_date]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return
        
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showwarning("Input Error", "Quantity must be integer and Price must be number")
            return
        
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medicines (name, quantity, price, expiry_date)
            VALUES (?, ?, ?, ?)
        ''', (name, quantity, price, expiry_date))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Medicine added successfully")
        self.clear_medicine_form()
        self.load_medicines()
    
    def on_medicine_select(self, event):
        selected = self.medicine_tree.focus()
        if not selected:
            return
        
        values = self.medicine_tree.item(selected, 'values')
        if not values:
            return
        
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, values[1])
        
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, values[2])
        
        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, values[3])
        
        self.entry_expiry.delete(0, tk.END)
        self.entry_expiry.insert(0, values[4])
    
    def update_medicine(self):
        selected = self.medicine_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a medicine to update")
            return
        
        medicine_id = self.medicine_tree.item(selected, 'values')[0]
        name = self.entry_name.get()
        quantity = self.entry_quantity.get()
        price = self.entry_price.get()
        expiry_date = self.entry_expiry.get()
        
        if not all([name, quantity, price, expiry_date]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return
        
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showwarning("Input Error", "Quantity must be integer and Price must be number")
            return
        
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE medicines 
            SET name=?, quantity=?, price=?, expiry_date=?
            WHERE id=?
        ''', (name, quantity, price, expiry_date, medicine_id))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Medicine updated successfully")
        self.clear_medicine_form()
        self.load_medicines()
    
    def delete_medicine(self):
        selected = self.medicine_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a medicine to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this medicine?"):
            return
        
        medicine_id = self.medicine_tree.item(selected, 'values')[0]
        
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM medicines WHERE id=?', (medicine_id,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Medicine deleted successfully")
        self.clear_medicine_form()
        self.load_medicines()
    
    def search_medicines(self):
        search_term = self.entry_search.get()
        if not search_term:
            self.load_medicines()
            return
        
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM medicines WHERE name LIKE ? ORDER BY name', ('%' + search_term + '%',))
        medicines = cursor.fetchall()
        conn.close()
        
        # Clear existing data
        for item in self.medicine_tree.get_children():
            self.medicine_tree.delete(item)
        
        # Add data to treeview
        for medicine in medicines:
            self.medicine_tree.insert('', 'end', values=medicine)
    
    def clear_medicine_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_expiry.delete(0, tk.END)
        self.medicine_tree.selection_remove(self.medicine_tree.selection())
    
    # Sales management methods
    def load_sales(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, m.name, s.quantity, s.total_price, s.date 
            FROM sales s 
            JOIN medicines m ON s.medicine_id = m.id 
            ORDER BY s.date DESC
        ''')
        sales = cursor.fetchall()
        conn.close()
        
        # Clear existing data
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Add data to treeview
        for sale in sales:
            self.sales_tree.insert('', 'end', values=sale)
    
    def load_medicine_combo(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM medicines ORDER BY name')
        medicines = cursor.fetchall()
        conn.close()
        
        medicine_dict = {}
        medicine_names = []
        for medicine in medicines:
            medicine_dict[medicine[1]] = medicine[0]
            medicine_names.append(medicine[1])
        
        self.sale_medicine_combo['values'] = medicine_names
        self.medicine_id_map = medicine_dict
    
    def on_medicine_select_sale(self, event):
        medicine_name = self.sale_medicine_var.get()
        if not medicine_name:
            return
        
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT quantity, price FROM medicines WHERE id=?', (self.medicine_id_map[medicine_name],))
        medicine = cursor.fetchone()
        conn.close()
        
        if medicine:
            self.available_qty_var.set(medicine[0])
            self.unit_price_var.set(f"${medicine[1]:.2f}")
    
    def calculate_total(self):
        if not self.sale_medicine_var.get():
            messagebox.showwarning("Input Error", "Please select a medicine first")
            return
        
        try:
            qty = int(self.sale_qty_entry.get())
            unit_price = float(self.unit_price_var.get().replace('$', ''))
            total = qty * unit_price
            self.total_amount_var.set(f"${total:.2f}")
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid quantity")
    
    def record_sale(self):
        if not self.sale_medicine_var.get():
            messagebox.showwarning("Input Error", "Please select a medicine")
            return
        
        try:
            qty = int(self.sale_qty_entry.get())
            if qty <= 0:
                messagebox.showwarning("Input Error", "Quantity must be positive")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid quantity")
            return
        
        available_qty = int(self.available_qty_var.get())
        if qty > available_qty:
            messagebox.showwarning("Stock Error", f"Only {available_qty} units available")
            return
        
        medicine_id = self.medicine_id_map[self.sale_medicine_var.get()]
        unit_price = float(self.unit_price_var.get().replace('$', ''))
        total_price = qty * unit_price
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Record the sale
        cursor.execute('''
            INSERT INTO sales (medicine_id, quantity, total_price)
            VALUES (?, ?, ?)
        ''', (medicine_id, qty, total_price))
        
        # Update medicine quantity
        cursor.execute('''
            UPDATE medicines 
            SET quantity = quantity - ?
            WHERE id = ?
        ''', (qty, medicine_id))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Sale recorded successfully")
        self.clear_sale_form()
        self.load_sales()
        self.load_medicines()
        self.load_medicine_combo()
    
    def clear_sale_form(self):
        self.sale_medicine_var.set('')
        self.available_qty_var.set('')
        self.unit_price_var.set('')
        self.sale_qty_entry.delete(0, tk.END)
        self.total_amount_var.set('')
    
    # Report generation methods
    def generate_report(self):
        report_type = self.report_type_var.get()
        period = self.period_var.get()
        
        self.report_text.delete(1.0, tk.END)
        
        if report_type == "sales_summary":
            self.generate_sales_summary(period)
        elif report_type == "inventory_status":
            self.generate_inventory_report()
        elif report_type == "expiry_alerts":
            self.generate_expiry_alerts()
    
    def generate_sales_summary(self, period):
        conn = self.connect_db()
        cursor = conn.cursor()
        
        if period == "daily":
            date_filter = datetime.now().date()
            cursor.execute('''
                SELECT SUM(total_price) FROM sales WHERE date(date) = date(?)
            ''', (date_filter,))
        elif period == "weekly":
            start_date = (datetime.now() - timedelta(days=7)).date()
            cursor.execute('''
                SELECT SUM(total_price) FROM sales WHERE date(date) >= date(?)
            ''', (start_date,))
        elif period == "monthly":
            start_date = datetime.now().replace(day=1).date()
            cursor.execute('''
                SELECT SUM(total_price) FROM sales WHERE date(date) >= date(?)
            ''', (start_date,))
        
        total_sales = cursor.fetchone()[0] or 0
        
        # Get detailed sales
        if period == "daily":
            cursor.execute('''
                SELECT m.name, s.quantity, s.total_price, s.date
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.id
                WHERE date(s.date) = date(?)
                ORDER BY s.date DESC
            ''', (datetime.now().date(),))
        elif period == "weekly":
            start_date = (datetime.now() - timedelta(days=7)).date()
            cursor.execute('''
                SELECT m.name, s.quantity, s.total_price, s.date
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.id
                WHERE date(s.date) >= date(?)
                ORDER BY s.date DESC
            ''', (start_date,))
        elif period == "monthly":
            start_date = datetime.now().replace(day=1).date()
            cursor.execute('''
                SELECT m.name, s.quantity, s.total_price, s.date
                FROM sales s
                JOIN medicines m ON s.medicine_id = m.id
                WHERE date(s.date) >= date(?)
                ORDER BY s.date DESC
            ''', (start_date,))
        
        sales_data = cursor.fetchall()
        conn.close()
        
        # Format report
        self.report_text.insert(tk.END, f"Sales Summary Report ({period.capitalize()})\n")
        self.report_text.insert(tk.END, "=" * 50 + "\n\n")
        self.report_text.insert(tk.END, f"Total Sales: ${total_sales:.2f}\n\n")
        
        if sales_data:
            self.report_text.insert(tk.END, "Detailed Sales:\n")
            self.report_text.insert(tk.END, "-" * 50 + "\n")
            for sale in sales_data:
                self.report_text.insert(tk.END, 
                    f"{sale[3]}: {sale[0]} - {sale[1]} units - ${sale[2]:.2f}\n")
        else:
            self.report_text.insert(tk.END, "No sales recorded for this period.\n")
    
    def generate_inventory_report(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM medicines ORDER BY name')
        medicines = cursor.fetchall()
        conn.close()
        
        # Calculate total value
        total_value = sum(med[2] * med[3] for med in medicines)
        
        # Format report
        self.report_text.insert(tk.END, "Inventory Status Report\n")
        self.report_text.insert(tk.END, "=" * 50 + "\n\n")
        self.report_text.insert(tk.END, f"Total Inventory Value: ${total_value:.2f}\n\n")
        
        if medicines:
            self.report_text.insert(tk.END, "Medicine Details:\n")
            self.report_text.insert(tk.END, "-" * 50 + "\n")
            for med in medicines:
                self.report_text.insert(tk.END, 
                    f"{med[1]}: {med[2]} units - ${med[3]:.2f} each - Expires: {med[4]}\n")
        else:
            self.report_text.insert(tk.END, "No medicines in inventory.\n")
    
    def generate_expiry_alerts(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        
        # Get medicines expiring in the next 30 days
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM medicines 
            WHERE expiry_date BETWEEN date('now') AND date(?)
            ORDER BY expiry_date
        ''', (future_date,))
        
        expiring_meds = cursor.fetchall()
        conn.close()
        
        # Format report
        self.report_text.insert(tk.END, "Expiry Alerts Report (Next 30 Days)\n")
        self.report_text.insert(tk.END, "=" * 50 + "\n\n")
        
        if expiring_meds:
            self.report_text.insert(tk.END, "Medicines Expiring Soon:\n")
            self.report_text.insert(tk.END, "-" * 50 + "\n")
            for med in expiring_meds:
                self.report_text.insert(tk.END, 
                    f"{med[1]}: {med[2]} units - Expires: {med[4]}\n")
        else:
            self.report_text.insert(tk.END, "No medicines expiring in the next 30 days.\n")
    
    # User management methods (admin only)
    def load_users(self):
        if logged_in_user[3] != 'admin':
            return
            
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role FROM users ORDER BY username')
        users = cursor.fetchall()
        conn.close()
        
        # Clear existing data
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Add data to treeview
        for user in users:
            self.user_tree.insert('', 'end', values=user)
    
    def on_user_select(self, event):
        if logged_in_user[3] != 'admin':
            return
            
        selected = self.user_tree.focus()
        if not selected:
            return
        
        values = self.user_tree.item(selected, 'values')
        if not values:
            return
        
        self.user_username.delete(0, tk.END)
        self.user_username.insert(0, values[1])
        
        self.user_password.delete(0, tk.END)
        
        self.user_role_var.set(values[2])
    
    def add_user(self):
        if logged_in_user[3] != 'admin':
            messagebox.showwarning("Permission Denied", "Only administrators can manage users")
            return
            
        username = self.user_username.get()
        password = self.user_password.get()
        role = self.user_role_var.get()
        
        if not all([username, password, role]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return
        
        hashed_password = hash_password(password)
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, role))
            conn.commit()
            messagebox.showinfo("Success", "User added successfully")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Input Error", "Username already exists")
        finally:
            conn.close()
        
        self.clear_user_form()
        self.load_users()
    
    def update_user(self):
        if logged_in_user[3] != 'admin':
            messagebox.showwarning("Permission Denied", "Only administrators can manage users")
            return
            
        selected = self.user_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a user to update")
            return
        
        user_id = self.user_tree.item(selected, 'values')[0]
        username = self.user_username.get()
        password = self.user_password.get()
        role = self.user_role_var.get()
        
        if not all([username, role]):
            messagebox.showwarning("Input Error", "Please fill all fields")
            return
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        if password:
            hashed_password = hash_password(password)
            cursor.execute('''
                UPDATE users 
                SET username=?, password=?, role=?
                WHERE id=?
            ''', (username, hashed_password, role, user_id))
        else:
            cursor.execute('''
                UPDATE users 
                SET username=?, role=?
                WHERE id=?
            ''', (username, role, user_id))
        
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "User updated successfully")
        self.clear_user_form()
        self.load_users()
    
    def delete_user(self):
        if logged_in_user[3] != 'admin':
            messagebox.showwarning("Permission Denied", "Only administrators can manage users")
            return
            
        selected = self.user_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a user to delete")
            return
        
        user_id = self.user_tree.item(selected, 'values')[0]
        
        # Prevent deleting the last admin
        if self.user_tree.item(selected, 'values')[2] == 'admin':
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users WHERE role="admin"')
            admin_count = cursor.fetchone()[0]
            conn.close()
            
            if admin_count <= 1:
                messagebox.showwarning("Delete Error", "Cannot delete the only administrator")
                return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            return
        
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "User deleted successfully")
        self.clear_user_form()
        self.load_users()
    
    def clear_user_form(self):
        self.user_username.delete(0, tk.END)
        self.user_password.delete(0, tk.END)
        self.user_role_var.set("staff")
        self.user_tree.selection_remove(self.user_tree.selection())

# Run the application
if __name__ == "__main__":
    LoginWindow()
    