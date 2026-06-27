from django.shortcuts import get_object_or_404
from django.core.cache import cache

from rest_framework import generics
from rest_framework.permissions import AllowAny

from ...serializers import AdListSerializer
from utils.paginations import DefaultPagination
from .....models import Ad, AdAttribute
from location.models import City

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class AdListAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    pagination_class = DefaultPagination
    serializer_class = AdListSerializer

    def get_queryset(self):
        return Ad.objects.filter(status=Ad.Status.PUBLISHED).select_related('category', 'province', 'city',
                                                                            'neighborhood').order_by('-id')

    city_param = openapi.Parameter(
        name='city',
        in_=openapi.IN_QUERY,
        description='Comma-separated cities بدون فاصله. مثال: tehran,shiraz',
        type=openapi.TYPE_STRING,
        required=False,
        example='tehran,shiraz',
    )

    @swagger_auto_schema(
        operation_summary='List ads by location/city/cities',
        operation_description=(
                '''
                ads list by 2 location. first one is 'iran' and second one is 'city_name' like 'tehran'
                or multiple cities like 'tehran,shiraz'. multiple cities separated by comma and without space
                separator of cities param is '?city=tehran,shiraz'
                '''
                'Ads list by 2 location.\n\n'
                'Examples:\n'
                '- /ad/api/v1/iran/ads/\n'
                '- /ad/api/v1/tehran/ads/\n'
                '- /ad/api/v1/iran/ads/?cities=tehran,shiraz\n'
        ),
        manual_parameters=[city_param],tags=['Ad']
    )
    def get(self, request, city):
        qs = self.get_queryset()
        cid = request.GET.get('cities')

        if city == 'iran':
            if cid:
                qs = qs.filter(city__slug__in=cid.split(','))
            else:
                qs = qs.all()
        else:
            search_city = get_object_or_404(City, slug=city)
            qs = qs.filter(city__slug=search_city.slug)

            # فیلتر قیمت
        order_by_price = request.query_params.get('order_by_price')
        if order_by_price:
            qs = qs.filter(price__lte=order_by_price)

        # اینجا پاجینیشن فعال میشه 👇
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)
