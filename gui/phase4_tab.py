# gui/phase4_tab.py
import sys
import os
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QCheckBox, QTextEdit,
    QProgressBar, QSplitter, QGridLayout, QRadioButton,
    QFileDialog, QComboBox, QMessageBox, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.phase4_analysis import Phase4Analysis


class Phase4Tab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.analyzer = None
        self.user_vars = None
        self.product_vars = None
        self.temp_plot_path = os.path.join(os.path.dirname(__file__), '..', 'temp_plot.png')
        self.setup_ui()

    def setup_ui(self):
        # ====== SCROLL AREA ======
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Main widget inside scroll
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ===== HEADER =====
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { background-color: #282840; border-radius: 10px; padding: 8px; }")
        header_layout = QHBoxLayout(header_frame)
        title_label = QLabel("📊 Advanced Data Analysis Dashboard")
        title_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title_label.setStyleSheet("color: #89b4fa; padding: 5px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addWidget(header_frame)

        # ===== CONTROL PANEL =====
        control_frame = QFrame()
        control_frame.setStyleSheet("QFrame { background-color: #282840; border-radius: 10px; padding: 8px; }")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(15)

        source_widget = QWidget()
        source_layout = QVBoxLayout(source_widget)
        source_label = QLabel("🎯 Data Source")
        source_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        source_label.setStyleSheet("color: #f5c2e7;")
        source_layout.addWidget(source_label)
        self.user_radio = QRadioButton("👤 User Analysis")
        self.product_radio = QRadioButton("📦 Product Analysis")
        self.user_radio.setChecked(True)
        source_layout.addWidget(self.user_radio)
        source_layout.addWidget(self.product_radio)
        control_layout.addWidget(source_widget)

        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setStyleSheet("color: #45475a;")
        control_layout.addWidget(separator1)

        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_label = QLabel("⚙️ Settings")
        settings_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        settings_label.setStyleSheet("color: #f5c2e7;")
        settings_layout.addWidget(settings_label)
        self.std_check = QCheckBox("Use Standardized Data")
        self.std_check.setToolTip("Recommended for PCA and Correlation")
        settings_layout.addWidget(self.std_check)

        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Target:"))
        self.target_param_combo = QComboBox()
        self.target_param_combo.addItems(["param1", "param2", "param3", "param4", "param5"])
        param_layout.addWidget(self.target_param_combo)
        param_layout.addStretch()
        settings_layout.addLayout(param_layout)
        control_layout.addWidget(settings_widget)
        control_layout.addStretch()
        main_layout.addWidget(control_frame)

        # ===== ANALYSIS BUTTONS =====
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("QFrame { background-color: #282840; border-radius: 10px; padding: 8px; }")
        buttons_layout = QGridLayout(buttons_frame)
        buttons_layout.setSpacing(8)

        basic_label = QLabel("📈 Basic Analysis")
        basic_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        basic_label.setStyleSheet("color: #a6e3a1;")
        buttons_layout.addWidget(basic_label, 0, 0, 1, 3)

        self.desc_single_btn = QPushButton("📊 Descriptive (Single)")
        self.desc_single_btn.clicked.connect(lambda: self.run_analysis('descriptive_single'))
        self.dist_single_btn = QPushButton("📈 Distribution (Single)")
        self.dist_single_btn.clicked.connect(lambda: self.run_analysis('distribution_single'))
        self.desc_all_btn = QPushButton("📊 Descriptive (All)")
        self.desc_all_btn.clicked.connect(lambda: self.run_analysis('descriptive_all'))
        buttons_layout.addWidget(self.desc_single_btn, 1, 0)
        buttons_layout.addWidget(self.dist_single_btn, 1, 1)
        buttons_layout.addWidget(self.desc_all_btn, 1, 2)

        stats_label = QLabel("🔬 Statistical Tests")
        stats_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        stats_label.setStyleSheet("color: #f9e2af;")
        buttons_layout.addWidget(stats_label, 2, 0, 1, 3)

        self.normality_btn = QPushButton("🔔 Normality Test")
        self.normality_btn.clicked.connect(lambda: self.run_analysis('normality'))
        self.outlier_btn = QPushButton("⚠ Outlier Detection")
        self.outlier_btn.clicked.connect(lambda: self.run_analysis('outliers'))
        self.anova_btn = QPushButton("📐 Variance Analysis")
        self.anova_btn.clicked.connect(lambda: self.run_analysis('anova'))
        buttons_layout.addWidget(self.normality_btn, 3, 0)
        buttons_layout.addWidget(self.outlier_btn, 3, 1)
        buttons_layout.addWidget(self.anova_btn, 3, 2)

        advanced_label = QLabel("🚀 Advanced Analysis")
        advanced_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        advanced_label.setStyleSheet("color: #cba6f7;")
        buttons_layout.addWidget(advanced_label, 4, 0, 1, 3)

        self.corr_btn = QPushButton("🔗 Correlation Matrix")
        self.corr_btn.clicked.connect(lambda: self.run_analysis('correlation'))
        self.pca_btn = QPushButton("📉 PCA Analysis")
        self.pca_btn.clicked.connect(lambda: self.run_analysis('pca'))
        self.all_btn = QPushButton("▶ Run All Analyses")
        self.all_btn.setObjectName("runButton")
        self.all_btn.clicked.connect(lambda: self.run_analysis('all'))
        buttons_layout.addWidget(self.corr_btn, 5, 0)
        buttons_layout.addWidget(self.pca_btn, 5, 1)
        buttons_layout.addWidget(self.all_btn, 5, 2)

        main_layout.addWidget(buttons_frame)

        # ===== RESULTS AREA =====
        results_frame = QFrame()
        results_frame.setStyleSheet("QFrame { background-color: #282840; border-radius: 10px; padding: 8px; }")
        results_layout = QVBoxLayout(results_frame)

        results_label = QLabel("📋 Analysis Results")
        results_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        results_label.setStyleSheet("color: #89b4fa; padding: 5px;")
        results_layout.addWidget(results_label)

        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(4)

        # Text Results
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(200)
        self.result_text.setFont(QFont('Consolas', 11))
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #181825;
                color: #cdd6f4;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        text_layout.addWidget(self.result_text)
        splitter.addWidget(text_container)

        # Plot Area
        plot_container = QWidget()
        plot_layout = QVBoxLayout(plot_container)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_label = QLabel("📈 Visualization")
        plot_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        plot_label.setStyleSheet("color: #f5c2e7; padding: 5px;")
        plot_layout.addWidget(plot_label)

        self.image_label = QLabel()
        self.image_label.setMinimumHeight(350)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #45475a;
                background-color: #181825;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.image_label.setText("📊 Plot will appear here after analysis")
        plot_layout.addWidget(self.image_label)
        splitter.addWidget(plot_container)

        splitter.setSizes([250, 400])
        results_layout.addWidget(splitter)
        main_layout.addWidget(results_frame, stretch=2)

        # ===== ACTION BAR =====
        action_frame = QFrame()
        action_frame.setStyleSheet("QFrame { background-color: #282840; border-radius: 10px; padding: 8px; }")
        action_layout = QHBoxLayout(action_frame)
        action_layout.setSpacing(15)

        self.save_btn = QPushButton("💾 Save Plot")
        self.save_btn.clicked.connect(self.save_plot)
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumWidth(120)

        self.clear_btn = QPushButton("🗑 Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setMinimumWidth(120)

        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.clear_btn)
        action_layout.addStretch()

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximumWidth(300)
        action_layout.addWidget(self.progress)

        main_layout.addWidget(action_frame)

        # ===== SET SCROLL =====
        scroll_area.setWidget(main_widget)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)

    # ===== بقیه متدها مثل قبل =====
    def on_tab_activated(self):
        try:
            self.user_vars = self.main_window.shared_data.get('user_vars')
            self.product_vars = self.main_window.shared_data.get('product_vars')
            if self.user_vars is None and self.product_vars is None:
                self.result_text.append("⚠ Please complete Phase 3 first")
                self.set_buttons_enabled(False)
            else:
                self.set_buttons_enabled(True)
                self.result_text.append("✅ Phase 3 data loaded successfully")
        except Exception as e:
            self.result_text.append(f"⚠ Error: {str(e)}")

    def set_buttons_enabled(self, enabled):
        buttons = [
            self.desc_single_btn, self.dist_single_btn, self.desc_all_btn,
            self.corr_btn, self.pca_btn, self.all_btn,
            self.normality_btn, self.outlier_btn, self.anova_btn
        ]
        for btn in buttons:
            btn.setEnabled(enabled)

    def run_analysis(self, analysis_type):
        if self.user_radio.isChecked():
            data_source = 'user'
        else:
            data_source = 'product'

        self.analyzer = Phase4Analysis(
            user_vars=self.user_vars if data_source == 'user' else None,
            product_vars=self.product_vars if data_source == 'product' else None
        )

        use_std = self.std_check.isChecked()
        target_param = self.target_param_combo.currentText()

        self.progress.setVisible(True)
        self.progress.setValue(10)
        self.save_btn.setEnabled(False)

        self.result_text.append("\n" + "━" * 70)
        self.result_text.append(f"⚡ Analysis: {analysis_type} | Source: {data_source}")
        if analysis_type in ['descriptive_single', 'distribution_single', 'normality', 'outliers']:
            self.result_text.append(f"   Target: {target_param}")
        self.result_text.append("━" * 70)

        try:
            if analysis_type == 'descriptive_single':
                self.run_descriptive_single(data_source, target_param, use_std)
            elif analysis_type == 'distribution_single':
                self.run_distribution_single(data_source, target_param, use_std)
            elif analysis_type == 'normality':
                self.run_normality_test(data_source, target_param, use_std)
            elif analysis_type == 'outliers':
                self.run_outlier_detection(data_source, target_param, use_std)
            elif analysis_type == 'descriptive_all':
                self.run_descriptive_all(data_source, use_std)
            elif analysis_type == 'correlation':
                self.run_correlation_analysis(data_source, use_std)
            elif analysis_type == 'pca':
                self.run_pca_analysis(data_source)
            elif analysis_type == 'anova':
                self.run_anova_analysis(data_source, use_std)
            elif analysis_type == 'all':
                self.run_all_analyses(data_source, target_param, use_std)

            self.progress.setValue(100)
            self.result_text.append("\n✅ Analysis completed successfully")

        except Exception as e:
            self.result_text.append(f"\n❌ Error: {str(e)}")
            import traceback
            self.result_text.append(traceback.format_exc())
        finally:
            self.progress.setVisible(False)

    def run_descriptive_single(self, data_source, target_param, use_std):
        stats = self.analyzer.descriptive_stats_single(data_source, target_param, use_std)
        if stats is None:
            self.result_text.append(f"   ❌ {target_param} is not initialized")
            return
        self.result_text.append(f"\n📊 Descriptive Statistics for {target_param}:")
        self.result_text.append(f"   {'Count:':<25} {stats['count']:.0f}")
        self.result_text.append(f"   {'Mean:':<25} {stats['mean']:.4f}")
        self.result_text.append(f"   {'Median:':<25} {stats['median']:.4f}")
        self.result_text.append(f"   {'Std Dev:':<25} {stats['std']:.4f}")
        self.result_text.append(f"   {'Min:':<25} {stats['min']:.4f}")
        self.result_text.append(f"   {'Max:':<25} {stats['max']:.4f}")

    def run_distribution_single(self, data_source, target_param, use_std):
        result = self.analyzer.distribution_single(data_source, target_param, use_std)
        if result is None:
            self.result_text.append(f"   ❌ {target_param} is not initialized")
            return
        self.result_text.append(f"\n📈 Distribution Analysis for {target_param}:")
        if result['type'] == 'numeric':
            self.result_text.append("   (Numeric variable - Displaying histogram)")
            data = result['data']
            try:
                plt.style.use('dark_background')
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
                fig.patch.set_facecolor('#181825')
                ax1.hist(data.dropna(), bins=30, edgecolor='white', alpha=0.8, color='#89b4fa', linewidth=0.5)
                ax1.set_xlabel(target_param, fontsize=12, color='#cdd6f4')
                ax1.set_ylabel('Frequency', fontsize=12, color='#cdd6f4')
                ax1.set_title(f'Distribution of {target_param}', fontsize=14, fontweight='bold', color='#cdd6f4')
                ax1.set_facecolor('#282840')
                ax1.tick_params(colors='#cdd6f4')
                ax1.grid(True, alpha=0.2, color='#cdd6f4')
                bp = ax2.boxplot(data.dropna(), vert=True, patch_artist=True)
                bp['boxes'][0].set_facecolor('#a6e3a1')
                bp['boxes'][0].set_alpha(0.8)
                ax2.set_ylabel(target_param, fontsize=12, color='#cdd6f4')
                ax2.set_title(f'Box Plot of {target_param}', fontsize=14, fontweight='bold', color='#cdd6f4')
                ax2.set_facecolor('#282840')
                ax2.tick_params(colors='#cdd6f4')
                ax2.grid(True, alpha=0.2, color='#cdd6f4')
                plt.tight_layout(pad=3)
                plt.savefig(self.temp_plot_path, dpi=150, bbox_inches='tight', facecolor='#181825', edgecolor='none')
                plt.close()
                self.display_plot()
            except Exception as e:
                self.result_text.append(f"   ⚠ Error drawing plot: {str(e)}")
        else:
            counts = result['counts']
            total = result['total']
            self.result_text.append(f"   Categories (Total: {total}):")
            for val, cnt in list(counts.head(10).items()):
                self.result_text.append(f"   {str(val):<20} {cnt:>5} ({cnt / total * 100:.1f}%)")

    def run_normality_test(self, data_source, target_param, use_std):
        result = self.analyzer.normality_test(data_source, target_param, use_std)
        if result is None:
            self.result_text.append(f"   ❌ Cannot perform normality test")
            return
        self.result_text.append(f"\n🔔 Normality Test for {target_param}:")
        self.result_text.append(f"   Shapiro-Wilk: stat={result['shapiro_stat']:.4f}, p={result['shapiro_p']:.4f}")
        self.result_text.append(f"   Normal: {'✅ Yes' if result['shapiro_normal'] else '❌ No'}")

    def run_outlier_detection(self, data_source, target_param, use_std):
        result = self.analyzer.outlier_detection(data_source, target_param, method='iqr', use_std=use_std)
        if result is None:
            self.result_text.append(f"   ❌ Cannot detect outliers")
            return
        self.result_text.append(f"\n⚠ Outlier Detection in {target_param}:")
        self.result_text.append(f"   Method: {result['method']}")
        self.result_text.append(f"   Count: {result['outliers_count']} ({result['outliers_pct']:.1f}%)")

    def run_descriptive_all(self, data_source, use_std):
        results = self.analyzer.descriptive_stats_all(data_source, use_std)
        if results is None:
            self.result_text.append("   ❌ No data available")
            return
        self.result_text.append(f"\n📊 Descriptive Statistics ({len(results)} columns):")
        for col, stats in list(results.items())[:20]:
            if stats:
                self.result_text.append(
                    f"   {col:<30} mean={stats['mean']:>10.2f} std={stats['std']:>10.2f}"
                )

    def run_correlation_analysis(self, data_source, use_std):
        try:
            result = self.analyzer.correlation_analysis(data_source, use_std)
            if result is None or result['matrix'] is None:
                self.result_text.append("   ❌ Insufficient data for correlation")
                return
            corr_matrix = result['matrix']
            try:
                plt.style.use('dark_background')
                fig, ax = plt.subplots(figsize=(12, 10))
                fig.patch.set_facecolor('#181825')
                mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
                sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm',
                            center=0, fmt='.2f', square=True, linewidths=0.5,
                            cbar_kws={"shrink": 0.8}, ax=ax, annot_kws={'size': 8, 'color': '#cdd6f4'})
                ax.set_title(f'Correlation Matrix - {data_source.capitalize()}',
                             fontsize=14, fontweight='bold', color='#cdd6f4', pad=15)
                ax.set_facecolor('#282840')
                ax.tick_params(colors='#cdd6f4', labelsize=8)
                plt.tight_layout()
                plt.savefig(self.temp_plot_path, dpi=150, bbox_inches='tight',
                            facecolor='#181825', edgecolor='none')
                plt.close()
                self.display_plot()
            except Exception as e:
                self.result_text.append(f"   ⚠ Error drawing heatmap: {str(e)}")
            self.result_text.append(f"\n🔗 Strongest Correlations:")
            for corr in result['strongest'][:5]:
                self.result_text.append(
                    f"   {corr['col1'][:25]:<27} ↔ {corr['col2'][:25]:<27} : {corr['correlation']:>7.3f}"
                )
        except Exception as e:
            self.result_text.append(f"   ❌ Error: {str(e)}")

    def run_pca_analysis(self, data_source):
        try:
            self.result_text.append("   ⏳ Computing PCA...")
            self.progress.setValue(30)
            pca_result, y_target, features = self.analyzer.pca_analysis(
                data_source, target_param='param1', use_std=True
            )
            if pca_result is None:
                self.result_text.append("   ❌ PCA failed - check data")
                return
            self.progress.setValue(70)
            try:
                plt.style.use('dark_background')
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
                fig.patch.set_facecolor('#181825')
                explained_var = self.analyzer.results['pca']['explained_variance']
                if y_target is not None and len(y_target) == len(pca_result):
                    scatter = ax1.scatter(pca_result[:, 0], pca_result[:, 1],
                                          c=y_target, cmap='viridis', alpha=0.7,
                                          edgecolors='white', linewidth=0.3, s=40)
                    plt.colorbar(scatter, ax=ax1)
                else:
                    ax1.scatter(pca_result[:, 0], pca_result[:, 1],
                                alpha=0.7, color='#89b4fa', edgecolors='white', linewidth=0.3, s=40)
                ax1.set_xlabel(f'PC1 ({explained_var[0]:.1%})', fontsize=11, color='#cdd6f4')
                ax1.set_ylabel(f'PC2 ({explained_var[1]:.1%})', fontsize=11, color='#cdd6f4')
                ax1.set_title(f'PCA - {data_source.capitalize()}', fontsize=13, fontweight='bold', color='#cdd6f4')
                ax1.set_facecolor('#282840')
                ax1.tick_params(colors='#cdd6f4')
                ax1.grid(True, alpha=0.2, color='#cdd6f4')
                cumsum_var = self.analyzer.results['pca']['explained_variance_cumsum']
                ax2.bar(range(1, len(explained_var) + 1), explained_var, alpha=0.7, color='#89b4fa')
                ax2.plot(range(1, len(cumsum_var) + 1), cumsum_var, 'o-', color='#a6e3a1', linewidth=2)
                ax2.set_xlabel('Principal Component', fontsize=11, color='#cdd6f4')
                ax2.set_ylabel('Variance Ratio', fontsize=11, color='#cdd6f4')
                ax2.set_title('Cumulative Variance', fontsize=13, fontweight='bold', color='#cdd6f4')
                ax2.set_facecolor('#282840')
                ax2.tick_params(colors='#cdd6f4')
                ax2.grid(True, alpha=0.2, color='#cdd6f4')
                plt.tight_layout(pad=3)
                plt.savefig(self.temp_plot_path, dpi=150, bbox_inches='tight',
                            facecolor='#181825', edgecolor='none')
                plt.close()
                self.display_plot()
            except Exception as e:
                self.result_text.append(f"   ⚠ Error drawing PCA: {str(e)}")
            self.result_text.append(f"\n📉 PCA Results:")
            self.result_text.append(f"   Features: {len(features)} columns")
            self.result_text.append(f"   PC1: {explained_var[0]:.2%}, PC2: {explained_var[1]:.2%}")
            self.result_text.append(f"   Total: {explained_var.sum():.2%}")
        except Exception as e:
            self.result_text.append(f"   ❌ Error in PCA: {str(e)}")

    def run_anova_analysis(self, data_source, use_std):
        result = self.analyzer.anova_analysis(data_source, 'param1', use_std)
        if result is None:
            self.result_text.append("   ❌ Cannot perform variance analysis")
            return
        self.result_text.append(f"\n📐 Variance Analysis:")
        for col, stats in list(result.items())[:10]:
            self.result_text.append(
                f"   {col:<30} CV={stats['cv']:>8.4f} Var={stats['variance']:>10.2f}"
            )

    def run_all_analyses(self, data_source, target_param, use_std):
        analyses = [
            ('descriptive_single', 'Descriptive (Single)'),
            ('distribution_single', 'Distribution'),
            ('normality', 'Normality Test'),
            ('outliers', 'Outlier Detection'),
            ('descriptive_all', 'Descriptive (All)'),
            ('correlation', 'Correlation'),
            ('anova', 'Variance Analysis'),
            ('pca', 'PCA')
        ]
        for i, (analysis, name) in enumerate(analyses):
            self.result_text.append(f"\n⏳ {i + 1}/8 - {name}...")
            self.progress.setValue(int((i / 8) * 100))
            self.run_analysis(analysis)

    def display_plot(self):
        try:
            if os.path.exists(self.temp_plot_path):
                pixmap = QPixmap(self.temp_plot_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled)
                    self.save_btn.setEnabled(True)
        except Exception as e:
            self.result_text.append(f"   ⚠ Error displaying plot: {str(e)}")

    def save_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Plot", "", "PNG (*.png);;JPG (*.jpg);;PDF (*.pdf)"
        )
        if file_path:
            import shutil
            shutil.copy(self.temp_plot_path, file_path)
            self.result_text.append(f"✅ Plot saved to {file_path}")

    def clear_results(self):
        self.result_text.clear()
        self.image_label.clear()
        self.image_label.setText("📊 Plot will appear here after analysis")
        self.save_btn.setEnabled(False)