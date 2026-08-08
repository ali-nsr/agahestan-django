from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ...serializers import AdListSerializer
from utils.paginations import DefaultPagination
from .....models import Ad, AdAttribute, Category

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class CategoryListAPIView(generics.GenericAPIView):
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
        required=True,
        example='tehran,shiraz',
    )
    category_slug_param = openapi.Parameter(name='category_slug',
                                            in_=openapi.IN_QUERY,
                                            description='category slug: apartment-sale',
                                            type=openapi.TYPE_STRING,
                                            required=True,
                                            example='apartment-sale', )

    @swagger_auto_schema(
        operation_summary='List ads by location/city',
        operation_description=(
                '''
                ads list by 2 location. first one is 'uae' and second one is 'city_name' like 'tehran'
                or multiple cities like 'tehran,shiraz'. multiple cities separated by comma and without space
                separator of cities param is '?city=tehran,shiraz'
                '''
                'Ads list by 2 location.\n\n'
                'Examples:\n'
                '- /ad/api/v1/{location}/{category}/\n'
                '- /ad/api/v1/{location}/{category}/?category_field_key=value&...\n'
        ),
        manual_parameters=[city_param, category_slug_param], tags=['Category']
    )
    def get(self, request, city, category_slug):
        category = get_object_or_404(Category, slug=category_slug)

        qs = self.get_queryset().filter(
            Q(category=category) | Q(category__parent=category) | Q(category__parent__parent=category) | Q(
                category__parent__parent__parent=category)
        )

        cid = request.query_params.get('cities', None)
        # cid = request.GET.get('cities', None)
        city = city.lower()

        if city == 'uae':
            if cid:
                qs = qs.filter(city__slug__in=cid.split(','))
            else:
                qs = qs.all()
        else:
            qs = qs.filter(city__slug=city)

        # فیلتر قیمت
        # order_by_price = request.query_params.get('order_by_price')
        # if order_by_price:
        #     qs = qs.filter(price__lte=order_by_price)

        # فیلتر داینامیک
        if request.query_params.items():
            for key, value in request.query_params.items():
                if key != 'page' and key != 'per_page' and key!='city':
                    print(f'filters: key: {key}, value: {value}')

                    ad_ids = AdAttribute.objects.filter(
                        category_field__key=key.strip(),
                        value__iexact=value.strip()
                    ).values_list('ad_id', flat=True)

                    qs = qs.filter(id__in=ad_ids)

        # اینجا پاجینیشن فعال میشه 👇
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(data=serializer.data)
