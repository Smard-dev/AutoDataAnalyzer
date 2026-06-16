"""
AutoDataAnalyzer - Intelligent Automated Data Analysis System
Main entry point for the application
"""

import sys
import os

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("AutoDataAnalyzer")
    app.setApplicationVersion("2.0.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()