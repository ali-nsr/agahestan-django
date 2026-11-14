from django.db import models
from django.urls import reverse


# from ckeditor_uploader.fields import RichTextUploadingField


# ============================================================
#  SHOP SETTINGS (Singleton — one row only)
# ============================================================
class SiteSetting(models.Model):
    # --- 1. Basic Shop Information ---
    title = models.CharField(
        max_length=50,
        verbose_name='عنوان سایت'
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات سایت'
    )

    # --- 2. Logo & Favicon ---
    logo = models.ImageField(
        upload_to='shop/logos/',
        blank=True,
        null=True,
        verbose_name='لوگو'
    )
    logo_alt = models.CharField(max_length=100, blank=True, null=True, verbose_name='متن جایگزین لوگو')
    favicon = models.ImageField(
        upload_to='shop/favicons/',
        blank=True,
        null=True,
        verbose_name='آیکون مرورگر'
    )

    # --- 3. Contact Information ---
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='شماره'
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name='ایمیل'
    )
    contact_address = models.TextField(
        blank=True,
        verbose_name='آدرس'
    )
    contact_working_hours = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='ساعت کاری',
    )

    # --- 4. Social Media ---
    social_instagram = models.URLField(
        blank=True,
        verbose_name='لینک اینستاگرام'
    )
    social_telegram = models.URLField(
        blank=True,
        verbose_name='لینک تلگرام'
    )
    social_linkedin = models.URLField(
        blank=True,
        verbose_name='لینک لینکدین'
    )
    social_twitter = models.URLField(
        blank=True,
        verbose_name='لینک تویتر'
    )
    social_youtube = models.URLField(
        blank=True,
        verbose_name='لینک یوتیوب'
    )
    social_whatsapp = models.URLField(
        blank=True,
        verbose_name='لینک واتساپ'
    )

    # --- 6. SEO Metadata ---
    meta_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='عنوان متا'
    )
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        verbose_name='توضیحات متا'
    )

    # --- 7. Technical SEO ---
    google_site_verification = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Google Verification Code'
    )
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='Google Analytics ID (e.g. G-XXXXXXXXXX).',
        verbose_name='Google Analytics ID'
    )

    # --- 8. Display Settings ---

    copyright_text = models.CharField(
        max_length=255,
        verbose_name='Copyright متن'
    )

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'

    def __str__(self):
        return self.title or 'تنظیمات سایت'


# ============================================================
#  PAGE (About Us, Contact, FAQ, ...)
# ============================================================
class Page(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='عنوان صفحه'
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='اسلاگ'
    )
    content = models.TextField(
        blank=True,
        verbose_name='محتوا'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='انتشار'
    )
    show_in_menu = models.BooleanField(
        default=True,
        verbose_name='نمایش در منوی اصلی'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب نمایش'
    )

    # --- SEO ---
    meta_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='عنوان متا'
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name='توضیحات متا'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )

    class Meta:
        verbose_name = 'صفحه'
        verbose_name_plural = 'صفحه ها'
        ordering = ('order', 'title')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:page', kwargs={'slug': self.slug})

    def get_meta_title(self):
        return self.meta_title or self.title

    def get_meta_description(self):
        return self.meta_description or self.content[:160]


class FooterColumn(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name='عنوان'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب نمایش'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )

    class Meta:
        verbose_name = 'ستون فوتر'
        verbose_name_plural = 'ستون های فوتر'
        ordering = ('order', 'title')

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    column = models.ForeignKey(
        FooterColumn,
        on_delete=models.CASCADE,
        related_name='links',
        verbose_name='ستون'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='عنوان'
    )
    url = models.URLField(
        max_length=255,
        blank=True,
        verbose_name='آدرس URL'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب نمایش'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    open_in_new_tab = models.BooleanField(
        default=False,
        verbose_name='باز شدن در تب جدید'
    )

    class Meta:
        verbose_name = 'لینک فوتر'
        verbose_name_plural = 'لینک های فوتر'
        ordering = ('order', 'title')

    def __str__(self):
        return self.title


# Contact Us Model
class ContactMessage(models.Model):
    '''
    Messages submitted through the contact form.
    '''
    STATUS_CHOICES = (
        ('new', 'جدید'),
        ('read', 'خوانده شده'),
        ('replied', 'پاسخ داده شده'),
        ('archived', 'آرشیو'),
    )

    fullname = models.CharField(
        max_length=100,
        verbose_name='نام و نام خانوادگی',
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='شماره'
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name='ایمیل'
    )
    subject = models.CharField(
        max_length=200,
        verbose_name='عنوان'
    )
    message = models.TextField(
        verbose_name='پیام'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='وضعیت'
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='آدرس IP'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )

    class Meta:
        verbose_name = 'تماس با ما'
        verbose_name_plural = 'تماس با ما'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.fullname} — {self.subject}'

class SliderManager(models.Manager):
    def get_main_image(self):
        qs = self.filter(type='main', is_active=True)
        return qs

    def get_banners(self):
        qs = self.filter(type='banner', is_active=True).order_by('id')[:2]
        return qs



class Slider(models.Model):
    TYPE_CHOICES = (
        ('main', 'تصویر اصلی'),
        ('banner', 'بنر'),
    )
    image = models.ImageField(upload_to='slider/%Y/%m/%d/', verbose_name='تصویر')
    link = models.URLField(null=True, blank=True, verbose_name='لینک')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='main', verbose_name='نوع')
    is_active = models.BooleanField(default=False, verbose_name='فعال')

    objects = SliderManager()

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'اسلایدر'
        verbose_name_plural = 'اسلایدر ها'
