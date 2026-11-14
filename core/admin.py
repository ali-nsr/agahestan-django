from django.contrib import admin
from .models import SiteSetting, Page, FooterColumn, FooterLink, Slider


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    change_form_template = 'admin/change_form.html'
    fieldsets = (
        ('برندینگ', {
            'fields': ('logo', 'favicon', 'copyright_text',),
        }),
        ('اطلاعات سایت', {
            'fields': ('title', 'description',),
        }),
        ('اطلاعات تماس', {
            'fields': ('contact_phone', 'contact_email', 'contact_address', 'contact_working_hours'),
        }),
        ('سوشال مدیا', {
            'fields': ('social_instagram', 'social_telegram', 'social_linkedin',
                       'social_twitter', 'social_youtube', 'social_whatsapp'),
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description',),
        }),
        ('Technical SEO', {
            'fields': ('google_site_verification', 'google_analytics_id'),
        }),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    # change_form_template = 'admin/change_form.html'
    list_display = ('title', 'slug', 'is_published', 'show_in_menu', 'order', 'updated_at')
    list_filter = ('is_published', 'show_in_menu')
    search_fields = ('title', 'slug', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order', 'title')

    fieldsets = (
        ('صفحه', {
            'fields': ('title', 'slug', 'content')
        }),
        ('تنظیمات', {
            'fields': ('is_published', 'show_in_menu', 'order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
    )


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1
    fields = ('title', 'url', 'order', 'is_active', 'open_in_new_tab')
    ordering = ('order',)


@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    inlines = [FooterLinkInline]


from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'email', 'subject', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('fullname', 'email', 'subject', 'message')
    readonly_fields = ('fullname', 'email', 'subject', 'message',
                       'ip_address', 'created_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('فرستنده', {
            'fields': ('fullname', 'email', 'ip_address', 'created_at')
        }),
        ('پیام', {
            'fields': ('subject', 'message')
        }),
        ('وضعیت', {
            'fields': ('status',)
        }),
    )

    actions = ['mark_read', 'mark_replied', 'mark_archived']

    @admin.display(description="وضعیت")
    def status_badge(self, obj):
        colors = {
            'new': '#dc3545',
            'read': '#ffc107',
            'replied': '#28a745',
            'archived': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:4px;font-size:11px;">{}</span>',
            color,
            obj.get_status_display(),
        )


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    # list_display = ('title',)
    ...
