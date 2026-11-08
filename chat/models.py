from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
import uuid

from ad.models import Ad

class AdChat(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='آگهی')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='فرستنده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')


    class Meta:
        unique_together = ('ad', 'sender')
        verbose_name = _('چت')
        verbose_name_plural = _('چت ها')
        indexes = [
            models.Index(fields=['uuid'])
        ]


class AdMessage(models.Model):
    chat = models.ForeignKey(AdChat, on_delete=models.CASCADE, related_name='messages', verbose_name='چت')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='فرستنده')
    text = models.TextField(verbose_name='پیام')
    is_seen = models.BooleanField(default=False, verbose_name='دیده شده')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = _('پیام')
        verbose_name_plural = _('پیام ها')
