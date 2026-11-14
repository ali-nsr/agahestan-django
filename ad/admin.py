from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.db.models import Count

from .models import Ad, Gallery, AdAttribute, CategoryField

from .models import *


class CategoryFieldInline(admin.TabularInline):
    model = CategoryField
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'parent', 'is_payable', 'is_special', 'price')
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}  # ساخت خودکار اسلاگ از روی عنوان
    autocomplete_fields = ('parent',)  # جلوگیری از لود دراپ‌دان‌های بزرگ در دسته‌بندی‌های چند سطحی
    inlines = (CategoryFieldInline,)


from django_json_widget.widgets import JSONEditorWidget

@admin.register(CategoryField)
class CategoryFieldAdmin(admin.ModelAdmin):
    list_display = ('label', 'key', 'category', 'type', 'is_required')
    list_filter = ('type', 'is_required', 'category')
    search_fields = ('label', 'key')
    autocomplete_fields = ('category',)  # فعال‌سازی جستجو برای فیلدهای وابسته

    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(AdViews)
class AdViewsAdmin(admin.ModelAdmin):
    ...


@admin.register(AdReportReason)
class AdReportReasonAdmin(admin.ModelAdmin):
    ...


@admin.register(AdReport)
class AdReportAdmin(admin.ModelAdmin):
    ...


admin.site.register(AdAttribute)
admin.site.register(Gallery)


# ۱. نمایش گالری تصاویر به صورت اینلاین و افقی (TabularInline)
class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1
    fields = ('image', 'preview_image', 'is_main')
    readonly_fields = ('preview_image',)
    classes = ('collapse',)  # قابلیت جمع شدن بخش گالری برای شلوغ نشدن صفحه

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 80px; border-radius: 4px;" />', obj.image.url)
        return _("No Image")

    preview_image.short_description = _("Preview")


# ۲. نمایش ویژگی‌های پویا (Attributes) آگهی به صورت اینلاین
class AdAttributeInline(admin.TabularInline):
    model = AdAttribute
    extra = 0
    # بهینه‌سازی لود فیلد دسته بندی برای جلوگیری از کوئری‌های سنگین
    autocomplete_fields = ('category_field',)


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    # تنظیمات پایه‌ای نمایش لیست
    list_display = (
        'show_thumbnail',
        'title',
        # 'user_link',
        'category',
        'province',
        'city',
        'price_display',
        'status_badge',
        'is_paid',
        'views_count',
        'chats_count',
        'published_at_jalali'
    )

    list_display_links = ('show_thumbnail', 'title')

    # فیلترهای پیشرفته و کاربردی در سایدبار راست
    # list_filter = (
    #     'status',
    #     'is_paid',
    #     'is_negotiable',
    #     'province',
    #     'city',
    #     'category',
    #     'created_at'
    # )

    # جستجوی سریع روی فیلدهای متنی و شناسه
    search_fields = (
        'uuid',
        'title',
        'description',
        'address'
    )

    # بهبود سرعت لود صفحات با Autocomplete برای ارتباط‌های Many-to-One بزرگ
    autocomplete_fields = ('user', 'category', 'province', 'city', 'neighborhood')

    # اینلاین‌های متصل به آگهی
    inlines = [GalleryInline, AdAttributeInline]

    # فیلدهای غیرقابل ویرایش در صفحه جزئیات
    readonly_fields = (
        'uuid',
        'views_count',
        'chats_count',
        'created_at',
        'updated_at',
        'attributes_cache_display'
    )

    # دسته‌بندی فیلدها در صفحه جزئیات (Fieldsets) جهت تمیزی و خوانایی بهتر
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('uuid', 'user', 'title', 'description', 'category', 'status', 'thumbnail')
        }),
        (_('Location & Address'), {
            'fields': ('province', 'city', 'neighborhood', 'address', 'latitude', 'longitude'),
        }),
        (_('Pricing & Features'), {
            'fields': ('price', 'is_negotiable', 'is_paid'),
        }),
        (_('Timing'), {
            'fields': ('published_at', 'expires_at', 'bumped_at', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        (_('Metrics & Cache'), {
            'fields': ('views_count', 'chats_count', 'attributes_cache_display'),
            'classes': ('collapse',),
        }),
    )

    # ۳. بهینه‌سازی کوئری‌ها (N+1 Query) با استفاده از select_related
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'user',
            'category',
            'province',
            'city',
            'neighborhood'
        )

    # ۴. دکمه‌های عملیاتی ادمین (Admin Actions) جهت تغییر وضعیت گروهی آگهی‌ها
    actions = ['make_published', 'make_rejected', 'make_expired', 'bump_ads']

    @admin.action(description=_("Publish selected ads"))
    def make_published(self, request, queryset):
        queryset.update(status=Ad.Status.PUBLISHED, published_at=timezone.now())
        self.message_user(request, _("Selected ads successfully published."))

    @admin.action(description=_("Reject selected ads"))
    def make_rejected(self, request, queryset):
        queryset.update(status=Ad.Status.REJECTED)
        self.message_user(request, _("Selected ads marked as rejected."))

    @admin.action(description=_("Expire selected ads"))
    def make_expired(self, request, queryset):
        queryset.update(status=Ad.Status.EXPIRED)
        self.message_user(request, _("Selected ads marked as expired."))

    @admin.action(description=_("Bump selected ads"))
    def bump_ads(self, request, queryset):
        queryset.update(bumped_at=timezone.now())
        self.message_user(request, _("Selected ads bumped successfully."))

    # ۵. توابع سفارشی برای خروجی‌های خواناتر و زیباتر (HTML Badges)

    def show_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail.url)
        # بررسی تصاویر گالری در صورتی که Thumbnail اختصاصی نداشت
        main_gallery_image = obj.gallery.filter(is_main=True).first()
        if main_gallery_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                main_gallery_image.image.url)
        return _("No Image")

    show_thumbnail.short_description = _("Thumbnail")

    def status_badge(self, obj):
        # ساخت نشان‌گرهای رنگی زیبا بر اساس وضعیت آگهی
        colors = {
            Ad.Status.PUBLISHED: '#28a745',  # سبز
            Ad.Status.DRAFT: '#6c757d',  # خاکستری
            Ad.Status.REVIEW: '#ffc107',  # زرد
            Ad.Status.REJECTED: '#dc3545',  # قرمز
            Ad.Status.EXPIRED: '#343a40',  # مشکی/تیره
            Ad.Status.ARCHIVED: '#17a2b8',  # آبی آسمانی
            Ad.Status.WAIT_TO_PAY: '#fd7e14'  # نارنجی
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = _("Status")
    status_badge.admin_order_field = 'status'

    def price_display(self, obj):
        if obj.is_negotiable:
            return _("Negotiable")
        # فرمت قیمت به صورت سه رقم سه رقم به همراه تومان
        return f"{obj.price:,} {_('Dirham')}"

    price_display.short_description = _("Price")
    price_display.admin_order_field = 'price'

    # def user_link(self, obj):
    #     # ساخت لینک سریع به صفحه جزئیات کاربر در ادمین
    #     from django.urls import reverse
    #     url = reverse("admin:index", args=[obj.user.id])
    #     return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)

    # user_link.short_description = _("User")
    # user_link.admin_order_field = 'user'

    def published_at_jalali(self, obj):
        # استفاده از متد شمسی موجود در مدل شما
        return obj.api_ad_created_at()

    published_at_jalali.short_description = _("Published At")
    published_at_jalali.admin_order_field = 'published_at'

    def attributes_cache_display(self, obj):
        # نمایش ساختاریافته فیلد JSON جهت راحتی کارشناس پشتیبانی
        import json
        if obj.attributes_cache:
            return format_html('<pre>{}</pre>', json.dumps(obj.attributes_cache, indent=4, ensure_ascii=False))
        return "-"

    attributes_cache_display.short_description = _("Attributes Cache")
