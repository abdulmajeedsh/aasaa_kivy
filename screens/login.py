from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp

Builder.load_string('''
<LoginScreen>:
    canvas.before:
        Color:
            rgba: 0.96, 0.96, 0.96, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(10)

        Widget:
            size_hint_y: 0.15

        # Logo area
        BoxLayout:
            size_hint_y: None
            height: dp(120)
            canvas.before:
                Color:
                    rgba: 0.13, 0.59, 0.95, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(10)]
            Label:
                text: "AASAA : Booking"
                font_size: sp(28)
                bold: True
                color: 1, 1, 1, 1

        Widget:
            size_hint_y: None
            height: dp(30)

        # Username
        TextInput:
            id: txt_username
            hint_text: "Username"
            size_hint_y: None
            height: dp(48)
            multiline: False
            font_size: sp(16)
            padding: [dp(15), dp(12)]

        # Password
        TextInput:
            id: txt_password
            hint_text: "Password"
            size_hint_y: None
            height: dp(48)
            multiline: False
            password: True
            font_size: sp(16)
            padding: [dp(15), dp(12)]

        Widget:
            size_hint_y: None
            height: dp(10)

        # Sign In button
        Button:
            id: btn_login
            text: "Sign In"
            size_hint_y: None
            height: dp(50)
            font_size: sp(18)
            bold: True
            background_color: 0.13, 0.59, 0.95, 1
            background_normal: ""
            color: 1, 1, 1, 1
            on_release: root.do_login()

        # Settings button
        Button:
            text: "Server Settings"
            size_hint_y: None
            height: dp(40)
            font_size: sp(14)
            background_color: 0, 0, 0, 0
            background_normal: ""
            color: 0.13, 0.59, 0.95, 1
            on_release: root.show_url_settings()

        # Loading label
        Label:
            id: lbl_status
            text: ""
            font_size: sp(14)
            color: 0.46, 0.46, 0.46, 1
            size_hint_y: None
            height: dp(30)

        Widget:
            size_hint_y: 0.3
''')


class LoginScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        # Check local credentials
        login = app.db.get_login()
        if login:
            self.ids.txt_username.text = login.get('username', '')
            self.ids.txt_password.text = login.get('password', '')

    def do_login(self):
        app = App.get_running_app()
        username = self.ids.txt_username.text.strip()
        password = self.ids.txt_password.text.strip()

        if not username or not password:
            self._show_error("Please enter username and password")
            return

        self.ids.lbl_status.text = "Signing in..."
        self.ids.btn_login.disabled = True

        phone_id = app.get_phone_id()
        app.prefs['PhoneID'] = phone_id
        app.prefs['username'] = username
        app.prefs['password'] = password

        # Try local auth first
        local_login = app.db.get_login()
        if local_login and local_login['username'] == username and local_login['password'] == password:
            self.ids.lbl_status.text = "Authenticated locally"
            self.ids.btn_login.disabled = False
            app.navigate_to('start_day')
            return

        # Remote auth
        app.api.login(username, password, phone_id,
                      callback=self._on_login_success,
                      error_callback=self._on_login_error)

    def _on_login_success(self, data):
        app = App.get_running_app()
        self.ids.lbl_status.text = ""
        self.ids.btn_login.disabled = False
        app.navigate_to('start_day')

    def _on_login_error(self, error):
        self.ids.lbl_status.text = ""
        self.ids.btn_login.disabled = False
        self._show_error(error)

    def _show_error(self, message):
        popup = Popup(
            title="Error",
            content=Label(text=message, text_size=(dp(250), None)),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def show_url_settings(self):
        app = App.get_running_app()
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        current_url = app.prefs.get('base_url', '')
        url_input = TextInput(
            text=current_url, hint_text="http://server:port",
            multiline=False, size_hint_y=None, height=dp(44)
        )
        content.add_widget(Label(text="Enter Server URL:", size_hint_y=None, height=dp(30)))
        content.add_widget(url_input)
        status_label = Label(text="", size_hint_y=None, height=dp(30), color=(0.96, 0.26, 0.21, 1))
        content.add_widget(status_label)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        popup = Popup(title="Server Settings", content=content, size_hint=(0.9, 0.4))

        def save_url(instance):
            url = url_input.text.strip()
            if url:
                app.db.save_url(url)
                app.prefs['base_url'] = url
                popup.dismiss()

        btn_save = Button(text="Save", background_color=(0.13, 0.59, 0.95, 1),
                          background_normal="", color=(1, 1, 1, 1))
        btn_save.bind(on_release=save_url)
        btn_cancel = Button(text="Cancel", background_color=(0.62, 0.62, 0.62, 1),
                            background_normal="", color=(1, 1, 1, 1))
        btn_cancel.bind(on_release=popup.dismiss)
        btn_row.add_widget(btn_save)
        btn_row.add_widget(btn_cancel)
        content.add_widget(btn_row)
        popup.open()
