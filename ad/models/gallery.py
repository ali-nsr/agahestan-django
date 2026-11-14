from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q


class Gallery(models.Model):
    ad = models.ForeignKey('ad.Ad', on_delete=models.CASCADE, related_name='gallery', verbose_name=_('آگهی'))
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
