from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_set',  # کسایی که این یوزر فالو کرده
        verbose_name=_('Follower')
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers_set',  # کسایی که این یوزر رو فالو کردن
        verbose_name=_('Following')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # جلوگیری از فالو تکراری
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'


    def __str__(self):
        return f'{self.follower} → {self.following}'