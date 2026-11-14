from .models import Page, SiteSetting, FooterColumn


def site(request):
    """Make ShopSettings and menu pages available in every template."""
    setting = None
    if SiteSetting.objects.exists():
        setting = SiteSetting.objects.first()
    pages_menu = Page.objects.filter(is_published=True, show_in_menu=True).order_by('order', 'title')
    footer_column = FooterColumn.objects.filter(is_active=True).prefetch_related('links').order_by('order', 'title')
    return {
        'setting': setting,
        'pages_menu': pages_menu,
        'footer_column': footer_column,
    }
