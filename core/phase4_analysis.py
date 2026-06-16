# core/phase4_analysis.py

import matplotlib

matplotlib.use('Agg')  # استفاده از backend غیرتعاملی برای جلوگیری از کرش
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats as scipy_stats
import warnings

warnings.filterwarnings('ignore')


class Phase4Analysis:
    """
    کلاس فاز 4 - تحلیل داده پیشرفته
    """

    def __init__(self, user_vars=None, product_vars=None):
        self.user_vars = user_vars
        self.product_vars = product_vars
        self.results = {
            'descriptive': {},
            'correlations': {},
            'pca': None,
            'normality_tests': {},
            'outliers': {},
            'variance_analysis': {}
        }

    def _get_data(self, data_source, use_std=False):
        """دریافت دیتاست کامل با مدیریت خطا"""
        try:
            if data_source == 'user' and self.user_vars:
                if use_std and hasattr(self.user_vars, 'stotalParam') and self.user_vars.stotalParam is not None:
                    data = self.user_vars.stotalParam
                    if isinstance(data, pd.DataFrame):
                        return data
                elif hasattr(self.user_vars, 'totalParam') and self.user_vars.totalParam is not None:
                    data = self.user_vars.totalParam
                    if isinstance(data, pd.DataFrame):
                        return data
            elif data_source == 'product' and self.product_vars:
                if use_std and hasattr(self.product_vars, 'stotalParam') and self.product_vars.stotalParam is not None:
                    data = self.product_vars.stotalParam
                    if isinstance(data, pd.DataFrame):
                        return data
                elif hasattr(self.product_vars, 'totalParam') and self.product_vars.totalParam is not None:
                    data = self.product_vars.totalParam
                    if isinstance(data, pd.DataFrame):
                        return data
            return None
        except Exception as e:
            print(f"Error getting data: {e}")
            return None

    def _get_target_series(self, data_source, target_param='param1'):
        """دریافت سری هدف (نسخه ساده - برای متدهای پایه)"""
        try:
            vars_obj = self.user_vars if data_source == 'user' else self.product_vars
            normal_data = self._get_data(data_source, use_std=False)

            if vars_obj is None:
                return None

            target = getattr(vars_obj, target_param, None)

            if target is None:
                return None

            if isinstance(target, pd.Series):
                return target

            if isinstance(target, str) and normal_data is not None and target in normal_data.columns:
                return normal_data[target]

            if isinstance(target, (np.ndarray, list)):
                return pd.Series(target, name=target_param)

            return None
        except Exception as e:
            print(f"Error getting target: {e}")
            return None

    def _get_target_series_v2(self, data_source, target_param='param1'):
        """دریافت سری هدف (نسخه پیشرفته - همراه با نام ستون)"""
        try:
            vars_obj = self.user_vars if data_source == 'user' else self.product_vars
            normal_data = self._get_data(data_source, use_std=False)

            if vars_obj is None:
                return None, None

            target = getattr(vars_obj, target_param, None)

            if target is None:
                return None, None

            target_name = target if isinstance(target, str) else target_param

            if isinstance(target, pd.Series):
                return target, target.name if target.name else target_param

            if isinstance(target, str) and normal_data is not None and target in normal_data.columns:
                return normal_data[target], target

            if isinstance(target, (np.ndarray, list)):
                series = pd.Series(target, name=target_param)
                return series, target_param

            return None, None
        except Exception as e:
            print(f"Error getting target: {e}")
            return None, None

    def descriptive_stats(self, data, name):
        """آمار توصیفی پیشرفته"""
        if data is None or len(data) == 0:
            return None

        clean_data = data.dropna()
        if len(clean_data) < 2:
            return None

        stats_dict = {
            'count': len(clean_data),
            'missing': len(data) - len(clean_data),
            'missing_pct': ((len(data) - len(clean_data)) / len(data)) * 100 if len(data) > 0 else 0,
            'mean': clean_data.mean(),
            'median': clean_data.median(),
            'std': clean_data.std(),
            'var': clean_data.var(),
            'min': clean_data.min(),
            'max': clean_data.max(),
            'range': clean_data.max() - clean_data.min(),
            'q1': clean_data.quantile(0.25),
            'q3': clean_data.quantile(0.75),
            'iqr': clean_data.quantile(0.75) - clean_data.quantile(0.25),
            'skewness': clean_data.skew(),
            'kurtosis': clean_data.kurtosis()
        }
        return stats_dict

    def descriptive_stats_single(self, data_source, target_param='param1', use_std=False):
        """آمار توصیفی یک پارامتر خاص"""
        y = self._get_target_series(data_source, target_param)

        if y is None:
            return None

        return self.descriptive_stats(y, target_param)

    def descriptive_stats_all(self, data_source, use_std=False):
        """آمار توصیفی همه ستون‌ها"""
        data = self._get_data(data_source, use_std)

        if data is None:
            return None

        results = {}
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            results[col] = self.descriptive_stats(data[col], col)

        return results

    def distribution_single(self, data_source, target_param='param1', use_std=False):
        """تحلیل توزیع یک پارامتر خاص"""
        y = self._get_target_series(data_source, target_param)

        if y is None:
            return None

        if y.dtype in ['int64', 'float64', 'int32', 'float32'] and y.nunique() > 10:
            return {'type': 'numeric', 'data': y}
        else:
            counts = y.value_counts()
            return {'type': 'categorical', 'counts': counts, 'total': len(y)}

    def normality_test(self, data_source, target_param='param1', use_std=False):
        """آزمون نرمال بودن توزیع"""
        y, y_name = self._get_target_series_v2(data_source, target_param)

        if y is None or len(y.dropna()) < 3:
            return None

        clean_data = y.dropna()

        # Shapiro-Wilk test (محدودیت 5000 نمونه)
        if len(clean_data) > 5000:
            clean_data_sample = clean_data.sample(5000, random_state=42)
        else:
            clean_data_sample = clean_data

        shapiro_stat, shapiro_p = scipy_stats.shapiro(clean_data_sample)

        # Kolmogorov-Smirnov test
        ks_stat, ks_p = scipy_stats.kstest(clean_data, 'norm',
                                           args=(clean_data.mean(), clean_data.std()))

        return {
            'shapiro_stat': shapiro_stat,
            'shapiro_p': shapiro_p,
            'shapiro_normal': shapiro_p > 0.05,
            'ks_stat': ks_stat,
            'ks_p': ks_p,
            'ks_normal': ks_p > 0.05
        }

    def outlier_detection(self, data_source, target_param='param1', method='iqr', use_std=False):
        """تشخیص داده‌های پرت"""
        y = self._get_target_series(data_source, target_param)

        if y is None or len(y.dropna()) < 4:
            return None

        clean_data = y.dropna()

        if method == 'iqr':
            Q1 = clean_data.quantile(0.25)
            Q3 = clean_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = clean_data[(clean_data < lower_bound) | (clean_data > upper_bound)]
            return {
                'method': 'IQR',
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'outliers_count': len(outliers),
                'outliers_pct': (len(outliers) / len(clean_data)) * 100 if len(clean_data) > 0 else 0,
                'outliers_values': outliers.tolist()[:10]
            }

        elif method == 'zscore':
            z_scores = np.abs(scipy_stats.zscore(clean_data))
            outliers = clean_data[z_scores > 3]
            return {
                'method': 'Z-Score',
                'threshold': 3,
                'outliers_count': len(outliers),
                'outliers_pct': (len(outliers) / len(clean_data)) * 100 if len(clean_data) > 0 else 0,
                'outliers_values': outliers.tolist()[:10]
            }

        return None

    def correlation_analysis(self, data_source, use_std=False):
        """ماتریس همبستگی با مدیریت خطا"""
        try:
            data = self._get_data(data_source, use_std)

            if data is None:
                return None

            # فقط ستون‌های عددی
            numeric_data = data.select_dtypes(include=[np.number])

            # حذف ستون‌های با واریانس صفر
            numeric_data = numeric_data.loc[:, numeric_data.std() > 0]

            if numeric_data.empty or len(numeric_data.columns) < 2:
                return None

            # محاسبه ماتریس همبستگی با مدیریت NaN
            corr_matrix = numeric_data.corr(method='pearson', min_periods=3)

            # استخراج جفت‌های همبسته
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if not np.isnan(corr_val):
                        corr_pairs.append({
                            'col1': corr_matrix.columns[i],
                            'col2': corr_matrix.columns[j],
                            'correlation': corr_val
                        })

            corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)

            return {
                'matrix': corr_matrix,
                'strongest': corr_pairs[:10],
                'numeric_columns': numeric_data.columns.tolist()
            }
        except Exception as e:
            print(f"Error in correlation analysis: {e}")
            return None

    def pca_analysis(self, data_source, target_param='param1', n_components=2, use_std=True):
        """تحلیل PCA با مدیریت کامل خطا"""
        try:
            full_data = self._get_data(data_source, use_std)

            if full_data is None:
                return None, None, None

            # فقط ستون‌های عددی
            numeric_data = full_data.select_dtypes(include=[np.number])

            if numeric_data.empty or len(numeric_data.columns) < 2:
                return None, None, None

            # حذف ستون هدف از X
            y, y_name = self._get_target_series_v2(data_source, target_param)

            target_col_name = None
            if y is not None and hasattr(y, 'name') and y.name is not None:
                target_col_name = y.name

            if target_col_name and target_col_name in numeric_data.columns:
                X_data = numeric_data.drop(columns=[target_col_name])
            else:
                X_data = numeric_data.copy()
                y = None

            # حذف سطرهای NaN
            X_clean = X_data.dropna()

            if len(X_clean) < 3 or len(X_clean.columns) < 2:
                return None, None, None

            # استانداردسازی مجدد برای اطمینان
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_clean)

            # PCA
            n_components = min(n_components, len(X_clean.columns), len(X_clean))
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(X_scaled)

            # هماهنگ‌سازی y با X
            y_clean = None
            if y is not None:
                y_clean = y.loc[X_clean.index] if hasattr(y, 'loc') else None
                if y_clean is not None and len(y_clean) != len(pca_result):
                    y_clean = None

            self.results['pca'] = {
                'explained_variance': pca.explained_variance_ratio_,
                'explained_variance_cumsum': np.cumsum(pca.explained_variance_ratio_),
                'components': pca.components_,
                'loadings': pd.DataFrame(
                    pca.components_.T,
                    columns=[f'PC{i + 1}' for i in range(n_components)],
                    index=X_clean.columns
                ),
                'result': pca_result,
                'target': y_clean,
                'target_name': target_col_name,
                'features_used': X_clean.columns.tolist(),
                'n_components': n_components
            }

            return pca_result, y_clean, X_clean.columns.tolist()
        except Exception as e:
            print(f"Error in PCA: {e}")
            return None, None, None

    def anova_analysis(self, data_source, target_param='param1', use_std=False):
        """تحلیل واریانس برای شناسایی تفاوت گروه‌ها"""
        data = self._get_data(data_source, use_std)

        if data is None:
            return None

        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()

        results = {}
        for col in numeric_cols[:10]:  # محدود به ۱۰ ستون اول برای سرعت
            mean_val = data[col].mean()
            std_val = data[col].std()
            cv = std_val / mean_val if mean_val != 0 else np.nan
            results[col] = {
                'cv': cv,  # ضریب تغییرات
                'variance': data[col].var(),
                'unique_values': data[col].nunique()
            }

        return results

    def get_results(self):
        return self.results