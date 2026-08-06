from django.shortcuts import get_object_or_404
from django.db.models import F
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema

from ...serializers import AdDetailSerializer
from ad.models import Ad, AdViews


class AdRetrieveAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AdDetailSerializer
    lookup_field = 'uuid'  # مشخص کردن فیلد جستجو برای DRF

    def get_queryset(self):
        # اضافه کردن روابط پرکاربرد جهت جلوگیری از کوئری‌های تکراری در سریالایزر
        return Ad.objects.filter(status=Ad.Status.PUBLISHED).select_related(
            'category', 'province', 'city', 'neighborhood', 'user'
        )

    @swagger_auto_schema(
        operation_summary='Ad detail',
        operation_description=(
                '''
                Ad detail \n
                '''
                'endpoint: /ad/api/v1/ads/{ad_uuid}/'
        ), tags=['Ad']
    )
    def get(self, request, uuid):
        # ۱. دریافت آگهی با استفاده از queryset بهینه شده (در صورت نبودن خطای 404 استاندارد بازمی‌گردد)
        ad = get_object_or_404(self.get_queryset(), uuid=uuid)

        # ۲. ثبت بازدید آگهی به صورت بهینه
        self._record_view(request, ad)

        # ۳. سریالایز کردن داده‌ها
        serializer = self.get_serializer(ad, context={'request': request, 'user': request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _record_view(self, request, ad):
        """
        متد کمکی برای استخراج IP، User-Agent و ثبت بازدید به صورت بهینه
        """
        # استخراج IP کلاینت
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        user_agent = request.headers.get('User-Agent', '')[:255] # محدود کردن طول برای دیتابیس

        # استفاده از get_or_create برای جلوگیری از مسابقه (Race Condition) و بهینه‌سازی
        created = AdViews.objects.get_or_create(
            ip=ip,
            user_agent=user_agent,
            ad_id=ad.id
        )[1] # اندیس ۱ مقدار Boolean ایجاد شدن را برمی‌گرداند

        if created:
            # استفاده از F() برای افزایش امن و همزمان تعداد بازدید بدون نیاز به ذخیره کامل مدل
            Ad.objects.filter(id=ad.id).update(views_count=F('views_count') + 1)
            # بروزرسانی مقدار در حافظه برای نمایش درست در خروجی سریالایزر فعلی
            ad.views_count += 1