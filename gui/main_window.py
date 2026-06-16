# gui/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar,
    QMessageBox, QApplication, QToolBar, QAction
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from gui.phase1_tab import Phase1Tab
from gui.phase2_tab import Phase2Tab
from gui.phase3_tab import Phase3Tab
from gui.phase4_tab import Phase4Tab
from gui.search_tab import SearchTab
from gui.styles import CATPPUCCIN_MOCHA, CATPPUCCIN_LATTE


class MainWindow(QMainWindow):
    """Main Application Window with Professional UI"""

    def __init__(self):
        super().__init__()

        # Window Configuration - تنظیم ارتفاع مناسب
        self.setWindowTitle("🔬 AutoDataAnalyzer - Intelligent Data Analysis System")
        self.setGeometry(100, 100, 1400, 850)  # کاهش ارتفاع از 950 به 850

        # Theme State
        self.dark_mode = True
        self.setStyleSheet(CATPPUCCIN_MOCHA)

        # Shared Data Between Tabs
        self.shared_data = {
            'original_data': None,
            'cleaned_data': None,
            'transformed_data': None,
            'std_data': None,
            'id_column': None,
            'id_column_data': None,
            'user_vars': None,
            'product_vars': None,
            'file_path': None,
        }

        # Setup UI Components
        self.setup_tabs()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_menu()

    def setup_tabs(self):
        """Create and configure tab widget"""
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)

        # Set tab icon size - کاهش سایز
        self.tabs.setIconSize(QSize(20, 20))

        # Create tabs
        self.phase1_tab = Phase1Tab(self)
        self.phase2_tab = Phase2Tab(self)
        self.phase3_tab = Phase3Tab(self)
        self.phase4_tab = Phase4Tab(self)
        self.search_tab = SearchTab(self)

        # Add tabs with emoji indicators
        self.tabs.addTab(self.phase1_tab, "📁 1. Data Cleaning")
        self.tabs.addTab(self.phase2_tab, "🔄 2. Transformation")
        self.tabs.addTab(self.phase3_tab, "🔗 3. Variable Assignment")
        self.tabs.addTab(self.phase4_tab, "📊 4. Data Analysis")
        self.tabs.addTab(self.search_tab, "🔍 5. Similarity Search")

        # Set tab size policy - کاهش ارتفاع تب‌ها
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 150px;
                max-width: 180px;
                min-height: 35px;
                max-height: 40px;
            }
        """)

        self.setCentralWidget(self.tabs)

        # Connect tab change event
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Disable dependent tabs initially
        self.phase2_tab.setEnabled(False)
        self.phase3_tab.setEnabled(False)
        self.phase4_tab.setEnabled(False)
        self.search_tab.setEnabled(False)

    def setup_toolbar(self):
        """Create top toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))  # کاهش سایز
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #181825;
                border-bottom: 2px solid #45475a;
                padding: 3px;
                spacing: 8px;
            }
        """)

        # Theme toggle button
        theme_action = QAction("🌓 Toggle Theme", self)
        theme_action.setToolTip("Switch between Dark and Light theme")
        theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_action)

        toolbar.addSeparator()

        # Reset button
        reset_action = QAction("🔄 Reset All", self)
        reset_action.setToolTip("Reset all phases and data")
        reset_action.triggered.connect(self.reset_all)
        toolbar.addAction(reset_action)

        self.addToolBar(toolbar)

    def setup_statusbar(self):
        """Configure status bar"""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.update_status("🚀 Ready | Dataset: None | Status: Waiting")

    def setup_menu(self):
        """Create menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("📂 File")
        exit_action = QAction("🚪 Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menubar.addMenu("⚙️ Settings")
        theme_action = QAction("🌓 Toggle Theme", self)
        theme_action.triggered.connect(self.toggle_theme)
        settings_menu.addAction(theme_action)

        reset_action = QAction("🔄 Reset All", self)
        reset_action.triggered.connect(self.reset_all)
        settings_menu.addAction(reset_action)

        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_tab_changed(self, index):
        """Handle tab switch events"""
        tab_actions = {
            2: lambda: hasattr(self.phase3_tab, 'on_tab_activated') and self.phase3_tab.on_tab_activated(),
            3: lambda: hasattr(self.phase4_tab, 'on_tab_activated') and self.phase4_tab.on_tab_activated(),
            4: lambda: hasattr(self.search_tab, 'on_tab_activated') and self.search_tab.on_tab_activated()
        }

        if index in tab_actions:
            tab_actions[index]()

    def toggle_theme(self):
        """Toggle between dark and light mode"""
        if self.dark_mode:
            self.setStyleSheet(CATPPUCCIN_LATTE)
            self.dark_mode = False
            self.update_status("☀️ Light mode activated")
        else:
            self.setStyleSheet(CATPPUCCIN_MOCHA)
            self.dark_mode = True
            self.update_status("🌙 Dark mode activated")

    def reset_all(self):
        """Reset all application state"""
        reply = QMessageBox.question(
            self, 'Reset Confirmation',
            'Are you sure you want to reset everything?\nAll data and settings will be lost.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.shared_data = {key: None for key in self.shared_data}
            self.phase2_tab.setEnabled(False)
            self.phase3_tab.setEnabled(False)
            self.phase4_tab.setEnabled(False)
            self.search_tab.setEnabled(False)
            self.update_status("🔄 Reset complete | Ready for new data")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About AutoDataAnalyzer",
            """<h2>🔬 AutoDataAnalyzer v2.0</h2>
            <p>Intelligent Data Analysis System</p>
            <p><b>Features:</b></p>
            <ul>
                <li>📊 Automated Data Cleaning</li>
                <li>🔄 Smart Data Transformation</li>
                <li>📈 Advanced Analytics (PCA, Correlation)</li>
                <li>🔍 KNN Similarity Search</li>
            </ul>
            <p><i>Made with ❤️ using PyQt5 & Scikit-learn</i></p>"""
        )

    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(f"  {message}")

    def show_message(self, title, message, icon=QMessageBox.Information):
        """Show message dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QPushButton {
                min-width: 80px;
            }
        """)
        msg.exec_()

    def on_phase1_complete(self):
        """Callback when Phase 1 completes"""
        self.phase2_tab.setEnabled(True)
        self.update_status("✅ Phase 1 Complete | Ready for Phase 2")
        self.tabs.setCurrentIndex(1)

    def on_phase2_complete(self):
        """Callback when Phase 2 completes"""
        self.phase3_tab.setEnabled(True)
        self.update_status("✅ Phase 2 Complete | Ready for Phase 3")
        self.tabs.setCurrentIndex(2)

    def on_phase3_complete(self):
        """Callback when Phase 3 completes"""
        self.phase4_tab.setEnabled(True)
        self.search_tab.setEnabled(True)
        self.update_status("✅ Phase 3 Complete | Ready for Analysis & Search")
        self.tabs.setCurrentIndex(3)