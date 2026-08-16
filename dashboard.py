import json
import os
import threading
from datetime import datetime
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.utils import platform
from plyer import notification, vibrator

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.fitimage import FitImage
from kivymd.app import MDApp

# File paths
REMINDERS_FILE = os.path.join("data", "reminders.json")
TRACK_FILE = os.path.join("data", "tracker.json")
SETTINGS_FILE = os.path.join("data", "settings.json")

# RGB helper
def rgb(r, g, b, a=255):
    return (r / 255, g / 255, b / 255, a / 255)

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.notification_count = 0
        self.pending_notifications = []
        self.notified_keys = set()
        self.today_meds_list = []

        # Initialize TTS engine once (desktop only)
        if platform != "android":
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
            except:
                self.tts_engine = None

        # Main layout
        self.layout = MDBoxLayout(orientation="vertical")

        # === Header ===
        self.header = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.13),
            padding=[10]*4,
            spacing=10
        )

        title_layout = MDBoxLayout(orientation="horizontal", spacing=10)
        logo = FitImage(
            source="assets/headerlogo.png",
            size_hint=(None, None),
            size=(90, 90)
        )
        title_label = MDLabel(
            text="Smart Medicine Reminder",
            halign="left",
            valign="middle",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6"
        )
        title_layout.add_widget(logo)
        title_layout.add_widget(title_label)

        self.notif_btn = MDIconButton(
            icon="bell-outline",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
            pos_hint={"center_y": 0.5},
            on_release=self.on_notif_pressed
        )

        self.header.add_widget(title_layout)
        self.header.add_widget(self.notif_btn)
        self.layout.add_widget(self.header)

        # === Body ===
        self.scroll = MDScrollView(size_hint=(1, 0.87))
        self.inner_layout = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint_y=None,
            padding=15
        )

        # Dashboard heading inside scroll
        self.dashboard_label = MDLabel(
            text="DASHBOARD",
            halign="left",
            theme_text_color="Custom",
            text_color=rgb(37, 50, 55),
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height="20dp"
        )
        self.inner_layout.add_widget(self.dashboard_label)

        self.inner_layout.bind(minimum_height=self.inner_layout.setter("height"))

        # Top row cards
        self.top_row = MDGridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        self.active_card, self.active_title, self.active_subtitle = self.create_card("Active\nReminders", "None")
        self.today_card, self.today_title, self.today_subtitle = self.create_card("Today’s\nMedicines", "0", on_press=self.show_today_meds)
        self.top_row.add_widget(self.active_card)
        self.top_row.add_widget(self.today_card)
        self.inner_layout.add_widget(self.top_row)

        # Next reminder card
        self.next_card, self.next_title, self.next_subtitle = self.create_card("Next Reminder", "None")
        self.inner_layout.add_widget(self.next_card)

        self.scroll.add_widget(self.inner_layout)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        # Check reminders every second
        Clock.schedule_interval(self.check_reminder_times, 1)

    def on_pre_enter(self, *args):
        settings = self.load_user_settings()
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if settings.get("dark_mode") else "Light"
        self.header.md_bg_color = (0.1, 0.1, 0.1, 1) if app.theme_cls.theme_style == "Dark" else (0.1, 0.6, 0.7, 1)
        self.update_dashboard()

    # -------------------- Card Creation --------------------
    def create_card(self, title, subtitle, on_press=None):
        card = MDCard(
            orientation="vertical",
            radius=[15],
            size_hint_y=None,
            height="100dp",
            md_bg_color=rgb(204, 240, 245),
            padding=10,
            elevation=1
        )

        # Title label (bold)
        title_label = MDLabel(
            text=title,
            halign="center",
            theme_text_color="Custom",
            text_color=rgb(37, 50, 55),
            font_style="H6"  # bold
        )

        # Subtitle label (bold, smaller, spaced)
        subtitle_label = MDLabel(
            text=subtitle,
            halign="center",
            theme_text_color="Custom",
            text_color=rgb(37, 50, 55),
            font_style="Subtitle1"
        )

        box = MDBoxLayout(orientation="vertical", spacing=5)
        box.add_widget(title_label)
        box.add_widget(subtitle_label)

        card.add_widget(box)

        if on_press:
            def _callback(instance, touch):
                if instance.collide_point(*touch.pos):
                    on_press()
                    return True
                return False
            card.bind(on_touch_down=_callback)

        return card, title_label, subtitle_label

    # -------------------- Dashboard Update --------------------
    def update_dashboard(self):
        now = datetime.now()
        active_count = 0
        today_meds = []
        next_reminder = None

        tracker_data = {}
        if os.path.exists(TRACK_FILE):
            with open(TRACK_FILE, "r") as f:
                try: tracker_data = json.load(f)
                except: tracker_data = {}

        reminders = []
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, "r") as f:
                try: reminders = json.load(f)
                except: reminders = []

        for r in reminders:
            med = r.get("medicine")
            time_str = r.get("time")
            date_str = r.get("date")
            key = f"{med}_{date_str}"

            try:
                reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
            except:
                continue

            if date_str == now.strftime("%Y-%m-%d"):
                today_meds.append(f"{med} at {time_str}")

            if key in tracker_data and tracker_data[key] == "missed" and reminder_time < now:
                active_count += 1
            elif key not in tracker_data and reminder_time < now:
                active_count += 1

            if reminder_time > now and (not next_reminder or reminder_time < next_reminder["time"]):
                next_reminder = {"medicine": med, "time": reminder_time}

        # Update subtitles dynamically
        self.active_subtitle.text = str(active_count) if active_count else "None"
        self.today_subtitle.text = str(len(today_meds)) if today_meds else "0"
        self.next_subtitle.text = f"{next_reminder['medicine']} - {next_reminder['time'].strftime('%I:%M %p')}" if next_reminder else "None"

        self.today_meds_list = today_meds

    # -------------------- Reminder Check --------------------
    def check_reminder_times(self, dt):
        now = datetime.now().replace(second=0, microsecond=0)
        settings = self.load_user_settings()

        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, "r") as f:
                try: reminders = json.load(f)
                except: reminders = []

        for r in reminders:
            med = r.get("medicine")
            time_str = r.get("time")
            date_str = r.get("date")

            key = f"{med}_{date_str}_{time_str}"

            if key in self.notified_keys:
                continue

            if date_str == now.strftime("%Y-%m-%d"):
                try:
                    reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")

                    if reminder_time == now:
                        self.notified_keys.add(key)
                        self.pending_notifications.append(key)
                        self.notification_count += 1
                        self.update_notif_icon()

                        if settings.get("notifications", True):
                            self.trigger_reminder_feedback(med)

                except:
                    continue

    # -------------------- TTS --------------------
    def speak_medicine(self, medicine):
        if hasattr(self, "tts_engine") and self.tts_engine:
            try:
                self.tts_engine.say(f"Please take your {medicine} medicine")
                self.tts_engine.runAndWait()
            except:
                print("⚠️ Desktop TTS failed.")

    def trigger_reminder_feedback(self, medicine):
        settings = self.load_user_settings()

        if settings.get("sound"):
            sound = SoundLoader.load("reminder.wav")
            if sound:
                sound.play()

        if settings.get("vibration") and platform == "android":
            try:
                vibrator.vibrate(time=0.5)
            except:
                print("⚠️ Vibration not supported.")

        if settings.get("tts"):
            if platform == "android":
                try:
                    from plyer import tts
                    tts.speak(f"Please take your {medicine} medicine")
                except:
                    print("⚠️ Android TTS failed.")
            else:
                threading.Thread(target=self.speak_medicine, args=(medicine,), daemon=True).start()

        if platform in ("win", "linux", "macosx"):
            try:
                notification.notify(
                    title="Medicine Reminder",
                    message=f"Please take your {medicine} medicine",
                    app_name="Smart Medicine Reminder",
                    timeout=5
                )
            except:
                print("⚠️ Desktop notification failed.")

    # -------------------- UI Events --------------------
    def update_notif_icon(self):
        if self.notification_count > 0:
            self.notif_btn.icon = "bell-ring"
            self.notif_btn.icon_color = (1, 0, 0, 1)
        else:
            self.notif_btn.icon = "bell-outline"
            self.notif_btn.icon_color = (1, 1, 1, 1)

    def on_notif_pressed(self, instance):
        if not self.pending_notifications:
            self.dialog = MDDialog(
                title="Notifications",
                text="No new medicine reminders.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return

        messages = [f"Please take your {key.split('_')[0]} medicine" for key in self.pending_notifications]
        self.dialog = MDDialog(
            title="Medicine Reminder",
            text="\n".join(messages),
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.clear_notifications())]
        )
        self.dialog.open()

    def clear_notifications(self):
        self.pending_notifications.clear()
        self.notification_count = 0
        self.update_notif_icon()
        if hasattr(self, "dialog"):
            self.dialog.dismiss()

    def show_today_meds(self):
        if not self.today_meds_list:
            text = "All medicines taken or no reminders today."
        else:
            text = "\n".join(self.today_meds_list)
        self.dialog = MDDialog(
            title="Today's Medicines",
            text=text,
            size_hint=(0.8, None),
            height=300
        )
        self.dialog.open()

    # -------------------- Utility --------------------
    def load_user_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def go_to_home(self, *args):
        if self.manager:
            self.manager.current = "dashboard"

    def go_to_add(self, *args):
        if self.manager:
            self.manager.current = "add_reminder"

    def go_to_view(self, *args):
        if self.manager:
            self.manager.current = "view_reminders"

    def go_to_tracker(self, *args):
        if self.manager:
            self.manager.current = "tracker"

    def go_to_settings(self, *args):
        if self.manager:
            self.manager.current = "settings"
