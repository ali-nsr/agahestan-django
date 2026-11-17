from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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
    class Purpose(models.TextChoices):
        LOGIN = 'login', _('ورود')
        REGISTER = 'register', _('ثبت نام')
        RESET = 'reset', _('بازیابی رمز')

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='otps', verbose_name=_('کاربر'),
    )
    phone = models.CharField(
        max_length=11, db_index=True, validators=[PHONE_VALIDATOR], verbose_name=_('موبایل'),
    )
    code = models.CharField(max_length=6, verbose_name=_('کد'))
    purpose = models.CharField(
        max_length=10, choices=Purpose.choices, default=Purpose.LOGIN,
        verbose_name=_('هدف'),
    )
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name=_('تلاش ها'))
    is_used = models.BooleanField(default=False, verbose_name=_('استفاده شده'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    expires_at = models.DateTimeField(verbose_name=_('تاریخ انقضا'))

    class Meta:
        verbose_name = _('کد یک‌بار مصرف')
        verbose_name_plural = _('کدهای یک‌بار مصرف')
        indexes = [
            models.Index(fields=['phone', 'is_used', 'expires_at']),
        ]
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.phone} - {self.purpose}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return (
            not self.is_used
            and not self.is_expired
            and self.attempts < 5
        )

class Bookmark(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_('کاربر'),
    )
    ad = models.ForeignKey(
        'ad.Ad', on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_('آگهی'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))

    class Meta:
        verbose_name = _('نشان شده')
        verbose_name_plural = _('نشان شده ها')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'ad'], name='unique_user_ad_bookmark',
            ),
        ]
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ad']),
        ]
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user_id} - {self.ad_id}'