from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

Builder.load_string('''
<MainDashboardScreen>:
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
            padding: [dp(10), 0]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: 0.13, 0.59, 0.95, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "="
                size_hint_x: None
                width: dp(44)
                font_size: sp(24)
                background_color: 0, 0, 0, 0
                background_normal: ""
                color: 1, 1, 1, 1
                on_release: root.toggle_drawer()
            Label:
                text: "AASAA : Booking"
                font_size: sp(18)
                bold: True
                color: 1, 1, 1, 1
                halign: "left"
                text_size: self.size
                valign: "center"

        # Main content with drawer overlay
        FloatLayout:
            id: content_area

            # Main content
            BoxLayout:
                id: main_content
                orientation: "vertical"
                pos_hint: {"x": 0, "y": 0}
                size_hint: 1, 1

            # Drawer overlay (hidden by default)
            BoxLayout:
                id: drawer
                orientation: "vertical"
                size_hint_x: 0.75
                pos_hint: {"x": -0.75, "y": 0}
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size

                # Drawer header
                BoxLayout:
                    size_hint_y: None
                    height: dp(100)
                    padding: dp(20)
                    canvas.before:
                        Color:
                            rgba: 0.10, 0.46, 0.82, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    Label:
                        id: drawer_username
                        text: "Welcome"
                        font_size: sp(18)
                        color: 1, 1, 1, 1
                        halign: "left"
                        valign: "bottom"
                        text_size: self.size

                # Menu items
                ScrollView:
                    BoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        padding: 0
                        spacing: dp(1)

                        DrawerItem:
                            text: "Routes"
                            on_release: root.menu_routes()
                        DrawerItem:
                            text: "Order History"
                            on_release: root.menu_order_history()
                        DrawerItem:
                            text: "Booking History"
                            on_release: root.menu_booking_history()
                        DrawerItem:
                            text: "Company Sales"
                            on_release: root.menu_company_sales()
                        DrawerItem:
                            text: "Error Logs"
                            on_release: root.menu_error_logs()
                        DrawerItem:
                            text: "Sync Data"
                            on_release: root.menu_sync()
                        DrawerItem:
                            text: "Settings"
                            on_release: root.menu_settings()
                        DrawerItem:
                            text: "End Day"
                            on_release: root.menu_end_day()
                        DrawerItem:
                            text: "Logout"
                            on_release: root.menu_logout()

<DrawerItem@Button>:
    size_hint_y: None
    height: dp(50)
    font_size: sp(16)
    background_color: 0, 0, 0, 0
    background_normal: ""
    color: 0.13, 0.13, 0.13, 1
    halign: "left"
    valign: "center"
    text_size: self.size
    padding: [dp(20), 0]
    canvas.after:
        Color:
            rgba: 0.9, 0.9, 0.9, 1
        Line:
            points: [self.x + dp(10), self.y, self.right - dp(10), self.y]
''')


class MainDashboardScreen(Screen):
    _drawer_open = False

    def on_enter(self):
        app = App.get_running_app()
        username = app.prefs.get('username', 'User')
        self.ids.drawer_username.text = f"Welcome, {username}"

        # Start auto-sync if enabled
        branch_code = app.prefs.get('branch_code', '')
        if branch_code and app.db.get_auto_sync(branch_code):
            app.sync_service.start()

        # Start GPS
        app.gps.start()

    def toggle_drawer(self):
        from kivy.animation import Animation
        drawer = self.ids.drawer
        if self._drawer_open:
            anim = Animation(pos_hint={"x": -0.75, "y": 0}, duration=0.2)
            self._drawer_open = False
        else:
            anim = Animation(pos_hint={"x": 0, "y": 0}, duration=0.2)
            self._drawer_open = True
        anim.start(drawer)

    def _close_drawer(self):
        if self._drawer_open:
            self.toggle_drawer()

    def menu_routes(self):
        self._close_drawer()
        App.get_running_app().navigate_to('routes')

    def menu_order_history(self):
        self._close_drawer()
        App.get_running_app().navigate_to('order_history')

    def menu_booking_history(self):
        self._close_drawer()
        App.get_running_app().navigate_to('booking_history')

    def menu_company_sales(self):
        self._close_drawer()
        App.get_running_app().navigate_to('company_sales')

    def menu_error_logs(self):
        self._close_drawer()
        App.get_running_app().navigate_to('error_logs')

    def menu_sync(self):
        self._close_drawer()
        app = App.get_running_app()
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        popup = Popup(title="Sync Data", content=content, size_hint=(0.8, 0.4))

        def sync_master(instance):
            popup.dismiss()
            branch = app.prefs.get('branch_code', '')
            user = app.prefs.get('user_code', '')
            app.api.sync_data(branch, user,
                              callback=lambda d: self._show_msg("Data synced successfully"),
                              error_callback=lambda e: self._show_msg(f"Sync failed: {e}"))

        def sync_focused(instance):
            popup.dismiss()
            branch = app.prefs.get('branch_code', '')
            app.api.fetch_focused_products(branch,
                                           callback=lambda d: self._show_msg("Focused products synced"),
                                           error_callback=lambda e: self._show_msg(f"Sync failed: {e}"))

        def sync_orders(instance):
            popup.dismiss()
            app.sync_service.force_sync(
                callback=lambda d: self._show_msg("Orders synced successfully"),
                error_callback=lambda e: self._show_msg(f"Order sync failed: {e}"))

        btn1 = Button(text="Sync Master Data", size_hint_y=None, height=dp(44),
                       background_color=(0.13, 0.59, 0.95, 1), background_normal="", color=(1, 1, 1, 1))
        btn1.bind(on_release=sync_master)
        btn2 = Button(text="Sync Focused Products", size_hint_y=None, height=dp(44),
                       background_color=(0.13, 0.59, 0.95, 1), background_normal="", color=(1, 1, 1, 1))
        btn2.bind(on_release=sync_focused)
        btn3 = Button(text="Sync Orders", size_hint_y=None, height=dp(44),
                       background_color=(0.30, 0.69, 0.31, 1), background_normal="", color=(1, 1, 1, 1))
        btn3.bind(on_release=sync_orders)
        content.add_widget(btn1)
        content.add_widget(btn2)
        content.add_widget(btn3)
        popup.open()

    def menu_settings(self):
        self._close_drawer()
        App.get_running_app().navigate_to('settings')

    def menu_end_day(self):
        self._close_drawer()
        app = App.get_running_app()

        # Validate: check unsynced orders
        if app.db.has_unsynced_orders():
            self._show_msg("Cannot end day: You have unsynced orders. Please sync first.")
            return

        # Reset bits and go to login
        app.db.reset_completion_bits()
        app.sync_service.stop()
        app.gps.stop()
        app.navigate_to('login', direction='right')

    def menu_logout(self):
        self._close_drawer()
        app = App.get_running_app()

        if app.db.has_unsynced_orders():
            self._show_msg("Cannot logout: You have unsynced orders. Please sync first.")
            return

        app.sync_service.stop()
        app.gps.stop()
        app.prefs.clear()
        app.db.clear_all_data()
        app.navigate_to('login', direction='right')

    def _show_msg(self, message):
        popup = Popup(title="Info",
                      content=Label(text=message, text_size=(dp(250), None)),
                      size_hint=(0.8, 0.3))
        popup.open()
