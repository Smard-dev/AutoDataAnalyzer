# gui/search_tab.py

import sys
import os
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QSpinBox,
    QTextEdit, QProgressBar, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class SearchTab(QWidget):
    """تب جستجوی مشابه (KNN Similarity)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.knn_model = None
        self.scaler = StandardScaler()

        self.setup_ui()
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #e67e22;
            }
            QPushButton {
                padding: 8px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
                color: white;
            }
            #searchButton {
                background-color: #e67e22;
                color: white;
                font-size: 14px;
            }
            QTableWidget {
                gridline-color: #444;
                alternate-background-color: #3c3c3c;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                padding: 5px;
                border: 1px solid #555;
                font-weight: bold;
            }
        """)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # ========== بخش 1: انتخاب هدف ==========
        target_group = QGroupBox("🎯 انتخاب هدف (محصول/کاربر)")
        target_layout = QVBoxLayout()

        # انتخاب نوع جستجو
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("نوع جستجو:"))
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["محصولات", "کاربران"])
        self.search_type_combo.currentIndexChanged.connect(self.on_search_type_changed)
        type_layout.addWidget(self.search_type_combo)
        type_layout.addStretch()
        target_layout.addLayout(type_layout)

        # انتخاب آیتم هدف (لیست کشویی - بعد از بارگذاری پر می‌شود)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel("آیتم هدف:"))
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(300)
        self.target_combo.setEditable(True)
        item_layout.addWidget(self.target_combo)
        item_layout.addStretch()
        target_layout.addLayout(item_layout)

        target_group.setLayout(target_layout)
        layout.addWidget(target_group)

        # ========== بخش 2: تنظیمات جستجو ==========
        settings_group = QGroupBox("⚙️ تنظیمات جستجو")
        settings_layout = QHBoxLayout()

        settings_layout.addWidget(QLabel("تعداد نتایج (k):"))
        self.k_spin = QSpinBox()
        self.k_spin.setRange(1, 20)
        self.k_spin.setValue(5)
        self.k_spin.setMinimumWidth(60)
        settings_layout.addWidget(self.k_spin)

        settings_layout.addWidget(QLabel("فاصله:"))
        self.distance_label = QLabel("اقلیدسی")
        settings_layout.addWidget(self.distance_label)

        settings_layout.addStretch()

        self.use_all_features_check = QCheckBox("استفاده از همه ویژگی‌ها")
        self.use_all_features_check.setChecked(True)
        self.use_all_features_check.toggled.connect(self.on_use_all_features_toggled)
        settings_layout.addWidget(self.use_all_features_check)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # ========== بخش 3: انتخاب ویژگی‌های مهم ==========
        features_group = QGroupBox("📊 انتخاب ویژگی‌های مهم برای سنجش شباهت")
        features_layout = QVBoxLayout()

        self.features_text = QTextEdit()
        self.features_text.setMaximumHeight(80)
        self.features_text.setPlaceholderText(
            "نام ستون‌های مورد نظر را با کاما وارد کنید\nمثال: imdb_score, release_year, runtime_minutes"
        )
        self.features_text.setEnabled(False)

        features_layout.addWidget(self.features_text)
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)

        # ========== بخش 4: دکمه جستجو ==========
        self.search_btn = QPushButton("🔍 جستجوی مشابه")
        self.search_btn.setObjectName("searchButton")
        self.search_btn.setMinimumHeight(40)
        self.search_btn.clicked.connect(self.run_search)
        self.search_btn.setEnabled(False)

        layout.addWidget(self.search_btn)

        # ========== بخش 5: نتایج ==========
        results_group = QGroupBox("📋 نتایج جستجو")
        results_layout = QVBoxLayout()

        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setMinimumHeight(250)
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(
            ["#", "شناسه/عنوان", "ویژگی 1", "ویژگی 2", "ویژگی 3", "فاصله"]
        )
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        results_layout.addWidget(self.results_table)

        # اطلاعات اضافی
        self.info_label = QLabel("جهت جستجو، ابتدا فاز 1 و 2 و 3 را اجرا کنید")
        self.info_label.setStyleSheet("color: #aaa; padding: 5px;")
        self.info_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.info_label)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # ========== نوار پیشرفت ==========
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def on_tab_activated(self):
        """وقتی تب فعال می‌شود"""
        try:
            # دریافت داده از shared_data
            self.id_column = self.main_window.shared_data.get('id_column')
            self.id_data = self.main_window.shared_data.get('id_column_data')
            self.transformed_data = self.main_window.shared_data.get('transformed_data')
            self.std_data = self.main_window.shared_data.get('std_data')
            self.user_vars = self.main_window.shared_data.get('user_vars')
            self.product_vars = self.main_window.shared_data.get('product_vars')

            if self.transformed_data is None:
                self.info_label.setText("⚠ لطفا ابتدا فاز 1، 2 و 3 را اجرا کنید")
                self.search_btn.setEnabled(False)
                return

            # پر کردن لیست کشویی آیتم‌های هدف
            self.update_target_list()

            self.search_btn.setEnabled(True)
            self.info_label.setText(f"✅ آماده جستجو | {len(self.target_combo)} آیتم یافت شد")

        except Exception as e:
            self.info_label.setText(f"❌ خطا: {str(e)}")

    def on_search_type_changed(self):
        """تغییر نوع جستجو (محصول/کاربر)"""
        self.update_target_list()

    def update_target_list(self):
        """به‌روزرسانی لیست کشویی آیتم‌های هدف"""
        self.target_combo.clear()

        if self.search_type_combo.currentText() == "محصولات":
            vars_obj = self.product_vars
        else:
            vars_obj = self.user_vars

        if self.id_column and self.id_data is not None:
            # حفظ نوع اصلی داده
            for item in self.id_data.head(100).tolist():
                self.target_combo.addItem(str(item))
        elif vars_obj is not None and hasattr(vars_obj, 'param1'):
            param = vars_obj.param1
            if isinstance(param, pd.Series):
                for item in param.head(100).tolist():
                    self.target_combo.addItem(str(item))
            elif isinstance(param, str) and self.transformed_data is not None:
                if param in self.transformed_data.columns:
                    for item in self.transformed_data[param].head(100).tolist():
                        self.target_combo.addItem(str(item))

        if self.target_combo.count() == 0:
            self.target_combo.addItem("No items found")

    def on_use_all_features_toggled(self, checked):
        """تغییر وضعیت استفاده از همه ویژگی‌ها"""
        self.features_text.setEnabled(not checked)

    def get_feature_columns(self):
        """دریافت لیست ستون‌های مورد استفاده برای سنجش شباهت"""
        if self.use_all_features_check.isChecked():
            # استفاده از همه ستون‌های عددی به جز ستون شناسایی
            if self.std_data is not None:
                numeric_cols = self.std_data.select_dtypes(include=[np.number]).columns.tolist()
            else:
                numeric_cols = self.transformed_data.select_dtypes(include=[np.number]).columns.tolist()

            if self.id_column and self.id_column in numeric_cols:
                numeric_cols.remove(self.id_column)

            return numeric_cols
        else:
            # استفاده از ستون‌های وارد شده توسط کاربر
            text = self.features_text.toPlainText().strip()
            if not text:
                return None
            features = [f.strip() for f in text.split(',')]
            return features

    def run_search(self):
        """اجرای جستجوی مشابه"""
        target_value = self.target_combo.currentText()

        if not target_value or target_value == "(آیتمی یافت نشد)":
            QMessageBox.warning(self, "خطا", "لطفاً یک آیتم هدف انتخاب کنید")
            return

        # تعیین منبع داده
        if self.search_type_combo.currentText() == "محصولات":
            vars_obj = self.product_vars
            data_source = 'product'
        else:
            vars_obj = self.user_vars
            data_source = 'user'

        if vars_obj is None:
            QMessageBox.warning(self, "خطا", f"داده‌های {data_source} وجود ندارد")
            return

        # انتخاب داده (استاندارد یا عادی)
        use_std = True  # برای KNN بهتر است داده استاندارد شود
        if use_std and self.std_data is not None:
            search_data = self.std_data
        else:
            search_data = self.transformed_data

        if search_data is None:
            QMessageBox.warning(self, "خطا", "داده‌ای برای جستجو وجود ندارد")
            return

        # انتخاب ستون‌های ویژگی
        feature_cols = self.get_feature_columns()

        if not feature_cols:
            QMessageBox.warning(self, "خطا", "لطفاً حداقل یک ستون ویژگی انتخاب کنید")
            return

        # بررسی وجود ستون‌ها در داده
        valid_cols = [col for col in feature_cols if col in search_data.columns]
        if len(valid_cols) < 2:
            QMessageBox.warning(self, "خطا", f"ستون‌های انتخابی در داده وجود ندارند\nستون‌های موجود: {list(search_data.columns[:5])}")
            return

        self.progress.setVisible(True)
        self.progress.setValue(10)

        self.results_table.setRowCount(0)
        self.info_label.setText("🔍 در حال جستجو...")

        try:
            # آماده‌سازی داده
            X = search_data[valid_cols].copy()
            X = X.dropna()

            if len(X) < self.k_spin.value():
                QMessageBox.warning(self, "خطا", f"تعداد نمونه‌های کافی وجود ندارد (حداقل نیاز: {self.k_spin.value()})")
                return

            self.progress.setValue(30)

            # استانداردسازی داده‌ها
            X_scaled = self.scaler.fit_transform(X)

            self.progress.setValue(50)

            # پیدا کردن ردیف هدف
            target_index = self.find_target_index(target_value, data_source)

            if target_index is None or target_index not in X.index:
                self.info_label.setText(f"❌ آیتم '{target_value}' در داده یافت نشد")
                return

            # تبدیل ردیف هدف به آرایه
            target_vector = X.loc[target_index:target_index].values

            self.progress.setValue(60)

            # اجرای KNN
            nn = NearestNeighbors(n_neighbors=self.k_spin.value() + 1, metric='euclidean')
            nn.fit(X_scaled)

            distances, indices = nn.kneighbors(target_vector)

            self.progress.setValue(80)

            # حذف خود آیتم هدف
            mask = X.index[indices[0]] != target_index
            similar_indices = X.index[indices[0][mask]][:self.k_spin.value()]
            similar_distances = distances[0][mask][:self.k_spin.value()]

            # نمایش نتایج
            self.display_results(similar_indices, similar_distances, valid_cols, data_source)

            self.progress.setValue(100)
            self.info_label.setText(f"✅ {len(similar_indices)} آیتم مشابه یافت شد")

        except Exception as e:
            self.info_label.setText(f"❌ خطا در جستجو: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            self.progress.setVisible(False)

    def find_target_index(self, target_value, data_source):
        """پیدا کردن index ردیف هدف - نسخه اصلاح شده"""

        # تبدیل target_value به انواع مختلف برای مقایسه
        def safe_match(series, target):
            """مقایسه امن با تبدیل نوع"""
            # تلاش با رشته
            matches = series[series.astype(str) == str(target)].index
            if len(matches) > 0:
                return matches

            # تلاش با عدد (اگر ممکنه)
            try:
                numeric_target = float(target)
                matches = series[series.astype(float) == numeric_target].index
                if len(matches) > 0:
                    return matches
            except:
                pass

            # تلاش با lower strip
            try:
                matches = series[series.astype(str).str.lower().str.strip() == str(target).lower().strip()].index
                if len(matches) > 0:
                    return matches
            except:
                pass

            return pd.Index([])

        # روش 1: استفاده از ستون شناسایی
        if self.id_column and self.id_data is not None:
            matches = safe_match(self.id_data, target_value)
            if len(matches) > 0:
                return matches[0]

        # روش 2: استفاده از param1
        if data_source == 'product' and self.product_vars:
            param = self.product_vars.param1
        elif data_source == 'user' and self.user_vars:
            param = self.user_vars.param1
        else:
            return None

        if isinstance(param, pd.Series):
            matches = safe_match(param, target_value)
            if len(matches) > 0:
                return matches[0]
        elif isinstance(param, str) and self.transformed_data is not None:
            if param in self.transformed_data.columns:
                matches = safe_match(self.transformed_data[param], target_value)
                if len(matches) > 0:
                    return matches[0]

        return None
    def display_results(self, indices, distances, feature_cols, data_source):
        """نمایش نتایج جستجو در جدول"""
        if len(indices) == 0:
            self.results_table.setRowCount(0)
            self.results_table.setHorizontalHeaderLabels(["#", "شناسه/عنوان", "ویژگی 1", "ویژگی 2", "ویژگی 3", "فاصله"])
            return

        # تنظیم ستون‌ها
        self.results_table.setRowCount(len(indices))
        self.results_table.setHorizontalHeaderLabels(["#", "شناسه/عنوان", feature_cols[0] if len(feature_cols) > 0 else "-",
                                                      feature_cols[1] if len(feature_cols) > 1 else "-",
                                                      feature_cols[2] if len(feature_cols) > 2 else "-",
                                                      "فاصله"])

        # پر کردن جدول
        for i, (idx, dist) in enumerate(zip(indices, distances)):
            # شماره
            self.results_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

            # شناسه/عنوان
            id_value = self.get_id_value(idx, data_source)
            self.results_table.setItem(i, 1, QTableWidgetItem(str(id_value)))

            # ویژگی‌ها
            row_data = self.transformed_data.loc[idx] if self.transformed_data is not None else None
            if row_data is not None:
                for j, col in enumerate(feature_cols[:3]):
                    val = row_data[col] if col in row_data.index else "-"
                    self.results_table.setItem(i, 2 + j, QTableWidgetItem(f"{val:.2f}" if isinstance(val, (int, float)) else str(val)))

            # فاصله
            self.results_table.setItem(i, 5, QTableWidgetItem(f"{dist:.4f}"))

        # تنظیم ارتفاع ردیف‌ها
        for i in range(len(indices)):
            self.results_table.resizeRowToContents(i)

    def get_id_value(self, idx, data_source):
        """دریافت مقدار شناسایی برای یک index"""
        # روش 1: ستون شناسایی
        if self.id_column and self.id_data is not None and idx in self.id_data.index:
            return self.id_data[idx]

        # روش 2: param1
        if data_source == 'product' and self.product_vars:
            param = self.product_vars.param1
        elif data_source == 'user' and self.user_vars:
            param = self.user_vars.param1
        else:
            return f"item_{idx}"

        if isinstance(param, pd.Series) and idx in param.index:
            return param[idx]
        elif isinstance(param, str) and self.transformed_data is not None and param in self.transformed_data.columns:
            return self.transformed_data.loc[idx, param]

        return f"item_{idx}"