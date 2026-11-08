from django import template

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