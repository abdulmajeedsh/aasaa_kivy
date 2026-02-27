"""
AASAA : Booking - Mobile Booking Application
Kivy-based Android app for field sales representatives.
Package: com.aasaa.jarrar.aasaa
Version: 1.1.11.1 (Build 36)
"""
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore

from database.db_model import DatabaseManager
from services.api_service import ApiService
from services.sync_service import SyncService
from services.gps_service import GPSService

from screens.splash import SplashScreen
from screens.login import LoginScreen
from screens.start_day import StartDayScreen
from screens.main_dashboard import MainDashboardScreen
from screens.routes import RoutesScreen
from screens.regions import RegionsScreen
from screens.subregions import SubRegionsScreen
from screens.customers import CustomersScreen
from screens.new_customer import NewCustomerScreen
from screens.orders import OrderScreen
from screens.place_order import PlaceOrderScreen
from screens.no_order import NoOrderScreen
from screens.order_history import OrderHistoryScreen
from screens.booking_history import BookingHistoryScreen
from screens.company_sales import CompanySalesScreen
from screens.error_logs import ErrorLogsScreen
from screens.settings import SettingsScreen


class AASAAApp(App):
    title = 'AASAA : Booking'

    # Navigation state attributes
    current_route_code = ''
    current_route_name = ''
    current_region_code = ''
    current_region_name = ''
    current_parent_region_code = ''
    current_customer_code = ''
    current_customer_name = ''

    def build(self):
        if platform not in ('android', 'ios'):
            Window.size = (400, 700)

        # Preferences store
        if platform == 'android':
            from android.storage import app_storage_path
            store_path = os.path.join(app_storage_path(), 'aasaa_prefs.json')
        else:
            store_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aasaa_prefs.json')

        self.store = JsonStore(store_path)
        self.prefs = PrefsWrapper(self.store)

        # Database
        self.db = DatabaseManager()

        # Services
        self.api = ApiService(self.db, self.prefs)
        self.gps = GPSService()
        self.sync_service = SyncService(self.api, self.db, self.prefs)

        # Android permissions
        if platform == 'android':
            self._request_android_permissions()

        # Screen manager
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(SplashScreen(name='splash'))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(StartDayScreen(name='start_day'))
        self.sm.add_widget(MainDashboardScreen(name='main_dashboard'))
        self.sm.add_widget(RoutesScreen(name='routes'))
        self.sm.add_widget(RegionsScreen(name='regions'))
        self.sm.add_widget(SubRegionsScreen(name='subregions'))
        self.sm.add_widget(CustomersScreen(name='customers'))
        self.sm.add_widget(NewCustomerScreen(name='new_customer'))
        self.sm.add_widget(OrderScreen(name='orders'))
        self.sm.add_widget(PlaceOrderScreen(name='place_order'))
        self.sm.add_widget(NoOrderScreen(name='no_order'))
        self.sm.add_widget(OrderHistoryScreen(name='order_history'))
        self.sm.add_widget(BookingHistoryScreen(name='booking_history'))
        self.sm.add_widget(CompanySalesScreen(name='company_sales'))
        self.sm.add_widget(ErrorLogsScreen(name='error_logs'))
        self.sm.add_widget(SettingsScreen(name='settings'))

        self.sm.current = 'splash'
        return self.sm

    def _request_android_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION,
                Permission.READ_PHONE_STATE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])
        except ImportError:
            pass

    def get_phone_id(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                Settings = autoclass('android.provider.Settings$Secure')
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                android_id = Settings.getString(
                    activity.getContentResolver(), Settings.ANDROID_ID)
                return android_id or 'unknown'
            except Exception:
                return 'android_unknown'
        else:
            import uuid
            return str(uuid.getnode())

    def navigate_to(self, screen_name, direction='left'):
        self.sm.transition.direction = direction
        self.sm.current = screen_name

    def go_back(self):
        self.sm.transition.direction = 'right'
        back_map = {
            'login': 'splash',
            'start_day': 'login',
            'main_dashboard': 'start_day',
            'routes': 'main_dashboard',
            'regions': 'routes',
            'subregions': 'regions',
            'customers': 'subregions',
            'new_customer': 'customers',
            'orders': 'customers',
            'place_order': 'orders',
            'no_order': 'orders',
            'order_history': 'main_dashboard',
            'booking_history': 'main_dashboard',
            'company_sales': 'main_dashboard',
            'error_logs': 'main_dashboard',
            'settings': 'main_dashboard',
        }
        self.sm.current = back_map.get(self.sm.current, 'main_dashboard')

    def on_stop(self):
        self.sync_service.stop()
        self.gps.stop()
        self.db.close()

    def on_pause(self):
        return True

    def on_resume(self):
        pass


class PrefsWrapper:
    """Dict-like wrapper around Kivy JsonStore for SharedPreferences equivalent."""

    def __init__(self, store):
        self._store = store

    def get(self, key, default=''):
        try:
            if self._store.exists(key):
                return self._store.get(key)['value']
        except Exception:
            pass
        return default

    def __getitem__(self, key):
        return self.get(key, '')

    def __setitem__(self, key, value):
        self._store.put(key, value=value)

    def __contains__(self, key):
        return self._store.exists(key)

    def delete(self, key):
        if self._store.exists(key):
            self._store.delete(key)

    def clear(self):
        for key in list(self._store.keys()):
            self._store.delete(key)


if __name__ == '__main__':
    AASAAApp().run()
