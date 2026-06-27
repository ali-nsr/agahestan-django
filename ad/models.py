from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.postgres.indexes import GinIndex
from jalali_date import datetime2jalali
import uuid

User = get_user_model()

from location.models import Province, City, Neighborhood
from jalali_date import date2jalali, datetime2jalali


class AdManager(models.Manager):
    def get_related_ads(self, category_id):
        qs = self.filter(category_id=category_id)
        return qs


class Ad(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('پیش‌نویس')
        REVIEW = 'review', _('در حال بررسی')
        PUBLISHED = 'published', _('منتشر شده')
        REJECTED = 'rejected', _('رد شده')
        EXPIRED = 'expired', _('منقضی شده')
        ARCHIVED = 'archived', _('آرشیو')
        WAIT_TO_PAY = 'wait_to_pay', _('در انتظار پرداخت')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('uuid'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    title = models.CharField(max_length=100, verbose_name=_('عنوان'))
    description = models.TextField(verbose_name=_('توضیحات'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='category_ads',
                                 verbose_name=_('دسته بندی'))
    thumbnail = models.ImageField(upload_to='%Y/%m/%d/thumbnails/', null=True, blank=True, verbose_name=_('thumbnail'))
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='province_ads',
                                 verbose_name=_('استان'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_ads',
                             verbose_name=_('شهر'))
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='neighborhood_ads',
                                     verbose_name=_('محله'))
    address = models.CharField(max_length=100, verbose_name=_('آدرس'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name=_('وضعیت'))
    price = models.PositiveBigIntegerField(verbose_name=_('قیمت'))
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True,
                                   verbose_name=_('عرض جغرافیایی'))
    longitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True,
                                    verbose_name=_('طول جغرافیایی'))
    is_negotiable = models.BooleanField(default=False, verbose_name=_('قابل مذاکره'))
    is_paid = models.BooleanField(default=False, verbose_name=_('پرداخت شده / نشده'))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('زمان انتشار'))
    expires_at = models.DateTimeField(verbose_name=_('تاریخ انقضا'))
    bumped_at = models.DateTimeField(null=True, blank=True, verbose_name=_('نردبان/بامپ'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('بازدید'))
    chats_count = models.PositiveIntegerField(default=0, verbose_name=_('گفت‌وگو'))
    attributes_cache = models.JSONField(null=True, blank=True, verbose_name=_('داده ‌های کش‌ شده'))

    objects = AdManager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'ads'
        verbose_name = _('آگهی')
        verbose_name_plural = _('آگهی ها')

        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['category']),
            models.Index(fields=['city']),
            models.Index(fields=['price']),
            models.Index(fields=['status']),
            GinIndex(fields=['attributes_cache']),
        ]

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def get_field_values(self):
        values = (
            AdAttribute.objects
            .select_related('category_field')
            .filter(ad=self)
        )

        return [
            {
                'id': v.category_field.id,
                'label': v.category_field.label,
                'type': v.category_field.type,
                'value': v.value,
                'data': v.category_field.data,  # اگه گزینه‌دار باشه
            }
            for v in values
        ]

    def api_ad_list_field_values(self):
        if self.attributes_cache != 'None':
            return [
                {
                    'label': v['label'],
                    'value': v['value'],
                }
                for v in self.attributes_cache
            ]
        else:
            return [{}]

    def api_ad_created_at(self):
        return datetime2jalali(self.created_at)

    def get_full_address(self):
        if self.neighborhood:
            return f'{self.province.name} {self.city.name} {self.neighborhood.name} {self.address}'
        else:
            return f'{self.province.name} {self.city.name} {self.address}'

    def save(self, *args, **kwargs):
        # self.attributes_cache = self.get_field_values()
        super().save(*args, **kwargs)

    # def get_gallery(self):
    #     qs = Gallery.objects.filter(ad=self)
    #     res = [{f'{q.id}': q.image.url} for q in qs]
    #     return res


class Gallery(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='gallery', verbose_name=_('آگهی'))
    image = models.ImageField(upload_to='ads/%Y/%m/%d/', verbose_name=_('تصویر'))
    is_main = models.BooleanField(default=False, verbose_name=_('تصویر اصلی'))

    class Meta:
        db_table = 'galleries'
        verbose_name = _('تصویر آگهی')
        verbose_name_plural = _('تصاویر آگهی')
        indexes = [models.Index(fields=['ad', 'is_main'])]
        constraints = [
            # فقط یک تصویر اصلی برای هر آگهی
            models.UniqueConstraint(
                fields=['ad', 'is_main'],
                condition=Q(is_main=True),
                name='uniq_main_image_per_ad'
            )
        ]

    def __str__(self):
        return f"{self.ad_id} - {('MAIN ' if self.is_main else '')}{self.image.name}"

    def save(self, *args, **kwargs):
        if self.is_main:
            Gallery.objects.filter(ad=self.ad, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)


class CategoryManager(models.Manager):
    def get_all_categories(self):
        # فقط یک کوئری
        rows = list(
            self.all()
            .values('id', 'title', 'slug', 'parent_id')
            .order_by('id')
        )

        # ساخت درخت بدون O(n^2)
        nodes = {}
        roots = []
        for r in rows:
            r['children'] = []
            nodes[r['id']] = r

        for r in rows:
            pid = r['parent_id']
            if pid:
                # ممکنه parent قبل یا بعد دیده شود، ولی چون nodes کامل است، مشکلی نیست
                nodes[pid]['children'].append(r)
            else:
                roots.append(r)

        # مرتب‌سازی ایمن برای هر سطح (در صورت نیاز)
        for n in nodes.values():
            n['children'].sort(key=lambda x: (x['id']))
        roots.sort(key=lambda x: (x['id']))

        return roots


class Category(models.Model):
    parent = models.ForeignKey('self', default=None, null=True, blank=True, on_delete=models.CASCADE,
                               related_name='children', verbose_name=_('والد'))
    title = models.CharField(max_length=50, verbose_name=_('عنوان'))
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True, verbose_name=_('آدرس URL'))
    icon = models.ImageField(upload_to='category/icon/', null=True, blank=True, verbose_name='آیکون')
    is_payable = models.BooleanField(default=False, verbose_name=_('پولی / رایگان'))
    is_special = models.BooleanField(default=False, verbose_name=_('مخصوص'))
    price = models.PositiveBigIntegerField(default=0, verbose_name=_('مبلغ'))

    objects = CategoryManager()

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])

    class Meta:
        db_table = 'categories'
        verbose_name = _('دسته بندی')
        verbose_name_plural = _('دسته بندی ها')
        ordering = ['id']

    def get_category_fields(self):
        res = CategoryField.objects.filter(category=self)

        return res


class CategoryField(models.Model):
    class FieldType(models.TextChoices):
        INTEGER = 'int', _('عدد صحیح')
        DECIMAL = 'decimal', _('عدد اعشاری')
        BOOLEAN = 'bool', _('درست / نادرست')
        STRING = 'str', _('رشته متنی کوتاه')
        TEXT = 'text', _('متن بلند')
        CHOICE = 'choice', _('انتخابی (لیستی)')
        MULTI_CHOICE = 'multi_choice', _('چندانتخابی')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('دسته'))
    key = models.SlugField(max_length=100, unique=True, verbose_name=_('کلید'))
    label = models.CharField(max_length=100, verbose_name=_('برچسب'))
    type = models.CharField(max_length=20, choices=FieldType.choices, verbose_name=_('نوع'))
    is_required = models.BooleanField(default=True, verbose_name=_('فیلد اجباری'))
    data = models.JSONField(null=True, blank=True, verbose_name=_('داده کمکی'))

    # پیشنهاد: {"options":[...], "unit":"m2", "min":0, "max":1000, "widget":"range"}

    class Meta:
        db_table = 'category_fields'
        verbose_name = _('فیلد دسته')
        verbose_name_plural = _('فیلدهای دسته')
        indexes = [
            models.Index(fields=['category'])
        ]

    def __str__(self):
        return f"{self.category} - {self.label}"


class AdAttribute(models.Model):
    category_field = models.ForeignKey(CategoryField, on_delete=models.CASCADE, verbose_name=_('فیلد دسته بندی'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='ad_attributes', verbose_name=_('آگهی'))
    value = models.CharField(max_length=50, verbose_name=_('مقدار'))

    class Meta:
        db_table = 'ad_attributes'
        verbose_name = _('مقدار آگهی')
        verbose_name_plural = _('مقدار آگهی')

        indexes = [
            models.Index(fields=['ad', 'category_field']),
        ]
        unique_together = ('ad', 'category_field')  # هر فیلد در هر آگهی فقط یک مقدار

    def __str__(self):
        return f"{self.category_field} - {self.value}"


class AdViews(models.Model):
    ip = models.CharField(max_length=20, verbose_name=_('IP'))
    user_agent = models.TextField(verbose_name=_('User Agent'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name=_('آگهی'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))

    class Meta:
        db_table = 'ad_views'
        verbose_name = 'بازدید آگهی'
        verbose_name_plural = 'بازدید های آگهی'

    def __str__(self):
        return self.ad.title


class AdReportReason(models.Model):
    reason = models.CharField(max_length=50, verbose_name=_('دلیل گزارش'))

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'ad_report_reasons'
        verbose_name = _('دلیل گزارش')
        verbose_name_plural = _('دلیل های گزارش')


class AdReport(models.Model):
    reason = models.ForeignKey(AdReportReason, on_delete=models.CASCADE, verbose_name=_('دلیل گزارش'))
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('گزارش دهنده'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name=_('آگهی'))
    description = models.TextField(null=True, blank=True, verbose_name=_('توضیحات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))

    def __str__(self):
        return f'{self.reporter} - {self.ad}'

    class Meta:
        db_table = 'ad_reports'
        verbose_name = 'گزارش'
        verbose_name_plural = 'گزارش ها'

# python manage.py loaddata ad/fixtures/ad.json
# python manage.py loaddata ad/fixtures/category.json
