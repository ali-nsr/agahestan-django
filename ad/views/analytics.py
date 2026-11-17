import json
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from ..models import Ad, AdViews


@login_required
def ad_analytics(request, ad_uuid):
    ad = get_object_or_404(Ad, uuid=ad_uuid, user=request.user)

    try:
        days = int(request.GET.get('days', 30))
    except (ValueError, TypeError):
        days = 30
    if days not in (7, 30, 90):
        days = 30

    today = timezone.now().date()
    start_date = today - timedelta(days=days - 1)

    base_qs = AdViews.objects.filter(ad=ad)

    # ═══ نمودار روزانه ═══
    daily = (
        base_qs
        .filter(created_at__date__gte=start_date)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    daily_map = {row['date']: row['count'] for row in daily}

    labels, data = [], []
    for i in range(days):
        d = start_date + timedelta(days=i)
        labels.append(d.strftime('%Y-%m-%d'))
        data.append(daily_map.get(d, 0))

    # ═══ بازدید یکتا ═══
    # کاربر لاگین → user_id
    # مهمان → session_key یا ip
    unique_total = (
        base_qs
        .values('user_id', 'session_key', 'ip')
        .distinct()
        .count()
    )

    # ═══ آمار کلی ═══
    total_views = base_qs.count()
    today_views = base_qs.filter(created_at__date=today).count()
    week_views = base_qs.filter(
        created_at__date__gte=today - timedelta(days=6)
    ).count()
    month_views = base_qs.filter(
        created_at__date__gte=today - timedelta(days=29)
    ).count()

    # ═══ آخرین بازدیدها (برای جدول پایین) ═══
    recent_views = (
        base_qs
        .select_related('user')
        .order_by('-created_at')[:10]
    )

    return render(request, 'ad/analytics.html', {
        'ad': ad,
        'labels_json': json.dumps(labels),
        'data_json': json.dumps(data),
        'total_views': total_views,
        'unique_total': unique_total,
        'today_views': today_views,
        'week_views': week_views,
        'month_views': month_views,
        'recent_views': recent_views,
        'days': days,
        'has_data': total_views > 0,
    })