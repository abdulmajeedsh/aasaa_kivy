from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

Builder.load_string('''
<CustomersScreen>:
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
                text: "Customers"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"
            Button:
                text: "+ New"
                size_hint_x: None
                width: dp(60)
                font_size: sp(13)
                background_color: 0,0,0,0
                background_normal: ""
                color: 1,1,1,1
                on_release: root.add_customer()
        BoxLayout:
            id: tab_area
            orientation: "vertical"
''')


class CustomerItem(BoxLayout):
    def __init__(self, data, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = [dp(15), dp(5)]
        self.spacing = dp(10)

        left = BoxLayout(orientation='vertical')
        name = Label(text=data['customer_name'], font_size='16sp',
                     color=(0.13, 0.13, 0.13, 1), halign='left', bold=True)
        name.bind(size=lambda *a: setattr(name, 'text_size', (name.width, None)))
        left.add_widget(name)

        contact = data.get('contact', '')
        if contact:
            cl = Label(text=contact, font_size='12sp', color=(0.46, 0.46, 0.46, 1), halign='left')
            cl.bind(size=lambda *a: setattr(cl, 'text_size', (cl.width, None)))
            left.add_widget(cl)
        self.add_widget(left)

        order_count = data.get('Order_Counter', 0)
        if order_count > 0:
            count_lbl = Label(text=str(order_count), font_size='14sp', size_hint_x=None,
                              width=dp(30), color=(0.13, 0.59, 0.95, 1), bold=True)
            self.add_widget(count_lbl)

        chevron = Label(text=">", font_size='20sp', size_hint_x=None,
                        width=dp(30), color=(0.62, 0.62, 0.62, 1))
        self.add_widget(chevron)

        btn = Button(opacity=0, background_color=(0, 0, 0, 0),
                     on_release=lambda x: callback(data))
        self.add_widget(btn)


class CustomersScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        name = getattr(app, 'current_region_name', 'Customers')
        self.ids.title_label.text = f"Customers - {name}"
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        region_code = getattr(app, 'current_region_code', '')
        tab_area = self.ids.tab_area
        tab_area.clear_widgets()

        tp = TabbedPanel(do_default_tab=False, tab_width=dp(150))

        for tab_name, customers in [("Incomplete", app.db.get_incomplete_customers(region_code)),
                                     ("Complete", app.db.get_complete_customers(region_code))]:
            tab = TabbedPanelItem(text=tab_name)
            scroll = ScrollView()
            box = BoxLayout(orientation='vertical', size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            if customers:
                for c in customers:
                    box.add_widget(CustomerItem(c, self.on_customer_tap))
                    sep = BoxLayout(size_hint_y=None, height=dp(1))
                    with sep.canvas.before:
                        Color(0.9, 0.9, 0.9, 1)
                        sep._rect = Rectangle(pos=sep.pos, size=sep.size)
                    sep.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                             size=lambda s, v: setattr(s._rect, 'size', v))
                    box.add_widget(sep)
            else:
                msg = "All customers visited!" if tab_name == "Incomplete" else "No completed visits"
                box.add_widget(Label(text=msg, font_size='16sp',
                                     color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
            scroll.add_widget(box)
            tab.add_widget(scroll)
            tp.add_widget(tab)

        tab_area.add_widget(tp)

    def on_customer_tap(self, data):
        app = App.get_running_app()
        app.current_customer_code = data['customer_code']
        app.current_customer_name = data['customer_name']
        app.navigate_to('orders')

    def add_customer(self):
        app = App.get_running_app()
        app.navigate_to('new_customer')

    def go_back(self):
        app = App.get_running_app()
        if hasattr(app, 'current_parent_region_code') and app.current_parent_region_code:
            app.navigate_to('subregions', direction='right')
        else:
            app.navigate_to('regions', direction='right')
