from django.shortcuts import get_object_or_404
from django.shortcuts import render

from ad.models import Ad


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

    return render(request, 'ad/ad_detail.html', {
        'ad': ad,
        'existing_chat': existing_chat,
    })