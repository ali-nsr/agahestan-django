from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import User, Profile, Bookmark, OTP
from .forms import UserCreateForm, UserChangeForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreateForm
    list_display = (
        'phone', 'uuid', 'is_superuser', 'is_verified', 'is_active', 'created_at', 'is_online',)
    list_filter = ('phone', 'is_active')
    fieldsets = (
        ('Infos', {'fields': ('phone', 'password', 'is_online',)}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_superuser',)}),
        ('Dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (
            None,
            {'fields': ('phone', 'password1', 'password2', 'is_active', 'is_verified', 'is_superuser',)}),
    )
    search_fields = ('phone',)
    ordering = ('-created_at',)
    readonly_fields = ('temp_code', 'password')
    filter_horizontal = ()


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', 'created_at', 'expires_at')


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Bookmark)
admin.site.unregister(Group)
