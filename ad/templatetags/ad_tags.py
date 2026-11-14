from django import template
from django.shortcuts import reverse

register = template.Library()


@register.filter
def split_comma(value):
    """مقادیر multi_choice رو به لیست تبدیل می‌کنه."""
    if not value:
        return []
    return [x.strip() for x in str(value).split(',') if x.strip()]


@register.filter
def attr_icon(field_type):
    icons = {
        'int': 'fa-ruler-combined',
        'decimal': 'fa-calculator',
        'bool': 'fa-check-circle',
        'str': 'fa-font',
        'text': 'fa-paragraph',
        'choice': 'fa-list-ul',
        'multi_choice': 'fa-layer-group',
    }
    return icons.get(field_type, 'fa-circle-info')


@register.filter
def attr_is_multiline(field_type):
    return field_type in ('multi_choice', 'text')

@register.simple_tag(takes_context=True)
def is_selected(context, key, value):
    request = context.get('request')
    if not request:
        return False
    return value in request.GET.getlist(key)

@register.filter
def get_item(dictionary, key):
    """دسترسی به مقدار dict از کلید در template."""
    if not dictionary:
        return ''
    return dictionary.get(key, '')