from kivy import Config

# Stability & OpenGL fixes
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'resizable', '1')
Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'fbo', 'hardware')

from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.uix.screenmanager import NoTransition
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

# Import screens
from home import HomeScreen
from dashboard import DashboardScreen
from add_reminder import AddReminderScreen
from view_reminders import ViewRemindersScreen
from tracker import TrackerScreen
from settings import SettingsScreen
from edit_reminder import EditReminderScreen

Window.size = (360, 640)


class CustomBottomNav(MDBoxLayout):
    def __init__(self, screen_manager_callback, active_screen, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height="70dp", padding="8dp", spacing=0, **kwargs)
        self.screen_manager_callback = screen_manager_callback
        self.current = active_screen
        self.md_bg_color = MDApp.get_running_app().theme_cls.primary_color

        self.items = {
            "dashboard": ("home", "Home"),
            "view_reminders": ("calendar", "View"),
            "add_reminder": ("plus-box", "Add"),
            "tracker": ("chart-line", "Tracker"),
            "settings": ("cog", "Settings"),
        }

        self.buttons = {}

        for key, (icon, label_text) in self.items.items():
            btn_box = MDBoxLayout(
                orientation="vertical",
                spacing=2,
                size_hint_x=1,
                size_hint_y=None,
                height="56dp",
                padding=[0, 4, 0, 0]
            )
            icon_btn = MDIconButton(
                icon=icon,
                pos_hint={"center_x": 0.5},
                on_release=lambda x, k=key: self.switch(k)
            )
            text_label = MDLabel(
                text=label_text,
                halign="center",
                pos_hint={"center_x": 0.5},
                font_style="Caption",
                theme_text_color="Custom"
            )
            btn_box.add_widget(icon_btn)
            btn_box.add_widget(text_label)
            self.buttons[key] = (icon_btn, text_label)
            self.add_widget(btn_box)

        self.update_active()

    def switch(self, screen_name):
        self.current = screen_name
        self.screen_manager_callback[screen_name]()
        self.update_active()

    def update_active(self):
        for key, (icon_btn, label) in self.buttons.items():
            is_active = key == self.current
            icon_btn.theme_text_color = "Custom"
            icon_btn.text_color = (1, 1, 1, 1) if is_active else (0.7, 0.7, 0.7, 1)
            label.text_color = (1, 1, 1, 1) if is_active else (0.7, 0.7, 0.7, 1)
            label.font_style = "Subtitle2" if is_active else "Caption"


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.nav_stack = []

        self.sm = MDScreenManager(transition=NoTransition(), size_hint_y=1)
        self.add_widget(self.sm)

        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(AddReminderScreen(name="add_reminder"))
        self.sm.add_widget(ViewRemindersScreen(name="view_reminders"))
        self.sm.add_widget(TrackerScreen(name="tracker"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(EditReminderScreen(name="edit_reminder"))

        nav_callbacks = {
            "dashboard": lambda: self.switch("dashboard"),
            "add_reminder": lambda: self.switch("add_reminder"),
            "view_reminders": lambda: self.switch("view_reminders"),
            "tracker": lambda: self.switch("tracker"),
            "settings": lambda: self.switch("settings"),
        }

        self.navbar = CustomBottomNav(screen_manager_callback=nav_callbacks, active_screen="dashboard")
        self.add_widget(self.navbar)

        self.sm.current = "home"
        self.update_navbar_visibility("home")

    def update_navbar_visibility(self, screen_name):
        self.navbar.opacity = 0 if screen_name == "home" else 1
        self.navbar.disabled = screen_name == "home"

    def switch(self, screen_name):
        if self.sm.current != screen_name:
            self.nav_stack.append(self.sm.current)

        self.sm.current = screen_name
        self.navbar.current = screen_name
        self.navbar.update_active()
        self.update_navbar_visibility(screen_name)

    def go_back(self):
        if self.nav_stack:
            prev_screen = self.nav_stack.pop()
            self.sm.current = prev_screen
            self.navbar.current = prev_screen
            self.navbar.update_active()
            self.update_navbar_visibility(prev_screen)
        else:
            self.sm.current = "dashboard"
            self.navbar.current = "dashboard"
            self.navbar.update_active()
            self.update_navbar_visibility("dashboard")


class MedicineReminderApp(MDApp):
    def build(self):
        # Calm, high-contrast healthcare palette: deep navy for trust,
        # teal for primary actions, mint for success, amber for attention.
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.theme_style = "Light"
        self.edit_index = None
        self.edit_id = None
        return MainLayout()


if __name__ == "__main__":
    MedicineReminderApp().run()
