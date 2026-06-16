# core/phase1_preprocessing.py
# ============================================
# phase1_preprocessing.py
# کلاس فاز 1: پاکسازی و آماده‌سازی اولیه داده
# ============================================

import pandas as pd
import numpy as np
from datetime import datetime


class Phase1Preprocessing:
    """
    کلاس فاز 1 - پیش‌پردازش اولیه داده

    نسخه GUI-Friendly: تمام input های کنسولی حذف شدن
    """

    def __init__(self, df=None, dataset_name="Unknown", id_column=None):
        self.df = df
        self.dataset_name = dataset_name
        self.id_column = id_column
        self.id_column_data = None
        self.verbose = True
        self.gui_callback = None  # برای ارتباط با GUI

        self.report = {
            "dataset_name": dataset_name,
            "original_shape": df.shape if df is not None else (0, 0),
            "duplicates_removed": 0,
            "duplicates_found": 0,
            "duplicates_kept": 0,
            "outliers_detected": {
                "mild": {},
                "moderate": {},
                "extreme": {}
            },
            "outliers_total": 0,
            "valid_ranges_applied": {},
            "valid_ranges_error": {},
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def set_gui_callback(self, callback):
        """تنظیم callback برای تعامل با GUI"""
        self.gui_callback = callback

    def set_id_column(self, column_name):
        """تنظیم ستون شناسایی و جدا کردن آن از داده اصلی"""
        if column_name and column_name in self.df.columns:
            self.id_column = column_name
            self.id_column_data = self.df[column_name].copy()
            self.df = self.df.drop(columns=[column_name])
            return True
        return False

    def get_id_column_data(self):
        """دریافت داده ستون شناسایی"""
        return self.id_column_data

    @property
    def final_shape(self):
        return self.df.shape if self.df is not None else (0, 0)

    def _print(self, message, force=False):
        if self.verbose or force:
            print(message)

    def load_data(self, file_path, file_type="csv"):
        """بارگذاری دیتاست از فایل"""
        try:
            if file_type == "csv":
                self.df = pd.read_csv(file_path)
            elif file_type == "excel":
                self.df = pd.read_excel(file_path)
            else:
                raise ValueError("فرمت فایل پشتیبانی نمی‌شود")
            self.report["original_shape"] = self.df.shape
            self._print(f"✅ دیتاست {self.dataset_name} با موفقیت بارگذاری شد")
            self._print(f"   شکل: {self.df.shape[0]} ردیف × {self.df.shape[1]} ستون")
            return True
        except Exception as e:
            print(f"❌ خطا در بارگذاری فایل: {e}")
            return False

    def get_valid_ranges_from_user_gui(self, numeric_cols, ranges_dict_from_gui):
        """
        دریافت بازه‌های معتبر از GUI

        Parameters:
        - numeric_cols: لیست ستون‌های عددی
        - ranges_dict_from_gui: دیکشنری از GUI {col_name: "min_max" or "ignore" or ""}
        """
        ranges = {}

        for col in numeric_cols:
            if col not in ranges_dict_from_gui:
                continue

            user_input = ranges_dict_from_gui[col]

            # حالت 1: رشته خالی → بررسی عادی با IQR
            if not user_input or user_input.strip() == "":
                continue

            # حالت 2: "ignore" → بدون بررسی outlier
            if user_input.lower() == "ignore":
                ranges[col] = ("ignore", "ignore")
                self.report["valid_ranges_applied"][col] = "NO_OUTLIER_DETECTION"
                continue

            # حالت 3: "min_max" → بازه بسته [min, max]
            if "_" in user_input:
                parts = user_input.split("_")
                if len(parts) == 2 and parts[0] and parts[1]:
                    try:
                        lower = float(parts[0])
                        upper = float(parts[1])
                        if lower > upper:
                            self.report["valid_ranges_error"][col] = f"min({lower}) > max({upper})"
                            continue
                        ranges[col] = (lower, upper)
                        self.report["valid_ranges_applied"][col] = f"[{lower}, {upper}]"
                    except ValueError:
                        self.report["valid_ranges_error"][col] = "Invalid format"
                        continue

                elif len(parts) == 2 and parts[0] and not parts[1]:
                    try:
                        lower = float(parts[0])
                        ranges[col] = (lower, None)
                        self.report["valid_ranges_applied"][col] = f"[{lower}, ∞)"
                    except ValueError:
                        self.report["valid_ranges_error"][col] = "Invalid format"
                        continue

                elif len(parts) == 2 and not parts[0] and parts[1]:
                    try:
                        upper = float(parts[1])
                        ranges[col] = (None, upper)
                        self.report["valid_ranges_applied"][col] = f"(-∞, {upper}]"
                    except ValueError:
                        self.report["valid_ranges_error"][col] = "Invalid format"
                        continue
            else:
                try:
                    lower = float(user_input)
                    ranges[col] = (lower, None)
                    self.report["valid_ranges_applied"][col] = f"[{lower}, ∞)"
                except ValueError:
                    self.report["valid_ranges_error"][col] = "Invalid format"
                    continue

        return ranges

    def apply_valid_ranges(self, ranges):
        """اعمال بازه‌های معتبر روی دیتاست"""
        if not ranges:
            return

        self._print("\n🔍 اعمال بازه‌های معتبر:")
        for col, (lower, upper) in ranges.items():
            if col not in self.df.columns:
                continue

            if lower == "ignore" and upper == "ignore":
                self._print(f"   ⏩ {col}: تشخیص outlier غیرفعال شد")
                continue

            mask = pd.Series([True] * len(self.df))
            if lower is not None:
                mask = mask & (self.df[col] >= lower)
            if upper is not None:
                mask = mask & (self.df[col] <= upper)

            invalid_count = (~mask).sum()
            if invalid_count > 0:
                if col not in self.report["outliers_detected"]["extreme"]:
                    self.report["outliers_detected"]["extreme"][col] = 0
                self.report["outliers_detected"]["extreme"][col] += invalid_count
                self.report["outliers_total"] += invalid_count
                self._print(f"   ⚠ {col}: {invalid_count} مقدار خارج از بازه شناسایی شد")
            else:
                self._print(f"   ✅ {col}: همه مقادیر در بازه معتبر هستند")

    def calculate_duplicate_probability(self):
        """محاسبه احتمال اینکه دو ردیف تصادفی دقیقاً یکسان باشند"""
        probability = 1.0
        for col in self.df.columns:
            unique_count = self.df[col].nunique()
            if unique_count > 1:
                probability *= (1.0 / unique_count)
        return probability

    def calculate_threshold(self):
        """محاسبه حد آستانه بر اساس تعداد ردیف‌ها"""
        n_rows = len(self.df)
        if n_rows < 100:
            return 0.01
        elif n_rows < 1000:
            return 0.005
        elif n_rows < 10000:
            return 0.001
        else:
            return 0.0001

    def remove_duplicates_statistical(self, ask_user=False, force_remove=None):
        """
        حذف ردیف‌های تکراری بر اساس محاسبه آماری احتمال

        Parameters:
        - ask_user: آیا از کاربر پرسیده شود
        - force_remove: اگر None محاسبه خودکار، اگر True/False تصمیم قطعی
        """
        if self.df is None:
            return False

        duplicate_count = self.df.duplicated().sum()
        self.report["duplicates_found"] = duplicate_count

        if duplicate_count == 0:
            return False

        prob_random_match = self.calculate_duplicate_probability()
        threshold = self.calculate_threshold()

        high_var_cols = [col for col in self.df.columns if self.df[col].nunique() > 3]
        low_var_cols = [col for col in self.df.columns if self.df[col].nunique() <= 3]

        self._duplicate_analysis = {
            "duplicate_count": duplicate_count,
            "prob_random_match": prob_random_match,
            "threshold": threshold,
            "high_var_count": len(high_var_cols),
            "low_var_count": len(low_var_cols),
            "should_remove": prob_random_match < threshold
        }

        # تصمیم‌گیری نهایی
        if force_remove is not None:
            should_remove = force_remove
        else:
            should_remove = prob_random_match < threshold

            if ask_user and self.gui_callback:
                should_remove = self.gui_callback('ask_duplicate', {
                    'count': duplicate_count,
                    'probability': prob_random_match,
                    'threshold': threshold,
                    'recommendation': should_remove
                })

        if should_remove:
            before = len(self.df)
            self.df = self.df.drop_duplicates()
            after = len(self.df)
            self.report["duplicates_removed"] = before - after
            self.report["duplicates_kept"] = duplicate_count - (before - after)
        else:
            self.report["duplicates_removed"] = 0
            self.report["duplicates_kept"] = duplicate_count

        return should_remove

    def detect_outliers_iqr_with_severity(self, factor=1.5):
        """
        شناسایی داده‌های پرت با روش IQR و طبقه‌بندی شدت
        """
        if self.df is None:
            return

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR

            is_lower_outlier = self.df[col] < lower_bound
            is_upper_outlier = self.df[col] > upper_bound
            is_outlier = is_lower_outlier | is_upper_outlier
            outlier_count = is_outlier.sum()

            if outlier_count == 0:
                continue

            distance = np.zeros(len(self.df))
            distance[is_lower_outlier] = lower_bound - self.df[col][is_lower_outlier]
            distance[is_upper_outlier] = self.df[col][is_upper_outlier] - upper_bound

            mild_mask = is_outlier & (distance <= 1.5 * IQR)
            moderate_mask = is_outlier & (distance > 1.5 * IQR) & (distance <= 3 * IQR)
            extreme_mask = is_outlier & (distance > 3 * IQR)

            if mild_mask.sum() > 0:
                self.report["outliers_detected"]["mild"][col] = mild_mask.sum()
            if moderate_mask.sum() > 0:
                self.report["outliers_detected"]["moderate"][col] = moderate_mask.sum()
            if extreme_mask.sum() > 0:
                self.report["outliers_detected"]["extreme"][col] = extreme_mask.sum()

            self.report["outliers_total"] += outlier_count

            self._print(f"\n⚠ ستون: {col}")
            self._print(f"   محدوده مجاز IQR: [{lower_bound:.4f}, {upper_bound:.4f}]")
            self._print(f"   تعداد کل outlier: {outlier_count}")
            if mild_mask.sum() > 0:
                self._print(f"      - خفیف: {mild_mask.sum()} مورد")
            if moderate_mask.sum() > 0:
                self._print(f"      - متوسط: {moderate_mask.sum()} مورد")
            if extreme_mask.sum() > 0:
                self._print(f"      - شدید: {extreme_mask.sum()} مورد")

    def run_full_pipeline(self, ask_duplicate=False, ask_ranges=True, verbose=True,
                          ranges_dict=None, force_duplicate=None):
        """
        اجرای کامل فاز 1 با پشتیبانی از GUI

        Parameters:
        - ask_duplicate: سوال از کاربر برای حذف تکراری‌ها
        - ask_ranges: دریافت بازه معتبر از کاربر
        - verbose: نمایش پرینت‌های داخلی
        - ranges_dict: دیکشنری بازه‌ها از GUI
        - force_duplicate: تصمیم قطعی برای حذف تکراری‌ها
        """
        self.verbose = verbose
        self._print(f"\n🚀 شروع فاز 1 بر روی دیتاست {self.dataset_name}")
        self._print("=" * 40)

        # گام 0: دریافت بازه‌های معتبر
        if ask_ranges:
            if ranges_dict is not None:
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
                valid_ranges = self.get_valid_ranges_from_user_gui(numeric_cols, ranges_dict)
            else:
                valid_ranges = {}
            self.apply_valid_ranges(valid_ranges)

        # گام 1: بررسی و حذف تکراری‌ها
        self.remove_duplicates_statistical(ask_user=ask_duplicate, force_remove=force_duplicate)

        # گام 2: شناسایی outlierها
        self._print("\n🔍 شناسایی داده‌های پرت با روش IQR:")
        self.detect_outliers_iqr_with_severity()

        self._print("\n" + "=" * 40)
        self._print(f"✅ فاز 1 با موفقیت به پایان رسید")
        self._print("💡 هیچ تغییری در داده‌های پرت اعمال نشد (به فاز ۲ موکول شد)")

        return self.df

    def get_cleaned_data(self):
        """دریافت دیتاست"""
        return self.df

    def get_report(self):
        """دریافت گزارش کامل"""
        return self.report

    def report_phase1(self):
        """چاپ گزارش کامل فاز 1"""
        print("\n" + "=" * 70)
        print(f"📋 گزارش فاز 1 - دیتاست: {self.report['dataset_name']}")
        print("=" * 70)
        print(f"🕒 زمان اجرا: {self.report['timestamp']}")
        print(f"📊 شکل اولیه: {self.report['original_shape'][0]} ردیف × {self.report['original_shape'][1]} ستون")
        print(f"📊 شکل نهایی: {self.final_shape[0]} ردیف × {self.final_shape[1]} ستون")

        if self.report['valid_ranges_error']:
            print("\n" + "─" * 50)
            print("⚠ خطاهای بازه معتبر:")
            for col, err in self.report['valid_ranges_error'].items():
                print(f"   - {col}: {err}")

        print("\n" + "─" * 50)
        print("📌 داده‌های تکراری:")
        print(f"   - تعداد یافت شده: {self.report.get('duplicates_found', 0)}")
        print(f"   - تعداد حذف شده: {self.report['duplicates_removed']}")
        if self.report.get('duplicates_kept', 0) > 0:
            print(f"   - تعداد نگهداری شده: {self.report['duplicates_kept']}")

        if hasattr(self, '_duplicate_analysis') and self._duplicate_analysis['duplicate_count'] > 0:
            da = self._duplicate_analysis
            print(f"\n   📐 تحلیل آماری:")
            print(f"   - احتمال یکسان بودن: {da['prob_random_match']:.8f}")
            print(f"   - حد آستانه: {da['threshold']:.4f}")
            print(f"   - تصمیم: {'حذف شد ✅' if da['should_remove'] else 'نگهداری شد ❌'}")

        if self.report['valid_ranges_applied']:
            print("\n" + "─" * 50)
            print("📐 بازه‌های معتبر اعمال شده:")
            for col, range_str in self.report['valid_ranges_applied'].items():
                print(f"   - {col}: {range_str}")

        if self.report['outliers_total'] > 0:
            print("\n" + "─" * 50)
            print(f"⚠ داده‌های پرت شناسایی شده: {self.report['outliers_total']} مورد")

            if self.report['outliers_detected']['mild']:
                print("\n   🟡 خفیف:")
                for col, count in self.report['outliers_detected']['mild'].items():
                    print(f"      - {col}: {count} مورد")

            if self.report['outliers_detected']['moderate']:
                print("\n   🟠 متوسط:")
                for col, count in self.report['outliers_detected']['moderate'].items():
                    print(f"      - {col}: {count} مورد")

            if self.report['outliers_detected']['extreme']:
                print("\n   🔴 شدید:")
                for col, count in self.report['outliers_detected']['extreme'].items():
                    print(f"      - {col}: {count} مورد")

        print("\n" + "─" * 50)
        print("✅ خلاصه نهایی:")
        if self.report['duplicates_removed'] == 0 and self.report['outliers_total'] == 0:
            print("   هیچ داده مشکوکی یافت نشد")
        else:
            if self.report['duplicates_removed'] > 0:
                print(f"   - {self.report['duplicates_removed']} ردیف تکراری حذف شد")
            if self.report['outliers_total'] > 0:
                print(f"   - {self.report['outliers_total']} داده پرت شناسایی شد")
        print("=" * 70 + "\n")