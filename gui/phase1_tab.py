# gui/phase1_tab.py
import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QFileDialog, QComboBox,
    QCheckBox, QTextEdit, QProgressBar, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.phase1_preprocessing import Phase1Preprocessing


class Phase1Tab(QWidget):
    """تب فاز 1 - پاکسازی داده"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.current_data = None
        self.preprocessor = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # بارگذاری دیتاست
        load_group = QGroupBox("📂 Load Dataset")
        load_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("color: #a6adc8;")
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        self.load_btn = QPushButton("Load")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.load_data)
        load_layout.addWidget(self.file_path_label)
        load_layout.addWidget(self.browse_btn)
        load_layout.addWidget(self.load_btn)
        load_group.setLayout(load_layout)
        layout.addWidget(load_group)

        # ستون شناسایی
        id_group = QGroupBox("🏷️ ID Column (for similarity search)")
        id_layout = QVBoxLayout()
        id_info = QLabel("Select the column that contains item titles/names")
        id_info.setWordWrap(True)
        id_info.setStyleSheet("color: #a6adc8; font-size: 11px;")
        self.id_column_combo = QComboBox()
        self.id_column_combo.setEnabled(False)
        self.id_column_combo.addItem("Load dataset first...")
        id_layout.addWidget(id_info)
        id_layout.addWidget(self.id_column_combo)
        id_group.setLayout(id_layout)
        layout.addWidget(id_group)

        # تنظیمات پاکسازی
        settings_group = QGroupBox("⚙️ Cleaning Settings")
        settings_layout = QVBoxLayout()
        self.duplicate_check = QCheckBox("Smart duplicate removal")
        self.duplicate_check.setChecked(True)
        self.range_check = QCheckBox("Set valid ranges for columns")
        self.range_check.setChecked(True)
        settings_layout.addWidget(self.duplicate_check)
        settings_layout.addWidget(self.range_check)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # دکمه اجرا
        self.run_btn = QPushButton("▶ Run Phase 1")
        self.run_btn.setEnabled(False)
        self.run_btn.setMinimumHeight(40)
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(self.run_phase1)
        layout.addWidget(self.run_btn)

        # گزارش
        report_group = QGroupBox("📊 Phase 1 Report")
        report_layout = QVBoxLayout()
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setMinimumHeight(200)
        self.report_text.setPlaceholderText("Report will appear here...")
        report_layout.addWidget(self.report_text)
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)

        # نوار پیشرفت
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Dataset", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self.file_path_label.setText(file_path)
            self.file_path_label.setStyleSheet("color: #cdd6f4;")
            self.load_btn.setEnabled(True)

    def load_data(self):
        file_path = self.file_path_label.text()
        try:
            if file_path.endswith('.csv'):
                self.current_data = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                self.current_data = pd.read_excel(file_path)
            else:
                self.main_window.show_message("Error", "Unsupported file format")
                return

            self.main_window.shared_data['original_data'] = self.current_data
            self.main_window.shared_data['file_path'] = file_path

            self.id_column_combo.clear()
            self.id_column_combo.addItem("(None - Skip)")
            for col in self.current_data.columns:
                self.id_column_combo.addItem(col)
            self.id_column_combo.setEnabled(True)
            self.run_btn.setEnabled(True)

            self.main_window.update_status(
                f"✅ Dataset loaded: {self.current_data.shape[0]} × {self.current_data.shape[1]}")
            self.report_text.append(f"✅ Dataset loaded successfully")
            self.report_text.append(f"   Shape: {self.current_data.shape[0]} rows × {self.current_data.shape[1]} cols")
        except Exception as e:
            self.main_window.show_message("Error", f"Failed to load file:\n{str(e)}")

    def run_phase1(self):
        """اجرای فاز 1 با GUI Dialog"""
        if self.current_data is None:
            self.main_window.show_message("Error", "Please load a dataset first")
            return

        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(10)
        self.report_text.clear()
        self.report_text.append("🚀 Starting Phase 1 - Data Cleaning...")
        self.report_text.append("-" * 60)

        try:
            selected_id_col = self.id_column_combo.currentText()
            if selected_id_col != "(None - Skip)":
                self.main_window.shared_data['id_column'] = selected_id_col
                self.main_window.shared_data['id_column_data'] = self.current_data[selected_id_col].copy()
                self.report_text.append(f"✅ ID column '{selected_id_col}' registered")
                self.progress.setValue(20)

            dataset_name = os.path.basename(
                self.main_window.shared_data['file_path']
            ).replace('.csv', '').replace('.xlsx', '')

            self.preprocessor = Phase1Preprocessing(
                df=self.current_data.copy(),
                dataset_name=dataset_name
            )
            self.preprocessor.set_gui_callback(self.gui_question_callback)

            if selected_id_col != "(None - Skip)":
                self.preprocessor.df = self.preprocessor.df.drop(columns=[selected_id_col])
                self.report_text.append(f"   ID column removed from processing data")

            self.report_text.append("✅ Preprocessor initialized")
            self.progress.setValue(30)

            # ==== پرسش برای حذف تکراری‌ها ====
            force_duplicate = None
            if self.duplicate_check.isChecked():
                dup_count = self.preprocessor.df.duplicated().sum()
                if dup_count > 0:
                    prob = self.preprocessor.calculate_duplicate_probability()
                    threshold = self.preprocessor.calculate_threshold()
                    should_remove = prob < threshold

                    msg = f"""<h3>Duplicate Row Analysis</h3>
<b>Duplicate rows found:</b> {dup_count}<br>
<b>Random match probability:</b> {prob:.8f} ({prob*100:.6f}%)<br>
<b>Threshold:</b> {threshold:.4f} ({threshold*100:.2f}%)<br><br>
<b>Recommendation:</b> {'✅ Remove' if should_remove else '❌ Keep'}<br><br>
Do you want to remove duplicate rows?"""

                    reply = QMessageBox.question(
                        self, "Duplicate Removal", msg,
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes if should_remove else QMessageBox.No
                    )
                    force_duplicate = (reply == QMessageBox.Yes)
                    self.report_text.append(
                        f"   Duplicates: {'Removed' if force_duplicate else 'Kept'} ({dup_count} rows)"
                    )
                else:
                    force_duplicate = False

            self.progress.setValue(40)

            # ==== پرسش برای بازه‌های معتبر ====
            ranges_dict = None
            if self.range_check.isChecked():
                reply = QMessageBox.question(
                    self, "Valid Ranges",
                    "Do you want to set valid ranges for numeric columns?\n\n"
                    "• Yes: Set ranges interactively\n"
                    "• No: Auto-detect with IQR method",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    numeric_cols = self.preprocessor.df.select_dtypes(
                        include=[np.number]
                    ).columns.tolist()
                    ranges_dict = {}

                    for col in numeric_cols[:10]:
                        current_min = self.preprocessor.df[col].min()
                        current_max = self.preprocessor.df[col].max()

                        user_input, ok = QInputDialog.getText(
                            self, f"Valid Range - {col}",
                            f"Column: {col}\n"
                            f"Current range: [{current_min:.2f}, {current_max:.2f}]\n"
                            f"Type: {self.preprocessor.df[col].dtype}\n\n"
                            f"Input formats:\n"
                            f"  Enter = Auto (IQR)\n"
                            f"  ignore = Skip outlier detection\n"
                            f"  number = Min only (e.g. 18)\n"
                            f"  _number = Max only (e.g. _90)\n"
                            f"  min_max = Range [min, max] (e.g. 18_90)",
                            text=""
                        )

                        if ok:
                            ranges_dict[col] = user_input.strip() if user_input else ""

                        if col != numeric_cols[:10][-1]:
                            cont = QMessageBox.question(
                                self, "Continue?",
                                f"Continue to next column?\n{len(ranges_dict)} columns set so far",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                            )
                            if cont == QMessageBox.No:
                                break

            self.progress.setValue(50)
            self.report_text.append("\n🔄 Running data cleaning...")

            cleaned_df = self.preprocessor.run_full_pipeline(
                ask_duplicate=False,
                ask_ranges=False,
                verbose=False,
                ranges_dict=ranges_dict,
                force_duplicate=force_duplicate
            )

            self.progress.setValue(90)
            self.main_window.shared_data['cleaned_data'] = cleaned_df

            # نمایش گزارش
            self.report_text.append("\n" + "-" * 60)
            self.report_text.append("📊 Phase 1 Report:")
            self.report_text.append("-" * 40)

            report = self.preprocessor.get_report()
            self.report_text.append(
                f"   Original shape: {report['original_shape'][0]} × {report['original_shape'][1]}"
            )
            self.report_text.append(
                f"   Final shape: {cleaned_df.shape[0]} × {cleaned_df.shape[1]}"
            )
            self.report_text.append(
                f"   Duplicates removed: {report.get('duplicates_removed', 0)}"
            )

            if report.get('valid_ranges_applied'):
                self.report_text.append(f"\n   📐 Valid ranges applied:")
                for col, range_str in report['valid_ranges_applied'].items():
                    self.report_text.append(f"      - {col}: {range_str}")

            if report.get('outliers_total', 0) > 0:
                self.report_text.append(
                    f"\n   ⚠ Outliers detected: {report['outliers_total']} total"
                )

            self.progress.setValue(100)
            self.report_text.append("\n✅ Phase 1 completed successfully")
            self.main_window.update_status(
                f"✅ Phase 1 done | Shape: {cleaned_df.shape[0]} × {cleaned_df.shape[1]}"
            )
            self.main_window.on_phase1_complete()

        except Exception as e:
            self.report_text.append(f"\n❌ Error: {str(e)}")
            self.main_window.show_message("Error", f"Phase 1 failed:\n{str(e)}")
        finally:
            self.progress.setVisible(False)
            self.run_btn.setEnabled(True)

    def gui_question_callback(self, question_type, data):
        """Callback for GUI questions from core"""
        if question_type == 'ask_duplicate':
            msg = f"""<b>Duplicate Analysis:</b><br>
• Count: {data['count']}<br>
• Probability: {data['probability']:.8f}<br>
• Threshold: {data['threshold']:.4f}<br>
• Recommendation: {'Remove' if data['recommendation'] else 'Keep'}<br><br>
Remove duplicates?"""
            reply = QMessageBox.question(self, "Duplicates", msg,
                                         QMessageBox.Yes | QMessageBox.No)
            return reply == QMessageBox.Yes
        return data.get('recommendation', False)