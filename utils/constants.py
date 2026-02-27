# App constants
APP_NAME = "AASAA : Booking"
PACKAGE_NAME = "com.aasaa.jarrar.aasaa"
VERSION = "1.1.11.1"
BUILD_NUMBER = 36

# SharedPreferences keys (mapped to Kivy Store)
PREF_USERNAME = "username"
PREF_PASSWORD = "password"
PREF_PHONE_ID = "PhoneID"
PREF_BRANCH_CODE = "branch_code"
PREF_BRANCH_NAME = "branch_name"
PREF_USER_CODE = "user_code"
PREF_SESSION_ID = "session_id"
PREF_BASE_URL = "base_url"
PREF_AUTO_SYNC = "auto_sync"
PREF_VIEW_MODE = "view_mode"

# API endpoints
API_LOGIN = "/WebServiceStartDayData/Request"
API_START_DAY = "/WebServiceStartDayData/Request"
API_SYNC_ORDER = "/api/SaleOrderChemist/SaleOrderChemist"
API_SYNC_CUSTOMER = "/WebServiceStartDayData/Request"
API_FOCUSED_PRODUCTS = "/WebServiceStartDayData/Request"
API_CHECK_URL = "/WebServiceStartDayData/Request"

# Request types
REQ_LOGIN = "1"
REQ_START_DAY = "2"
REQ_SYNC_DATA = "3"
REQ_NEW_CUSTOMER = "4"
REQ_FOCUSED_PRODUCTS = "5"

# View modes
VIEW_STANDARD = "standard"
VIEW_CLASSICAL = "classical"

# Order status
ORDER_OPEN = 0
ORDER_CLOSED = 1
ORDER_SYNCED = 2

# Colors (matching the Android app theme)
PRIMARY_COLOR = [0.13, 0.59, 0.95, 1]       # #2196F3 Blue
PRIMARY_DARK = [0.10, 0.46, 0.82, 1]        # #1976D2
ACCENT_COLOR = [1.0, 0.34, 0.13, 1]         # #FF5722 Deep Orange
WHITE = [1, 1, 1, 1]
BLACK = [0, 0, 0, 1]
GREY_LIGHT = [0.96, 0.96, 0.96, 1]
GREY = [0.62, 0.62, 0.62, 1]
GREEN = [0.30, 0.69, 0.31, 1]               # #4CAF50
RED = [0.96, 0.26, 0.21, 1]                 # #F44336
AMBER = [1.0, 0.76, 0.03, 1]               # #FFC107
TEXT_PRIMARY = [0.13, 0.13, 0.13, 1]
TEXT_SECONDARY = [0.46, 0.46, 0.46, 1]

# Sync intervals
DEFAULT_SYNC_INTERVAL = 60  # seconds
FAST_SYNC_INTERVAL = 1      # seconds

# HTTP timeouts
HTTP_TIMEOUT = 300  # 5 minutes in seconds
