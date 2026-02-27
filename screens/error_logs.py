from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

Builder.load_string('''
<ErrorLogsScreen>:
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
                text: "Error Logs"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"
            Button:
                text: "Clear"
                size_hint_x: None
                width: dp(55)
                font_size: sp(13)
                background_color: 0,0,0,0
                background_normal: ""
                color: 1,1,1,1
                on_release: root.clear_logs()
        ScrollView:
            BoxLayout:
                id: logs_list
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(5)
                spacing: dp(2)
''')


class ErrorLogsScreen(Screen):
    def on_enter(self):
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        logs_list = self.ids.logs_list
        logs_list.clear_widgets()

        logs = app.db.get_error_logs()
        if not logs:
            logs_list.add_widget(Label(text="No error logs", font_size='16sp',
                                       color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
            return

        for log in logs:
            row = BoxLayout(size_hint_y=None, height=dp(65), padding=[dp(10), dp(5)], spacing=dp(5))
            with row.canvas.before:
                Color(1, 0.97, 0.97, 1)
                row._rect = Rectangle(pos=row.pos, size=row.size)
            row.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                     size=lambda s, v: setattr(s._rect, 'size', v))

            info = BoxLayout(orientation='vertical')
            ts = Label(text=f"{log.get('timestamp', '')} | {log.get('branch_code', '')}",
                       font_size='11sp', color=(0.96, 0.26, 0.21, 1), halign='left')
            ts.bind(size=lambda *a: setattr(ts, 'text_size', (ts.width, None)))
            info.add_widget(ts)

            err_text = log.get('error_details', '')
            truncated = err_text[:80] + "..." if len(err_text) > 80 else err_text
            el = Label(text=truncated, font_size='12sp', color=(0.13, 0.13, 0.13, 1), halign='left')
            el.bind(size=lambda *a: setattr(el, 'text_size', (el.width, None)))
            info.add_widget(el)
            row.add_widget(info)

            view_btn = Button(text="...", size_hint_x=None, width=dp(40),
                              font_size='16sp', background_color=(0.62, 0.62, 0.62, 1),
                              background_normal="", color=(1, 1, 1, 1))
            full_err = str(err_text)
            view_btn.bind(on_release=lambda inst, e=full_err: self._show_full(e))
            row.add_widget(view_btn)
            logs_list.add_widget(row)

    def _show_full(self, error_text):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        scroll = ScrollView()
        lbl = Label(text=error_text, font_size='13sp', color=(0.13, 0.13, 0.13, 1),
                    size_hint_y=None, text_size=(dp(280), None))
        lbl.bind(texture_size=lbl.setter('size'))
        scroll.add_widget(lbl)
        content.add_widget(scroll)
        Popup(title="Error Details", content=content, size_hint=(0.9, 0.6)).open()

    def clear_logs(self):
        app = App.get_running_app()
        app.db.clear_error_logs()
        self.load_data()

    def go_back(self):
        App.get_running_app().navigate_to('main_dashboard', direction='right')
