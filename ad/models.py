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
        DRAFT = 'draft', _('Draft')
        REVIEW = 'review', _('Review')
        PUBLISHED = 'published', _('Published')
        REJECTED = 'rejected', _('Rejected')
        EXPIRED = 'expired', _('Expired')
        ARCHIVED = 'archived', _('Archived')
        WAIT_TO_PAY = 'wait_to_pay', _('Wait To Pay')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='category_ads',
                                 verbose_name=_('Category'))
    thumbnail = models.ImageField(upload_to='%Y/%m/%d/thumbnails/', null=True, blank=True, verbose_name=_('thumbnail'))
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='province_ads',
                                 verbose_name=_('Province'))
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_ads',
                             verbose_name=_('City'))
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='neighborhood_ads',
                                     verbose_name=_('Neighborhood'))
    address = models.CharField(max_length=100, verbose_name=_('Address'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name=_('Status'))
    price = models.PositiveBigIntegerField(verbose_name=_('Price'))
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True,
                                   verbose_name=_('Latitude'))
    longitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True,
                                    verbose_name=_('Longitude'))
    is_negotiable = models.BooleanField(default=False, verbose_name=_('Is Negotiable'))
    is_paid = models.BooleanField(default=False, verbose_name=_('Is Paid'))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Published At'))
    expires_at = models.DateTimeField(verbose_name=_('Expires At'))
    bumped_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Bumped At'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Views Count'))
    chats_count = models.PositiveIntegerField(default=0, verbose_name=_('Chats Count'))
    attributes_cache = models.JSONField(null=True, blank=True, verbose_name=_('Attributes Cache'))

    objects = AdManager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'ads'
        verbose_name = _('Ad')
        verbose_name_plural = _('Ads')

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
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='gallery', verbose_name=_('Ad'))
    image = models.ImageField(upload_to='ads/%Y/%m/%d/', verbose_name=_('Image'))
    is_main = models.BooleanField(default=False, verbose_name=_('Is Main'))

    class Meta:
        db_table = 'galleries'
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')
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
                               related_name='children', verbose_name=_('Parent'))
    title = models.CharField(max_length=50, verbose_name=_('Title'))
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True, verbose_name=_('Slug'))
    icon = models.ImageField(upload_to='category/icon/', null=True, blank=True, verbose_name='Icon')
    is_payable = models.BooleanField(default=False, verbose_name=_('Is Payable'))
    is_special = models.BooleanField(default=False, verbose_name=_('Is Special'))
    price = models.PositiveBigIntegerField(default=0, verbose_name=_('Price'))

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
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
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

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Category'))
    key = models.SlugField(max_length=100, unique=True, verbose_name=_('Key'))
    label = models.CharField(max_length=100, verbose_name=_('Label'))
    type = models.CharField(max_length=20, choices=FieldType.choices, verbose_name=_('Type'))
    is_required = models.BooleanField(default=True, verbose_name=_('Is Required'))
    data = models.JSONField(null=True, blank=True, verbose_name=_('Data'))

    # پیشنهاد: {"options":[...], "unit":"m2", "min":0, "max":1000, "widget":"range"}

    class Meta:
        db_table = 'category_fields'
        verbose_name = _('Category Field')
        verbose_name_plural = _('Category Fields')
        indexes = [
            models.Index(fields=['category'])
        ]

    def __str__(self):
        return f"{self.category} - {self.label}"


class AdAttribute(models.Model):
    category_field = models.ForeignKey(CategoryField, on_delete=models.CASCADE, verbose_name=_('Category Field'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='ad_attributes', verbose_name=_('Ad'))
    value = models.CharField(max_length=50, verbose_name=_('Value'))

    class Meta:
        db_table = 'ad_attributes'
        verbose_name = _('Ad Attribute')
        verbose_name_plural = _('Ad Attributes')

        indexes = [
            models.Index(fields=['ad', 'category_field']),
        ]
        unique_together = ('ad', 'category_field')  # هر فیلد در هر آگهی فقط یک مقدار

    def __str__(self):
        return f"{self.category_field} - {self.value}"


class AdViews(models.Model):
    ip = models.CharField(max_length=20, verbose_name=_('IP'))
    user_agent = models.TextField(verbose_name=_('User Agent'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name=_('Ad'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    class Meta:
        db_table = 'ad_views'
        verbose_name = 'Ad View'
        verbose_name_plural = 'Ad Views'

    def __str__(self):
        return self.ad.title


class AdReportReason(models.Model):
    reason = models.CharField(max_length=50, verbose_name=_('Report Reason'))

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'ad_report_reasons'
        verbose_name = _('Report Reason')
        verbose_name_plural = _('Report Reasons')


class AdReport(models.Model):
    reason = models.ForeignKey(AdReportReason, on_delete=models.CASCADE, verbose_name=_('Report Reason'))
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Reported'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name=_('Ad'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))

    def __str__(self):
        return f'{self.reporter} - {self.ad}'

    class Meta:
        db_table = 'ad_reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

# python manage.py loaddata ad/fixtures/ad.json
# python manage.py loaddata ad/fixtures/category.json
