import json
import os
from datetime import datetime, timedelta
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivy.metrics import dp
from kivy.app import App
from kivymd.app import MDApp
from kivy.graphics import Color, Rectangle

REMINDERS_FILE = os.path.join("data", "reminders.json")
TRACK_FILE = os.path.join("data", "tracker.json")

class TrackerScreen(MDScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        theme = MDApp.get_running_app().theme_cls.theme_style
        taken_bg = (0.8, 1, 0.8, 1) if theme == "Light" else (0.2, 0.4, 0.2, 1)
        missed_bg = (1, 0.8, 0.8, 1) if theme == "Light" else (0.4, 0.2, 0.2, 1)

        main = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))

        # === TRACKER PAGE HEADING ===
        heading_color = (1, 1, 1, 1) if theme == "Dark" else (0, 0, 0, 1)
        heading_label = MDLabel(
            text="Tracker Page",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=heading_color,
            size_hint_y=None,
            height=dp(40)
        )
        main.add_widget(heading_label)

        summary_box = MDBoxLayout(size_hint_y=None, height=dp(120), spacing=dp(20))

        self.taken_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            radius=[dp(15)],
            md_bg_color=taken_bg,
            elevation=1
        )
        self.taken_label = MDLabel(text="0", halign="center", font_style="H4", theme_text_color="Primary")
        self.taken_card.add_widget(MDLabel(text="Taken", halign="center", theme_text_color="Primary"))
        self.taken_card.add_widget(self.taken_label)

        self.missed_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            radius=[dp(15)],
            md_bg_color=missed_bg,
            elevation=1
        )
        self.missed_label = MDLabel(text="0", halign="center", font_style="H4", theme_text_color="Primary")
        self.missed_card.add_widget(MDLabel(text="Missed", halign="center", theme_text_color="Primary"))
        self.missed_card.add_widget(self.missed_label)

        summary_box.add_widget(self.taken_card)
        summary_box.add_widget(self.missed_card)

        today_str = datetime.now().strftime("%Y-%m-%d")
        date_label = MDLabel(
            text=f"{today_str}",
            halign="center",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Primary"
        )

        scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)

        back_container = MDAnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_y=None,
            height=dp(70),
            padding=[0, dp(10), 0, dp(10)]
        )
        back_btn = MDRaisedButton(
            text="Back",
            on_release=lambda x: self.go_back(),
            size_hint=(None, None),
            size=(dp(100), dp(50))
        )
        back_container.add_widget(back_btn)

        main.add_widget(summary_box)
        main.add_widget(date_label)
        main.add_widget(scroll)
        main.add_widget(back_container)

        self.add_widget(main)

        self.load_tracker_counts()
        self.load_reminders()

    def load_reminders(self):
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()
        reminders = []

        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, "r") as f:
                try:
                    reminders = json.load(f)
                except json.JSONDecodeError:
                    reminders = []

        self.list_box.clear_widgets()

        for r in reminders:
            med_name = r.get("medicine", "Unknown")
            time_str = r.get("time", "00:00 AM")
            date_str = r.get("date", today)

            try:
                reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
            except:
                continue

            key = f"{med_name}_{date_str}"

            if date_str < today:
                if not self.was_marked(med_name, date_str):
                    self.tracker_data[key] = "missed"
                continue

            if date_str == today and reminder_time + timedelta(hours=2) < datetime.now():
                if not self.was_marked(med_name, date_str):
                    self.tracker_data[key] = "missed"

            self.add_medicine_item(med_name, date_str, reminder_time)

        self.save_tracker_counts()
        self.update_summary_ui()

    def add_medicine_item(self, medicine_name, date_str, reminder_time):
        key = f"{medicine_name}_{date_str}"
        row = MDBoxLayout(orientation="horizontal", spacing=dp(10), padding=dp(10), size_hint_y=None, height=dp(60))
        row.add_widget(MDLabel(text=medicine_name, halign="left", theme_text_color="Primary"))

        if self.was_marked(medicine_name, date_str):
            status = self.tracker_data[key]
            status_label = MDLabel(
                text=f"Marked as {status.capitalize()}",
                halign="right",
                theme_text_color="Custom",
                text_color=("#4CAF50" if status == "taken" else "#E53935")
            )
            row.add_widget(status_label)
        else:
            now = datetime.now()
            if reminder_time + timedelta(hours=2) < now:
                self.tracker_data[key] = "missed"
                status_label = MDLabel(
                    text="Marked as Missed",
                    halign="right",
                    theme_text_color="Custom",
                    text_color="#E53935"
                )
                row.add_widget(status_label)
            else:
                taken_btn = MDRaisedButton(
                    text="Taken",
                    md_bg_color="#4CAF50",
                    on_release=lambda x: self.mark_and_replace(row, medicine_name, date_str, "taken")
                )
                missed_btn = MDRaisedButton(
                    text="Missed",
                    md_bg_color="#E53935",
                    on_release=lambda x: self.mark_and_replace(row, medicine_name, date_str, "missed")
                )
                row.add_widget(taken_btn)
                row.add_widget(missed_btn)

        self.list_box.add_widget(row)

        # === Divider Line ===
        divider = MDBoxLayout(size_hint_y=None, height=1)
        with divider.canvas.before:
            Color(0.7, 0.7, 0.7, 1)
            divider.rect = Rectangle()
        divider.bind(pos=self.update_divider, size=self.update_divider)
        self.list_box.add_widget(divider)

    def update_divider(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def mark_and_replace(self, row, medicine_name, date_str, status):
        key = f"{medicine_name}_{date_str}"
        if key in self.tracker_data:
            return

        self.tracker_data[key] = status
        if status == "taken":
            self.taken_count += 1
        else:
            self.missed_count += 1

        self.save_tracker_counts()
        self.update_summary_ui()

        row.clear_widgets()
        row.add_widget(MDLabel(text=medicine_name, halign="left", theme_text_color="Primary"))
        status_label = MDLabel(
            text=f"Marked as {status.capitalize()}",
            halign="right",
            theme_text_color="Custom",
            text_color=("#4CAF50" if status == "taken" else "#E53935")
        )
        row.add_widget(status_label)

    def load_tracker_counts(self):
        self.taken_count = 0
        self.missed_count = 0
        self.tracker_data = {}

        if os.path.exists(TRACK_FILE):
            with open(TRACK_FILE, "r") as f:
                try:
                    self.tracker_data = json.load(f)
                except:
                    self.tracker_data = {}

        today = datetime.now().strftime("%Y-%m-%d")
        for key, status in self.tracker_data.items():
            if key.endswith(today):
                if status == "taken":
                    self.taken_count += 1
                elif status == "missed":
                    self.missed_count += 1

    def save_tracker_counts(self):
        # Remove previous summary keys to avoid duplication
        self.tracker_data = {k: v for k, v in self.tracker_data.items() if k not in ["taken", "missed"]}
        with open(TRACK_FILE, "w") as f:
            json.dump(self.tracker_data, f, indent=4)

    def update_summary_ui(self):
        self.taken_label.text = str(self.taken_count)
        self.missed_label.text = str(self.missed_count)

    def was_marked(self, medicine_name, date_str):
        key = f"{medicine_name}_{date_str}"
        return key in self.tracker_data

    def go_back(self):
        App.get_running_app().root.go_back()