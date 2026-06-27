from django.contrib import admin

from .models import *


class MessageInline(admin.TabularInline):
    model = AdMessage
    extra = 0


@admin.register(AdChat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['ad', 'sender', 'uuid']
    inlines = [MessageInline]


@admin.register(AdMessage)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['get_text']

    def get_text(self, obj):
        return obj.text[:20]
