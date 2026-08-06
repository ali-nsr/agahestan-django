from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid
from .manager import UserManager


class User(AbstractBaseUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'))
    phone = models.CharField(max_length=11, unique=True, verbose_name=_('Phone'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('Is Superuser'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Is Verified'))
    temp_code = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Temp Code'))
    is_online = models.BooleanField(default=False, verbose_name=_('Is Online'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    # fields required for admin
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['uuid'])
        ]
        verbose_name = _('User')
        verbose_name_plural = _('Users')

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name=_('User'))
    first_name = models.CharField(max_length=250, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=250, verbose_name=_('Last Name'))
    image = models.ImageField(upload_to='profile/%Y/%m/%d/', verbose_name=_('Image'))
    email = models.EmailField(max_length=250, verbose_name=_('Email'))

    def __str__(self):
        return self.user.phone

    class Meta:
        db_table = 'profiles'
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


class OTP(models.Model):
    phone = models.CharField(max_length=11, verbose_name='Phone')
    code = models.CharField(max_length=6, verbose_name='Code')
    created_at = models.DateTimeField(verbose_name='Created At')
    expires_at = models.DateTimeField(verbose_name='Expires At')
    is_used = models.BooleanField(default=False, verbose_name='Is Used')

    def __str__(self):
        return f"{self.phone} - {self.code}"

    class Meta:
        db_table = 'otp'
        verbose_name = 'OTP'
        verbose_name_plural = 'OTP'


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_('User'))
    ad = models.ForeignKey('ad.Ad', on_delete=models.CASCADE, related_name='bookmarks', verbose_name=_('Ad'))

    def __str__(self):
        return f'{self.user.phone} - {self.ad}'

    class Meta:
        db_table = 'bookmarks'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'ad'],
                name='unique_user_ad_bookmark'
            )
        ]
        verbose_name = _('Bookmark')
        verbose_name_plural = _('Bookmarks')
