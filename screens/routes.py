from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import StringProperty

Builder.load_string('''
<RoutesScreen>:
    BoxLayout:
        orientation: "vertical"
        # Toolbar
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
                text: "Routes"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"
            Button:
                text: "Refresh"
                size_hint_x: None
                width: dp(70)
                font_size: sp(13)
                background_color: 0,0,0,0
                background_normal: ""
                color: 1,1,1,1
                on_release: root.load_data()

        # Tabs
        BoxLayout:
            id: tab_area
            orientation: "vertical"
''')


class RouteItem(BoxLayout):
    def __init__(self, route_data, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(15), dp(5)]
        self.spacing = dp(10)
        self.route_data = route_data

        left = BoxLayout(orientation='vertical')
        name_label = Label(text=route_data['route_name'], font_size='16sp',
                           color=(0.13, 0.13, 0.13, 1), halign='left',
                           text_size=(None, None), bold=True)
        name_label.bind(size=lambda *a: setattr(name_label, 'text_size', (name_label.width, None)))
        left.add_widget(name_label)
        self.add_widget(left)

        if route_data.get('MandatoryBit', 0) == 1:
            badge = Label(text="Mandatory", font_size='11sp', size_hint_x=None,
                          width=dp(70), color=(0.96, 0.26, 0.21, 1), bold=True)
            self.add_widget(badge)

        chevron = Label(text=">", font_size='20sp', size_hint_x=None,
                        width=dp(30), color=(0.62, 0.62, 0.62, 1))
        self.add_widget(chevron)

        btn = Button(opacity=0, background_color=(0, 0, 0, 0), on_release=lambda x: callback(route_data))
        self.add_widget(btn)


class RoutesScreen(Screen):
    def on_enter(self):
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        branch_code = app.prefs.get('branch_code', '')

        tab_area = self.ids.tab_area
        tab_area.clear_widgets()

        tp = TabbedPanel(do_default_tab=False, tab_width=self.width / 2 if self.width > 0 else dp(150))

        # Incomplete tab
        inc_tab = TabbedPanelItem(text="Incomplete")
        inc_scroll = ScrollView()
        inc_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(1))
        inc_box.bind(minimum_height=inc_box.setter('height'))

        incomplete = app.db.get_incomplete_routes(branch_code)
        if incomplete:
            for r in incomplete:
                inc_box.add_widget(RouteItem(r, self.on_route_tap))
                sep = BoxLayout(size_hint_y=None, height=dp(1))
                sep.canvas.before.add(
                    type('Color', (), {'rgba': (0.9, 0.9, 0.9, 1)})() if False else BoxLayout()
                )
                # Simple separator
                from kivy.graphics import Color, Rectangle
                with sep.canvas.before:
                    Color(0.9, 0.9, 0.9, 1)
                    sep._rect = Rectangle(pos=sep.pos, size=sep.size)
                sep.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                         size=lambda s, v: setattr(s._rect, 'size', v))
                inc_box.add_widget(sep)
        else:
            inc_box.add_widget(Label(text="All routes completed!", font_size='16sp',
                                     color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
        inc_scroll.add_widget(inc_box)
        inc_tab.add_widget(inc_scroll)

        # Complete tab
        comp_tab = TabbedPanelItem(text="Complete")
        comp_scroll = ScrollView()
        comp_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(1))
        comp_box.bind(minimum_height=comp_box.setter('height'))

        complete = app.db.get_complete_routes(branch_code)
        if complete:
            for r in complete:
                comp_box.add_widget(RouteItem(r, self.on_route_tap))
        else:
            comp_box.add_widget(Label(text="No completed routes", font_size='16sp',
                                      color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
        comp_scroll.add_widget(comp_box)
        comp_tab.add_widget(comp_scroll)

        tp.add_widget(inc_tab)
        tp.add_widget(comp_tab)
        tab_area.add_widget(tp)

    def on_route_tap(self, route_data):
        app = App.get_running_app()
        app.current_route_code = route_data['route_code']
        app.current_route_name = route_data['route_name']
        app.navigate_to('regions')

    def go_back(self):
        App.get_running_app().navigate_to('main_dashboard', direction='right')
