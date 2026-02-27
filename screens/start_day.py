from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp

Builder.load_string('''
<StartDayScreen>:
    canvas.before:
        Color:
            rgba: 0.96, 0.96, 0.96, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"

        # Toolbar
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(15)
            canvas.before:
                Color:
                    rgba: 0.13, 0.59, 0.95, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "Start Day"
                font_size: sp(20)
                bold: True
                color: 1, 1, 1, 1
                halign: "left"
                text_size: self.size
                valign: "center"

        BoxLayout:
            orientation: "vertical"
            padding: dp(30)
            spacing: dp(20)

            Widget:
                size_hint_y: 0.15

            Label:
                text: "Select Branch"
                font_size: sp(18)
                color: 0.13, 0.13, 0.13, 1
                size_hint_y: None
                height: dp(30)

            Spinner:
                id: branch_spinner
                text: "Select Branch"
                size_hint_y: None
                height: dp(50)
                font_size: sp(16)
                background_color: 1, 1, 1, 1
                color: 0.13, 0.13, 0.13, 1

            Widget:
                size_hint_y: None
                height: dp(20)

            Button:
                id: btn_start
                text: "Start Day"
                size_hint_y: None
                height: dp(55)
                font_size: sp(18)
                bold: True
                background_color: 0.13, 0.59, 0.95, 1
                background_normal: ""
                color: 1, 1, 1, 1
                on_release: root.start_day()

            Label:
                id: lbl_status
                text: ""
                font_size: sp(14)
                color: 0.46, 0.46, 0.46, 1
                size_hint_y: None
                height: dp(30)

            Widget:
                size_hint_y: None
                height: dp(20)

            Button:
                text: "Logout"
                size_hint_y: None
                height: dp(44)
                font_size: sp(16)
                background_color: 0.96, 0.26, 0.21, 1
                background_normal: ""
                color: 1, 1, 1, 1
                on_release: root.logout()

            Widget:
                size_hint_y: 0.3
''')


class StartDayScreen(Screen):
    _branches = {}

    def on_enter(self):
        app = App.get_running_app()
        branches = app.db.get_branches()
        self._branches = {}
        names = []
        for b in branches:
            name = b['branch_name']
            self._branches[name] = b
            names.append(name)

        if names:
            self.ids.branch_spinner.values = names
            self.ids.branch_spinner.text = names[0]
        else:
            self.ids.branch_spinner.values = ["No branches available"]
            self.ids.branch_spinner.text = "No branches available"

    def start_day(self):
        app = App.get_running_app()
        selected = self.ids.branch_spinner.text
        if selected not in self._branches:
            self._show_error("Please select a valid branch")
            return

        branch = self._branches[selected]
        branch_code = branch['branch_code']
        user_code = branch.get('user_code', '')

        app.prefs['branch_code'] = branch_code
        app.prefs['branch_name'] = selected
        app.prefs['user_code'] = user_code

        # Check if day already started
        if app.db.is_day_started(branch_code):
            app.navigate_to('main_dashboard')
            return

        self.ids.lbl_status.text = "Loading data..."
        self.ids.btn_start.disabled = True

        app.api.start_day_data(branch_code, user_code,
                               callback=self._on_data_loaded,
                               error_callback=self._on_data_error)

    def _on_data_loaded(self, data):
        self.ids.lbl_status.text = ""
        self.ids.btn_start.disabled = False
        app = App.get_running_app()
        app.navigate_to('main_dashboard')

    def _on_data_error(self, error):
        self.ids.lbl_status.text = ""
        self.ids.btn_start.disabled = False
        self._show_error(error)

    def _show_error(self, message):
        popup = Popup(title="Error",
                      content=Label(text=message, text_size=(dp(250), None)),
                      size_hint=(0.8, 0.3))
        popup.open()

    def logout(self):
        app = App.get_running_app()
        app.prefs.clear()
        app.db.clear_all_data()
        app.navigate_to('login', direction='right')
