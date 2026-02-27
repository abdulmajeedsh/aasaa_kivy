from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

Builder.load_string('''
<CompanySalesScreen>:
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
                text: "Company Wise Sales"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"
        ScrollView:
            BoxLayout:
                id: sales_list
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                spacing: dp(10)
''')


class CompanySalesScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        sales_list = self.ids.sales_list
        sales_list.clear_widgets()

        data = app.db.get_company_wise_sales()
        if not data:
            sales_list.add_widget(Label(text="No sales data available", font_size='16sp',
                                        color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
            return

        for s in data:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100),
                             padding=dp(10), spacing=dp(5))
            with card.canvas.before:
                Color(1, 1, 1, 1)
                card._rect = Rectangle(pos=card.pos, size=card.size)
            card.bind(pos=lambda c, v: setattr(c._rect, 'pos', v),
                      size=lambda c, v: setattr(c._rect, 'size', v))

            company = s.get('company', '')
            target = float(s.get('target_amount', 0))
            actual = float(s.get('actual_amount', 0))
            pct = (actual / target * 100) if target > 0 else 0

            if pct >= 100:
                pct_color = (0.30, 0.69, 0.31, 1)
            elif pct >= 50:
                pct_color = (1.0, 0.76, 0.03, 1)
            else:
                pct_color = (0.96, 0.26, 0.21, 1)

            header = BoxLayout(size_hint_y=None, height=dp(25))
            header.add_widget(Label(text=company, font_size='15sp',
                                     color=(0.13, 0.13, 0.13, 1), halign='left', bold=True,
                                     text_size=(None, None)))
            header.add_widget(Label(text=f"{pct:.1f}%", font_size='14sp',
                                     color=pct_color, halign='right', bold=True,
                                     size_hint_x=None, width=dp(60)))
            card.add_widget(header)

            pb = ProgressBar(max=target if target > 0 else 1, value=min(actual, target),
                             size_hint_y=None, height=dp(20))
            card.add_widget(pb)

            amounts = BoxLayout(size_hint_y=None, height=dp(20))
            amounts.add_widget(Label(text=f"Actual: Rs. {actual:.0f}", font_size='12sp',
                                      color=(0.46, 0.46, 0.46, 1), halign='left'))
            amounts.add_widget(Label(text=f"Target: Rs. {target:.0f}", font_size='12sp',
                                      color=(0.46, 0.46, 0.46, 1), halign='right'))
            card.add_widget(amounts)
            sales_list.add_widget(card)

    def go_back(self):
        App.get_running_app().navigate_to('main_dashboard', direction='right')
