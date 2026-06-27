from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from rest_framework import views
from rest_framework.response import Response
from datetime import timedelta
from django.utils.timezone import now

from drf_yasg.utils import swagger_auto_schema

from .....models import AdViews


class AdViewsChartAPIView(views.APIView):
    """
    دریافت تعداد بازدیدهای یک آگهی در بازه‌های مختلف زمانی.

    مسیر:
        GET /api/ads/<ad_id>/views/

    پارامترهای Query:
        range:
            - daily   (پیش‌فرض)
            - weekly
            - monthly

    خروجی:
        آرایه‌ای شامل تاریخ و تعداد بازدید:
        [
            { "date": "2025-02-01", "views": 14 },
            { "date": "2025-02-02", "views": 9 }
        ]

    کاربرد:
        مناسب برای نمودارهای فرانت‌اند (Line / Bar / Area Chart)
    """

    @swagger_auto_schema(
        operation_summary='Ad views chart',
        operation_description=(
                'endpoint: /ad/api/v1/ads/{ad_id}/views/'

                '''
                Exaample \n\n

                {
                 دریافت تعداد بازدیدهای یک آگهی در بازه‌های مختلف زمانی.

                مسیر:
                    GET ad/api/v1/ads/<ad_uuid>/views/
            
                پارامترهای Query:
                    range:
                        - daily   (پیش‌فرض)
                        - weekly
                        - monthly
            
                خروجی:
                    آرایه‌ای شامل تاریخ و تعداد بازدید:
                    [
                        { "date": "2025-02-01", "views": 14 },
                        { "date": "2025-02-02", "views": 9 }
                    ]
            
                کاربرد:
                مناسب برای نمودارهای فرانت‌اند (Line / Bar / Area Chart)
                '''
        ), tags=['Ad']
    )
    def get(self, request, ad_uuid):
        range_type = request.GET.get('range', 'daily')
        today = now()

        if range_type == 'daily':
            queryset = (
                AdViews.objects.filter(ad__uuid=ad_uuid)
                .annotate(date=TruncDay('created_at'))
                .values('created_at')
                .annotate(views=Count('id'))
                .order_by('created_at')
            )

        elif range_type == 'weekly':
            week_ago = today - timedelta(days=7)
            queryset = (
                AdViews.objects.filter(ad__uuid=ad_uuid, created_at__gte=week_ago)
                .annotate(date=TruncDay('created_at'))
                .values('created_at')
                .annotate(views=Count('id'))
                .order_by('created_at')
            )

        elif range_type == 'monthly':
            queryset = (
                AdViews.objects.filter(ad__uuid=ad_uuid)
                .annotate(date=TruncMonth('created_at'))
                .values('created_at')
                .annotate(views=Count('id'))
                .order_by('created_at')
            )

        else:
            return Response({'error': 'Invalid range'}, status=400)

        # خروجی نهایی
        data = [
            {
                'date': item['created_at'].strftime('%Y-%m-%d'),
                'views': item['views']
            }
            for item in queryset
        ]

        return Response(data)
