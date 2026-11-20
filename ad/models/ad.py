from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.indexes import GinIndex
import uuid


from jalali_date import datetime2jalali


class AdManager(models.Manager):
    def published(self):
        return self.filter(status=Ad.Status.PUBLISHED)

    def get_related_ads(self, category_id, exclude_id=None, limit=8):
        qs = self.published().filter(category_id=category_id)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs.order_by('-published_at')[:limit]


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
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE,related_name='ads', verbose_name=_('کاربر'))
    title = models.CharField(max_length=100, verbose_name=_('عنوان'))
    description = models.TextField(verbose_name=_('توضیحات'))
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='category_ads',
                                 verbose_name=_('دسته بندی'))
    thumbnail = models.ImageField(upload_to='%Y/%m/%d/thumbnails/', null=True, blank=True,
                                  verbose_name=_('تصویر بند انگشتی'))

    # ─── موقعیت ───
    province = models.ForeignKey('location.Province', on_delete=models.CASCADE, related_name='province_ads',
                                 verbose_name=_('استان'))
    city = models.ForeignKey('location.City', on_delete=models.CASCADE, related_name='city_ads',
                             verbose_name=_('شهر'))
    neighborhood = models.ForeignKey('location.Neighborhood', on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='neighborhood_ads',
                                     verbose_name=_('محله'))
    address = models.CharField(max_length=100, verbose_name=_('آدرس'))
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True, blank=True, verbose_name=_('عرض جغرافیایی'),
    )
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True, blank=True, verbose_name=_('طول جغرافیایی'),
    )

    # ─── قیمت ───
    price = models.PositiveBigIntegerField(null=True, blank=True, verbose_name=_('قیمت'))
    is_negotiable = models.BooleanField(default=False, verbose_name=_('قابل مذاکره'))

    # ─── وضعیت ───
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name=_('وضعیت'))
    is_paid = models.BooleanField(default=False, verbose_name=_('پرداخت شده'))
    rejection_reason = models.TextField(null=True, blank=True, verbose_name=_('دلیل رد'))

    # ─── زمان‌ها ───
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاریخ انتشار'))
    expires_at = models.DateTimeField(verbose_name=_('تاریخ انتقضا'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))
    bumped_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاریخ پله'))

    # ─── کش‌ها (فقط برای سرعت) ───
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد بازدید'))
    chats_count = models.PositiveIntegerField(default=0, verbose_name=_('تعداد چت'))
    attributes_cache = models.JSONField(null=True, blank=True, verbose_name=_('اتریبیوت ها'))

    objects = AdManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('آگهی')
        verbose_name_plural = _('آگهی ها')
        ordering = ('-published_at', '-created_at')

        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['city', 'status']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['price']),
            GinIndex(fields=['attributes_cache']),
        ]

    def save(self, *args, **kwargs):
        # expires_at خالی → ۳۰ روز بعد
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(
                days=30,
            )

        # آگهی جدید → REVIEW (تا ادمین تأیید کنه)
        if not self.pk and self.status == self.Status.DRAFT:
            self.status = self.Status.REVIEW

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return bool(self.expires_at and timezone.now() > self.expires_at)

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED and not self.is_expired

    @property
    def is_special(self):
        return self.category.is_special or self.is_paid

    @property
    def price_per_meter(self):
        """قیمت هر متر — فقط اگه دسته‌اش فیلد متراژ داشته باشه."""
        if not self.price:
            return None
        area = self._get_attribute_value('area')
        if area and str(area).isdigit():
            return self.price // int(area)
        return None

    @property
    def main_image(self):
        """اولویت: thumbnail → اولین عکس گالری."""
        if self.thumbnail:
            return self.thumbnail
        first = self.gallery.order_by('-is_main', 'id').first()
        return first.image if first else None

    # ═══════════════════════════════════════════
    # آدرس
    # ═══════════════════════════════════════════

    def get_full_address(self):
        parts = [self.province.name, self.city.name]
        if self.neighborhood:
            parts.append(self.neighborhood.name)
        parts.append(self.address)
        return ' '.join(parts)

    # ═══════════════════════════════════════════
    # اتریبیوت‌ها
    # ═══════════════════════════════════════════

    def _get_attribute_value(self, key_suffix):
        """مثلاً area → مقدار فیلد متراژ دسته‌اش."""
        if not self.category_id:
            return None

        attr = (
            self.ad_attributes
            .filter(category_field__key=f'{self.category.slug}__{key_suffix}')
            .first()
        )
        return attr.value if attr else None

    def get_field_values(self):
        return [
            {
                'id': v.category_field.id,
                'label': v.category_field.label,
                'type': v.category_field.type,
                'value': v.value,
                'data': v.category_field.data,
            }
            for v in self.ad_attributes.select_related('category_field').all()
        ]

    def api_ad_list_field_values(self):
        """برای API — سریع، از cache."""
        if not self.attributes_cache:
            return []
        return [
            {'label': v.get('label', ''), 'value': v.get('value', '')}
            for v in self.attributes_cache
        ]

    # ═══════════════════════════════════════════
    # تاریخ شمسی
    # ═══════════════════════════════════════════

    def api_ad_created_at(self):
        return datetime2jalali(self.created_at)