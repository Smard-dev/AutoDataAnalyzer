# ============================================
# phase2_transformation.py
# کلاس فاز 2: تبدیل داده‌ها به عددی و استانداردسازی
# ============================================

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler


class Phase2Transformation:
    """
    کلاس فاز 2 - تبدیل داده‌ها به عددی و استانداردسازی

    ترتیب اجرا:
    1. تبدیل Boolean به 0/1
    2. حذف ستون‌های اسمی با تنوع بیشتر از 20%
    3. مپ کردن هوشمند ستون‌های اسمی باقیمانده
    4. نمایش نقشه به کاربر و دریافت تأیید (بازگشتی)
    5. حذف ستون‌های تکراری و دارای رابطه مستقیم (همبستگی > 0.95)
    6. پر کردن مقادیر گمشده با KNN Imputer
    7. استانداردسازی با StandardScaler (Z-Score)

    خروجی:
    - final_df: دیتاست نهایی قبل از استانداردسازی
    - std_df: دیتاست استاندارد شده
    """

    def __init__(self, df=None, dataset_name="Unknown"):
        self.df = df
        self.df_original = df.copy() if df is not None else None
        self.dataset_name = dataset_name
        self.verbose = True
        self.mappings = {}  # نقشه‌های نهایی {col_name: {value: code}}
        self.columns_removed = []  # ستون‌های حذف شده
        self.final_df = None  # نسخه نهایی قبل از استاندارد
        self.std_df = None  # نسخه استاندارد شده
        self.std_scaler = StandardScaler()

        self.report = {
            "dataset_name": dataset_name,
            "original_shape": df.shape if df is not None else (0, 0),
            "boolean_converted": [],
            "nominal_removed_columns": [],
            "nominal_converted": [],
            "user_modified_mappings": {},
            "duplicate_columns_removed": [],
            "correlated_columns_removed": [],
            "missing_values_filled": {},
            "final_shape_before_std": None,
            "final_shape_after_std": None,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _print(self, message, force=False):
        if self.verbose or force:
            print(message)

    # ============================================================
    # گام 1: تبدیل Boolean به 0/1
    # ============================================================

    def convert_boolean_to_numeric(self):
        """تبدیل ستون‌های Boolean به 0 و 1"""
        bool_cols = self.df.select_dtypes(include=['bool']).columns

        for col in bool_cols:
            self.df[col] = self.df[col].astype(int)
            self.report["boolean_converted"].append(col)
            self._print(f"✅ ستون Boolean '{col}' → 0/1 تبدیل شد")

        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                unique_vals = self.df[col].dropna().unique()
                if set(unique_vals).issubset({'True', 'False', 'TRUE', 'FALSE', 'true', 'false'}):
                    self.df[col] = self.df[col].map(lambda x: 1 if str(x).lower() == 'true' else 0)
                    self.report["boolean_converted"].append(col)
                    self._print(f"✅ ستون Boolean (object) '{col}' → 0/1 تبدیل شد")

    # ============================================================
    # گام 2: حذف ستون‌های اسمی با تنوع بالا
    # ============================================================

    def remove_high_variance_nominal_columns(self, threshold_percent=20):
        """حذف ستون‌های اسمی با تنوع بیشتر از threshold_percent"""
        n_rows = len(self.df)
        threshold = n_rows * threshold_percent / 100

        object_cols = self.df.select_dtypes(include=['object']).columns
        object_cols = [col for col in object_cols if col not in self.report["boolean_converted"]]

        if not object_cols:
            self._print("   ✅ هیچ ستون اسمی برای بررسی وجود ندارد")
            return

        self._print(f"\n🔍 حذف ستون‌های اسمی با تنوع > {threshold_percent}% (>{threshold:.0f} مقدار):")

        for col in object_cols:
            unique_count = self.df[col].nunique()

            if unique_count >= threshold:
                self.df = self.df.drop(columns=[col])
                self.columns_removed.append(col)
                self.report["nominal_removed_columns"].append(col)
                self._print(f"   ⚠ حذف: '{col}' ({unique_count} مقدار منحصربفرد)")
            else:
                self._print(f"   ✅ نگهداری: '{col}' ({unique_count} مقدار منحصربفرد)")

    # ============================================================
    # گام 3: مپ کردن هوشمند ستون‌های اسمی باقیمانده
    # ============================================================

    def get_smart_mapping(self, col):
        """ایجاد نقشه هوشمند: بیشترین تکرار → کمترین عدد (0)"""
        value_counts = self.df[col].value_counts()
        sorted_values = value_counts.index.tolist()
        return {value: idx for idx, value in enumerate(sorted_values)}

    def map_nominal_columns(self):
        """مپ کردن ستون‌های اسمی باقیمانده به اعداد"""
        object_cols = self.df.select_dtypes(include=['object']).columns
        object_cols = [col for col in object_cols if col not in self.report["boolean_converted"]]

        if not object_cols:
            self._print("   ✅ هیچ ستون اسمی برای مپ کردن وجود ندارد")
            return

        self._print(f"\n📊 مپ کردن هوشمند ستون‌های اسمی:")

        for col in object_cols:
            unique_count = self.df[col].nunique()
            mapping = self.get_smart_mapping(col)
            self.mappings[col] = mapping
            self.df[col] = self.df[col].map(mapping)
            self.report["nominal_converted"].append(col)
            self._print(f"   ✅ '{col}': {unique_count} مقدار → مپ شد")

    # ============================================================
    # گام 4: نمایش نقشه و دریافت تأیید از کاربر (بازگشتی)
    # ============================================================

    def show_mappings_summary(self):
        """نمایش خلاصه نقشه‌ها"""
        if not self.mappings:
            self._print("   هیچ ستونی مپ نشده است")
            return

        print("\n" + "─" * 60)
        print("📋 خلاصه نقشه‌های ایجاد شده:")
        for idx, (col, mapping) in enumerate(self.mappings.items()):
            print(f"\n{idx + 1}. {col}: {mapping}")

    def modify_column_mapping(self, col, current_mapping):
        """اصلاح نقشه یک ستون توسط کاربر"""
        print(f"\n🔧 اصلاح نقشه '{col}':")
        new_mapping = current_mapping.copy()

        for value, current_code in current_mapping.items():
            user_input = input(f"   '{value}' (فعلی: {current_code}) → عدد جدید: ").strip()
            if user_input != "":
                try:
                    new_mapping[value] = int(user_input)
                    print(f"      ✅ تغییر: {current_code} → {new_mapping[value]}")
                except ValueError:
                    print(f"      ❌ عدد نامعتبر")
        return new_mapping

    def confirm_and_modify_mappings_recursive(self, ask_user=True):
        """
        تأیید و اصلاح نقشه‌ها توسط کاربر

        اگر ask_user=False باشه، خودکار تأیید میشه
        اگر GUI callback تنظیم شده باشه، ازش استفاده میشه
        """
        if not self.mappings:
            return True

        # اگه قرار نیست بپرسیم، خودکار تأیید کن
        if not ask_user:
            self._print("   ⏩ تأیید خودکار نقشه‌ها (بدون پرسش از کاربر)")
            return True

        # چاپ خلاصه
        print("\n📋 خلاصه نقشه‌های ایجاد شده:\n")
        for i, (col, mapping) in enumerate(self.mappings.items(), 1):
            print(f"{i}. {col}: {mapping}\n")

        # اگه GUI callback داریم، ازش استفاده کن
        if hasattr(self, 'gui_callback') and self.gui_callback:
            return self.gui_callback('confirm_mappings', {
                'mappings': self.mappings,
                'count': len(self.mappings)
            })

        # Fallback به console (فقط اگه callback نیست)
        answer = input("\n✅ نقشه‌ها را تأیید می‌کنید؟ (y/n): ").strip().lower()
        return answer == 'y'

    # ============================================================
    # گام 5: حذف ستون‌های تکراری و دارای رابطه مستقیم
    # ============================================================

    def find_direct_relationship(self, col1, col2, threshold=0.95):
        """بررسی رابطه مستقیم بین دو ستون"""
        temp_df = self.df[[col1, col2]].dropna()
        if len(temp_df) == 0:
            return False

        # همبستگی
        if pd.api.types.is_numeric_dtype(temp_df[col1]) and pd.api.types.is_numeric_dtype(temp_df[col2]):
            correlation = temp_df[col1].corr(temp_df[col2])
            if abs(correlation) > threshold:
                return True

        # یکسان بودن مقادیر
        if temp_df[col1].equals(temp_df[col2]):
            return True

        # رابطه یک‌به‌یک
        if temp_df[col1].nunique() == temp_df[col2].nunique():
            unique_pairs = temp_df[[col1, col2]].drop_duplicates()
            if len(unique_pairs) == temp_df[col1].nunique():
                return True

        return False

    def select_column_to_keep(self, col1, col2):
        """انتخاب ستون باقیمانده (دامنه گسترده‌تر → اولویت)"""
        unique1 = self.df[col1].nunique()
        unique2 = self.df[col2].nunique()

        if unique1 > unique2:
            return col1
        elif unique2 > unique1:
            return col2

        # دامنه یکسان → میانگین کمتر
        if pd.api.types.is_numeric_dtype(self.df[col1]):
            if self.df[col1].mean() < self.df[col2].mean():
                return col1
        return col1

    def remove_duplicate_and_correlated_columns(self, threshold=0.95):
        """حذف ستون‌های تکراری و دارای رابطه مستقیم"""
        columns = list(self.df.columns)
        to_remove = set()

        self._print(f"\n🔍 حذف ستون‌های تکراری و دارای رابطه مستقیم (آستانه: {threshold}):")

        for i in range(len(columns)):
            col1 = columns[i]
            if col1 in to_remove:
                continue

            for j in range(i + 1, len(columns)):
                col2 = columns[j]
                if col2 in to_remove:
                    continue

                if self.find_direct_relationship(col1, col2, threshold):
                    keep = self.select_column_to_keep(col1, col2)
                    remove = col2 if keep == col1 else col1
                    to_remove.add(remove)
                    self.report["correlated_columns_removed"].append({"kept": keep, "removed": remove})
                    self._print(f"   ⚠ '{remove}' (مشابه '{keep}') → حذف شد")

        for col in to_remove:
            if col in self.df.columns:
                self.df = self.df.drop(columns=[col])
                self.columns_removed.append(col)

        self._print(f"   ✅ {len(to_remove)} ستون حذف شد")

    # ============================================================
    # گام 6: پر کردن مقادیر گمشده با KNN
    # ============================================================

    def handle_missing_values_with_knn(self, k=None):
        """پر کردن مقادیر گمشده با KNN Imputer"""
        missing_cols = [col for col in self.df.columns if self.df[col].isnull().any()]

        if not missing_cols:
            self._print("✅ هیچ مقدار گمشده‌ای وجود ندارد")
            return

        if k is None:
            k = min(5, max(2, int(np.sqrt(len(self.df)))))

        missing_before = {col: self.df[col].isna().sum() for col in missing_cols}

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        imputer = KNNImputer(n_neighbors=k)
        df_imputed = pd.DataFrame(
            imputer.fit_transform(self.df[numeric_cols]),
            columns=numeric_cols,
            index=self.df.index
        )

        for col in numeric_cols:
            self.df[col] = df_imputed[col]

        for col in missing_cols:
            self.report["missing_values_filled"][col] = {
                "before": missing_before[col],
                "after": self.df[col].isna().sum(),
                "filled": missing_before[col],
                "method": f"KNN (k={k})"
            }

        self._print(f"✅ مقادیر گمشده با KNN (k={k}) پر شدند")

    # ============================================================
    # گام 7: استانداردسازی و ایجاد کپی
    # ============================================================

    def create_standardized_copy(self):
        """ایجاد نسخه استاندارد شده و کپی نهایی"""
        self.final_df = self.df.copy()

        numeric_cols = self.final_df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0:
            self.std_df = self.final_df.copy()
            self.std_df[numeric_cols] = self.std_scaler.fit_transform(self.final_df[numeric_cols])
            self._print(f"✅ استانداردسازی روی {len(numeric_cols)} ستون عددی اعمال شد")
        else:
            self.std_df = self.final_df.copy()
            self._print("⚠ هیچ ستون عددی برای استانداردسازی وجود ندارد")

        self.report["final_shape_before_std"] = self.final_df.shape
        self.report["final_shape_after_std"] = self.std_df.shape

    # ============================================================
    # اجرای کامل فاز 2
    # ============================================================

    def run_full_pipeline(self, threshold_percent=20, correlation_threshold=0.95,
                          ask_user_confirmation=True, verbose=True):
        """
        اجرای کامل فاز 2 با همه گام‌ها
        """
        self.verbose = verbose

        if self.df is None:
            print("❌ دیتاست بارگذاری نشده است")
            return None, None

        self._print(f"\n🚀 شروع فاز 2 بر روی دیتاست {self.dataset_name}")
        self._print("=" * 60)

        # گام 1: Boolean
        self._print("\n📌 گام 1: تبدیل Boolean به عددی")
        self.convert_boolean_to_numeric()

        # گام 2: حذف ستون‌های اسمی با تنوع بالا
        self._print(f"\n📌 گام 2: حذف ستون‌های اسمی با تنوع > {threshold_percent}%")
        self.remove_high_variance_nominal_columns(threshold_percent)

        # گام 3: مپ کردن هوشمند
        self._print(f"\n📌 گام 3: مپ کردن هوشمند ستون‌های اسمی باقیمانده")
        self.map_nominal_columns()

        # گام 4: تأیید کاربر
        if ask_user_confirmation and self.mappings:
            # اگه callback هست، خودش GUI رو هندل میکنه
            if hasattr(self, 'gui_callback') and self.gui_callback:
                confirmed = self.confirm_and_modify_mappings_recursive(ask_user=False)
                # callback خودش GUI رو نشون میده
                self.gui_callback('show_mappings', {'mappings': self.mappings})
                # منتظر تأیید از GUI میمونیم
                confirmed = self.gui_callback('confirm_mappings', {
                    'mappings': self.mappings,
                    'count': len(self.mappings)
                })
            else:
                confirmed = self.confirm_and_modify_mappings_recursive(ask_user=ask_user_confirmation)

        # گام 5: حذف ستون‌های تکراری و دارای رابطه مستقیم
        self._print(f"\n📌 گام 5: حذف ستون‌های تکراری و دارای رابطه مستقیم")
        self.remove_duplicate_and_correlated_columns(correlation_threshold)

        # گام 6: پر کردن گمشده‌ها با KNN
        self._print(f"\n📌 گام 6: پر کردن مقادیر گمشده با KNN")
        self.handle_missing_values_with_knn()

        # گام 7: استانداردسازی
        self._print(f"\n📌 گام 7: استانداردسازی و ایجاد کپی")
        self.create_standardized_copy()

        self._print("\n" + "=" * 60)
        self._print(f"✅ فاز 2 با موفقیت به پایان رسید")
        self._print(f"   final_df: {self.final_df.shape[0]} × {self.final_df.shape[1]}")
        self._print(f"   std_df: {self.std_df.shape[0]} × {self.std_df.shape[1]}")

        return self.final_df, self.std_df

    # ============================================================
    # توابع دریافت خروجی
    # ============================================================

    def get_final_dataframe(self):
        return self.final_df

    def get_standardized_data(self):
        return self.std_df

    def get_mappings(self):
        return self.mappings

    def get_removed_columns(self):
        return self.columns_removed

    def get_report(self):
        return self.report

    def report_phase2(self):
        """چاپ گزارش کامل فاز 2"""
        print("\n" + "═" * 70)
        print(f"📋 گزارش فاز 2 - دیتاست: {self.report['dataset_name']}")
        print("═" * 70)
        print(f"🕒 زمان اجرا: {self.report['timestamp']}")
        print(f"📊 شکل اولیه: {self.report['original_shape'][0]} × {self.report['original_shape'][1]}")

        if self.report['final_shape_before_std']:
            print(
                f"📊 شکل نهایی (قبل از استاندارد): {self.report['final_shape_before_std'][0]} × {self.report['final_shape_before_std'][1]}")
            print(
                f"📊 شکل نهایی (بعد از استاندارد): {self.report['final_shape_after_std'][0]} × {self.report['final_shape_after_std'][1]}")

        if self.report['boolean_converted']:
            print("\n" + "─" * 50)
            print("✅ ستون‌های Boolean تبدیل شده:")
            for col in self.report['boolean_converted']:
                print(f"   - {col}")

        if self.report['nominal_removed_columns']:
            print("\n" + "─" * 50)
            print("🗑 ستون‌های حذف شده (تنوع بالا):")
            for col in self.report['nominal_removed_columns']:
                print(f"   - {col}")

        if self.report['nominal_converted']:
            print("\n" + "─" * 50)
            print("✅ ستون‌های اسمی مپ شده:")
            for col in self.report['nominal_converted']:
                print(f"   - {col}")

        if self.report['correlated_columns_removed']:
            print("\n" + "─" * 50)
            print("🔗 ستون‌های حذف شده (رابطه مستقیم):")
            for item in self.report['correlated_columns_removed']:
                print(f"   - '{item['removed']}' (مشابه '{item['kept']}')")

        if self.report['missing_values_filled']:
            print("\n" + "─" * 50)
            print("📌 مقادیر گمشده پر شده:")
            for col, info in self.report['missing_values_filled'].items():
                print(f"   - {col}: {info['filled']} مقدار پر شد")

        if self.mappings:
            print("\n" + "─" * 50)
            print("📋 نقشه‌های نهایی:")
            for col, mapping in self.mappings.items():
                print(f"\n   {col}:")
                for val, code in mapping.items():
                    print(f"      '{val}' → {code}")

        print("\n" + "═" * 70)