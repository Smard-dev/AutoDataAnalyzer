# gui/phase3_tab.py

import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QRadioButton,
    QTextEdit, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QButtonGroup, QLineEdit
)
from PyQt5.QtCore import Qt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.phase3_variables import UserVariables, ProductVariables


class Phase3Tab(QWidget):
    """تب فاز 3.5 - مقداردهی متغیرها (اتصال ستون‌ها به پارامترها)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.user_vars = None
        self.product_vars = None
        self.transformed_data = None

        self.setup_ui()

    def setup_ui(self):
        """ایجاد رابط کاربری تب فاز 3 با جدول‌های بهینه"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # Dataset Type
        type_group = QGroupBox("📊 Dataset Type")
        type_layout = QHBoxLayout()
        self.user_radio = QRadioButton("👤 User Dataset")
        self.product_radio = QRadioButton("📦 Product Dataset")
        self.hybrid_radio = QRadioButton("🔗 Hybrid")
        self.user_radio.setChecked(True)
        type_layout.addWidget(self.user_radio)
        type_layout.addWidget(self.product_radio)
        type_layout.addWidget(self.hybrid_radio)
        type_layout.addStretch()
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # User Variables Table
        self.user_group = QGroupBox("👤 User Variables")
        user_layout = QVBoxLayout()

        self.user_table = QTableWidget(5, 3)
        self.user_table.setHorizontalHeaderLabels(["Param", "Meaning (optional)", "Data Column"])

        # تنظیمات عرض ستون
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.user_table.setColumnWidth(0, 80)

        # تنظیم ارتفاع ردیف
        for row in range(5):
            self.user_table.setRowHeight(row, 45)

        for row, param in enumerate(["param1", "param2", "param3", "param4", "param5"]):
            self.user_table.setItem(row, 0, QTableWidgetItem(param))

            meaning_edit = QLineEdit()
            meaning_edit.setPlaceholderText("e.g. Age")
            meaning_edit.setMinimumWidth(120)
            self.user_table.setCellWidget(row, 1, meaning_edit)

            combo = QComboBox()
            combo.addItem("(Not selected)")
            combo.setMinimumWidth(150)
            self.user_table.setCellWidget(row, 2, combo)

        self.user_table.setMaximumHeight(300)
        user_layout.addWidget(self.user_table)
        self.user_group.setLayout(user_layout)
        layout.addWidget(self.user_group)

        # Product Variables Table
        self.product_group = QGroupBox("📦 Product Variables")
        product_layout = QVBoxLayout()

        self.product_table = QTableWidget(5, 3)
        self.product_table.setHorizontalHeaderLabels(["Param", "Meaning (optional)", "Data Column"])

        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.product_table.setColumnWidth(0, 80)

        for row in range(5):
            self.product_table.setRowHeight(row, 45)

        for row, param in enumerate(["param1", "param2", "param3", "param4", "param5"]):
            self.product_table.setItem(row, 0, QTableWidgetItem(param))

            meaning_edit = QLineEdit()
            meaning_edit.setPlaceholderText("e.g. Rating")
            meaning_edit.setMinimumWidth(120)
            self.product_table.setCellWidget(row, 1, meaning_edit)

            combo = QComboBox()
            combo.addItem("(Not selected)")
            combo.setMinimumWidth(150)
            self.product_table.setCellWidget(row, 2, combo)

        self.product_table.setMaximumHeight(300)
        product_layout.addWidget(self.product_table)
        self.product_group.setLayout(product_layout)
        layout.addWidget(self.product_group)

        # Save Button
        self.save_btn = QPushButton("💾 Save Variable Assignment")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setObjectName("runButton")
        self.save_btn.clicked.connect(self.save_mapping)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

        # Status
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(120)
        self.status_text.setPlaceholderText("Status will appear here...")
        layout.addWidget(self.status_text)

        # Events
        self.user_radio.toggled.connect(self.on_dataset_type_changed)
        self.product_radio.toggled.connect(self.on_dataset_type_changed)
        self.hybrid_radio.toggled.connect(self.on_dataset_type_changed)

        self.setLayout(layout)


    def on_tab_activated(self):
        """زمانی که این تب فعال می‌شود"""
        self.transformed_data = self.main_window.shared_data.get('transformed_data')

        if self.transformed_data is not None:
            self.update_column_combos()
            self.save_btn.setEnabled(True)
            self.status_text.append("✅ داده‌های تبدیل شده (فاز 2) بارگذاری شد")
            self.status_text.append(f"   شکل داده: {self.transformed_data.shape[0]} × {self.transformed_data.shape[1]}")
            self.status_text.append(f"   ستون‌ها: {', '.join(self.transformed_data.columns[:5])}...")
        else:
            self.status_text.append("⚠ لطفا ابتدا فاز 2 را اجرا کنید")
            self.save_btn.setEnabled(False)

    def update_column_combos(self):
        """به‌روزرسانی لیست کشویی ستون‌ها در جداول"""
        if self.transformed_data is None:
            return

        columns = ["(انتخاب نشده)"] + list(self.transformed_data.columns)

        # به‌روزرسانی جدول کاربر
        for row in range(self.user_table.rowCount()):
            combo = self.user_table.cellWidget(row, 2)
            if combo:
                combo.clear()
                combo.addItems(columns)

        # به‌روزرسانی جدول محصول
        for row in range(self.product_table.rowCount()):
            combo = self.product_table.cellWidget(row, 2)
            if combo:
                combo.clear()
                combo.addItems(columns)

    def on_dataset_type_changed(self):
        """تغییر نمایش جداول بر اساس نوع دیتاست"""
        if self.user_radio.isChecked():
            self.user_group.setVisible(True)
            self.product_group.setVisible(False)
        elif self.product_radio.isChecked():
            self.user_group.setVisible(False)
            self.product_group.setVisible(True)
        else:  # hybrid
            self.user_group.setVisible(True)
            self.product_group.setVisible(True)

    def get_meaning_from_table(self, table, row):
        """دریافت مقدار معنی از جدول"""
        widget = table.cellWidget(row, 1)
        if widget and isinstance(widget, QLineEdit):
            text = widget.text().strip()
            return text if text else None
        return None

    def save_mapping(self):
        """ذخیره مقداردهی متغیرها"""
        if self.transformed_data is None:
            self.main_window.show_message("خطا", "داده‌ای برای مقداردهی وجود ندارد")
            return

        self.status_text.append("\n" + "-" * 50)
        self.status_text.append("🔄 در حال ذخیره مقداردهی...")

        try:
            # ذخیره متغیرهای کاربر
            if self.user_radio.isChecked() or self.hybrid_radio.isChecked():
                self.user_vars = UserVariables()

                params = {}
                meanings = {}
                for row in range(self.user_table.rowCount()):
                    param_name = self.user_table.item(row, 0).text()
                    combo = self.user_table.cellWidget(row, 2)
                    col_name = combo.currentText() if combo else "(انتخاب نشده)"

                    # ذخیره معنی
                    meaning = self.get_meaning_from_table(self.user_table, row)
                    if meaning:
                        meanings[param_name] = meaning

                    if col_name != "(انتخاب نشده)":
                        params[param_name] = self.transformed_data[col_name]
                        self.status_text.append(
                            f"   ✅ {param_name} ← {col_name} ({meaning if meaning else 'بدون معنی'})")
                    else:
                        params[param_name] = None

                # تنظیم پارامترها
                self.user_vars.User(
                    param1=params.get('param1'),
                    param2=params.get('param2'),
                    param3=params.get('param3'),
                    param4=params.get('param4'),
                    param5=params.get('param5'),
                    totalParam=self.transformed_data
                )

                # ذخیره معانی (در صورت نیاز)
                self.user_vars.meanings = meanings

                self.main_window.shared_data['user_vars'] = self.user_vars

            # ذخیره متغیرهای محصول
            if self.product_radio.isChecked() or self.hybrid_radio.isChecked():
                self.product_vars = ProductVariables()

                params = {}
                meanings = {}
                for row in range(self.product_table.rowCount()):
                    param_name = self.product_table.item(row, 0).text()
                    combo = self.product_table.cellWidget(row, 2)
                    col_name = combo.currentText() if combo else "(انتخاب نشده)"

                    # ذخیره معنی
                    meaning = self.get_meaning_from_table(self.product_table, row)
                    if meaning:
                        meanings[param_name] = meaning

                    if col_name != "(انتخاب نشده)":
                        params[param_name] = self.transformed_data[col_name]
                        self.status_text.append(
                            f"   ✅ {param_name} ← {col_name} ({meaning if meaning else 'بدون معنی'})")
                    else:
                        params[param_name] = None

                self.product_vars.Product(
                    param1=params.get('param1'),
                    param2=params.get('param2'),
                    param3=params.get('param3'),
                    param4=params.get('param4'),
                    param5=params.get('param5'),
                    totalParam=self.transformed_data
                )

                self.product_vars.meanings = meanings

                self.main_window.shared_data['product_vars'] = self.product_vars

            self.status_text.append("\n✅ مقداردهی متغیرها با موفقیت ذخیره شد")

            # فعال کردن تب بعدی
            self.main_window.on_phase3_complete()

        except Exception as e:
            self.status_text.append(f"\n❌ خطا: {str(e)}")
            self.main_window.show_message("خطا", f"خطا در ذخیره مقداردهی:\n{str(e)}")