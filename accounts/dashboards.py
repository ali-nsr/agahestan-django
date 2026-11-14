from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from ad.models import (
    Ad, Category, CategoryField, AdAttribute, Gallery
)
from location.models import Province, City, Neighborhood



def dashboard(request):
    return render(request, 'accounts/dashboard/index.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ad.models import Ad


@login_required
def user_ads(request):
    status_filter = request.GET.get('status', '')

    # همه آگهی‌های کاربر
    all_ads = Ad.objects.filter(user=request.user)

    # آمار
    stats = {
        'total': all_ads.count(),
        'published': all_ads.filter(status=Ad.Status.PUBLISHED).count(),
        'review': all_ads.filter(status=Ad.Status.REVIEW).count(),
        'rejected': all_ads.filter(status=Ad.Status.REJECTED).count(),
        'draft': all_ads.filter(status=Ad.Status.DRAFT).count(),
        'expired': all_ads.filter(status=Ad.Status.EXPIRED).count(),
    }

    # فیلتر
    ads = all_ads.select_related('category', 'province', 'city', 'neighborhood').order_by('-created_at')
    if status_filter:
        ads = ads.filter(status=status_filter)

    # Pagination
    paginator = Paginator(ads, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'accounts/dashboard/user_ads.html', {
        'ads': page_obj,
        'page_obj': page_obj,
        'stats': stats,
        'status_filter': status_filter,
    })

@login_required
@require_POST
def ad_delete(request, uuid):
    ad = get_object_or_404(Ad, uuid=uuid, user=request.user)
    ad.delete()
    return JsonResponse({'ok': True})