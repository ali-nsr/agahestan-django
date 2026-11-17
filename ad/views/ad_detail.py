from django.shortcuts import get_object_or_404
from django.shortcuts import render

from ad.models import Ad,AdViews


from chat.models import AdChat


def ad_detail(request, uuid):
    ad = get_object_or_404(
        Ad.objects
        .select_related('category', 'province', 'city', 'neighborhood', 'user')
        .prefetch_related('gallery', 'ad_attributes__category_field'),
        uuid=uuid,
    )

    # افزایش بازدید
    Ad.objects.filter(pk=ad.pk).update(views_count=ad.views_count + 1)

    # ═══ چت موجود بین کاربر و صاحب آگهی ═══
    existing_chat = None
    if request.user.is_authenticated and request.user.id != ad.user_id:
        existing_chat = AdChat.objects.filter(
            ad=ad, sender=request.user,
        ).first()

    # ═══ ثبت بازدید ═══
    if request.user.is_authenticated:
        AdViews.objects.create(ad=ad, user=request.user, ip=get_client_ip(request))
    else:
        # مهمان: با session_key
        if not request.session.session_key:
            request.session.create()
        AdViews.objects.create(
            ad=ad,
            session_key=request.session.session_key,
            ip=get_client_ip(request),
        )

    return render(request, 'ad/ad_detail.html', {
        'ad': ad,
        'existing_chat': existing_chat,
    })

def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')