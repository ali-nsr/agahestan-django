from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.filter
def smart_time(dt):
    if not dt:
        return ''

    now = timezone.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return 'الان'
    if diff < timedelta(hours=1):
        return f'{int(diff.total_seconds() // 60)} دقیقه'
    if diff < timedelta(hours=24) and dt.date() == now.date():
        return dt.strftime('%H:%M')
    if dt.date() == (now - timedelta(days=1)).date():
        return 'دیروز'
    if diff < timedelta(days=7):
        days = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']
        return days[dt.weekday()]
    return dt.strftime('%Y/%m/%d')