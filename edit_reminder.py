import json
import os
from kivy.app import App
from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivy.uix.anchorlayout import AnchorLayout
from storage import load_reminders, save_reminders, validate_reminder

DATA_FILE = os.path.join("data", "reminders.json")

class EditReminderScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.edit_dialog = None
        self.reminder_index = None
        self.reminder_data = None

        anchor_layout = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))

        form_card = MDCard(
            padding=20,
            orientation="vertical",
            radius=[15],
            size_hint=(0.9, None),
            height=420,
            elevation=1,
            spacing=20,
        )

        form_card.add_widget(MDLabel(text="Edit Reminder", halign="center", font_style="H5"))

        self.medicine_input = MDTextField(hint_text="Medicine Name", mode="rectangle")
        self.time_input = MDTextField(hint_text="Time (for example 08:30 AM)", mode="rectangle")
        self.date_input = MDTextField(hint_text="Date (YYYY-MM-DD)", mode="rectangle")

        form_card.add_widget(self.medicine_input)
        form_card.add_widget(self.time_input)
        form_card.add_widget(self.date_input)

        button_layout = MDBoxLayout(orientation="horizontal", spacing=20, size_hint_y=None, height=60)
        save_btn = MDRaisedButton(text="Edit", on_release=self.save_edit)
        back_btn = MDRaisedButton(text="Back", on_release=self.go_back)
        button_layout.add_widget(save_btn)
        button_layout.add_widget(back_btn)
        form_card.add_widget(button_layout)

        anchor_layout.add_widget(form_card)
        self.add_widget(anchor_layout)

    def on_pre_enter(self, *args):
        self.reminder_id = getattr(App.get_running_app().root, "edit_id", None)
        if self.reminder_id is None:
            return
        self.reminder_data = next((r for r in load_reminders() if r.get("id") == self.reminder_id), None)
        if self.reminder_data:
            self.medicine_input.text = self.reminder_data.get("medicine", "")
            self.time_input.text = self.reminder_data.get("time", "")
            self.date_input.text = self.reminder_data.get("date", "")

    def save_edit(self, instance):
        new_medicine = self.medicine_input.text.strip()
        if not new_medicine:
            self.show_dialog("⚠️ Medicine name cannot be empty")
            return

        if self.reminder_data and self.reminder_id:
            self.reminder_data["medicine"] = new_medicine

            reminders = load_reminders()
            reminders = [self.reminder_data if r.get("id") == self.reminder_id else r for r in reminders]
            save_reminders(reminders)

            self.show_dialog("✅ Input Edited Successfully")

    def show_dialog(self, message):
        if self.edit_dialog:
            self.edit_dialog.dismiss()
        self.edit_dialog = MDDialog(
            title="Edit Reminder",
            text=message,
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: self.edit_dialog.dismiss())
            ]
        )
        self.edit_dialog.open()

    def go_back(self, instance=None):
        App.get_running_app().root.go_back()
