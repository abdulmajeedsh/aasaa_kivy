"""
Sync Service - Background order synchronization.
Equivalent to Service_Class.java from the Android app.
"""
from kivy.clock import Clock
from kivy.logger import Logger


class SyncService:
    def __init__(self, api_service, db_manager, prefs):
        self.api = api_service
        self.db = db_manager
        self.prefs = prefs
        self._running = False
        self._clock_event = None
        self._interval = 60

    def start(self):
        if self._running:
            return
        self._running = True
        try:
            rows = self.db.execute_query("SELECT timer_interval FROM service_table LIMIT 1")
            if rows:
                self._interval = max(1, rows[0]['timer_interval'] // 1000)
        except Exception:
            self._interval = 60
        Logger.info(f"SyncService: Starting with interval {self._interval}s")
        self._clock_event = Clock.schedule_interval(self._sync_tick, self._interval)

    def stop(self):
        self._running = False
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None
        Logger.info("SyncService: Stopped")

    def _sync_tick(self, dt):
        if not self._running:
            return
        branch_code = self.prefs.get('branch_code', '')
        user_code = self.prefs.get('user_code', '')
        if not branch_code or not user_code:
            return
        unsynced = self.db.get_unsynced_orders()
        if not unsynced:
            return
        Logger.info(f"SyncService: Found {len(unsynced)} unsynced orders, syncing...")
        self.api.send_orders(branch_code, user_code,
                             callback=self._on_sync_success,
                             error_callback=self._on_sync_error)

    def _on_sync_success(self, data):
        Logger.info("SyncService: Orders synced successfully")

    def _on_sync_error(self, error):
        Logger.error(f"SyncService: Sync failed - {error}")
        branch_code = self.prefs.get('branch_code', '')
        if branch_code:
            self.db.log_error(branch_code, f"Auto-sync failed: {error}")

    def force_sync(self, callback=None, error_callback=None):
        branch_code = self.prefs.get('branch_code', '')
        user_code = self.prefs.get('user_code', '')
        if not branch_code or not user_code:
            if error_callback:
                error_callback("Branch not selected")
            return
        self.api.send_orders(branch_code, user_code,
                             callback=callback or self._on_sync_success,
                             error_callback=error_callback or self._on_sync_error)

    @property
    def is_running(self):
        return self._running
