# from django.db import models
# from django.utils.translation import gettext_lazy as _
#
# class Follow(models.Model):
#     follower = models.ForeignKey(
#         'accounts.User',
#         on_delete=models.CASCADE,
#         related_name='following_set',  # کسایی که این یوزر فالو کرده
#         verbose_name=_('کاربر فالو کرده')
#     )
#     following = models.ForeignKey(
#         'accounts.User',
#         on_delete=models.CASCADE,
#         related_name='followers_set',  # کسایی که این یوزر رو فالو کردن
#         verbose_name=_('کاربر را فالو کرده')
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ('follower', 'following')  # جلوگیری از فالو تکراری
#         verbose_name = 'فالو'
#         verbose_name_plural = 'فالو ها'
#
#
#     def __str__(self):
#         return f'{self.follower} → {self.following}'