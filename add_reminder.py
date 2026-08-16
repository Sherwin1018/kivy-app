from datetime import datetime
from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.snackbar import Snackbar
from storage import load_reminders, save_reminders, validate_reminder

class AddReminderScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs); self.build_ui()
    def field(self, hint, text=""):
        return MDTextField(hint_text=hint, text=text, mode="rectangle", size_hint_y=None, height=dp(48))
    def build_ui(self):
        box=MDBoxLayout(orientation="vertical",padding=dp(20),spacing=dp(10),size_hint_y=None); box.bind(minimum_height=box.setter("height"))
        box.add_widget(MDLabel(text="Add Medication",halign="center",font_style="H5",size_hint_y=None,height=dp(45)))
        self.medicine=self.field("Medication name"); self.dosage=self.field("Dose (for example 500)"); self.unit=self.field("Unit (tablet, capsule, ml, drops)","tablet")
        self.time=self.field("Time (for example 08:30 AM)"); self.date=self.field("Start date (YYYY-MM-DD)",datetime.now().strftime("%Y-%m-%d")); self.frequency=self.field("Frequency: once, daily, or weekly","once")
        self.weekdays=self.field("Weekly days, comma-separated (optional)"); self.end_date=self.field("End date (YYYY-MM-DD, optional)"); self.quantity=self.field("Quantity in stock (optional)"); self.instructions=self.field("Instructions (before/after food, etc.)")
        for w in (self.medicine,self.dosage,self.unit,self.time,self.date,self.frequency,self.weekdays,self.end_date,self.quantity,self.instructions): box.add_widget(w)
        actions=MDBoxLayout(spacing=dp(10),size_hint_y=None,height=dp(55)); actions.add_widget(MDRaisedButton(text="Save medication",on_release=self.save)); actions.add_widget(MDFlatButton(text="Back",on_release=self.go_back)); box.add_widget(actions); self.add_widget(box)
    def save(self,*_):
        item={"medicine":self.medicine.text.strip(),"dosage":self.dosage.text.strip(),"unit":self.unit.text.strip() or "tablet","time":self.time.text.strip().upper(),"date":self.date.text.strip(),"frequency":self.frequency.text.strip().lower() or "once","weekdays":[x.strip() for x in self.weekdays.text.split(",") if x.strip()],"end_date":self.end_date.text.strip(),"quantity":self.quantity.text.strip(),"instructions":self.instructions.text.strip(),"active":True}
        errors=validate_reminder(item)
        if errors: Snackbar(text=errors[0]).open(); return
        reminders=load_reminders()
        if any(r.get("medicine","").casefold()==item["medicine"].casefold() and r.get("date")==item["date"] and r.get("time")==item["time"] for r in reminders): Snackbar(text="That reminder already exists.").open(); return
        import uuid; item["id"]=uuid.uuid4().hex; save_reminders(reminders+[item]); Snackbar(text="Medication reminder saved.").open()
    def go_back(self,*_): App.get_running_app().root.go_back()
