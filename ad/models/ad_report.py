from django.db import models
from django.utils.translation import gettext_lazy as _


class AdReport(models.Model):
    reason = models.ForeignKey('ad.AdReportReason', on_delete=models.CASCADE, verbose_name=_('علت'))
    reporter = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name=_('گزارش دهنده'))
    ad = models.ForeignKey('ad.Ad', on_delete=models.CASCADE, verbose_name=_('آگهی'))
    description = models.TextField(null=True, blank=True, verbose_name=_('توضیحات'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))

    def __str__(self):
        return f'{self.reporter} - {self.ad}'

    class Meta:
        verbose_name = _('گزارش')
        verbose_name_plural = _('گزارش ها')
