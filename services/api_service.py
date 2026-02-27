"""
API Service - handles all network communication with the remote server.
Equivalent to Login_Model_Class, GetAllData_DayStart_Model, GetAllData_SyncCall_Model,
GetMasterData_Model, Get_New_Customers_Sync_Model, Is_Focused_Products_Model_Class,
CheckURL_Model from the Android app.
"""
import json
import threading
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from kivy.clock import Clock
from kivy.logger import Logger


class ApiService:
    def __init__(self, db_manager, prefs):
        self.db = db_manager
        self.prefs = prefs
        self.session_id = ""
        self.timeout = 300

    def _get_base_url(self):
        url = self.prefs.get('base_url', '')
        if not url:
            row = self.db.get_url()
            url = row if row else ''
        return url

    def _post_request(self, endpoint, payload, callback, error_callback):
        """
        The server expects application/x-www-form-urlencoded with the JSON
        as the value of a field named 'response' — matching the original Android app.
        """
        def _do_request():
            try:
                base_url = self._get_base_url()
                if not base_url:
                    Clock.schedule_once(lambda dt: error_callback("Server URL not configured"), 0)
                    return
                url = base_url.rstrip('/') + endpoint
                json_str = json.dumps(payload)
                form_data = urlencode({'response': json_str}).encode('utf-8')
                req = Request(url, data=form_data, method='POST')
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
                if self.session_id:
                    req.add_header('Cookie', self.session_id)
                print(f"[API] POST {url}")
                print(f"[API] JSON payload: {json_str}")
                response = urlopen(req, timeout=self.timeout)
                raw = response.read().decode('utf-8')
                print(f"[API] Response ({response.status}): {raw[:1000]}")
                response_data = json.loads(raw)
                Clock.schedule_once(lambda dt: callback(response_data), 0)
            except HTTPError as e:
                msg = f"HTTP Error {e.code}: {e.reason}"
                Clock.schedule_once(lambda dt: error_callback(msg), 0)
            except URLError as e:
                msg = f"Connection Error: {str(e.reason)}"
                Clock.schedule_once(lambda dt: error_callback(msg), 0)
            except Exception as e:
                msg = f"Error: {str(e)}"
                Clock.schedule_once(lambda dt: error_callback(msg), 0)
        threading.Thread(target=_do_request, daemon=True).start()

    def check_url(self, url, callback, error_callback):
        def _check():
            try:
                test_url = url.rstrip('/') + '/WebServiceStartDayData/Request'
                req = Request(test_url, method='GET')
                response = urlopen(req, timeout=10)
                if response.status == 200:
                    self.db.save_url(url)
                    self.prefs['base_url'] = url
                    Clock.schedule_once(lambda dt: callback(True), 0)
                else:
                    Clock.schedule_once(lambda dt: error_callback("Invalid URL"), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: error_callback(str(e)), 0)
        threading.Thread(target=_check, daemon=True).start()

    def login(self, username, password, phone_id, callback, error_callback):
        payload = {
            "result": [{"user": username, "pass": password, "User_Type": "Bookman"}],
            "request": "Login",
            "PhoneID": phone_id,
            "URL": self._get_base_url() + "/",
        }
        def on_success(data):
            try:
                if isinstance(data, dict):
                    self.db.save_login(username, password, "Bookman", phone_id)
                    branches = data.get('Branches', data.get('branches', []))
                    if branches:
                        bl = []
                        for b in branches:
                            bl.append({
                                'branch_code': b.get('BranchCode', b.get('branch_code', '')),
                                'branch_name': b.get('BranchName', b.get('branch_name', '')),
                                'user_code': b.get('UserCode', b.get('user_code', ''))
                            })
                        self.db.insert_branches(bl)
                    self.session_id = data.get('SessionID', data.get('session_id', ''))
                    if self.session_id:
                        self.prefs['session_id'] = self.session_id
                    callback(data)
                else:
                    error_callback("Invalid server response")
            except Exception as e:
                error_callback(f"Parse error: {str(e)}")
        self._post_request('/WebServiceStartDayData/Request', payload, on_success, error_callback)

    def start_day_data(self, branch_code, user_code, callback, error_callback):
        payload = {
            "BranchCode": branch_code,
            "request": "StartDay",
            "PhoneID": self.prefs.get('PhoneID', ''),
            "UserCode": user_code,
            "URL": self._get_base_url() + "/",
        }
        def on_success(data):
            try:
                self._parse_master_data(data, branch_code)
                callback(data)
            except Exception as e:
                error_callback(f"Data parse error: {str(e)}")
        self._post_request('/WebServiceStartDayData/Request', payload, on_success, error_callback)

    def _parse_master_data(self, data, branch_code):
        routes = data.get('Routes', data.get('routes', []))
        if routes:
            rl = []
            for r in routes:
                rl.append({
                    'route_code': r.get('RouteCode', r.get('route_code', '')),
                    'route_name': r.get('RouteName', r.get('route_name', '')),
                    'branch_code': branch_code,
                    'RouteCompleteBit': 0,
                    'MandatoryBit': r.get('MandatoryBit', r.get('mandatory_bit', 0))
                })
            self.db.insert_routes(rl)

        regions = data.get('Regions', data.get('regions', []))
        if regions:
            rgl = []
            for r in regions:
                rgl.append({
                    'region_code': r.get('RegionCode', r.get('region_code', '')),
                    'region_name': r.get('RegionName', r.get('region_name', '')),
                    'route_code': r.get('RouteCode', r.get('route_code', '')),
                    'parent_region_code': r.get('ParentRegionCode', r.get('parent_region_code', '')),
                    'RegionCompleteBit': 0,
                    'MandatoryBit': r.get('MandatoryBit', r.get('mandatory_bit', 0))
                })
            self.db.insert_regions(rgl)

        customers = data.get('Customers', data.get('customers', []))
        if customers:
            cl = []
            for c in customers:
                cl.append({
                    'customer_code': c.get('CustomerCode', c.get('customer_code', '')),
                    'customer_name': c.get('CustomerName', c.get('customer_name', '')),
                    'contact': c.get('Contact', c.get('contact', '')),
                    'address': c.get('Address', c.get('address', '')),
                    'region_code': c.get('RegionCode', c.get('region_code', '')),
                    'sub_region_code': c.get('SubRegionCode', c.get('sub_region_code', '')),
                    'route_code': c.get('RouteCode', c.get('route_code', '')),
                    'latitude': float(c.get('Latitude', c.get('latitude', 0))),
                    'longitude': float(c.get('Longitude', c.get('longitude', 0))),
                    'MandatoryBit': c.get('MandatoryBit', c.get('mandatory_bit', 0))
                })
            self.db.insert_customers(cl)

        products = data.get('Products', data.get('products', []))
        if products:
            pl = []
            for p in products:
                pl.append({
                    'product_code': p.get('ProductCode', p.get('product_code', '')),
                    'product_name': p.get('ProductName', p.get('product_name', '')),
                    'unit_price': float(p.get('UnitPrice', p.get('unit_price', 0))),
                    'company': p.get('Company', p.get('company', '')),
                    'Is_Focused': p.get('Is_Focused', p.get('is_focused', 0))
                })
            self.db.insert_products(pl)

        for r in data.get('AllRoutes', data.get('all_routes', [])):
            self.db.execute_insert(
                "INSERT OR REPLACE INTO all_routes (route_code, route_name) VALUES (?,?)",
                (r.get('RouteCode', ''), r.get('RouteName', ''))
            )
        for r in data.get('AllRegions', data.get('all_regions', [])):
            self.db.execute_insert(
                "INSERT OR REPLACE INTO all_regions (region_code, region_name) VALUES (?,?)",
                (r.get('RegionCode', ''), r.get('RegionName', ''))
            )
        for m in data.get('Mandatory', data.get('mandatory', [])):
            self.db.execute_insert(
                "INSERT OR REPLACE INTO mandatory (item_code, item_type, category) VALUES (?,?,?)",
                (m.get('ItemCode', ''), m.get('ItemType', ''), m.get('Category', ''))
            )
        for t in data.get('CompanyTargets', data.get('company_targets', [])):
            self.db.execute_insert(
                "INSERT OR REPLACE INTO Company_Wise_Sale_Target_Table (company, target_amount, actual_amount, month) VALUES (?,?,?,?)",
                (t.get('Company', ''), float(t.get('TargetAmount', 0)),
                 float(t.get('ActualAmount', 0)), t.get('Month', ''))
            )
        self.db.set_day_started(branch_code, 1)

    def sync_data(self, branch_code, user_code, callback, error_callback):
        payload = {
            "user": self.prefs.get('username', ''),
            "pass": self.prefs.get('password', ''),
            "User_Type": "Bookman",
            "PhoneID": self.prefs.get('PhoneID', ''),
            "URL": self._get_base_url(),
            "BranchCode": branch_code, "UserCode": user_code,
            "RequestType": "3"
        }
        def on_success(data):
            try:
                self._parse_master_data(data, branch_code)
                callback(data)
            except Exception as e:
                error_callback(f"Sync error: {str(e)}")
        self._post_request('/WebServiceStartDayData/Request', payload, on_success, error_callback)

    def sync_new_customer(self, customer_data, callback, error_callback):
        payload = {
            "user": self.prefs.get('username', ''),
            "pass": self.prefs.get('password', ''),
            "User_Type": "Bookman",
            "PhoneID": self.prefs.get('PhoneID', ''),
            "URL": self._get_base_url(),
            "RequestType": "4",
            "CustomerData": customer_data
        }
        self._post_request('/WebServiceStartDayData/Request', payload, callback, error_callback)

    def fetch_focused_products(self, branch_code, callback, error_callback):
        payload = {
            "user": self.prefs.get('username', ''),
            "pass": self.prefs.get('password', ''),
            "User_Type": "Bookman",
            "PhoneID": self.prefs.get('PhoneID', ''),
            "URL": self._get_base_url(),
            "BranchCode": branch_code,
            "RequestType": "5"
        }
        def on_success(data):
            try:
                for m in data.get('FocusedProducts', data.get('focused_products', [])):
                    cust = m.get('CustomerCode', m.get('customer_code', ''))
                    prod = m.get('ProductCode', m.get('product_code', ''))
                    focused = m.get('IsFocused', m.get('is_focused', 1))
                    self.db.execute_insert(
                        "INSERT OR REPLACE INTO Customer_Product_Is_Focused_Mapping_Table (customer_code, product_code, is_focused) VALUES (?,?,?)",
                        (cust, prod, focused)
                    )
                callback(data)
            except Exception as e:
                error_callback(str(e))
        self._post_request('/WebServiceStartDayData/Request', payload, on_success, error_callback)

    def send_orders(self, branch_code, user_code, callback, error_callback):
        def _build_and_send():
            try:
                orders = self.db.get_unsynced_orders()
                if not orders:
                    Clock.schedule_once(lambda dt: callback({"message": "No orders to sync"}), 0)
                    return
                grouped = {}
                for order in orders:
                    key = (order['customer_code'], order['order_id'])
                    grouped.setdefault(key, []).append(order)

                order_masters = []
                all_details = []
                for (cust_code, order_id), items in grouped.items():
                    total_amount = sum(float(i.get('total_amount', 0)) for i in items)
                    total_net = sum(float(i.get('net_amount', 0)) for i in items)
                    total_disc = sum(float(i.get('discount_amount', 0)) for i in items)
                    first = items[0]
                    order_masters.append({
                        "Customer_Code": cust_code, "Total_Amount": total_amount,
                        "Total_Net": total_net, "Total_Disc": total_disc,
                        "No_Order": first.get('No_Order', 0),
                        "Reason": first.get('Reason', ''),
                        "Immediate": first.get('Immediate', 0),
                        "X_Co": first.get('X_Co', 0), "Y_Co": first.get('Y_Co', 0),
                        "X_Co_Close": first.get('X_Co_Close', 0),
                        "Y_Co_Close": first.get('Y_Co_Close', 0),
                        "AndroidOrderID": first.get('AndroidOrderID', ''),
                        "TimeStamp_Start": first.get('TimeStamp_Start', ''),
                        "TimeStamp_End": first.get('TimeStamp_End', ''),
                        "TimeStamp_Start_Customer": first.get('TimeStamp_Start_Customer', '')
                    })
                    for item in items:
                        all_details.append({
                            "Customer_Code": cust_code,
                            "Discount_Type": item.get('discount_type', ''),
                            "Product_Code": item.get('product_code', ''),
                            "Product_Name": item.get('product_name', ''),
                            "Unit_Price": item.get('unit_price', 0),
                            "Discount_Amount": item.get('discount_amount', 0),
                            "Quantity": item.get('quantity', 0),
                            "Net_Amount": item.get('net_amount', 0),
                            "Total_Amount": item.get('total_amount', 0)
                        })

                payload = {
                    "UserInfo": {"BranchCode": branch_code, "UserCode": user_code, "Mode": "Android"},
                    "OrderMaster": order_masters, "OrderDetails": all_details
                }
                base_url = self._get_base_url()
                url = base_url.rstrip('/') + '/api/SaleOrderChemist/SaleOrderChemist'
                data = json.dumps(payload).encode('utf-8')
                req = Request(url, data=data, method='POST')
                req.add_header('Content-Type', 'application/json; charset=utf-8')
                if self.session_id:
                    req.add_header('Cookie', self.session_id)
                response = urlopen(req, timeout=self.timeout)
                response_data = json.loads(response.read().decode('utf-8'))
                for (cust_code, order_id), items in grouped.items():
                    self.db.mark_order_synced(order_id)
                Clock.schedule_once(lambda dt: callback(response_data), 0)
            except Exception as e:
                error_msg = str(e)
                self.db.log_error(branch_code, f"Sync failed: {error_msg}")
                Clock.schedule_once(lambda dt: error_callback(error_msg), 0)
        threading.Thread(target=_build_and_send, daemon=True).start()
