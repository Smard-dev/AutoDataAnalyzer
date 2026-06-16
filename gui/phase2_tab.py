# gui/phase2_tab.py
import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QCheckBox, QTextEdit,
    QProgressBar, QSpinBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.phase2_transformation import Phase2Transformation


class MappingDialog(QDialog):
    def __init__(self, col_name, mapping, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Mapping - {col_name}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.col_name = col_name
        self.new_mapping = mapping.copy()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>Mapping for: {col_name}</b>"))
        layout.addWidget(QLabel(f"Unique values: {len(mapping)}"))

        self.table = QTableWidget(len(mapping), 2)
        self.table.setHorizontalHeaderLabels(["Original Value", "Numeric Code"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for row, (value, code) in enumerate(mapping.items()):
            self.table.setItem(row, 0, QTableWidgetItem(str(value)))
            self.table.setItem(row, 1, QTableWidgetItem(str(code)))

        layout.addWidget(self.table)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_mapping(self):
        for row in range(self.table.rowCount()):
            value = self.table.item(row, 0).text()
            code_str = self.table.item(row, 1).text()
            try:
                self.new_mapping[value] = int(code_str)
            except ValueError:
                self.new_mapping[value] = 0
        return self.new_mapping


class Phase2Tab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.transformer = None
        self.current_mappings = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        settings_group = QGroupBox("⚙️ Transformation Settings")
        settings_layout = QVBoxLayout()

        thresh_layout = QHBoxLayout()
        thresh_layout.addWidget(QLabel("High-variety threshold:"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(5, 50)
        self.threshold_spin.setValue(20)
        self.threshold_spin.setSuffix(" %")
        thresh_layout.addWidget(self.threshold_spin)
        thresh_layout.addStretch()
        settings_layout.addLayout(thresh_layout)

        corr_layout = QHBoxLayout()
        corr_layout.addWidget(QLabel("Correlation threshold:"))
        self.corr_spin = QSpinBox()
        self.corr_spin.setRange(80, 100)
        self.corr_spin.setValue(95)
        self.corr_spin.setSuffix(" %")
        corr_layout.addWidget(self.corr_spin)
        corr_layout.addStretch()
        settings_layout.addLayout(corr_layout)

        self.confirm_check = QCheckBox("Confirm mappings before applying")
        self.confirm_check.setChecked(True)
        settings_layout.addWidget(self.confirm_check)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        mapping_group = QGroupBox("📋 Mappings")
        mapping_layout = QVBoxLayout()
        self.mapping_label = QLabel("Mappings will appear after execution")
        self.mapping_label.setStyleSheet("color: #a6adc8;")
        mapping_layout.addWidget(self.mapping_label)

        self.mapping_table = QTableWidget(0, 2)
        self.mapping_table.setHorizontalHeaderLabels(["Column", "Mapping"])
        self.mapping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mapping_table.setVisible(False)
        self.mapping_table.setMaximumHeight(200)
        mapping_layout.addWidget(self.mapping_table)

        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)

        self.run_btn = QPushButton("▶ Run Phase 2")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(self.run_phase2)
        layout.addWidget(self.run_btn)

        report_group = QGroupBox("📊 Report")
        report_layout = QVBoxLayout()
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setMinimumHeight(200)
        self.report_text.setPlaceholderText("Report will appear here...")
        report_layout.addWidget(self.report_text)
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def run_phase2(self):
        cleaned_data = self.main_window.shared_data.get('cleaned_data')
        if cleaned_data is None:
            self.main_window.show_message("Error", "Run Phase 1 first")
            return

        self.run_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(10)
        self.report_text.clear()
        self.report_text.append("🚀 Starting Phase 2...")
        self.report_text.append("-" * 60)

        try:
            dataset_name = os.path.basename(
                self.main_window.shared_data.get('file_path', 'unknown')
            ).replace('.csv', '').replace('.xlsx', '')

            self.transformer = Phase2Transformation(
                df=cleaned_data.copy(),
                dataset_name=dataset_name
            )

            self.report_text.append("✅ Transformer initialized")
            self.progress.setValue(20)

            # ==== مدیریت mapping با GUI ====
            if self.confirm_check.isChecked():
                self.report_text.append("\n📋 Generating mappings...")
                self.progress.setValue(30)

                # اجرای مراحل اولیه
                self.transformer.convert_boolean_to_numeric()
                self.transformer.remove_high_variance_nominal_columns(
                    self.threshold_spin.value()
                )
                self.transformer.map_nominal_columns()

                # دریافت و نمایش mapping ها
                self.current_mappings = self.transformer.get_mappings()
                self.display_mappings()

                if self.current_mappings:
                    self.progress.setValue(40)

                    # پرسش از کاربر
                    msg = f"{len(self.current_mappings)} columns mapped:\n\n"
                    for col, mapping in self.current_mappings.items():
                        msg += f"• {col}: {len(mapping)} values\n"
                    msg += "\nDo you want to review/edit mappings?"

                    reply = QMessageBox.question(
                        self, "Confirm Mappings", msg,
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )

                    if reply == QMessageBox.Yes:
                        for col, mapping in self.current_mappings.items():
                            dialog = MappingDialog(col, mapping, self)
                            if dialog.exec_() == QDialog.Accepted:
                                self.transformer.mappings[col] = dialog.get_mapping()
                                self.report_text.append(f"   ✅ '{col}' mapping updated")

                    self.report_text.append("✅ Mappings confirmed")

            # ==== اجرای کامل pipeline (بدون پرسش کنسولی) ====
            self.report_text.append("\n🔄 Running full pipeline...")
            self.progress.setValue(60)

            final_df, std_df = self.transformer.run_full_pipeline(
                threshold_percent=self.threshold_spin.value(),
                correlation_threshold=self.corr_spin.value() / 100,
                ask_user_confirmation=False,  # مهم: False تا input کنسولی نخواد
                verbose=False
            )

            self.progress.setValue(90)

            # ذخیره
            self.main_window.shared_data['transformed_data'] = final_df
            self.main_window.shared_data['std_data'] = std_df

            # نمایش مجدد mapping های نهایی
            self.current_mappings = self.transformer.get_mappings()
            self.display_mappings()

            # گزارش
            self.report_text.append("\n" + "-" * 60)
            self.report_text.append("📊 Phase 2 Report:")
            report = self.transformer.get_report()
            self.report_text.append(f"   Original: {report['original_shape']}")
            self.report_text.append(f"   Final: {final_df.shape}")
            self.report_text.append(f"   Std: {std_df.shape}")

            if report.get('nominal_converted'):
                self.report_text.append(f"\n   ✅ Mapped: {', '.join(report['nominal_converted'])}")

            self.progress.setValue(100)
            self.report_text.append("\n✅ Phase 2 completed!")
            self.main_window.update_status(f"✅ Phase 2 done")
            self.main_window.on_phase2_complete()

        except Exception as e:
            self.report_text.append(f"\n❌ Error: {str(e)}")
            import traceback
            self.report_text.append(traceback.format_exc())
        finally:
            self.progress.setVisible(False)
            self.run_btn.setEnabled(True)

    def display_mappings(self):
        if not self.current_mappings:
            self.mapping_label.setText("✅ No mappings needed")
            self.mapping_table.setVisible(False)
            return

        self.mapping_label.setText(f"Mappings ({len(self.current_mappings)} columns):")
        self.mapping_table.setRowCount(len(self.current_mappings))
        self.mapping_table.setVisible(True)

        for row, (col, mapping) in enumerate(self.current_mappings.items()):
            self.mapping_table.setItem(row, 0, QTableWidgetItem(col))
            mapping_str = str(mapping)
            if len(mapping_str) > 60:
                mapping_str = mapping_str[:57] + "..."
            self.mapping_table.setItem(row, 1, QTableWidgetItem(mapping_str))

        self.mapping_table.resizeRowsToContents()