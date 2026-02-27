"""
GPS Service - Location tracking for customer visit verification.
Equivalent to TrackGPS.java from the Android app.
"""
from kivy.logger import Logger

try:
    from plyer import gps
    HAS_GPS = True
except ImportError:
    HAS_GPS = False


class GPSService:
    def __init__(self):
        self.latitude = 0.0
        self.longitude = 0.0
        self._active = False
        self._callbacks = []

    def start(self):
        if not HAS_GPS:
            Logger.warning("GPSService: plyer GPS not available")
            return False
        try:
            gps.configure(on_location=self._on_location, on_status=self._on_status)
            gps.start(minTime=0, minDistance=0)
            self._active = True
            Logger.info("GPSService: Started")
            return True
        except NotImplementedError:
            Logger.warning("GPSService: GPS not implemented on this platform")
            return False
        except Exception as e:
            Logger.error(f"GPSService: Failed to start - {e}")
            return False

    def stop(self):
        if not HAS_GPS or not self._active:
            return
        try:
            gps.stop()
            self._active = False
            Logger.info("GPSService: Stopped")
        except Exception as e:
            Logger.error(f"GPSService: Failed to stop - {e}")

    def _on_location(self, **kwargs):
        self.latitude = kwargs.get('lat', 0.0)
        self.longitude = kwargs.get('lon', 0.0)
        for cb in self._callbacks:
            try:
                cb(self.latitude, self.longitude)
            except Exception:
                pass

    def _on_status(self, stype, status):
        Logger.info(f"GPSService: Status {stype} = {status}")

    def get_location(self):
        return self.latitude, self.longitude

    def can_get_location(self):
        return self._active and HAS_GPS

    def add_callback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def remove_callback(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def request_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ])
            return True
        except ImportError:
            return True
