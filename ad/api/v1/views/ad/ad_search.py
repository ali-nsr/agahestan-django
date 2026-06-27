from django.db.models import Q

from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from ...serializers import AdListSerializer,CategorySuggestionSerializer
from ad.models import Ad,Category

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


import functools
import operator


class AdSearchGetAPIView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='Search list',
        operation_description=(
                'Examples:\n'
                '- /ad/api/v1/search/?q=query'

        ), tags=['Ad']
    )
    def get(self, request, *args, **kwargs):
        name = request.query_params.get('q')
        qs = Ad.objects.filter(Q(title__icontains=name))
        serializer = AdListSerializer(qs, many=True)
        return Response(serializer.data)

class AdSearchAjaxAPIView(views.APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='Ajax search list',
        operation_description=(
                'Examples:\n'
                '- /ad/api/v1/search-ajax/?q=query'

        ), tags=['Ad']
    )
    def get(self, request, *args, **kwargs):
        name = request.query_params.get('q').strip().split()

        q = functools.reduce(
            operator.or_,
            (Q(category_ads__title__icontains=word) for word in name),
        )
        # qs = Ad.objects.filter(Q(title__icontains=name))
        qs = Category.objects.filter(q)
        # qs = qs.filter(Q(ad__title__icontains=request.query_params.get('q').strip()))
        serializer = CategorySuggestionSerializer(qs, many=True,context={'name':request.query_params.get('q')})
        return Response(data=serializer.data)

