# ============================================
# phase3_variables.py
# فاز 3: تعریف متغیرها به صورت آرایه‌ای
# 5 پارامتر اصلی + 5 پارامتر استاندارد
# ============================================

class UserVariables:
    """
    متغیرهای مربوط به داده‌های کاربران
    هر تابع = یک کانستراکتور برای مقداردهی مستقیم
    """

    def User(self, param1=None, param2=None, param3=None, param4=None, param5=None, totalParam=None):
        """
        پارامترهای اصلی کاربر
        param1: سن / age
        param2: جنسیت / gender
        param3: نوع دستگاه / device_type
        param4: زمان در سایت / time_on_site
        param5: صفحات دیده شده / pages_viewed
        totalParam: کل داده‌های کاربر (بدون ستون‌های بی‌اهمیت)
        """
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.param4 = param4
        self.param5 = param5
        self.totalParam = totalParam
        return self

    def stdUser(self, sparam1=None, sparam2=None, sparam3=None, sparam4=None, sparam5=None, stotalParam=None):
        """
        پارامترهای استاندارد شده کاربر
        (برای داده‌هایی که قبلاً استاندارد شده‌اند)
        """
        self.sparam1 = sparam1
        self.sparam2 = sparam2
        self.sparam3 = sparam3
        self.sparam4 = sparam4
        self.sparam5 = sparam5
        self.stotalParam = stotalParam
        return self


class ProductVariables:
    """
    متغیرهای مربوط به داده‌های محصولات
    """

    def Product(self, param1=None, param2=None, param3=None, param4=None, param5=None, totalParam=None):
        """
        پارامترهای اصلی محصول
        param1: امتیاز / rating / imdb_score
        param2: نوع / type (فیلم/سریال)
        param3: کشور تولید / production_country
        param4: سال انتشار / release_year
        param5: مدت زمان / runtime
        totalParam: کل داده‌های محصول (بدون ستون‌های بی‌اهمیت)
        """
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.param4 = param4
        self.param5 = param5
        self.totalParam = totalParam
        return self

    def stdProduct(self, sparam1=None, sparam2=None, sparam3=None, sparam4=None, sparam5=None, stotalParam=None):
        """
        پارامترهای استاندارد شده محصول
        """
        self.sparam1 = sparam1
        self.sparam2 = sparam2
        self.sparam3 = sparam3
        self.sparam4 = sparam4
        self.sparam5 = sparam5
        self.stotalParam = stotalParam
        return self