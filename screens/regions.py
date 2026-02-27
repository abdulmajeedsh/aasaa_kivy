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
<RegionsScreen>:
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
                text: "Regions"
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


class RegionItem(BoxLayout):
    def __init__(self, data, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(15), dp(5)]
        self.spacing = dp(10)

        left = BoxLayout(orientation='vertical')
        name = Label(text=data['region_name'], font_size='16sp',
                     color=(0.13, 0.13, 0.13, 1), halign='left', bold=True)
        name.bind(size=lambda *a: setattr(name, 'text_size', (name.width, None)))
        left.add_widget(name)
        self.add_widget(left)

        if data.get('MandatoryBit', 0) == 1:
            badge = Label(text="Mandatory", font_size='11sp', size_hint_x=None,
                          width=dp(70), color=(0.96, 0.26, 0.21, 1), bold=True)
            self.add_widget(badge)

        chevron = Label(text=">", font_size='20sp', size_hint_x=None,
                        width=dp(30), color=(0.62, 0.62, 0.62, 1))
        self.add_widget(chevron)

        btn = Button(opacity=0, background_color=(0, 0, 0, 0),
                     on_release=lambda x: callback(data))
        self.add_widget(btn)


class RegionsScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        route_name = getattr(app, 'current_route_name', 'Regions')
        self.ids.title_label.text = f"Regions - {route_name}"
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        route_code = getattr(app, 'current_route_code', '')
        tab_area = self.ids.tab_area
        tab_area.clear_widgets()

        tp = TabbedPanel(do_default_tab=False, tab_width=dp(150))

        for tab_name, regions in [("Incomplete", app.db.get_incomplete_regions(route_code)),
                                   ("Complete", app.db.get_complete_regions(route_code))]:
            tab = TabbedPanelItem(text=tab_name)
            scroll = ScrollView()
            box = BoxLayout(orientation='vertical', size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            if regions:
                for r in regions:
                    box.add_widget(RegionItem(r, self.on_region_tap))
                    sep = BoxLayout(size_hint_y=None, height=dp(1))
                    with sep.canvas.before:
                        Color(0.9, 0.9, 0.9, 1)
                        sep._rect = Rectangle(pos=sep.pos, size=sep.size)
                    sep.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                             size=lambda s, v: setattr(s._rect, 'size', v))
                    box.add_widget(sep)
            else:
                msg = "All regions completed!" if tab_name == "Incomplete" else "No completed regions"
                box.add_widget(Label(text=msg, font_size='16sp',
                                     color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
            scroll.add_widget(box)
            tab.add_widget(scroll)
            tp.add_widget(tab)

        tab_area.add_widget(tp)

    def on_region_tap(self, data):
        app = App.get_running_app()
        region_code = data['region_code']

        if app.db.has_subregions(region_code):
            app.current_parent_region_code = region_code
            app.current_region_name = data['region_name']
            app.navigate_to('subregions')
        else:
            app.current_region_code = region_code
            app.current_region_name = data['region_name']
            app.navigate_to('customers')

    def go_back(self):
        App.get_running_app().navigate_to('routes', direction='right')
