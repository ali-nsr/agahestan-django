from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.indexes import GinIndex
import uuid


from jalali_date import datetime2jalali


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
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('کاربر'))
    title = models.CharField(max_length=100, verbose_name=_('عنوان'))
    description = models.TextField(verbose_name=_('توضیحات'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='category_ads',
                                 verbose_name=_('دسته بندی'))
    thumbnail = models.ImageField(upload_to='%Y/%m/%d/thumbnails/', null=True, blank=True,
                                  verbose_name=_('تصویر بند انگشتی'))
    province = models.ForeignKey('location.Province', on_delete=models.CASCADE, related_name='province_ads',
                                 verbose_name=_('استان'))
    city = models.ForeignKey('location.City', on_delete=models.CASCADE, related_name='city_ads',
                             verbose_name=_('شهر'))
    neighborhood = models.ForeignKey('location.Neighborhood', on_delete=models.CASCADE, null=True, blank=True,
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
        from . import AdAttribute

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

    # def save(self, *args, **kwargs):
        # self.attributes_cache = self.get_field_values()
        # super().save(*args, **kwargs)

    # def get_gallery(self):
    #     qs = Gallery.objects.filter(ad=self)
    #     res = [{f'{q.id}': q.image.url} for q in qs]
    #     return res
