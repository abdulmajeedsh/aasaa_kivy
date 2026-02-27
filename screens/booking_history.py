from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

Builder.load_string('''
<BookingHistoryScreen>:
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
                text: "Booking History"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"
        BoxLayout:
            id: tab_area
            orientation: "vertical"
''')


class BookingHistoryScreen(Screen):
    def on_enter(self):
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        tab_area = self.ids.tab_area
        tab_area.clear_widgets()

        tp = TabbedPanel(do_default_tab=False, tab_width=dp(150))

        # Today's bookings
        today_tab = TabbedPanelItem(text="Today")
        today_scroll = ScrollView()
        today_box = BoxLayout(orientation='vertical', size_hint_y=None)
        today_box.bind(minimum_height=today_box.setter('height'))

        today_data = app.db.get_today_bookings()
        total_orders = 0
        total_amount = 0

        if today_data:
            for t in today_data:
                row = BoxLayout(size_hint_y=None, height=dp(55), padding=[dp(10), dp(5)])
                info = BoxLayout(orientation='vertical')
                nl = Label(text=t.get('customer_name', t.get('customer_code', '')),
                           font_size='14sp', color=(0.13, 0.13, 0.13, 1), halign='left', bold=True)
                nl.bind(size=lambda *a: setattr(nl, 'text_size', (nl.width, None)))
                info.add_widget(nl)
                oc = t.get('order_count', 0)
                ta = t.get('total_amount', 0)
                dl = Label(text=f"Orders: {oc} | Rs. {ta:.2f}",
                           font_size='11sp', color=(0.46, 0.46, 0.46, 1), halign='left')
                dl.bind(size=lambda *a: setattr(dl, 'text_size', (dl.width, None)))
                info.add_widget(dl)
                row.add_widget(info)
                today_box.add_widget(row)
                total_orders += oc
                total_amount += ta
                sep = BoxLayout(size_hint_y=None, height=dp(1))
                with sep.canvas.before:
                    Color(0.9, 0.9, 0.9, 1)
                    sep._rect = Rectangle(pos=sep.pos, size=sep.size)
                sep.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                         size=lambda s, v: setattr(s._rect, 'size', v))
                today_box.add_widget(sep)

            # Summary
            summary = BoxLayout(size_hint_y=None, height=dp(45), padding=[dp(10), dp(5)])
            with summary.canvas.before:
                Color(0.2, 0.2, 0.2, 1)
                summary._rect = Rectangle(pos=summary.pos, size=summary.size)
            summary.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                         size=lambda s, v: setattr(s._rect, 'size', v))
            summary.add_widget(Label(text=f"Total: {total_orders} orders | Rs. {total_amount:.2f}",
                                      font_size='14sp', color=(1, 1, 1, 1), bold=True))
            today_box.add_widget(summary)
        else:
            today_box.add_widget(Label(text="No bookings today", font_size='16sp',
                                       color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
        today_scroll.add_widget(today_box)
        today_tab.add_widget(today_scroll)

        # Monthly
        monthly_tab = TabbedPanelItem(text="Monthly")
        monthly_scroll = ScrollView()
        monthly_box = BoxLayout(orientation='vertical', size_hint_y=None)
        monthly_box.bind(minimum_height=monthly_box.setter('height'))

        monthly_data = app.db.get_monthly_bookings()
        if monthly_data:
            for m in monthly_data:
                row = BoxLayout(size_hint_y=None, height=dp(55), padding=[dp(10), dp(5)])
                info = BoxLayout(orientation='vertical')
                nl = Label(text=m.get('month', ''), font_size='15sp',
                           color=(0.13, 0.13, 0.13, 1), halign='left', bold=True)
                nl.bind(size=lambda *a: setattr(nl, 'text_size', (nl.width, None)))
                info.add_widget(nl)
                dl = Label(text=f"Orders: {m.get('total_orders', 0)} | Rs. {m.get('total_amount', 0):.2f}",
                           font_size='12sp', color=(0.46, 0.46, 0.46, 1), halign='left')
                dl.bind(size=lambda *a: setattr(dl, 'text_size', (dl.width, None)))
                info.add_widget(dl)
                row.add_widget(info)
                monthly_box.add_widget(row)
        else:
            monthly_box.add_widget(Label(text="No monthly data", font_size='16sp',
                                         color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
        monthly_scroll.add_widget(monthly_box)
        monthly_tab.add_widget(monthly_scroll)

        tp.add_widget(today_tab)
        tp.add_widget(monthly_tab)
        tab_area.add_widget(tp)

    def go_back(self):
        App.get_running_app().navigate_to('main_dashboard', direction='right')
