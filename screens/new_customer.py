import uuid
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp

Builder.load_string('''
<NewCustomerScreen>:
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
                text: "New Customer"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"

        ScrollView:
            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(20)
                spacing: dp(15)

                Label:
                    text: "Personal Info"
                    font_size: sp(18)
                    bold: True
                    color: 0.13, 0.59, 0.95, 1
                    size_hint_y: None
                    height: dp(30)
                    halign: "left"
                    text_size: self.size

                TextInput:
                    id: txt_name
                    hint_text: "Customer Name *"
                    size_hint_y: None
                    height: dp(44)
                    multiline: False
                    font_size: sp(15)
                    padding: [dp(10), dp(10)]

                TextInput:
                    id: txt_contact
                    hint_text: "Contact Number"
                    size_hint_y: None
                    height: dp(44)
                    multiline: False
                    font_size: sp(15)
                    input_filter: "int"
                    padding: [dp(10), dp(10)]

                TextInput:
                    id: txt_address
                    hint_text: "Address"
                    size_hint_y: None
                    height: dp(80)
                    multiline: True
                    font_size: sp(15)
                    padding: [dp(10), dp(10)]

                Label:
                    text: "Business Info"
                    font_size: sp(18)
                    bold: True
                    color: 0.13, 0.59, 0.95, 1
                    size_hint_y: None
                    height: dp(30)
                    halign: "left"
                    text_size: self.size

                Spinner:
                    id: spn_route
                    text: "Select Route"
                    size_hint_y: None
                    height: dp(44)
                    font_size: sp(15)

                Spinner:
                    id: spn_region
                    text: "Select Region"
                    size_hint_y: None
                    height: dp(44)
                    font_size: sp(15)

                Spinner:
                    id: spn_city
                    text: "Select City"
                    size_hint_y: None
                    height: dp(44)
                    font_size: sp(15)

                Label:
                    text: "License Info"
                    font_size: sp(18)
                    bold: True
                    color: 0.13, 0.59, 0.95, 1
                    size_hint_y: None
                    height: dp(30)
                    halign: "left"
                    text_size: self.size

                Spinner:
                    id: spn_license
                    text: "Select License Type"
                    size_hint_y: None
                    height: dp(44)
                    font_size: sp(15)

                TextInput:
                    id: txt_license_num
                    hint_text: "License Number"
                    size_hint_y: None
                    height: dp(44)
                    multiline: False
                    font_size: sp(15)
                    padding: [dp(10), dp(10)]

                Widget:
                    size_hint_y: None
                    height: dp(10)

                Button:
                    text: "Save Customer"
                    size_hint_y: None
                    height: dp(50)
                    font_size: sp(16)
                    bold: True
                    background_color: 0.13, 0.59, 0.95, 1
                    background_normal: ""
                    color: 1,1,1,1
                    on_release: root.save_customer()

                Widget:
                    size_hint_y: None
                    height: dp(20)
''')


class NewCustomerScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        # Populate spinners
        routes = app.db.get_all_routes_ref()
        self.ids.spn_route.values = [r['route_name'] for r in routes] if routes else ["No routes"]

        regions = app.db.get_all_regions_ref()
        self.ids.spn_region.values = [r['region_name'] for r in regions] if regions else ["No regions"]

        cities = app.db.get_all_cities_ref()
        self.ids.spn_city.values = [c['city_name'] for c in cities] if cities else ["No cities"]

        licenses = app.db.get_license_types()
        self.ids.spn_license.values = [l['license_name'] for l in licenses] if licenses else ["N/A"]

    def save_customer(self):
        app = App.get_running_app()
        name = self.ids.txt_name.text.strip()
        if not name:
            self._show_msg("Customer name is required")
            return

        lat, lon = app.gps.get_location()
        customer_code = f"NC-{uuid.uuid4().hex[:8].upper()}"
        region_code = getattr(app, 'current_region_code', '')

        data = {
            'customer_code': customer_code,
            'customer_name': name,
            'contact': self.ids.txt_contact.text.strip(),
            'address': self.ids.txt_address.text.strip(),
            'region_code': region_code,
            'sub_region_code': region_code,
            'route_code': getattr(app, 'current_route_code', ''),
            'latitude': lat,
            'longitude': lon
        }
        app.db.add_new_customer(data)

        # Save license if provided
        license_num = self.ids.txt_license_num.text.strip()
        if license_num:
            app.db.save_customer_license(customer_code,
                                         self.ids.spn_license.text, license_num)

        # Sync to server
        app.api.sync_new_customer(data,
                                  callback=lambda d: None,
                                  error_callback=lambda e: None)

        self._show_msg("Customer saved successfully")
        self._clear_form()

    def _clear_form(self):
        self.ids.txt_name.text = ""
        self.ids.txt_contact.text = ""
        self.ids.txt_address.text = ""
        self.ids.txt_license_num.text = ""

    def _show_msg(self, msg):
        Popup(title="Info", content=Label(text=msg, text_size=(dp(250), None)),
              size_hint=(0.8, 0.3)).open()

    def go_back(self):
        App.get_running_app().navigate_to('customers', direction='right')
