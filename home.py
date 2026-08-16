from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivymd.app import MDApp

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(30),
            padding=[dp(40), dp(80), dp(40), dp(80)],  # More vertical padding
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        logo = FitImage(
            source="assets/homelogo.png",
            size_hint=(None, None),
            size=(dp(300), dp(300)),  # Larger image
            pos_hint={"center_x": 0.5}
        )

        title = MDLabel(
            text="Smart Medicine Reminder",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        )

        get_started_btn = MDRaisedButton(
            text="Get Started",
            size_hint=(None, None),
            size=(dp(160), dp(50)),
            pos_hint={"center_x": 0.5},
            on_release=self.go_to_dashboard
        )

        layout.add_widget(logo)
        layout.add_widget(title)
        layout.add_widget(get_started_btn)

        self.add_widget(layout)

    def go_to_dashboard(self, *args):
        app = MDApp.get_running_app()
        if hasattr(app.root, "switch"):
            app.root.switch("dashboard")
