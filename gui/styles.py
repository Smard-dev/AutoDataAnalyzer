# gui/styles.py

CATPPUCCIN_MOCHA = """
/* ===== Global Styles ===== */
QWidget {
    font-size: 13px;
    font-family: 'Segoe UI', 'Cascadia Code', 'Tahoma', 'Verdana', sans-serif;
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QMainWindow {
    background-color: #1e1e2e;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 2px solid #45475a;
    border-radius: 12px;
    background-color: #181825;
    margin-top: -1px;
}

QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    padding: 12px 25px;
    margin-right: 4px;
    font-size: 14px;
    font-weight: bold;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    border: 1px solid #45475a;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #181825;
    color: #89b4fa;
    border-bottom: 3px solid #89b4fa;
}

QTabBar::tab:hover:!selected {
    background-color: #45475a;
    color: #cdd6f4;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #45475a;
    color: #cdd6f4;
    border: 2px solid #585b70;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: 2px solid #89b4fa;
}

QPushButton:pressed {
    background-color: #74c7ec;
    border: 2px solid #74c7ec;
}

QPushButton:disabled {
    background-color: #313244;
    color: #6c7086;
    border: 2px solid #45475a;
}

#runButton {
    background-color: #a6e3a1;
    color: #1e1e2e;
    font-size: 15px;
    padding: 12px 25px;
    border: 2px solid #94e2d5;
    font-weight: 900;
}

#runButton:hover {
    background-color: #94e2d5;
    border: 2px solid #a6e3a1;
}

#searchButton {
    background-color: #fab387;
    color: #1e1e2e;
    font-size: 15px;
    padding: 12px 25px;
    border: 2px solid #f9e2af;
    font-weight: 900;
}

#searchButton:hover {
    background-color: #f9e2af;
    border: 2px solid #fab387;
}

/* ===== Labels ===== */
QLabel {
    color: #cdd6f4;
    font-size: 13px;
}

/* ===== Group Box ===== */
QGroupBox {
    color: #89b4fa;
    border: 2px solid #45475a;
    border-radius: 12px;
    margin-top: 16px;
    padding: 20px 15px 15px 15px;
    font-size: 14px;
    font-weight: bold;
    background-color: #282840;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    color: #89b4fa;
    background-color: #282840;
    border-radius: 6px;
}

/* ===== Input Widgets ===== */
QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid #45475a;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    min-width: 120px;
}

QComboBox:hover {
    border: 2px solid #89b4fa;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
    border: 2px solid #45475a;
    border-radius: 4px;
}

QLineEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid #45475a;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 13px;
}

QLineEdit:focus {
    border: 2px solid #89b4fa;
}

QSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid #45475a;
    padding: 8px;
    border-radius: 6px;
    font-size: 13px;
}

/* ===== Text Edit ===== */
QTextEdit, QPlainTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 12px;
    font-size: 13px;
    line-height: 1.6;
}

/* ===== Check Box & Radio Button ===== */
QCheckBox {
    color: #cdd6f4;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #585b70;
    border-radius: 4px;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #a6e3a1;
    border: 2px solid #a6e3a1;
}

QRadioButton {
    color: #cdd6f4;
    font-size: 13px;
    font-weight: bold;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #585b70;
    border-radius: 10px;
    background-color: #313244;
}

QRadioButton::indicator:checked {
    background-color: #89b4fa;
    border: 2px solid #89b4fa;
}

/* ===== Table Widget ===== */
QTableWidget {
    background-color: #181825;
    color: #cdd6f4;
    gridline-color: #45475a;
    border: 2px solid #45475a;
    border-radius: 8px;
    font-size: 12px;
    alternate-background-color: #1e1e2e;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QHeaderView::section {
    background-color: #313244;
    color: #89b4fa;
    padding: 10px;
    border: 1px solid #45475a;
    font-weight: bold;
    font-size: 13px;
}

/* ===== Progress Bar ===== */
QProgressBar {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    color: #cdd6f4;
    height: 25px;
    font-size: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #89b4fa, stop:1 #a6e3a1);
    border-radius: 6px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    font-size: 12px;
    border-top: 2px solid #45475a;
    padding: 5px;
}

/* ===== Splitter ===== */
QSplitter::handle {
    background-color: #45475a;
    width: 3px;
    height: 3px;
}

/* ===== Scroll Bar ===== */
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar:horizontal {
    background-color: #1e1e2e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 6px;
    min-width: 30px;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 2px solid #45475a;
    padding: 5px;
}

QMenuBar::item {
    padding: 8px 15px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background-color: #45475a;
}

QMenu {
    background-color: #313244;
    color: #cdd6f4;
    border: 2px solid #45475a;
    border-radius: 8px;
    padding: 5px;
}

QMenu::item {
    padding: 8px 30px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
"""

CATPPUCCIN_LATTE = """
/* ===== Global Styles (Light Theme) ===== */
QWidget {
    font-size: 13px;
    font-family: 'Segoe UI', 'Cascadia Code', 'Tahoma', 'Verdana', sans-serif;
    background-color: #eff1f5;
    color: #4c4f69;
}

QMainWindow {
    background-color: #eff1f5;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 2px solid #ccd0da;
    border-radius: 12px;
    background-color: #e6e9ef;
    margin-top: -1px;
}

QTabBar::tab {
    background-color: #dce0e8;
    color: #5c5f77;
    padding: 12px 25px;
    margin-right: 4px;
    font-size: 14px;
    font-weight: bold;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    border: 1px solid #ccd0da;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #e6e9ef;
    color: #1e66f5;
    border-bottom: 3px solid #1e66f5;
}

QTabBar::tab:hover:!selected {
    background-color: #ccd0da;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #1e66f5;
    color: #eff1f5;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: bold;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #2a7eff;
}

QPushButton:pressed {
    background-color: #0d5bd5;
}

QPushButton:disabled {
    background-color: #ccd0da;
    color: #9ca0b0;
}

#runButton {
    background-color: #40a02b;
    color: white;
    font-size: 15px;
    padding: 12px 25px;
}

#runButton:hover {
    background-color: #50b040;
}

#searchButton {
    background-color: #fe640b;
    color: white;
    font-size: 15px;
    padding: 12px 25px;
}

#searchButton:hover {
    background-color: #ff7b33;
}

/* ===== Group Box ===== */
QGroupBox {
    color: #1e66f5;
    border: 2px solid #ccd0da;
    border-radius: 12px;
    margin-top: 16px;
    padding: 20px 15px 15px 15px;
    font-size: 14px;
    font-weight: bold;
    background-color: #e6e9ef;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 15px;
    padding: 0 10px;
    background-color: #e6e9ef;
    border-radius: 6px;
}

/* ===== Input Widgets ===== */
QComboBox, QLineEdit, QSpinBox {
    background-color: #f4f5f9;
    color: #4c4f69;
    border: 2px solid #ccd0da;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 13px;
}

QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
    border: 2px solid #1e66f5;
}

/* ===== Text Edit ===== */
QTextEdit, QPlainTextEdit {
    background-color: #f4f5f9;
    color: #4c4f69;
    border: 2px solid #ccd0da;
    border-radius: 8px;
    padding: 12px;
    font-size: 13px;
}

/* ===== Table Widget ===== */
QTableWidget {
    background-color: #f4f5f9;
    color: #4c4f69;
    gridline-color: #ccd0da;
    border: 2px solid #ccd0da;
    border-radius: 8px;
    alternate-background-color: #eff1f5;
}

QTableWidget::item:selected {
    background-color: #1e66f5;
    color: white;
}

QHeaderView::section {
    background-color: #dce0e8;
    color: #1e66f5;
    padding: 10px;
    border: 1px solid #ccd0da;
    font-weight: bold;
}

/* ===== Progress Bar ===== */
QProgressBar {
    background-color: #dce0e8;
    border: 2px solid #ccd0da;
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    color: #4c4f69;
    height: 25px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1e66f5, stop:1 #40a02b);
    border-radius: 6px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #dce0e8;
    color: #5c5f77;
    border-top: 2px solid #ccd0da;
    padding: 5px;
}

/* ===== Check Box & Radio ===== */
QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #ccd0da;
    border-radius: 4px;
    background-color: white;
}

QCheckBox::indicator:checked {
    background-color: #40a02b;
    border: 2px solid #40a02b;
}

QRadioButton::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid #ccd0da;
    border-radius: 10px;
    background-color: white;
}

QRadioButton::indicator:checked {
    background-color: #1e66f5;
    border: 2px solid #1e66f5;
}

/* ===== Scroll Bar ===== */
QScrollBar:vertical {
    background-color: #eff1f5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #ccd0da;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #bcc0cc;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #dce0e8;
    color: #4c4f69;
    border-bottom: 2px solid #ccd0da;
    padding: 5px;
}

QMenu {
    background-color: #eff1f5;
    color: #4c4f69;
    border: 2px solid #ccd0da;
    border-radius: 8px;
}

QMenu::item:selected {
    background-color: #1e66f5;
    color: white;
}
"""

# برای سازگاری با کد قبلی
DARK_STYLE = CATPPUCCIN_MOCHA
LIGHT_STYLE = CATPPUCCIN_LATTE