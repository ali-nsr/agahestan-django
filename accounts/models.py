from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

import uuid
from .manager import UserManager

PHONE_VALIDATOR = RegexValidator(
    regex=r'^09\d{9}$',
    message=_('شماره موبایل باید با 09 شروع شده و ۱۱ رقم باشد.'),
)


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'))
    phone = models.CharField(max_length=11, unique=True,validators=[PHONE_VALIDATOR], verbose_name=_('موبایل'))
    is_superuser = models.BooleanField(default=False, verbose_name='مدیر')
    is_admin = models.BooleanField(default=False, verbose_name='ادمین')
    is_staff = models.BooleanField(default=False, verbose_name='کارمند')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    is_online = models.BooleanField(default=False, verbose_name=_('آنلاین'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ بروزرسانی'))

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    # fields required for admin
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'is_verified']),
        ]
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربر ها')

    def __str__(self):
        return self.phone

    @property
    def full_name(self):
        profile = getattr(self, 'profile', None)
        if profile and profile.first_name:
            return profile.first_name + (
                ' ' + profile.last_name if profile.last_name else ''
            )
        return self.phone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('کاربر'))
    first_name = models.CharField(max_length=50, blank=True, verbose_name=_('نام'))
    last_name = models.CharField(max_length=50, blank=True, verbose_name=_('نام خانوادگی'))
    image = models.ImageField(upload_to='profile/%Y/%m/%d/', null=True, blank=True, verbose_name=_('تصویر'))
    email = models.EmailField(max_length=100, null=True, blank=True, unique=True, verbose_name=_('ایمیل'))

    def __str__(self):
        return self.user.phone

    class Meta:
        verbose_name = _('پروفایل')
        verbose_name_plural = _('پروفایل ها')

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        super().save(*args, **kwargs)


class OTP(models.Model):
    username = models.CharField(max_length=50, verbose_name='نام کاربری')
    code = models.CharField(max_length=255, verbose_name='کد')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    expires_at = models.DateTimeField(verbose_name='تاریخ انقضا')
    is_used = models.BooleanField(default=False, verbose_name='استفاده شده')

    class Meta:
        verbose_name = _('کد یک‌بار مصرف')
        verbose_name_plural = _('کدهای یک‌بار مصرف')
        indexes = [
            models.Index(fields=['username', 'is_used', 'expires_at']),
        ]
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.username} - {self.code}"

    def is_expired(self):
        if self.expires_at >= now():
            return False
        return True
