import os
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QFont

from core.gesture_engine import GESTURE_META


class MiniHUD(QWidget):
    """Floating, always-on-top HUD widget for real-time gesture feedback on desktop."""

    def __init__(self, main_window=None):
        super().__init__(None)
        self.main_window = main_window
        self._drag_pos = QPoint()

        # Window Flags: Always on top, frameless tool window
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumSize(220, 50)
        self.resize(240, 54)

        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Main pill frame
        self.card = QFrame(self)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #0b0e14;
                border: 1px solid #00b4d8;
                border-radius: 12px;
            }
        """)
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(12, 6, 12, 6)
        card_layout.setSpacing(10)

        # Lock Status dot
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #ef4444; font-size: 14px;")
        card_layout.addWidget(self.status_dot)

        # Gesture Icon & Name Column
        text_col = QVBoxLayout()
        text_col.setSpacing(1)

        self.gesture_title = QLabel("LOCKED")
        self.gesture_title.setStyleSheet("color: #00b4d8; font-weight: 800; font-size: 12px; letter-spacing: 1px;")

        self.action_subtitle = QLabel("Show Open Palm")
        self.action_subtitle.setStyleSheet("color: #64748b; font-size: 10px;")

        text_col.addWidget(self.gesture_title)
        text_col.addWidget(self.action_subtitle)
        card_layout.addLayout(text_col, 1)

        # Close / Hide button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(18, 18)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748b;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ef4444;
            }
        """)
        close_btn.clicked.connect(self.hide)
        card_layout.addWidget(close_btn)

        root.addWidget(self.card)

    def update_status(self, displayed: str, action_label: str, unlocked: bool, confidence: float = 0.0):
        if unlocked:
            self.status_dot.setStyleSheet("color: #06d6a0; font-size: 14px;")
            self.card.setStyleSheet("""
                QFrame {
                    background-color: #0b0e14;
                    border: 1px solid #06d6a0;
                    border-radius: 12px;
                }
            """)
        else:
            self.status_dot.setStyleSheet("color: #ef4444; font-size: 14px;")
            self.card.setStyleSheet("""
                QFrame {
                    background-color: #0b0e14;
                    border: 1px solid #1e293b;
                    border-radius: 12px;
                }
            """)

        meta = GESTURE_META.get(displayed, GESTURE_META["NONE"])
        name = meta.get("desc", "").upper() if displayed not in ("NONE", "") else ("READY" if unlocked else "LOCKED")
        color = meta.get("color", "#00b4d8") if unlocked else "#94a3b8"

        self.gesture_title.setText(name)
        self.gesture_title.setStyleSheet(f"color: {color}; font-weight: 800; font-size: 12px; letter-spacing: 1px;")

        subtitle = action_label if action_label else ("Control Unlocked" if unlocked else "Show Open Palm")
        self.action_subtitle.setText(subtitle)

    # ── Mouse Drag Handling for Desktop Movement ─────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
