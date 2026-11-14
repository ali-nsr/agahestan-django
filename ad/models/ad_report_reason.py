from django.db import models
from django.utils.translation import gettext_lazy as _


class AdReportReason(models.Model):
    reason = models.CharField(max_length=50, verbose_name=_('علت'))

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = _('علت گزارش')
        verbose_name_plural = _('علت های گزارش')
