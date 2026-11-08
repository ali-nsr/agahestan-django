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
        DRAFT = 'draft', _('پیش نویس')
        REVIEW = 'review', _('در حال بررسی')
        PUBLISHED = 'published', _('منتشر شده')
        REJECTED = 'rejected', _('رد شده')
        EXPIRED = 'expired', _('منقضی شده')
        ARCHIVED = 'archived', _('آرشیو')
        WAIT_TO_PAY = 'wait_to_pay', _('در انتظار پرداخت')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    title = models.CharField(max_length=100, verbose_name=_('عنوان'))
    description = models.TextField(verbose_name=_('توضیحات'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='category_ads',
                                 verbose_name=_('دسته بندی'))
    thumbnail = models.ImageField(upload_to='%Y/%m/%d/thumbnails/', null=True, blank=True,
                                  verbose_name=_('تصویر بند انگشتی'))
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='province_ads',
                                 verbose_name=_('استان'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_ads',
                             verbose_name=_('شهر'))
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='neighborhood_ads',
                                     verbose_name=_('محله'))
    address = models.CharField(max_length=100, verbose_name=_('آدرس'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name=_('وضعیت'))
    price = models.PositiveBigIntegerField(null=True, blank=True, verbose_name=_('قیمت'))
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True,
                                   verbose_name=_('طول جغرافیایی'))
    longitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True,
                                    verbose_name=_('عرض جغرافیایی'))
    is_negotiable = models.BooleanField(default=False, verbose_name=_('قابل مذاکره'))
    is_paid = models.BooleanField(default=False, verbose_name=_('پرداخت شده'))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاریخ انتشار'))
    expires_at = models.DateTimeField(verbose_name=_('تاریخ انتقضا'))
    bumped_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاریخ پله'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد بازدید'))
    chats_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد چت'))
    attributes_cache = models.JSONField(null=True, blank=True, verbose_name=_('اتریبیوت ها'))

    objects = AdManager()

    def __str__(self):
        return self.title

    class Meta:
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
        verbose_name = _('گالری')
        verbose_name_plural = _('گالری ها')
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
            .values('id', 'title', 'slug', 'parent_id', 'icon')
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
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True, verbose_name=_('اسلاگ'))
    icon = models.ImageField(upload_to='category/icon/', null=True, blank=True, verbose_name='آیکون')
    is_payable = models.BooleanField(default=False, verbose_name=_('پولی'))
    is_special = models.BooleanField(default=False, verbose_name=_('ویژه'))
    price = models.PositiveBigIntegerField(default=0, verbose_name=_('قیمت'))

    objects = CategoryManager()

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' / '.join(full_path[::-1])

    class Meta:
        verbose_name = _('دسته بندی')
        verbose_name_plural = _('دسته بندی ها')
        ordering = ['id']

    def get_category_fields(self):
        res = CategoryField.objects.filter(category=self)

        return res


class CategoryField(models.Model):
    class FieldType(models.TextChoices):
        INTEGER = 'int', _('Integer')
        DECIMAL = 'decimal', _('Decimal')
        BOOLEAN = 'bool', _('Boolean')
        STRING = 'str', _('String')
        TEXT = 'text', _('Text')
        CHOICE = 'choice', _('Choice')
        MULTI_CHOICE = 'multi_choice', _('Multi Choice')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fields', verbose_name=_('دسته بندی'))
    key = models.SlugField(max_length=100, unique=True, verbose_name=_('کلید'))
    label = models.CharField(max_length=100, verbose_name=_('لیبل'))
    type = models.CharField(max_length=20, choices=FieldType.choices, verbose_name=_('نوع'))
    is_required = models.BooleanField(default=True, verbose_name=_('اجباری'))
    data = models.JSONField(null=True, blank=True, verbose_name=_('دیتا'))

    # پیشنهاد: {"options":[...], "unit":"m2", "min":0, "max":1000, "widget":"range"}

    class Meta:
        verbose_name = _('فیلد دسته بندی')
        verbose_name_plural = _('فیلد های دسته بندی')
        indexes = [
            models.Index(fields=['category'])
        ]

    def __str__(self):
        return f"{self.category} - {self.label}"


class AdAttribute(models.Model):
    category_field = models.ForeignKey(CategoryField, on_delete=models.CASCADE, verbose_name=_('فیلد دسته بندی'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='ad_attributes', verbose_name=_('آگهی'))
    value = models.CharField(max_length=500, verbose_name=_('مقدار'))

    class Meta:
        verbose_name = _('اتریبیوت آگهی')
        verbose_name_plural = _('اتریبیوت های آگهی')

        indexes = [
            models.Index(fields=['ad', 'category_field']),
        ]
        unique_together = ('ad', 'category_field')  # هر فیلد در هر آگهی فقط یک مقدار

    def __str__(self):
        return f"{self.category_field} - {self.value}"


class AdViews(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP'))
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name=_('سشن'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name=_('آگهی'))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ad_views',
                             verbose_name=_('کاربر')
                             )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))

    class Meta:
        verbose_name = _('بازدید آگهی')
        verbose_name_plural = _('بازدید های آگهی')
        indexes = [models.Index(fields=['ad', 'created_at'])]

    def __str__(self):
        return self.ad.title


class AdReportReason(models.Model):
    reason = models.CharField(max_length=50, verbose_name=_('علت'))

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = _('علت گزارش')
        verbose_name_plural = _('علت های گزارش')


class AdReport(models.Model):
    reason = models.ForeignKey(AdReportReason, on_delete=models.CASCADE, verbose_name=_('علت'))
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('گزارش دهنده'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name=_('آگهی'))
    description = models.TextField(null=True, blank=True, verbose_name=_('توضیحات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))

    def __str__(self):
        return f'{self.reporter} - {self.ad}'

    class Meta:
        verbose_name = _('گزارش')
        verbose_name_plural = _('گزارش ها')

# python manage.py loaddata ad/fixtures/ad.json
# python manage.py loaddata ad/fixtures/category.json
