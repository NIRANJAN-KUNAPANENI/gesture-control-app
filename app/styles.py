STYLE = """
/* ═══════════════════════════════════════════════════════════════
   GESTUREFLOW — Neural Interface Theme
   Cyberpunk HUD | Dark | Electric Cyan + Magenta
═══════════════════════════════════════════════════════════════ */

* {
    font-family: 'Segoe UI', 'Arial', sans-serif;
    outline: none;
}

QMainWindow, QWidget {
    background-color: #080b14;
    color: #e2e8f0;
}

QDialog {
    background-color: #0d1117;
    color: #e2e8f0;
    border: 1px solid #1a2744;
}

/* ─── SIDEBAR ─────────────────────────────────────────────── */
QWidget#sidebar {
    background-color: #060810;
    border-right: 1px solid #0f1929;
}

QLabel#logo_label {
    color: #00b4d8;
    font-size: 18px;
    font-weight: 900;
    letter-spacing: 6px;
    padding: 30px 20px 20px 20px;
    border-bottom: 1px solid #0f1929;
    qproperty-alignment: AlignCenter;
}

QLabel#logo_sub {
    color: #1e3a5f;
    font-size: 9px;
    letter-spacing: 4px;
    padding: 0px 20px 16px 20px;
    qproperty-alignment: AlignCenter;
}

QPushButton#nav_btn {
    background: transparent;
    color: #334155;
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 15px 20px 15px 22px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    border-radius: 0px;
}

QPushButton#nav_btn:hover {
    background-color: #0a1628;
    color: #7dd3e8;
    border-left: 3px solid #0077b6;
}

QPushButton#nav_btn[active="true"] {
    background-color: #0f1f38;
    color: #00b4d8;
    border-left: 3px solid #00b4d8;
}

QLabel#version_label {
    color: #1e3a5f;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 12px;
    qproperty-alignment: AlignCenter;
}

QLabel#status_dot {
    color: #06d6a0;
    font-size: 10px;
    padding: 8px 20px;
}

/* ─── CONTENT AREA ────────────────────────────────────────── */
QWidget#content_area {
    background-color: #080b14;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* ─── CARDS ───────────────────────────────────────────────── */
QFrame#card {
    background-color: #0a0e1a;
    border: 1px solid #0f1929;
    border-radius: 14px;
}

QFrame#card_accent {
    background-color: #0a0e1a;
    border: 1px solid #00b4d8;
    border-radius: 14px;
}

QFrame#card_glow {
    background-color: #080c18;
    border: 1px solid #003d5c;
    border-radius: 14px;
}

QFrame#camera_frame {
    background-color: #050709;
    border: 2px solid #0f1929;
    border-radius: 16px;
}

QFrame#camera_frame_active {
    background-color: #050709;
    border: 2px solid #00b4d8;
    border-radius: 16px;
}

/* ─── BUTTONS ─────────────────────────────────────────────── */
QPushButton#primary_btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #005580, stop:1 #00b4d8);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 12px 28px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    min-height: 20px;
}

QPushButton#primary_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00b4d8, stop:1 #48cae4);
}

QPushButton#primary_btn:pressed {
    background: #003d5c;
}

QPushButton#primary_btn:disabled {
    background: #1e293b;
    color: #475569;
}

QPushButton#danger_btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7f1d1d, stop:1 #ef4444);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 12px 28px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    min-height: 20px;
}

QPushButton#danger_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ef4444, stop:1 #f87171);
}

QPushButton#success_btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #064e3b, stop:1 #06d6a0);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 12px 28px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    min-height: 20px;
}

QPushButton#success_btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #06d6a0, stop:1 #34d399);
}

QPushButton#ghost_btn {
    background: transparent;
    color: #475569;
    border: 1px solid #0f1929;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
}

QPushButton#ghost_btn:hover {
    background-color: #0a1628;
    color: #00b4d8;
    border: 1px solid #00b4d8;
}

QPushButton#icon_btn {
    background: transparent;
    color: #475569;
    border: 1px solid #0f1929;
    border-radius: 8px;
    padding: 8px;
    font-size: 14px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
}

QPushButton#icon_btn:hover {
    background-color: #0a1628;
    color: #00b4d8;
    border: 1px solid #00b4d8;
}

QPushButton#preset_btn {
    background-color: #0a0e1a;
    color: #64748b;
    border: 1px solid #0f1929;
    border-radius: 10px;
    padding: 16px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-align: center;
}

QPushButton#preset_btn:hover {
    background-color: #0f1929;
    color: #cbd5e1;
    border: 1px solid #1e3a5f;
}

QPushButton#preset_btn[active="true"] {
    background-color: #061624;
    color: #00b4d8;
    border: 1px solid #00b4d8;
}

/* ─── INPUTS ──────────────────────────────────────────────── */
QLineEdit {
    background-color: #0a0e1a;
    border: 1px solid #0f1929;
    border-radius: 8px;
    color: #e2e8f0;
    padding: 11px 14px;
    font-size: 13px;
    selection-background-color: #00b4d8;
}

QLineEdit:focus {
    border: 1px solid #00b4d8;
    background-color: #080c18;
}

QLineEdit::placeholder {
    color: #334155;
}

QComboBox {
    background-color: #0a0e1a;
    border: 1px solid #0f1929;
    border-radius: 8px;
    color: #e2e8f0;
    padding: 10px 14px;
    font-size: 12px;
    min-height: 20px;
}

QComboBox:focus {
    border: 1px solid #00b4d8;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #475569;
    width: 0;
    height: 0;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #0d1117;
    border: 1px solid #0f1929;
    border-radius: 8px;
    color: #e2e8f0;
    selection-background-color: #0f1929;
    selection-color: #00b4d8;
    padding: 4px;
}

/* ─── LABELS ──────────────────────────────────────────────── */
QLabel#h1 {
    font-size: 30px;
    font-weight: 900;
    color: #f1f5f9;
    letter-spacing: 2px;
}

QLabel#h2 {
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: 1px;
}

QLabel#h3 {
    font-size: 13px;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 3px;
    text-transform: uppercase;
}

QLabel#muted {
    color: #334155;
    font-size: 11px;
    letter-spacing: 1px;
}

QLabel#accent {
    color: #00b4d8;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#gesture_big {
    color: #00b4d8;
    font-size: 36px;
    font-weight: 900;
    letter-spacing: 6px;
}

QLabel#gesture_action {
    color: #475569;
    font-size: 13px;
    letter-spacing: 3px;
    font-weight: 600;
}

QLabel#badge {
    background-color: #061624;
    color: #00b4d8;
    border: 1px solid #00b4d8;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}

QLabel#badge_off {
    background-color: #0a0e1a;
    color: #334155;
    border: 1px solid #0f1929;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}

QLabel#badge_success {
    background-color: #022c22;
    color: #06d6a0;
    border: 1px solid #06d6a0;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}

QLabel#badge_danger {
    background-color: #2d0b0b;
    color: #ef4444;
    border: 1px solid #ef4444;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}

QLabel#camera_placeholder {
    color: #1e3a5f;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 3px;
    qproperty-alignment: AlignCenter;
}

/* ─── SCROLLBARS ──────────────────────────────────────────── */
QScrollBar:vertical {
    background: #060810;
    width: 5px;
    border-radius: 2px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #0f1929;
    border-radius: 2px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #00b4d8;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #060810;
    height: 5px;
    border-radius: 2px;
}

QScrollBar::handle:horizontal {
    background: #0f1929;
    border-radius: 2px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #00b4d8;
}

/* ─── LIST / TABLE ────────────────────────────────────────── */
QListWidget {
    background-color: #0a0e1a;
    border: 1px solid #0f1929;
    border-radius: 10px;
    color: #e2e8f0;
    padding: 6px;
    font-size: 12px;
}

QListWidget::item {
    padding: 10px 12px;
    border-radius: 6px;
    margin: 1px 0px;
    border: none;
}

QListWidget::item:selected {
    background-color: #061624;
    color: #00b4d8;
}

QListWidget::item:hover {
    background-color: #0a1628;
    color: #cbd5e1;
}

/* ─── RADIO / CHECK ───────────────────────────────────────── */
QRadioButton {
    color: #94a3b8;
    font-size: 12px;
    spacing: 8px;
    font-weight: 600;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #1e293b;
    background: transparent;
}

QRadioButton::indicator:checked {
    background: #00b4d8;
    border: 2px solid #00b4d8;
}

QCheckBox {
    color: #94a3b8;
    font-size: 12px;
    spacing: 8px;
    font-weight: 600;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid #1e293b;
    background: transparent;
}

QCheckBox::indicator:checked {
    background: #00b4d8;
    border: 2px solid #00b4d8;
}

/* ─── SLIDER ──────────────────────────────────────────────── */
QSlider::groove:horizontal {
    height: 4px;
    background: #0f1929;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #00b4d8;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #005580, stop:1 #00b4d8);
    border-radius: 2px;
}

/* ─── SPINBOX ─────────────────────────────────────────────── */
QSpinBox {
    background-color: #0a0e1a;
    border: 1px solid #0f1929;
    border-radius: 8px;
    color: #e2e8f0;
    padding: 10px 12px;
    font-size: 13px;
}

QSpinBox:focus {
    border: 1px solid #00b4d8;
}

QSpinBox::up-button, QSpinBox::down-button {
    background: transparent;
    border: none;
    width: 20px;
}

/* ─── SEPARATOR ───────────────────────────────────────────── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #0f1929;
    background-color: #0f1929;
    max-height: 1px;
}

/* ─── STATUS BAR ──────────────────────────────────────────── */
QStatusBar {
    background: #060810;
    color: #1e3a5f;
    border-top: 1px solid #0f1929;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 4px 12px;
}

/* ─── TOOLTIP ─────────────────────────────────────────────── */
QToolTip {
    background-color: #0d1117;
    color: #e2e8f0;
    border: 1px solid #00b4d8;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}

/* ─── MESSAGE BOX ─────────────────────────────────────────── */
QMessageBox {
    background-color: #0d1117;
    color: #e2e8f0;
}

QMessageBox QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #005580, stop:1 #00b4d8);
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 700;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background: #48cae4;
}

/* ─── CONTROL WORKSPACE ─────────────────────────────────── */
QWidget#content_area {
    background: #111416;
}

QWidget#sidebar {
    background: #0d1012;
    border-right: 1px solid #252b2e;
}

QLabel#logo_label {
    color: #f2f4ef;
    font-size: 22px;
    letter-spacing: 2px;
    padding: 28px 18px 8px 18px;
    border: none;
}

QLabel#logo_sub, QLabel#version_label {
    color: #788184;
    letter-spacing: 1px;
}

QPushButton#nav_btn {
    color: #899397;
    border: none;
    border-left: 2px solid transparent;
    padding: 13px 18px;
    font-size: 12px;
    letter-spacing: 0px;
}

QPushButton#nav_btn:hover {
    background: #171c1e;
    color: #f2f4ef;
    border-left-color: #82d8c0;
}

QPushButton#nav_btn[active="true"] {
    background: #192322;
    color: #9be6d1;
    border-left-color: #82d8c0;
}

QLabel#status_dot {
    color: #82d8c0;
    padding: 8px 18px;
}

QLabel#page_title {
    color: #f2f4ef;
    font-size: 28px;
    font-weight: 700;
}

QLabel#page_subtitle, QLabel#muted_label {
    color: #899397;
    font-size: 12px;
}

QFrame#workspace_panel {
    background: #171c1e;
    border: 1px solid #293235;
    border-radius: 10px;
}

QLabel#camera_view {
    background: #0b0e0f;
    border: 1px solid #293235;
    border-radius: 7px;
    color: #657174;
    font-size: 13px;
    letter-spacing: 1px;
}

QLabel#panel_overline {
    color: #788184;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#gesture_value {
    color: #f2f4ef;
    font-size: 25px;
    font-weight: 700;
}

QLabel#status_badge_on, QLabel#status_badge_off {
    border-radius: 12px;
    padding: 7px 12px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#status_badge_on {
    background: #21463d;
    color: #9be6d1;
}

QLabel#status_badge_off {
    background: #252b2e;
    color: #aab2b3;
}

QPushButton#primary_btn, QPushButton#danger_btn, QPushButton#secondary_btn,
QPushButton#text_btn {
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0px;
    min-height: 18px;
}

QPushButton#primary_btn {
    background: #82d8c0;
    color: #10201b;
    padding: 11px 16px;
}

QPushButton#primary_btn:hover {
    background: #9be6d1;
}

QPushButton#danger_btn {
    background: #dc806d;
    color: #271313;
    padding: 11px 16px;
}

QPushButton#secondary_btn {
    background: #222a2d;
    color: #d6dcd8;
    border: 1px solid #3a4548;
    padding: 9px 12px;
}

QPushButton#text_btn {
    background: transparent;
    color: #82d8c0;
    border: none;
    padding: 4px;
}

QComboBox, QCheckBox {
    color: #d6dcd8;
    font-size: 12px;
}

QComboBox {
    background: #111416;
    border: 1px solid #3a4548;
    border-radius: 5px;
    padding: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QListWidget {
    background: #111416;
    border: 1px solid #293235;
    border-radius: 5px;
    color: #aab2b3;
    font-size: 11px;
    padding: 4px;
}
"""
