from django.contrib import admin

from .models import *


class AdAttributeInline(admin.TabularInline):
    model = AdAttribute
    extra = 0
    readonly_fields = ['category_field', 'value']

class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 0

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title','uuid', 'category', 'province', 'city']
    search_fields = ['title', 'category__title']
    autocomplete_fields = ['user', 'category', 'province', 'city']
    # readonly_fields = ['user', 'category', 'province', 'city', 'neighborhood']
    inlines = [AdAttributeInline,GalleryInline]


class CategoryFieldInline(admin.TabularInline):
    model = CategoryField
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    search_fields = ['title']
    inlines = [CategoryFieldInline]


@admin.register(CategoryField)
class CategoryFieldAdmin(admin.ModelAdmin):
    search_fields = ['category__title']


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
