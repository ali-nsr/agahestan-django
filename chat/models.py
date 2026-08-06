from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
import uuid

from ad.models import Ad

class AdChat(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'))
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Ad')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Sender')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')


    class Meta:
        db_table = 'ad_chats'
        unique_together = ('ad', 'sender')
        verbose_name = _('Chat')
        verbose_name_plural = _('Chats')
        indexes = [
            models.Index(fields=['uuid'])
        ]


class AdMessage(models.Model):
    chat = models.ForeignKey(AdChat, on_delete=models.CASCADE, related_name='messages', verbose_name='Chat')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Sender')
    text = models.TextField(verbose_name='Text')
    is_seen = models.BooleanField(default=False, verbose_name='Is Seen')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')

    class Meta:
        db_table = 'ad_messages'
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
