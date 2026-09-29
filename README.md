# GestureFlow
### Gesture-Based Control System | Computer Vision + ML

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python main.py
```

On Windows, use Python 3.10 for the optional TFLite model backend. If TensorFlow
is not installed, GestureFlow safely uses its built-in normalized landmark rules.

> **Python 3.9+** required. Tested on Windows 10/11 and Ubuntu 22.04.

---

## Features

| Screen | Description |
|---|---|
| **Home** | Manage user profiles and select control presets |
| **Control** | Live gesture detection with real-time action mapping |
| **Recorder** | Record and label custom gestures with camera feedback |
| **Settings** | Camera, detection confidence, cooldown, save path |

## Daily Use

1. Open **Control** and press **START CONTROL**.
2. Show an open palm to unlock system control.
3. Use **CALIBRATE CURSOR AREA**, then move your index finger around the area
     where you want the cursor to work.
4. Enable pinch click/drag only when you need it. It is off by default.
5. Use the system tray to show the app, pause control, or exit.

Control locks automatically after the hand disappears for two seconds.
Cursor sensitivity, edge margin, confidence, and safety toggles are saved in
`data/profiles.json`.

## Application Profiles

In **Settings**, map an executable such as `chrome.exe` to an existing preset.
The active preset switches automatically when that application is foreground.

## Packaging

Create a Windows executable with PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name GestureFlow \
    --add-data "models;models" --add-data "data;data" main.py
```

The portable build is created at `dist/GestureFlow/GestureFlow.exe`.
To create a normal Windows installer, install Inno Setup and open
`installer/GestureFlow.iss`, then choose **Build**. The installer is configured
for a per-user install under `%LOCALAPPDATA%`, so it does not require admin
rights and can create writable settings beside the installed app.

Runtime problems are written to `data/gestureflow.log`.

---

## Supported Gestures

| Gesture | Detection Method |
|---|---|
| Open Palm | All 5 landmarks extended |
| Fist | All landmarks closed |
| Thumbs Up / Down | Single thumb landmark + wrist Y |
| Peace / V | Index + Middle extended |
| Point | Index only |
| Pinch | Thumb + index together; volume or optional click/drag |
| Swipe Left/Right/Up/Down | Wrist motion vector tracking |

---

## Control Presets

### Media Player
- Open Palm → Play/Pause
- Fist → Mute
- Swipe Right → Next Track
- Swipe Left → Previous Track
- Thumbs Up → Volume Up
- Thumbs Down → Volume Down

### Browser
- Swipe Left/Right → Back/Forward
- Swipe Up/Down → Scroll
- Open Palm → New Tab
- Fist → Close Tab
- Peace → Refresh

### Gaming
- Open Palm → Jump (Space)
- Fist → Interact (E)
- Swipe Left/Right → Move A/D
- Swipe Up/Down → W/S
- Point → Fire/Use (F)

### Navigation
- Swipe Up/Down → Page Up/Down
- Open Palm → Ctrl+Home
- Fist → Ctrl+End

---

## ML Pipeline

```
Camera Input
    ↓ OpenCV capture + mirror flip
Pre-Processing
    ↓ BGR→RGB conversion, normalization
Hand Detection
    ↓ MediaPipe CNN (21 landmark points)
Feature Extraction
    ↓ Fingertip Y/X relative to PIP joints
    ↓ Wrist motion vector (deque of 20 frames)
Static Classification
    ↓ Rule-based landmark comparison
Dynamic Swipe Detection
    ↓ Δx/Δy threshold on wrist trajectory
Action Mapping
    ↓ Preset JSON lookup
pynput Execution
    ↓ Keyboard/Mouse/Media event injection
Application Response
```

---

## Tech Stack
- **PyQt5** — Desktop GUI
- **MediaPipe Hands** — Hand landmark detection (CNN)
- **OpenCV** — Camera capture + frame processing
- **pynput** — System-level keyboard/media control
- **NumPy** — Numerical operations
