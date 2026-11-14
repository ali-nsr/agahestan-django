from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model




class AdViews(models.Model):
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('IP'))
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name=_('سشن'))
    ad = models.ForeignKey('ad.Ad', on_delete=models.CASCADE, verbose_name=_('آگهی'))
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='ad_views',
                             verbose_name=_('کاربر')
                             )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))

    class Meta:
        verbose_name = _('بازدید آگهی')
        verbose_name_plural = _('بازدید های آگهی')
        indexes = [models.Index(fields=['ad', 'created_at'])]

    def __str__(self):
        return self.ad.title
