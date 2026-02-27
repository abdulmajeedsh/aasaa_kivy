import uuid
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

Builder.load_string('''
<OrderScreen>:
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: [dp(10), 0]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: 0.13, 0.59, 0.95, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "<"
                size_hint_x: None
                width: dp(44)
                font_size: sp(22)
                background_color: 0,0,0,0
                background_normal: ""
                color: 1,1,1,1
                on_release: root.go_back()
            Label:
                id: title_label
                text: "Order"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"

        BoxLayout:
            id: tab_area
            orientation: "vertical"

        # Bottom bar
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(5)
            padding: dp(5)
            canvas.before:
                Color:
                    rgba: 0.96, 0.96, 0.96, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "No Order"
                font_size: sp(13)
                background_color: 0.96, 0.26, 0.21, 1
                background_normal: ""
                color: 1,1,1,1
                on_release: root.no_order()
            Button:
                text: "Place Order"
                font_size: sp(13)
                background_color: 0.30, 0.69, 0.31, 1
                background_normal: ""
                color: 1,1,1,1
                on_release: root.place_order()
            Button:
                text: "Close Order"
                font_size: sp(13)
                background_color: 0.13, 0.59, 0.95, 1
                background_normal: ""
                color: 1,1,1,1
                on_release: root.close_order()
''')


class OrderScreen(Screen):
    _order_id = ""
    _timestamp_start = ""

    def on_enter(self):
        app = App.get_running_app()
        cust_name = getattr(app, 'current_customer_name', 'Customer')
        self.ids.title_label.text = f"Order - {cust_name}"
        self._order_id = str(uuid.uuid4().hex[:12].upper())
        self._timestamp_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        customer_code = getattr(app, 'current_customer_code', '')
        tab_area = self.ids.tab_area
        tab_area.clear_widgets()

        tp = TabbedPanel(do_default_tab=False, tab_width=dp(150))

        # Products tab
        prod_tab = TabbedPanelItem(text="Products")
        prod_layout = BoxLayout(orientation='vertical', spacing=dp(5))

        # Search bar
        search_box = BoxLayout(size_hint_y=None, height=dp(44), padding=[dp(10), dp(5)])
        search_input = TextInput(hint_text="Search products...", multiline=False, font_size='14sp')
        search_input.bind(text=lambda inst, val: self._filter_products(val, prod_list_box))
        search_box.add_widget(search_input)
        prod_layout.add_widget(search_box)

        scroll = ScrollView()
        prod_list_box = BoxLayout(orientation='vertical', size_hint_y=None)
        prod_list_box.bind(minimum_height=prod_list_box.setter('height'))
        self._populate_products(prod_list_box, app.db.get_all_products())
        scroll.add_widget(prod_list_box)
        prod_layout.add_widget(scroll)
        prod_tab.add_widget(prod_layout)

        # Added products tab
        added_tab = TabbedPanelItem(text="Added Products")
        self._added_tab_content = BoxLayout(orientation='vertical')
        self._refresh_added(customer_code)
        added_tab.add_widget(self._added_tab_content)

        tp.add_widget(prod_tab)
        tp.add_widget(added_tab)
        tab_area.add_widget(tp)

    def _populate_products(self, box, products):
        box.clear_widgets()
        for i, p in enumerate(products):
            row = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(10), dp(5)], spacing=dp(5))
            bg_color = (1, 1, 1, 1) if i % 2 == 0 else (0.96, 0.96, 0.96, 1)
            with row.canvas.before:
                Color(*bg_color)
                row._rect = Rectangle(pos=row.pos, size=row.size)
            row.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                     size=lambda s, v: setattr(s._rect, 'size', v))

            info = BoxLayout(orientation='vertical')
            nl = Label(text=p['product_name'], font_size='14sp', color=(0.13, 0.13, 0.13, 1),
                       halign='left', bold=True)
            nl.bind(size=lambda *a: setattr(nl, 'text_size', (nl.width, None)))
            info.add_widget(nl)
            cl = Label(text=f"{p.get('company', '')} | Rs. {p.get('unit_price', 0):.2f}",
                       font_size='11sp', color=(0.46, 0.46, 0.46, 1), halign='left')
            cl.bind(size=lambda *a: setattr(cl, 'text_size', (cl.width, None)))
            info.add_widget(cl)
            row.add_widget(info)

            add_btn = Button(text="Add", size_hint_x=None, width=dp(55),
                             font_size='13sp', background_color=(0.13, 0.59, 0.95, 1),
                             background_normal="", color=(1, 1, 1, 1))
            product_data = dict(p)
            add_btn.bind(on_release=lambda inst, pd=product_data: self._show_add_dialog(pd))
            row.add_widget(add_btn)
            box.add_widget(row)

    def _filter_products(self, query, box):
        app = App.get_running_app()
        if query.strip():
            products = app.db.search_products(query.strip())
        else:
            products = app.db.get_all_products()
        self._populate_products(box, products)

    def _show_add_dialog(self, product):
        app = App.get_running_app()
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=product['product_name'], font_size='16sp',
                                  color=(0.13, 0.13, 0.13, 1), size_hint_y=None, height=dp(30), bold=True))
        content.add_widget(Label(text=f"Unit Price: Rs. {product['unit_price']:.2f}",
                                  font_size='14sp', color=(0.46, 0.46, 0.46, 1),
                                  size_hint_y=None, height=dp(25)))

        qty_input = TextInput(hint_text="Quantity", input_filter="int",
                              multiline=False, size_hint_y=None, height=dp(40), font_size='15sp')
        disc_input = TextInput(hint_text="Discount", input_filter="float",
                               multiline=False, size_hint_y=None, height=dp(40), font_size='15sp')
        disc_type = Spinner(text="Amount", values=["Amount", "Percentage"],
                            size_hint_y=None, height=dp(40), font_size='14sp')
        net_label = Label(text="Net: Rs. 0.00", font_size='14sp',
                          color=(0.30, 0.69, 0.31, 1), size_hint_y=None, height=dp(25), bold=True)

        def calc_net(*args):
            try:
                qty = int(qty_input.text) if qty_input.text else 0
                disc = float(disc_input.text) if disc_input.text else 0
                up = product['unit_price']
                if disc_type.text == "Percentage":
                    disc_amt = up * disc / 100
                else:
                    disc_amt = disc
                net = (up - disc_amt) * qty
                net_label.text = f"Net: Rs. {net:.2f}"
            except (ValueError, ZeroDivisionError):
                net_label.text = "Net: Rs. 0.00"

        qty_input.bind(text=calc_net)
        disc_input.bind(text=calc_net)
        disc_type.bind(text=calc_net)

        content.add_widget(qty_input)
        content.add_widget(disc_input)
        content.add_widget(disc_type)
        content.add_widget(net_label)

        popup = Popup(title="Add Product", content=content, size_hint=(0.9, 0.55))

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        add_btn = Button(text="Add to Order", background_color=(0.13, 0.59, 0.95, 1),
                         background_normal="", color=(1, 1, 1, 1))

        def do_add(instance):
            try:
                qty = int(qty_input.text) if qty_input.text else 0
                if qty <= 0:
                    return
                disc = float(disc_input.text) if disc_input.text else 0
                up = product['unit_price']
                if disc_type.text == "Percentage":
                    disc_amt = up * disc / 100
                else:
                    disc_amt = disc
                net = (up - disc_amt) * qty
                total = net
                customer_code = getattr(app, 'current_customer_code', '')
                app.db.add_temp_order(customer_code, product['product_code'],
                                      product['product_name'], up, qty, net, total,
                                      self._order_id, disc_type.text, disc)
                popup.dismiss()
                self._refresh_added(customer_code)
            except ValueError:
                pass

        add_btn.bind(on_release=do_add)
        cancel_btn = Button(text="Cancel", background_color=(0.62, 0.62, 0.62, 1),
                            background_normal="", color=(1, 1, 1, 1))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(add_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        popup.open()

    def _refresh_added(self, customer_code):
        app = App.get_running_app()
        if not hasattr(self, '_added_tab_content'):
            return
        self._added_tab_content.clear_widgets()

        orders = app.db.get_temp_orders(customer_code)
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        total = 0
        for o in orders:
            row = BoxLayout(size_hint_y=None, height=dp(55), padding=[dp(10), dp(3)], spacing=dp(5))
            info = BoxLayout(orientation='vertical')
            nl = Label(text=o['product_name'], font_size='14sp', color=(0.13, 0.13, 0.13, 1),
                       halign='left', bold=True)
            nl.bind(size=lambda *a: setattr(nl, 'text_size', (nl.width, None)))
            info.add_widget(nl)
            dl = Label(text=f"Qty: {o['quantity']} | Disc: {o.get('Discount', 0)} | Net: Rs. {o['net_amount']:.2f}",
                       font_size='11sp', color=(0.46, 0.46, 0.46, 1), halign='left')
            dl.bind(size=lambda *a: setattr(dl, 'text_size', (dl.width, None)))
            info.add_widget(dl)
            row.add_widget(info)

            rm_btn = Button(text="X", size_hint_x=None, width=dp(40),
                            font_size='14sp', background_color=(0.96, 0.26, 0.21, 1),
                            background_normal="", color=(1, 1, 1, 1))
            temp_id = o['id']
            rm_btn.bind(on_release=lambda inst, tid=temp_id: self._remove_temp(tid, customer_code))
            row.add_widget(rm_btn)
            box.add_widget(row)
            total += o.get('net_amount', 0)

        if not orders:
            box.add_widget(Label(text="No products added yet", font_size='16sp',
                                  color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))

        scroll.add_widget(box)
        self._added_tab_content.add_widget(scroll)

        # Total bar
        total_bar = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(15), dp(5)])
        with total_bar.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            total_bar._rect = Rectangle(pos=total_bar.pos, size=total_bar.size)
        total_bar.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                       size=lambda s, v: setattr(s._rect, 'size', v))
        total_bar.add_widget(Label(text=f"Total: Rs. {total:.2f}", font_size='16sp',
                                    color=(1, 1, 1, 1), bold=True))
        self._added_tab_content.add_widget(total_bar)

    def _remove_temp(self, temp_id, customer_code):
        app = App.get_running_app()
        app.db.remove_temp_order(temp_id)
        self._refresh_added(customer_code)

    def place_order(self):
        app = App.get_running_app()
        customer_code = getattr(app, 'current_customer_code', '')
        temp_orders = app.db.get_temp_orders(customer_code)
        if not temp_orders:
            self._show_msg("No products to place order")
            return

        branch_code = app.prefs.get('branch_code', '')
        lat, lon = app.gps.get_location()
        android_order_id = str(uuid.uuid4().hex[:16].upper())

        for t in temp_orders:
            order_data = {
                'customer_code': customer_code,
                'product_code': t['product_code'],
                'product_name': t['product_name'],
                'unit_price': t['unit_price'],
                'discount_amount': t.get('Discount', 0),
                'discount_type': t.get('Disc_Type', ''),
                'quantity': t['quantity'],
                'net_amount': t['net_amount'],
                'total_amount': t['total_amount'],
                'branch_code': branch_code,
                'order_id': self._order_id,
                'SyncBit': 0, 'CloseBit': 0, 'No_Order': 0,
                'Reason': '', 'Immediate': 0,
                'X_Co': lat, 'Y_Co': lon,
                'X_Co_Close': 0, 'Y_Co_Close': 0,
                'Edit_Mode': 0,
                'AndroidOrderID': android_order_id,
                'TimeStamp_Start': self._timestamp_start,
                'TimeStamp_End': '',
                'TimeStamp_Start_Customer': self._timestamp_start
            }
            app.db.insert_order(order_data)

        app.db.clear_temp_orders(customer_code)
        app.db.increment_order_counter(customer_code)
        self._order_id = str(uuid.uuid4().hex[:12].upper())
        self._refresh_added(customer_code)
        self._show_msg("Order placed successfully!")

    def close_order(self):
        app = App.get_running_app()
        customer_code = getattr(app, 'current_customer_code', '')
        lat, lon = app.gps.get_location()
        timestamp_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        orders = app.db.get_orders_by_customer(customer_code)
        if not orders:
            self._show_msg("No orders to close")
            return

        # Close all orders for this customer
        for o in orders:
            if o.get('CloseBit', 0) == 0:
                app.db.close_order(customer_code, o['order_id'], lat, lon, timestamp_end)

        app.db.set_customer_complete(customer_code, 1)
        self._show_msg("Order closed successfully!")
        app.navigate_to('customers', direction='right')

    def no_order(self):
        app = App.get_running_app()
        app.navigate_to('no_order')

    def _show_msg(self, msg):
        Popup(title="Info", content=Label(text=msg, text_size=(dp(250), None)),
              size_hint=(0.8, 0.3)).open()

    def go_back(self):
        App.get_running_app().navigate_to('customers', direction='right')
