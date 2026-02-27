"""
DatabaseManager - SQLite database layer.
Equivalent to Local_DB_Model.java from the Android app.
Database: AASAA, Schema Version: 32
"""
import sqlite3
import os
import threading
from datetime import datetime
from kivy.utils import platform
from kivy.logger import Logger


class DatabaseManager:
    DB_NAME = "AASAA.db"
    DB_VERSION = 32

    def __init__(self, db_path=None):
        if db_path:
            self._db_path = db_path
        elif platform == 'android':
            from android.storage import app_storage_path
            self._db_path = os.path.join(app_storage_path(), self.DB_NAME)
        else:
            self._db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), '..', self.DB_NAME
            )
        self._local = threading.local()
        self._create_tables()

    def _get_connection(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self._db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _create_tables(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.executescript('''
            CREATE TABLE IF NOT EXISTS login_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT, password TEXT, user_type TEXT, phone_id TEXT
            );
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_code TEXT, branch_name TEXT, user_code TEXT
            );
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_code TEXT, route_name TEXT, branch_code TEXT,
                RouteCompleteBit INTEGER DEFAULT 0, MandatoryBit INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_code TEXT, region_name TEXT, route_code TEXT,
                parent_region_code TEXT,
                RegionCompleteBit INTEGER DEFAULT 0, MandatoryBit INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS customer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT, customer_name TEXT, contact TEXT, address TEXT,
                region_code TEXT, sub_region_code TEXT, route_code TEXT,
                latitude REAL DEFAULT 0, longitude REAL DEFAULT 0,
                CustomerCompleteBit INTEGER DEFAULT 0, SyncBit INTEGER DEFAULT 0,
                placed_order_check INTEGER DEFAULT 0, Order_Counter INTEGER DEFAULT 0,
                MandatoryBit INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT, product_name TEXT, unit_price REAL,
                company TEXT, Is_Focused INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS order_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT, product_code TEXT, product_name TEXT,
                unit_price REAL, discount_amount REAL, discount_type TEXT,
                quantity INTEGER, net_amount REAL, total_amount REAL,
                branch_code TEXT, order_id TEXT,
                SyncBit INTEGER DEFAULT 0, CloseBit INTEGER DEFAULT 0,
                No_Order INTEGER DEFAULT 0, Reason TEXT, Immediate INTEGER DEFAULT 0,
                X_Co REAL DEFAULT 0, Y_Co REAL DEFAULT 0,
                X_Co_Close REAL DEFAULT 0, Y_Co_Close REAL DEFAULT 0,
                Edit_Mode INTEGER DEFAULT 0, AndroidOrderID TEXT,
                TimeStamp_Start TEXT, TimeStamp_End TEXT, TimeStamp_Start_Customer TEXT
            );
            CREATE TABLE IF NOT EXISTS order_details_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT, product_code TEXT, product_name TEXT,
                unit_price REAL, discount_amount REAL, discount_type TEXT,
                quantity INTEGER, net_amount REAL, total_amount REAL,
                branch_code TEXT, order_id TEXT,
                SyncBit INTEGER DEFAULT 0, CloseBit INTEGER DEFAULT 0,
                No_Order INTEGER DEFAULT 0, Reason TEXT, Immediate INTEGER DEFAULT 0,
                X_Co REAL DEFAULT 0, Y_Co REAL DEFAULT 0,
                X_Co_Close REAL DEFAULT 0, Y_Co_Close REAL DEFAULT 0,
                Edit_Mode INTEGER DEFAULT 0, AndroidOrderID TEXT,
                TimeStamp_Start TEXT, TimeStamp_End TEXT, TimeStamp_Start_Customer TEXT
            );
            CREATE TABLE IF NOT EXISTS start_day (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_code TEXT, day_started INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS url_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT, base_url TEXT
            );
            CREATE TABLE IF NOT EXISTS service_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timer_interval INTEGER DEFAULT 60000
            );
            CREATE TABLE IF NOT EXISTS license (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_type TEXT, license_name TEXT
            );
            CREATE TABLE IF NOT EXISTS _customer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT, license_type TEXT, license_number TEXT
            );
            CREATE TABLE IF NOT EXISTS all_routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_code TEXT, route_name TEXT
            );
            CREATE TABLE IF NOT EXISTS all_regions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region_code TEXT, region_name TEXT
            );
            CREATE TABLE IF NOT EXISTS all_cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_code TEXT, city_name TEXT
            );
            CREATE TABLE IF NOT EXISTS mandatory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT, item_type TEXT, category TEXT
            );
            CREATE TABLE IF NOT EXISTS Auto_Sync_Table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_code TEXT, auto_sync INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS Temp_Order_Table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT, product_code TEXT, product_name TEXT,
                unit_price REAL, quantity INTEGER, net_amount REAL, total_amount REAL,
                OrderID TEXT, Disc_Type TEXT, Discount REAL
            );
            CREATE TABLE IF NOT EXISTS Settings_Table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                StandardView INTEGER DEFAULT 1, ClassicalView INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS Error_Log_Table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_code TEXT, error_details TEXT, timestamp TEXT
            );
            CREATE TABLE IF NOT EXISTS Company_Wise_Sale_Target_Table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT, target_amount REAL, actual_amount REAL, month TEXT
            );
            CREATE TABLE IF NOT EXISTS Customer_Product_Is_Focused_Mapping_Table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT, product_code TEXT, is_focused INTEGER DEFAULT 0
            );
        ''')
        # Ensure default settings row exists
        row = c.execute("SELECT COUNT(*) FROM Settings_Table").fetchone()
        if row[0] == 0:
            c.execute("INSERT INTO Settings_Table (StandardView, ClassicalView) VALUES (1, 0)")
        conn.commit()

    # ── Generic helpers ──────────────────────────────────────────────
    def execute_insert(self, sql, params=()):
        conn = self._get_connection()
        try:
            conn.execute(sql, params)
            conn.commit()
        except Exception as e:
            Logger.error(f"DB insert error: {e}")

    def execute_query(self, sql, params=()):
        conn = self._get_connection()
        try:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]
        except Exception as e:
            Logger.error(f"DB query error: {e}")
            return []

    # ── Login ────────────────────────────────────────────────────────
    def save_login(self, username, password, user_type, phone_id):
        conn = self._get_connection()
        conn.execute("DELETE FROM login_info")
        conn.execute(
            "INSERT INTO login_info (username, password, user_type, phone_id) VALUES (?,?,?,?)",
            (username, password, user_type, phone_id)
        )
        conn.commit()

    def get_login(self):
        rows = self.execute_query("SELECT * FROM login_info LIMIT 1")
        return rows[0] if rows else None

    # ── URL ──────────────────────────────────────────────────────────
    def save_url(self, url):
        conn = self._get_connection()
        conn.execute("DELETE FROM url_table")
        conn.execute("INSERT INTO url_table (base_url) VALUES (?)", (url,))
        conn.commit()

    def get_url(self):
        rows = self.execute_query("SELECT base_url FROM url_table LIMIT 1")
        return rows[0]['base_url'] if rows else None

    # ── Branches ─────────────────────────────────────────────────────
    def insert_branches(self, branches_list):
        conn = self._get_connection()
        conn.execute("DELETE FROM branches")
        for b in branches_list:
            conn.execute(
                "INSERT INTO branches (branch_code, branch_name, user_code) VALUES (?,?,?)",
                (b['branch_code'], b['branch_name'], b.get('user_code', ''))
            )
        conn.commit()

    def get_branches(self):
        return self.execute_query("SELECT * FROM branches")

    # ── Routes ───────────────────────────────────────────────────────
    def insert_routes(self, routes_list):
        conn = self._get_connection()
        conn.execute("DELETE FROM routes")
        for r in routes_list:
            conn.execute(
                "INSERT INTO routes (route_code, route_name, branch_code, RouteCompleteBit, MandatoryBit) VALUES (?,?,?,?,?)",
                (r['route_code'], r['route_name'], r['branch_code'],
                 r.get('RouteCompleteBit', 0), r.get('MandatoryBit', 0))
            )
        conn.commit()

    def get_routes_by_branch(self, branch_code):
        return self.execute_query(
            "SELECT * FROM routes WHERE branch_code=? ORDER BY MandatoryBit DESC, route_name",
            (branch_code,)
        )

    def get_incomplete_routes(self, branch_code):
        return self.execute_query(
            "SELECT * FROM routes WHERE branch_code=? AND RouteCompleteBit=0 ORDER BY MandatoryBit DESC, route_name",
            (branch_code,)
        )

    def get_complete_routes(self, branch_code):
        return self.execute_query(
            "SELECT * FROM routes WHERE branch_code=? AND RouteCompleteBit=1 ORDER BY route_name",
            (branch_code,)
        )

    def set_route_complete(self, route_code, complete=1):
        conn = self._get_connection()
        conn.execute("UPDATE routes SET RouteCompleteBit=? WHERE route_code=?", (complete, route_code))
        conn.commit()

    # ── Regions ──────────────────────────────────────────────────────
    def insert_regions(self, regions_list):
        conn = self._get_connection()
        conn.execute("DELETE FROM regions")
        for r in regions_list:
            conn.execute(
                "INSERT INTO regions (region_code, region_name, route_code, parent_region_code, RegionCompleteBit, MandatoryBit) VALUES (?,?,?,?,?,?)",
                (r['region_code'], r['region_name'], r['route_code'],
                 r.get('parent_region_code', ''), r.get('RegionCompleteBit', 0), r.get('MandatoryBit', 0))
            )
        conn.commit()

    def get_regions_by_route(self, route_code):
        return self.execute_query(
            "SELECT * FROM regions WHERE route_code=? AND (parent_region_code='' OR parent_region_code IS NULL) ORDER BY MandatoryBit DESC, region_name",
            (route_code,)
        )

    def get_subregions_by_parent(self, parent_region_code):
        return self.execute_query(
            "SELECT * FROM regions WHERE parent_region_code=? ORDER BY MandatoryBit DESC, region_name",
            (parent_region_code,)
        )

    def get_incomplete_regions(self, route_code):
        return self.execute_query(
            "SELECT * FROM regions WHERE route_code=? AND (parent_region_code='' OR parent_region_code IS NULL) AND RegionCompleteBit=0 ORDER BY MandatoryBit DESC, region_name",
            (route_code,)
        )

    def get_complete_regions(self, route_code):
        return self.execute_query(
            "SELECT * FROM regions WHERE route_code=? AND (parent_region_code='' OR parent_region_code IS NULL) AND RegionCompleteBit=1 ORDER BY region_name",
            (route_code,)
        )

    def get_incomplete_subregions(self, parent_region_code):
        return self.execute_query(
            "SELECT * FROM regions WHERE parent_region_code=? AND RegionCompleteBit=0 ORDER BY MandatoryBit DESC, region_name",
            (parent_region_code,)
        )

    def get_complete_subregions(self, parent_region_code):
        return self.execute_query(
            "SELECT * FROM regions WHERE parent_region_code=? AND RegionCompleteBit=1 ORDER BY region_name",
            (parent_region_code,)
        )

    def has_subregions(self, region_code):
        rows = self.execute_query(
            "SELECT COUNT(*) as cnt FROM regions WHERE parent_region_code=?", (region_code,)
        )
        return rows[0]['cnt'] > 0 if rows else False

    def set_region_complete(self, region_code, complete=1):
        conn = self._get_connection()
        conn.execute("UPDATE regions SET RegionCompleteBit=? WHERE region_code=?", (complete, region_code))
        conn.commit()

    # ── Customers ────────────────────────────────────────────────────
    def insert_customers(self, customers_list):
        conn = self._get_connection()
        conn.execute("DELETE FROM customer")
        for c_data in customers_list:
            conn.execute(
                """INSERT INTO customer (customer_code, customer_name, contact, address,
                   region_code, sub_region_code, route_code, latitude, longitude, MandatoryBit)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (c_data['customer_code'], c_data['customer_name'], c_data.get('contact', ''),
                 c_data.get('address', ''), c_data.get('region_code', ''),
                 c_data.get('sub_region_code', ''), c_data.get('route_code', ''),
                 c_data.get('latitude', 0), c_data.get('longitude', 0),
                 c_data.get('MandatoryBit', 0))
            )
        conn.commit()

    def get_customers_by_region(self, region_code):
        return self.execute_query(
            "SELECT * FROM customer WHERE region_code=? OR sub_region_code=? ORDER BY MandatoryBit DESC, customer_name",
            (region_code, region_code)
        )

    def get_incomplete_customers(self, region_code):
        return self.execute_query(
            "SELECT * FROM customer WHERE (region_code=? OR sub_region_code=?) AND CustomerCompleteBit=0 ORDER BY MandatoryBit DESC, customer_name",
            (region_code, region_code)
        )

    def get_complete_customers(self, region_code):
        return self.execute_query(
            "SELECT * FROM customer WHERE (region_code=? OR sub_region_code=?) AND CustomerCompleteBit=1 ORDER BY customer_name",
            (region_code, region_code)
        )

    def set_customer_complete(self, customer_code, complete=1):
        conn = self._get_connection()
        conn.execute("UPDATE customer SET CustomerCompleteBit=? WHERE customer_code=?", (complete, customer_code))
        conn.commit()

    def get_customer_by_code(self, customer_code):
        rows = self.execute_query("SELECT * FROM customer WHERE customer_code=?", (customer_code,))
        return rows[0] if rows else None

    def get_customer_order_count(self, customer_code):
        rows = self.execute_query("SELECT Order_Counter FROM customer WHERE customer_code=?", (customer_code,))
        return rows[0]['Order_Counter'] if rows else 0

    def increment_order_counter(self, customer_code):
        conn = self._get_connection()
        conn.execute("UPDATE customer SET Order_Counter = Order_Counter + 1 WHERE customer_code=?", (customer_code,))
        conn.commit()

    def update_customer_gps(self, customer_code, lat, lon):
        conn = self._get_connection()
        conn.execute("UPDATE customer SET latitude=?, longitude=? WHERE customer_code=?", (lat, lon, customer_code))
        conn.commit()

    def add_new_customer(self, data):
        conn = self._get_connection()
        conn.execute(
            """INSERT INTO customer (customer_code, customer_name, contact, address,
               region_code, sub_region_code, route_code, latitude, longitude)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (data['customer_code'], data['customer_name'], data.get('contact', ''),
             data.get('address', ''), data.get('region_code', ''),
             data.get('sub_region_code', ''), data.get('route_code', ''),
             data.get('latitude', 0), data.get('longitude', 0))
        )
        conn.commit()

    # ── Products ─────────────────────────────────────────────────────
    def insert_products(self, products_list):
        conn = self._get_connection()
        conn.execute("DELETE FROM products")
        for p in products_list:
            conn.execute(
                "INSERT INTO products (product_code, product_name, unit_price, company, Is_Focused) VALUES (?,?,?,?,?)",
                (p['product_code'], p['product_name'], p.get('unit_price', 0),
                 p.get('company', ''), p.get('Is_Focused', 0))
            )
        conn.commit()

    def get_all_products(self):
        return self.execute_query("SELECT * FROM products ORDER BY company, product_name")

    def get_products_by_company(self, company):
        return self.execute_query("SELECT * FROM products WHERE company=? ORDER BY product_name", (company,))

    def get_companies(self):
        return self.execute_query("SELECT DISTINCT company FROM products ORDER BY company")

    def search_products(self, query):
        return self.execute_query(
            "SELECT * FROM products WHERE product_name LIKE ? OR product_code LIKE ? ORDER BY product_name",
            (f"%{query}%", f"%{query}%")
        )

    def get_focused_products(self, customer_code):
        return self.execute_query(
            """SELECT p.* FROM products p
               INNER JOIN Customer_Product_Is_Focused_Mapping_Table m
               ON p.product_code = m.product_code
               WHERE m.customer_code=? AND m.is_focused=1""",
            (customer_code,)
        )

    # ── Orders ───────────────────────────────────────────────────────
    def insert_order(self, order_data):
        conn = self._get_connection()
        conn.execute(
            """INSERT INTO order_details (customer_code, product_code, product_name,
               unit_price, discount_amount, discount_type, quantity, net_amount, total_amount,
               branch_code, order_id, SyncBit, CloseBit, No_Order, Reason, Immediate,
               X_Co, Y_Co, X_Co_Close, Y_Co_Close, Edit_Mode, AndroidOrderID,
               TimeStamp_Start, TimeStamp_End, TimeStamp_Start_Customer)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (order_data.get('customer_code', ''), order_data.get('product_code', ''),
             order_data.get('product_name', ''), order_data.get('unit_price', 0),
             order_data.get('discount_amount', 0), order_data.get('discount_type', ''),
             order_data.get('quantity', 0), order_data.get('net_amount', 0),
             order_data.get('total_amount', 0), order_data.get('branch_code', ''),
             order_data.get('order_id', ''), order_data.get('SyncBit', 0),
             order_data.get('CloseBit', 0), order_data.get('No_Order', 0),
             order_data.get('Reason', ''), order_data.get('Immediate', 0),
             order_data.get('X_Co', 0), order_data.get('Y_Co', 0),
             order_data.get('X_Co_Close', 0), order_data.get('Y_Co_Close', 0),
             order_data.get('Edit_Mode', 0), order_data.get('AndroidOrderID', ''),
             order_data.get('TimeStamp_Start', ''), order_data.get('TimeStamp_End', ''),
             order_data.get('TimeStamp_Start_Customer', ''))
        )
        conn.commit()

    def get_orders_by_customer(self, customer_code):
        return self.execute_query(
            "SELECT * FROM order_details WHERE customer_code=? ORDER BY id", (customer_code,)
        )

    def get_unsynced_orders(self):
        return self.execute_query(
            "SELECT * FROM order_details WHERE CloseBit=1 AND SyncBit=0 AND Edit_Mode=0 ORDER BY id"
        )

    def get_all_unsynced_count(self):
        rows = self.execute_query("SELECT COUNT(*) as cnt FROM order_details WHERE CloseBit=1 AND SyncBit=0")
        return rows[0]['cnt'] if rows else 0

    def mark_order_synced(self, order_id):
        conn = self._get_connection()
        # Move to history
        conn.execute(
            """INSERT INTO order_details_history
               SELECT * FROM order_details WHERE order_id=?""",
            (order_id,)
        )
        conn.execute("DELETE FROM order_details WHERE order_id=?", (order_id,))
        conn.commit()

    def close_order(self, customer_code, order_id, x_close, y_close, timestamp_end):
        conn = self._get_connection()
        conn.execute(
            """UPDATE order_details SET CloseBit=1, X_Co_Close=?, Y_Co_Close=?, TimeStamp_End=?
               WHERE customer_code=? AND order_id=?""",
            (x_close, y_close, timestamp_end, customer_code, order_id)
        )
        conn.commit()

    def get_order_history(self):
        return self.execute_query("SELECT * FROM order_details_history ORDER BY id DESC")

    def get_order_history_details(self, order_id):
        return self.execute_query("SELECT * FROM order_details_history WHERE order_id=?", (order_id,))

    # ── Temp Orders ──────────────────────────────────────────────────
    def add_temp_order(self, customer_code, product_code, product_name, unit_price,
                       quantity, net_amount, total_amount, order_id, disc_type='', discount=0):
        conn = self._get_connection()
        conn.execute(
            """INSERT INTO Temp_Order_Table (customer_code, product_code, product_name,
               unit_price, quantity, net_amount, total_amount, OrderID, Disc_Type, Discount)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (customer_code, product_code, product_name, unit_price, quantity,
             net_amount, total_amount, order_id, disc_type, discount)
        )
        conn.commit()

    def get_temp_orders(self, customer_code):
        return self.execute_query(
            "SELECT * FROM Temp_Order_Table WHERE customer_code=?", (customer_code,)
        )

    def clear_temp_orders(self, customer_code):
        conn = self._get_connection()
        conn.execute("DELETE FROM Temp_Order_Table WHERE customer_code=?", (customer_code,))
        conn.commit()

    def remove_temp_order(self, temp_id):
        conn = self._get_connection()
        conn.execute("DELETE FROM Temp_Order_Table WHERE id=?", (temp_id,))
        conn.commit()

    # ── Error Logs ───────────────────────────────────────────────────
    def log_error(self, branch_code, error_details):
        conn = self._get_connection()
        conn.execute(
            "INSERT INTO Error_Log_Table (branch_code, error_details, timestamp) VALUES (?,?,?)",
            (branch_code, error_details, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

    def get_error_logs(self):
        return self.execute_query("SELECT * FROM Error_Log_Table ORDER BY id DESC")

    def clear_error_logs(self):
        conn = self._get_connection()
        conn.execute("DELETE FROM Error_Log_Table")
        conn.commit()

    # ── Settings ─────────────────────────────────────────────────────
    def get_settings(self):
        rows = self.execute_query("SELECT * FROM Settings_Table LIMIT 1")
        return rows[0] if rows else {'StandardView': 1, 'ClassicalView': 0}

    def update_settings(self, standard, classical):
        conn = self._get_connection()
        conn.execute("UPDATE Settings_Table SET StandardView=?, ClassicalView=?", (standard, classical))
        conn.commit()

    # ── Start Day ────────────────────────────────────────────────────
    def is_day_started(self, branch_code):
        rows = self.execute_query(
            "SELECT day_started FROM start_day WHERE branch_code=?", (branch_code,)
        )
        return rows[0]['day_started'] == 1 if rows else False

    def set_day_started(self, branch_code, started):
        conn = self._get_connection()
        rows = conn.execute("SELECT id FROM start_day WHERE branch_code=?", (branch_code,)).fetchall()
        if rows:
            conn.execute("UPDATE start_day SET day_started=? WHERE branch_code=?", (started, branch_code))
        else:
            conn.execute("INSERT INTO start_day (branch_code, day_started) VALUES (?,?)", (branch_code, started))
        conn.commit()

    # ── Auto Sync ────────────────────────────────────────────────────
    def get_auto_sync(self, branch_code):
        rows = self.execute_query(
            "SELECT auto_sync FROM Auto_Sync_Table WHERE branch_code=?", (branch_code,)
        )
        return rows[0]['auto_sync'] == 1 if rows else True

    def set_auto_sync(self, branch_code, enabled):
        conn = self._get_connection()
        rows = conn.execute("SELECT id FROM Auto_Sync_Table WHERE branch_code=?", (branch_code,)).fetchall()
        if rows:
            conn.execute("UPDATE Auto_Sync_Table SET auto_sync=? WHERE branch_code=?",
                         (1 if enabled else 0, branch_code))
        else:
            conn.execute("INSERT INTO Auto_Sync_Table (branch_code, auto_sync) VALUES (?,?)",
                         (branch_code, 1 if enabled else 0))
        conn.commit()

    # ── Company Wise Sales ───────────────────────────────────────────
    def get_company_wise_sales(self):
        return self.execute_query("SELECT * FROM Company_Wise_Sale_Target_Table ORDER BY company")

    # ── Reference Tables ─────────────────────────────────────────────
    def get_all_routes_ref(self):
        return self.execute_query("SELECT * FROM all_routes ORDER BY route_name")

    def get_all_regions_ref(self):
        return self.execute_query("SELECT * FROM all_regions ORDER BY region_name")

    def get_all_cities_ref(self):
        return self.execute_query("SELECT * FROM all_cities ORDER BY city_name")

    # ── Reset / Clear ────────────────────────────────────────────────
    def reset_completion_bits(self):
        conn = self._get_connection()
        conn.execute("UPDATE routes SET RouteCompleteBit=0")
        conn.execute("UPDATE regions SET RegionCompleteBit=0")
        conn.execute("UPDATE customer SET CustomerCompleteBit=0")
        conn.execute("UPDATE start_day SET day_started=0")
        conn.commit()

    def clear_all_data(self):
        conn = self._get_connection()
        tables = ['login_info', 'branches', 'routes', 'regions', 'customer',
                  'products', 'start_day', 'all_routes', 'all_regions', 'all_cities',
                  'mandatory', 'Auto_Sync_Table', 'Temp_Order_Table',
                  'Company_Wise_Sale_Target_Table', 'Customer_Product_Is_Focused_Mapping_Table']
        for t in tables:
            conn.execute(f"DELETE FROM {t}")
        conn.commit()

    def has_unsynced_orders(self):
        return self.get_all_unsynced_count() > 0

    def get_today_bookings(self):
        today = datetime.now().strftime("%Y-%m-%d")
        return self.execute_query(
            """SELECT od.customer_code, c.customer_name,
                      SUM(od.total_amount) as total_amount,
                      COUNT(DISTINCT od.order_id) as order_count
               FROM order_details_history od
               LEFT JOIN customer c ON od.customer_code = c.customer_code
               WHERE od.TimeStamp_Start LIKE ?
               GROUP BY od.customer_code""",
            (f"{today}%",)
        )

    def get_monthly_bookings(self):
        return self.execute_query(
            """SELECT strftime('%Y-%m', TimeStamp_Start) as month,
                      COUNT(DISTINCT order_id) as total_orders,
                      SUM(total_amount) as total_amount
               FROM order_details_history
               WHERE TimeStamp_Start IS NOT NULL AND TimeStamp_Start != ''
               GROUP BY strftime('%Y-%m', TimeStamp_Start)
               ORDER BY month DESC"""
        )

    # ── License ──────────────────────────────────────────────────────
    def save_customer_license(self, customer_code, license_type, license_number):
        conn = self._get_connection()
        conn.execute(
            "INSERT INTO _customer (customer_code, license_type, license_number) VALUES (?,?,?)",
            (customer_code, license_type, license_number)
        )
        conn.commit()

    def get_license_types(self):
        return self.execute_query("SELECT * FROM license")

    def close(self):
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
