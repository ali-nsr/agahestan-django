# from django.db import models
# from django.utils.translation import gettext_lazy as _
#
# class Bookmark(models.Model):
#     user = models.ForeignKey(
#         'accounts.User', on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_('کاربر'),
#     )
#     ad = models.ForeignKey(
#         'ad.Ad', on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_('آگهی'),
#     )
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
#
#     class Meta:
#         verbose_name = _('نشان شده')
#         verbose_name_plural = _('نشان شده ها')
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['user', 'ad'], name='unique_user_ad_bookmark',
#             ),
#         ]
#         indexes = [
#             models.Index(fields=['user', '-created_at']),
#             models.Index(fields=['ad']),
#         ]
#         ordering = ('-created_at',)
#
#     def __str__(self):
#         return f'{self.user_id} - {self.ad_id}'
