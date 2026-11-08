from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid
from .manager import UserManager


class User(AbstractBaseUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'))
    phone = models.CharField(max_length=11, unique=True, verbose_name=_('موبایل'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('مدیر'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))
    is_verified = models.BooleanField(default=False, verbose_name=_('تایید شده'))
    temp_code = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('کد موقت'))
    is_online = models.BooleanField(default=False, verbose_name=_('آنلاین'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    # fields required for admin
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=['uuid'])
        ]
        verbose_name = _('کاربر')
        verbose_name_plural = _('کابر ها')

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True

    def has_module_perms(self, app_label):
        return True
        # if app_label == 'django_celery_beat':
        #     if self.is_superuser:
        #         return True

    # @property
    def is_staff(self):
        if self.is_superuser:
            return True

    def full_name(self):
        if self.profile.first_name and self.profile.last_name:
            return f'{self.profile.first_name} {self.profile.last_name}'
        else:
            return self.phone



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('کاربر'))
    first_name = models.CharField(max_length=250, verbose_name=_('نام'))
    last_name = models.CharField(max_length=250, verbose_name=_('نام خانوادگی'))
    image = models.ImageField(upload_to='profile/%Y/%m/%d/', verbose_name=_('تصویر'))
    email = models.EmailField(max_length=250, verbose_name=_('ایمیل'))

    def __str__(self):
        return self.user.phone

    class Meta:
        verbose_name = _('پروفایل')
        verbose_name_plural = _('پروفایل ها')


# class OTP(models.Model):
#     phone = models.CharField(max_length=11, verbose_name='Phone')
#     code = models.CharField(max_length=6, verbose_name='Code')
#     created_at = models.DateTimeField(verbose_name='Created At')
#     expires_at = models.DateTimeField(verbose_name='Expires At')
#     is_used = models.BooleanField(default=False, verbose_name='Is Used')
#
#     def __str__(self):
#         return f"{self.phone} - {self.code}"
#
#     class Meta:
#         db_table = 'otp'
#         verbose_name = 'OTP'
#         verbose_name_plural = 'OTP'

class OTP(models.Model):
    username = models.CharField(max_length=50, verbose_name=_('نام کاربری'))
    code = models.CharField(max_length=255, verbose_name=_('کد'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    expires_at = models.DateTimeField(verbose_name=_('تاریخ انقضا'))
    is_used = models.BooleanField(default=False, verbose_name=_('استفاده شده'))

    def __str__(self):
        return f"{self.username} - {self.code}"

    class Meta:
        verbose_name = _('OTP کد')
        verbose_name_plural = _('OTP کد های')

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_('کاربر'))
    ad = models.ForeignKey('ad.Ad', on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_('آگهی'))

    def __str__(self):
        return f'{self.user.phone} - {self.ad}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'ad'],
                name='unique_user_ad_bookmark'
            )
        ]
        verbose_name = _('نشان')
        verbose_name_plural = _('نشان ها')
