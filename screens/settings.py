from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp

Builder.load_string('''
<SettingsScreen>:
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
                text: "Settings"
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
                spacing: dp(20)

                # Product View Mode
                Label:
                    text: "Product View Mode"
                    font_size: sp(16)
                    bold: True
                    color: 0.13, 0.13, 0.13, 1
                    size_hint_y: None
                    height: dp(30)
                    halign: "left"
                    text_size: self.size

                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(10)
                    CheckBox:
                        id: chk_standard
                        group: "view_mode"
                        active: True
                        size_hint_x: None
                        width: dp(44)
                        on_active: root.on_view_mode('standard', self.active)
                    Label:
                        text: "Standard View"
                        font_size: sp(14)
                        color: 0.13, 0.13, 0.13, 1
                        halign: "left"
                        text_size: self.size
                        valign: "center"

                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(10)
                    CheckBox:
                        id: chk_classical
                        group: "view_mode"
                        active: False
                        size_hint_x: None
                        width: dp(44)
                        on_active: root.on_view_mode('classical', self.active)
                    Label:
                        text: "Classical View"
                        font_size: sp(14)
                        color: 0.13, 0.13, 0.13, 1
                        halign: "left"
                        text_size: self.size
                        valign: "center"

                # Separator
                BoxLayout:
                    size_hint_y: None
                    height: dp(1)
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.9, 0.9, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size

                # Auto Sync
                Label:
                    text: "Auto Sync"
                    font_size: sp(16)
                    bold: True
                    color: 0.13, 0.13, 0.13, 1
                    size_hint_y: None
                    height: dp(30)
                    halign: "left"
                    text_size: self.size

                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(10)
                    Switch:
                        id: sw_auto_sync
                        active: True
                        size_hint_x: None
                        width: dp(80)
                        on_active: root.on_auto_sync(self.active)
                    Label:
                        text: "Enable Auto Sync"
                        font_size: sp(14)
                        color: 0.13, 0.13, 0.13, 1
                        halign: "left"
                        text_size: self.size
                        valign: "center"

                # Separator
                BoxLayout:
                    size_hint_y: None
                    height: dp(1)
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.9, 0.9, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size

                # Server URL
                Label:
                    text: "Server URL"
                    font_size: sp(16)
                    bold: True
                    color: 0.13, 0.13, 0.13, 1
                    size_hint_y: None
                    height: dp(30)
                    halign: "left"
                    text_size: self.size

                Label:
                    id: lbl_url
                    text: "Not configured"
                    font_size: sp(14)
                    color: 0.46, 0.46, 0.46, 1
                    size_hint_y: None
                    height: dp(25)
                    halign: "left"
                    text_size: self.size

                Button:
                    text: "Change URL"
                    size_hint_y: None
                    height: dp(40)
                    size_hint_x: None
                    width: dp(130)
                    font_size: sp(13)
                    background_color: 0.13, 0.59, 0.95, 1
                    background_normal: ""
                    color: 1,1,1,1
                    on_release: root.change_url()

                # App info
                Widget:
                    size_hint_y: None
                    height: dp(40)

                Label:
                    text: "AASAA : Booking\\nv1.1.11.1 (Build 36)\\nPackage: com.aasaa.jarrar.aasaa"
                    font_size: sp(12)
                    color: 0.62, 0.62, 0.62, 1
                    size_hint_y: None
                    height: dp(60)
                    halign: "center"
                    text_size: self.size

                Widget:
                    size_hint_y: None
                    height: dp(20)
''')


class SettingsScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        settings = app.db.get_settings()
        self.ids.chk_standard.active = settings.get('StandardView', 1) == 1
        self.ids.chk_classical.active = settings.get('ClassicalView', 0) == 1

        branch_code = app.prefs.get('branch_code', '')
        if branch_code:
            self.ids.sw_auto_sync.active = app.db.get_auto_sync(branch_code)

        url = app.prefs.get('base_url', '')
        self.ids.lbl_url.text = url if url else "Not configured"

    def on_view_mode(self, mode, active):
        if not active:
            return
        app = App.get_running_app()
        if mode == 'standard':
            app.db.update_settings(1, 0)
        else:
            app.db.update_settings(0, 1)

    def on_auto_sync(self, active):
        app = App.get_running_app()
        branch_code = app.prefs.get('branch_code', '')
        if branch_code:
            app.db.set_auto_sync(branch_code, active)
            if active:
                app.sync_service.start()
            else:
                app.sync_service.stop()

    def change_url(self):
        app = App.get_running_app()
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        url_input = TextInput(text=app.prefs.get('base_url', ''),
                              hint_text="http://server:port",
                              multiline=False, size_hint_y=None, height=dp(44))
        content.add_widget(Label(text="Enter Server URL:", size_hint_y=None, height=dp(25)))
        content.add_widget(url_input)

        popup = Popup(title="Server URL", content=content, size_hint=(0.9, 0.35))

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        save_btn = Button(text="Save", background_color=(0.13, 0.59, 0.95, 1),
                          background_normal="", color=(1, 1, 1, 1))

        def save(inst):
            url = url_input.text.strip()
            if url:
                app.db.save_url(url)
                app.prefs['base_url'] = url
                self.ids.lbl_url.text = url
            popup.dismiss()

        save_btn.bind(on_release=save)
        cancel_btn = Button(text="Cancel", background_color=(0.62, 0.62, 0.62, 1),
                            background_normal="", color=(1, 1, 1, 1))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        popup.open()

    def go_back(self):
        App.get_running_app().navigate_to('main_dashboard', direction='right')
