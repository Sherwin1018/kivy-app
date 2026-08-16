import json
import os
from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import App
from storage import load_reminders, save_reminders

DATA_FILE = os.path.join("data", "reminders.json")

class ViewRemindersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.delete_dialog = None

    def on_pre_enter(self, *args):
        self.load_reminders()

    def load_reminders(self):
        self.clear_widgets()

        anchor_layout = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))

        main_card = MDCard(
            padding=20,
            orientation="vertical",
            radius=[15],
            size_hint=(0.9, None),
            height=500,
            spacing=15,
            elevation=1
        )

        main_card.add_widget(MDLabel(
            text="Your Reminders",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        ))

        scroll = MDScrollView(size_hint=(1, None), height=350)
        list_layout = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter("height"))

        reminders = load_reminders()

        def parse_datetime(reminder):
            try:
                return datetime.strptime(f"{reminder.get('date', '')} {reminder.get('time', '')}", "%Y-%m-%d %I:%M %p")
            except:
                return datetime.min

        reminders = sorted(reminders, key=parse_datetime)

        if reminders:
            for reminder in reminders:
                medicine = reminder.get("medicine", "Unknown")
                time = reminder.get("time", "Unknown")
                date = reminder.get("date", "Unknown")

                record_card = MDCard(
                    padding=10,
                    orientation="vertical",
                    radius=[10],
                    size_hint_y=None,
                    height=140,
                    spacing=10
                )

                # Medicine name
                record_card.add_widget(MDLabel(
                    text=medicine,
                    halign="center",
                    theme_text_color="Primary",
                    font_style="Subtitle1"
                ))

                # Date and time layout
                datetime_layout = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=30)
                datetime_layout.add_widget(MDLabel(text=f"Date: {date}", halign="left", theme_text_color="Hint"))
                datetime_layout.add_widget(MDLabel(text=f"Time: {time}", halign="right", theme_text_color="Hint"))
                record_card.add_widget(datetime_layout)

                # Buttons
                btn_layout = MDBoxLayout(orientation="horizontal", spacing=20, size_hint_y=None, height=40)
                reminder_id = reminder.get("id")
                edit_btn = MDRaisedButton(text="Edit", on_release=lambda x, rid=reminder_id: self.edit_reminder(rid))
                delete_btn = MDFlatButton(text="Delete", on_release=lambda x, rid=reminder_id: self.delete_reminder(rid))
                btn_layout.add_widget(edit_btn)
                btn_layout.add_widget(delete_btn)
                record_card.add_widget(btn_layout)

                list_layout.add_widget(record_card)

                # Separator line
                separator = MDBoxLayout(size_hint_y=None, height=1, md_bg_color=(0.6, 0.6, 0.6, 1))
                list_layout.add_widget(separator)
        else:
            list_layout.add_widget(MDLabel(
                text="No reminders yet.",
                halign="center",
                theme_text_color="Hint"
            ))

        scroll.add_widget(list_layout)
        main_card.add_widget(scroll)

        back_btn = MDRaisedButton(
            text="Back",
            size_hint=(1, None),
            height=50,
            on_release=self.go_back
        )
        main_card.add_widget(back_btn)

        anchor_layout.add_widget(main_card)
        self.add_widget(anchor_layout)

    def edit_reminder(self, reminder_id):
        App.get_running_app().root.edit_id = reminder_id
        App.get_running_app().root.switch("edit_reminder")

    def delete_reminder(self, reminder_id):
        reminders = load_reminders()
        removed = next((r for r in reminders if r.get("id") == reminder_id), None)
        if not removed:
            return
        save_reminders([r for r in reminders if r.get("id") != reminder_id])

        self.show_delete_dialog(removed.get("medicine", "Reminder"))
        self.load_reminders()

    def show_delete_dialog(self, med_name):
        if self.delete_dialog:
            self.delete_dialog.dismiss()
        self.delete_dialog = MDDialog(
            title="Deleted",
            text=f"{med_name} Reminder Deleted Successfully",
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: self.delete_dialog.dismiss())
            ]
        )
        self.delete_dialog.open()

    def go_back(self, instance=None):
        App.get_running_app().root.go_back()
