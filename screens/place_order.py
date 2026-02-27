from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

Builder.load_string('''
<PlaceOrderScreen>:
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
                text: "Product Wise Order"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"

        ScrollView:
            id: scroll_area
            BoxLayout:
                id: product_list
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                spacing: dp(5)

        # Total and Save bar
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            padding: dp(10)
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: 0.2, 0.2, 0.2, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                id: total_label
                text: "Total: Rs. 0.00"
                font_size: sp(16)
                color: 1,1,1,1
                bold: True
            Button:
                text: "Save All"
                size_hint_x: None
                width: dp(100)
                font_size: sp(14)
                background_color: 0.30, 0.69, 0.31, 1
                background_normal: ""
                color: 1,1,1,1
                on_release: root.save_all()
''')


class PlaceOrderScreen(Screen):
    _product_inputs = []

    def on_enter(self):
        self._product_inputs = []
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        product_list = self.ids.product_list
        product_list.clear_widgets()

        companies = app.db.get_companies()
        for company_row in companies:
            company = company_row['company']
            products = app.db.get_products_by_company(company)
            if not products:
                continue

            # Company header
            header = BoxLayout(size_hint_y=None, height=dp(40), padding=[dp(5), dp(5)])
            with header.canvas.before:
                Color(0.10, 0.46, 0.82, 1)
                header._rect = Rectangle(pos=header.pos, size=header.size)
            header.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                        size=lambda s, v: setattr(s._rect, 'size', v))
            header.add_widget(Label(text=f"{company} ({len(products)} items)",
                                     font_size='14sp', color=(1, 1, 1, 1), bold=True,
                                     halign='left', text_size=(None, None)))
            product_list.add_widget(header)

            for p in products:
                row = BoxLayout(size_hint_y=None, height=dp(50), padding=[dp(5), dp(3)], spacing=dp(5))
                info_lbl = Label(text=f"{p['product_name']}\nRs. {p['unit_price']:.2f}",
                                 font_size='12sp', color=(0.13, 0.13, 0.13, 1),
                                 halign='left', size_hint_x=0.5)
                info_lbl.bind(size=lambda *a: setattr(info_lbl, 'text_size', (info_lbl.width, None)))
                row.add_widget(info_lbl)

                qty_input = TextInput(hint_text="Qty", input_filter="int",
                                      multiline=False, size_hint_x=0.2, font_size='13sp')
                disc_input = TextInput(hint_text="Disc", input_filter="float",
                                       multiline=False, size_hint_x=0.2, font_size='13sp')
                net_lbl = Label(text="0", font_size='12sp', color=(0.30, 0.69, 0.31, 1),
                                size_hint_x=0.15, bold=True)

                product_data = dict(p)

                def make_calc(up, qi, di, nl):
                    def calc(*args):
                        try:
                            q = int(qi.text) if qi.text else 0
                            d = float(di.text) if di.text else 0
                            net = (up - d) * q
                            nl.text = f"{net:.0f}"
                        except ValueError:
                            nl.text = "0"
                    return calc

                calc_fn = make_calc(p['unit_price'], qty_input, disc_input, net_lbl)
                qty_input.bind(text=calc_fn)
                disc_input.bind(text=calc_fn)

                row.add_widget(qty_input)
                row.add_widget(disc_input)
                row.add_widget(net_lbl)
                product_list.add_widget(row)

                self._product_inputs.append({
                    'product': product_data,
                    'qty_input': qty_input,
                    'disc_input': disc_input,
                    'net_label': net_lbl
                })

    def save_all(self):
        app = App.get_running_app()
        customer_code = getattr(app, 'current_customer_code', '')
        order_id = getattr(app, '_current_order_id', 'BATCH')
        added = 0
        total = 0

        for entry in self._product_inputs:
            try:
                qty = int(entry['qty_input'].text) if entry['qty_input'].text else 0
            except ValueError:
                qty = 0
            if qty <= 0:
                continue

            try:
                disc = float(entry['disc_input'].text) if entry['disc_input'].text else 0
            except ValueError:
                disc = 0

            p = entry['product']
            net = (p['unit_price'] - disc) * qty
            app.db.add_temp_order(customer_code, p['product_code'], p['product_name'],
                                  p['unit_price'], qty, net, net, order_id, 'Amount', disc)
            added += 1
            total += net

        if added > 0:
            self.ids.total_label.text = f"Total: Rs. {total:.2f}"
            Popup(title="Saved", content=Label(text=f"{added} products added to order"),
                  size_hint=(0.8, 0.25)).open()
        else:
            Popup(title="Info", content=Label(text="Enter quantities for products"),
                  size_hint=(0.8, 0.25)).open()

    def go_back(self):
        App.get_running_app().navigate_to('orders', direction='right')
