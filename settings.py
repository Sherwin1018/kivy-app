import json
import os
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.core.audio import SoundLoader
from kivy.utils import platform
from plyer import vibrator

SETTINGS_FILE = os.path.join("data", "settings.json")

class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = {
            "sound": True,
            "vibration": True,
            "notifications": True,
            "dark_mode": False,
            "tts": False
        }
        self.switch_refs = {}
        self.load_settings()
        self.sound_enabled = self.settings["sound"]
        self.vibration_enabled = self.settings["vibration"]
        self.build_ui()

    def build_ui(self):
        scroll = MDScrollView(size_hint=(1, 1), do_scroll_x=False)
        content = MDBoxLayout(
            orientation="vertical",
            padding=[dp(20)] * 4,
            spacing=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        def toggle_row(text, key, handler):
            row = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(10),
                padding=[0, 0, dp(15), 0],
                size_hint_y=None,
                height=dp(40)
            )
            label = MDLabel(
                text=text,
                halign="left",
                valign="middle",
                font_style="Body1",
                size_hint_x=0.85
            )
            switch = MDSwitch(pos_hint={"center_y": 0.5})
            switch.active = self.settings[key]
            switch.bind(active=handler)
            self.switch_refs[key] = switch
            row.add_widget(label)
            row.add_widget(switch)
            return row

        # Reminder Notifications
        reminder_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            radius=[dp(15)],
            elevation=1,
            size_hint_y=None
        )
        reminder_card.bind(minimum_height=reminder_card.setter("height"))
        reminder_card.add_widget(MDLabel(
            text="Settings",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=dp(40)
        ))
        reminder_card.add_widget(MDLabel(
            text="Reminder Notifications",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.3, 0.4, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        reminder_card.add_widget(toggle_row("Sound Alerts", "sound", self.toggle_sound))
        reminder_card.add_widget(toggle_row("Vibration Feedback", "vibration", self.toggle_vibration))
        content.add_widget(reminder_card)

        # Notification Settings
        notif_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            radius=[dp(15)],
            elevation=1,
            size_hint_y=None
        )
        notif_card.bind(minimum_height=notif_card.setter("height"))
        notif_card.add_widget(MDLabel(
            text="Notification Settings",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.3, 0.4, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        notif_card.add_widget(toggle_row("Enable Notifications", "notifications", self.toggle_notifications))
        content.add_widget(notif_card)

        # Accessibility Options
        access_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            radius=[dp(15)],
            elevation=1,
            size_hint_y=None
        )
        access_card.bind(minimum_height=access_card.setter("height"))
        access_card.add_widget(MDLabel(
            text="Accessibility Options",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.3, 0.4, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        access_card.add_widget(toggle_row("Text-to-Speech Reminders", "tts", self.toggle_tts))
        content.add_widget(access_card)

        # Theme Mode
        theme_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            radius=[dp(15)],
            elevation=1,
            size_hint_y=None
        )
        theme_card.bind(minimum_height=theme_card.setter("height"))
        theme_card.add_widget(MDLabel(
            text="Theme Mode",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.3, 0.4, 1),
            size_hint_y=None,
            height=dp(30)
        ))
        theme_card.add_widget(toggle_row("Dark Mode", "dark_mode", self.toggle_theme))
        content.add_widget(theme_card)

        content.add_widget(Widget(size_hint_y=None, height=dp(20)))
        back_btn = MDRaisedButton(
            text="Back",
            size_hint=(None, None),
            height=dp(50),
            width=dp(100),
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.6, 0.7, 1)
        )
        back_btn.bind(on_release=self.go_back)
        content.add_widget(back_btn)

        scroll.add_widget(content)
        self.add_widget(scroll)

    # Toggle Handlers
    def toggle_sound(self, instance, value):
        self.settings["sound"] = value
        self.sound_enabled = value
        self.save_settings()
        print("🔊 Sound Enabled:", value)

    def toggle_vibration(self, instance, value):
        self.settings["vibration"] = value
        self.vibration_enabled = value
        self.save_settings()
        print("📳 Vibration Enabled:", value)

    def toggle_notifications(self, instance, value):
        self.settings["notifications"] = value
        self.save_settings()
        print("🔔 Notifications Enabled:", value)

    def toggle_tts(self, instance, value):
        self.settings["tts"] = value
        self.save_settings()
        print("🗣 Text-to-Speech Enabled:", value)

    def toggle_theme(self, instance, value):
        self.settings["dark_mode"] = value
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if value else "Light"
        self.save_settings()
        print("🎨 Theme switched to:", app.theme_cls.theme_style)

    def go_back(self, instance=None):
        if hasattr(self.manager.parent, "go_back"):
            self.manager.parent.go_back()

    # Reminder Feedback
    def play_reminder_sound(self):
        if self.sound_enabled:
            sound = SoundLoader.load("reminder.wav")
            if sound:
                sound.play()

    def vibrate_reminder(self):
        if self.vibration_enabled:
            try:
                vibrator.vibrate(time=0.5)
            except:
                print("⚠️ Vibration not supported on this platform.")

    def speak_reminder(self, text):
        if self.settings.get("tts"):
            if platform == "android":
                try:
                    from plyer import tts
                    tts.speak(text)
                except:
                    print("⚠️ Android TTS failed.")
            else:
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except:
                    print("⚠️ Desktop TTS failed.")

    # Settings Persistence
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    self.settings.update(json.load(f))
            except:
                pass

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)
