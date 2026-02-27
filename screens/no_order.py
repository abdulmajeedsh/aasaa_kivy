import uuid
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp

Builder.load_string('''
<NoOrderScreen>:
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
                text: "No Order Reason"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"

        BoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(15)

            Label:
                text: "Please provide a reason for not placing an order:"
                font_size: sp(15)
                color: 0.13, 0.13, 0.13, 1
                size_hint_y: None
                height: dp(40)
                halign: "left"
                text_size: self.size

            TextInput:
                id: txt_reason
                hint_text: "Enter reason..."
                size_hint_y: None
                height: dp(120)
                multiline: True
                font_size: sp(15)
                padding: [dp(10), dp(10)]

            BoxLayout:
                size_hint_y: None
                height: dp(44)
                spacing: dp(10)
                CheckBox:
                    id: chk_immediate
                    size_hint_x: None
                    width: dp(44)
                    active: False
                Label:
                    text: "Immediate Delivery Required"
                    font_size: sp(14)
                    color: 0.13, 0.13, 0.13, 1
                    halign: "left"
                    text_size: self.size
                    valign: "center"

            Button:
                text: "Submit"
                size_hint_y: None
                height: dp(50)
                font_size: sp(16)
                bold: True
                background_color: 0.96, 0.26, 0.21, 1
                background_normal: ""
                color: 1, 1, 1, 1
                on_release: root.submit()

            Widget:
''')


class NoOrderScreen(Screen):
    def submit(self):
        app = App.get_running_app()
        reason = self.ids.txt_reason.text.strip()
        if not reason:
            Popup(title="Error", content=Label(text="Please enter a reason"),
                  size_hint=(0.8, 0.25)).open()
            return

        customer_code = getattr(app, 'current_customer_code', '')
        branch_code = app.prefs.get('branch_code', '')
        lat, lon = app.gps.get_location()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        immediate = 1 if self.ids.chk_immediate.active else 0

        order_data = {
            'customer_code': customer_code,
            'product_code': '', 'product_name': '',
            'unit_price': 0, 'discount_amount': 0, 'discount_type': '',
            'quantity': 0, 'net_amount': 0, 'total_amount': 0,
            'branch_code': branch_code,
            'order_id': f"NO-{uuid.uuid4().hex[:8].upper()}",
            'SyncBit': 0, 'CloseBit': 1, 'No_Order': 1,
            'Reason': reason, 'Immediate': immediate,
            'X_Co': lat, 'Y_Co': lon,
            'X_Co_Close': lat, 'Y_Co_Close': lon,
            'Edit_Mode': 0,
            'AndroidOrderID': uuid.uuid4().hex[:16].upper(),
            'TimeStamp_Start': now, 'TimeStamp_End': now,
            'TimeStamp_Start_Customer': now
        }
        app.db.insert_order(order_data)
        app.db.set_customer_complete(customer_code, 1)

        self.ids.txt_reason.text = ""
        self.ids.chk_immediate.active = False

        Popup(title="Submitted", content=Label(text="No-order recorded"),
              size_hint=(0.8, 0.25)).open()
        app.navigate_to('customers', direction='right')

    def go_back(self):
        App.get_running_app().navigate_to('orders', direction='right')
