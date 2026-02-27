from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App

Builder.load_string('''
<SplashScreen>:
    canvas.before:
        Color:
            rgba: 0.13, 0.59, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size
    FloatLayout:
        Label:
            text: "AASAA"
            font_size: sp(48)
            bold: True
            color: 1, 1, 1, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.6}
        Label:
            text: "Booking"
            font_size: sp(24)
            color: 1, 1, 1, 0.9
            pos_hint: {"center_x": 0.5, "center_y": 0.52}
        Label:
            text: "Mobile Booking Application"
            font_size: sp(14)
            color: 1, 1, 1, 0.7
            pos_hint: {"center_x": 0.5, "center_y": 0.45}
        ProgressBar:
            id: progress
            max: 100
            value: 0
            size_hint_x: 0.6
            pos_hint: {"center_x": 0.5, "center_y": 0.35}
        Label:
            text: "v1.1.11.1 (Build 36)"
            font_size: sp(12)
            color: 1, 1, 1, 0.5
            pos_hint: {"center_x": 0.5, "y": 0.02}
''')


class SplashScreen(Screen):
    def on_enter(self):
        self._progress = 0
        Clock.schedule_interval(self._update_progress, 0.03)

    def _update_progress(self, dt):
        self._progress += 2
        self.ids.progress.value = self._progress
        if self._progress >= 100:
            Clock.unschedule(self._update_progress)
            app = App.get_running_app()
            app.navigate_to('login')
