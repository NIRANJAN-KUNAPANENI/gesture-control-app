import os
import logging
import json

from PyQt5.QtWidgets import (
    QDialog, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QAction, QApplication, QLabel, QMenu, QPushButton, QStackedWidget,
    QStatusBar, QStyle, QSystemTrayIcon, QDialogButtonBox
)
from PyQt5.QtCore    import QEvent, Qt, QTimer

from core.camera_thread import CameraThread
from core.action_mapper import ActionMapper

from app.screens.home_screen     import HomeScreen
from app.screens.control_screen  import ControlScreen
from app.screens.recorder_screen import RecorderScreen
from app.screens.settings_screen import SettingsScreen

try:
    from pynput import keyboard
except Exception:
    keyboard = None

NAV_ITEMS = [
    ("HOME",     "H", 0),
    ("CONTROL",  "C", 1),
    ("RECORDER", "R", 2),
    ("SETTINGS", "S", 3),
]


class MainWindow(QMainWindow):
    def __init__(self, base_dir: str):
        super().__init__()
        logging.basicConfig(
            filename=os.path.join(base_dir, "data", "gestureflow.log"),
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )
        self.base_dir    = base_dir
        self.data_dir    = os.path.join(base_dir, "data")
        self.presets_path  = os.path.join(self.data_dir, "presets.json")
        self.profiles_path = os.path.join(self.data_dir, "profiles.json")

        self.setWindowTitle("GestureFlow")
        self.setMinimumSize(1280, 780)
        self.resize(1400, 840)

        # ── Shared resources ──────────────────────────────────────────────────
        self.action_mapper = ActionMapper(self.presets_path, profiles_path=self.profiles_path)
        self.cam_thread    = CameraThread()
        self.cam_thread.set_action_mapper(self.action_mapper)

        # ── Build UI ──────────────────────────────────────────────────────────
        central = QWidget()
        central.setObjectName("content_area")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._sidebar = self._build_sidebar()
        root.addWidget(self._sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")
        root.addWidget(self.stack)

        # ── Screens ───────────────────────────────────────────────────────────
        self.home_screen     = HomeScreen(self)
        self.control_screen  = ControlScreen(self)
        self.recorder_screen = RecorderScreen(self)
        self.settings_screen = SettingsScreen(self)

        for screen in [self.home_screen, self.control_screen,
                       self.recorder_screen, self.settings_screen]:
            self.stack.addWidget(screen)

        # ── Status bar ────────────────────────────────────────────────────────
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status_label = QLabel("SYSTEM READY  |  CAMERA INITIALIZING...")
        sb.addWidget(self._status_label)

        # ── Start camera thread ───────────────────────────────────────────────
        self.cam_thread.error_signal.connect(self._on_cam_error)
        self.cam_thread.start()

        # Status update timer
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick_status)
        self._tick_timer.start(2000)
        self._cam_ready = False
        self._create_tray()
        self._start_global_hotkey()

        # Default nav selection
        self._nav_buttons[0].setProperty("active", "true")
        self._nav_buttons[0].style().unpolish(self._nav_buttons[0])
        self._nav_buttons[0].style().polish(self._nav_buttons[0])
        self._navigate(1)
        if not self._setup_complete():
            QTimer.singleShot(250, self._show_setup_wizard)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _create_tray(self):
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self._tray.setToolTip("GestureFlow")
        menu = QMenu()

        show_action = QAction("Show GestureFlow", self)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        pause_action = QAction("Pause / Resume control", self)
        pause_action.triggered.connect(self.control_screen._toggle_control)
        menu.addAction(pause_action)
        menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self._exit_application)
        menu.addAction(exit_action)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(
            lambda reason: self._show_window()
            if reason == QSystemTrayIcon.DoubleClick else None
        )
        if QSystemTrayIcon.isSystemTrayAvailable():
            self._tray.show()

    def _start_global_hotkey(self):
        if keyboard is None:
            self._hotkey_listener = None
            return
        try:
            self._hotkey_listener = keyboard.GlobalHotKeys({
                "<ctrl>+<alt>+g": self._toggle_control_from_hotkey,
            })
            self._hotkey_listener.start()
        except Exception:
            self._hotkey_listener = None

    def _toggle_control_from_hotkey(self):
        QTimer.singleShot(0, self.control_screen._toggle_control)

    def _setup_complete(self):
        try:
            with open(self.profiles_path) as profiles_file:
                return bool(json.load(profiles_file).get("setup_complete", False))
        except (OSError, ValueError):
            return False

    def _show_setup_wizard(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("GestureFlow setup")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        title = QLabel("Set up GestureFlow")
        title.setObjectName("page_title")
        text = QLabel(
            "1. Choose your camera in Settings.\n"
            "2. Start Control and show an open palm to unlock.\n"
            "3. Calibrate the cursor area before enabling click/drag.\n"
            "4. Keep pinch click/drag off until you are comfortable."
        )
        text.setWordWrap(True)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(title)
        layout.addWidget(text)
        layout.addWidget(buttons)
        dialog.exec_()
        try:
            with open(self.profiles_path) as profiles_file:
                data = json.load(profiles_file)
            data["setup_complete"] = True
            with open(self.profiles_path, "w") as profiles_file:
                json.dump(data, profiles_file, indent=2)
        except (OSError, ValueError):
            logging.exception("Could not save setup state")

    def _show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _exit_application(self):
        self._tray.hide()
        self.close()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            QTimer.singleShot(0, self.hide)

    def _build_sidebar(self):
        sb = QWidget()
        sb.setObjectName("sidebar")
        sb.setFixedWidth(190)

        layout = QVBoxLayout(sb)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo block
        logo_frame = QWidget()
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(2)

        logo = QLabel("GESTURE\nFLOW")
        logo.setObjectName("logo_label")
        logo_sub = QLabel("HAND CONTROL")
        logo_sub.setObjectName("logo_sub")

        logo_layout.addWidget(logo)
        logo_layout.addWidget(logo_sub)
        layout.addWidget(logo_frame)

        layout.addSpacing(12)

        # Nav buttons
        self._nav_buttons = []
        for label, key, idx in NAV_ITEMS:
            btn = QPushButton(f"  [{key}]  {label}")
            btn.setObjectName("nav_btn")
            btn.setProperty("active", "false")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self._navigate(i))
            self._nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch(1)

        # Cam status dot
        self._cam_dot = QLabel("● CAMERA READY")
        self._cam_dot.setObjectName("status_dot")
        layout.addWidget(self._cam_dot)

        # Version
        ver = QLabel("GESTUREFLOW v1.0.0")
        ver.setObjectName("version_label")
        layout.addWidget(ver)

        layout.addSpacing(10)
        return sb

    # ── Navigation ────────────────────────────────────────────────────────────
    def _navigate(self, idx: int):
        # De-activate all
        for btn in self._nav_buttons:
            btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Activate selected
        self._nav_buttons[idx].setProperty("active", "true")
        self._nav_buttons[idx].style().unpolish(self._nav_buttons[idx])
        self._nav_buttons[idx].style().polish(self._nav_buttons[idx])

        self.stack.setCurrentIndex(idx)

        # Update camera thread mode based on active screen
        if idx == 1:   # Control screen
            mode = (CameraThread.MODE_CONTROL
                    if getattr(self.control_screen, "_active", False)
                    else CameraThread.MODE_IDLE)
            self.cam_thread.set_mode(mode)
        elif idx == 2: # Recorder screen
            self.cam_thread.set_mode(CameraThread.MODE_RECORD)
        else:
            self.cam_thread.set_mode(CameraThread.MODE_IDLE)

        # Notify screens
        screen = self.stack.currentWidget()
        if hasattr(screen, "on_activated"):
            screen.on_activated()

    def navigate_to(self, idx: int):
        """Public method for screens to trigger navigation."""
        self._navigate(idx)

    # ── Signals ───────────────────────────────────────────────────────────────
    def _on_cam_error(self, msg: str):
        logging.error(msg)
        self._status_label.setText(f"CAMERA ERROR: {msg}")
        self._cam_dot.setText("● CAMERA ERROR")
        self._cam_dot.setStyleSheet("color:#ef4444; font-size:10px; padding:8px 20px;")

    def _tick_status(self):
        if not self._cam_ready and self.cam_thread.isRunning():
            self._cam_ready = True
            self._status_label.setText(
                "SYSTEM ONLINE  |  MEDIAPIPE ACTIVE  |  ALL PRESETS LOADED"
            )
            self._cam_dot.setText("● CAMERA ACTIVE")
            self._cam_dot.setStyleSheet("color:#06d6a0; font-size:10px; padding:8px 20px;")

    # ── Cleanup ───────────────────────────────────────────────────────────────
    def closeEvent(self, event):
        if self._hotkey_listener:
            self._hotkey_listener.stop()
        self.cam_thread.stop()
        event.accept()
