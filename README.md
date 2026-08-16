# Smart Medicine Reminder

Offline-first medication reminder built with Python, Kivy, and KivyMD.

## Features

- Stable reminder IDs (editing/deleting never depends on list order)
- One-time, daily, and weekly schedules
- Multiple reminders per day
- Dose, unit, instructions, quantity, start date, and optional end date
- Sound, vibration, desktop notification, and text-to-speech settings
- Taken/missed tracking
- Atomic JSON writes and automatic local backups
- No account, subscription, server, or paid service required

## Run on Windows

Open PowerShell in this project folder and run:

```powershell
.\venv\Scripts\python.exe main.py
```

If the virtual environment is not available, create one and install the dependencies:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install kivy==2.3.1 kivymd==1.2.0 plyer==2.1.0 pillow
.\venv\Scripts\python.exe main.py
```

Keep the `assets`, `data`, and `reminder.wav` files beside `main.py`. The app creates backups in `data/backups` whenever reminders are saved.

## Notes

This is a personal offline reminder, not medical advice or a clinical system. It does not replace a doctor or pharmacist. The current notification scheduler runs while the app is open; reliable reminders while the app is closed require a platform background-service implementation.

## Free Windows executable

Install PyInstaller in the environment:

```powershell
.\venv\Scripts\python.exe -m pip install pyinstaller
.\venv\Scripts\pyinstaller.exe --noconfirm --windowed --name SmartMedicineReminder --add-data "assets;assets" --add-data "reminder.wav;." main.py
```

The executable is created under `dist\SmartMedicineReminder`. Copy the entire folder and keep it writable so local data can be saved.
