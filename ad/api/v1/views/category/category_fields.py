from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from ...serializers import CategoryFieldSerializer
from .....models import CategoryField

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class CategoryFieldsAPIView(views.APIView):
    permission_classes = [AllowAny]

    category_slug_param = openapi.Parameter(name='category_slug',
                                            in_=openapi.IN_QUERY,
                                            description='category slug: apartment-sale',
                                            type=openapi.TYPE_STRING,
                                            required=True,
                                            example='apartment-sale', )

    @swagger_auto_schema(
        operation_summary='Category fields',
        operation_description=(
                '''
                Each category has (or may not) a few fields like this:
                [
                    {
                        "id": 5,
                        "key": "apartment-sale-rooms",
                        "label": "تعداد اتاق",
                        "type": "choice",
                        "is_required": true,
                        "data": {
                                    "options": [
                                                "۱",
                                                "۲",
                                                "۳",
                                                "۴",
                                                "۵+"
                                                ]
                                },
                        "category": 19
                    },
                    {
                        "id": 6,
                        "key": "apartment-sale-year-built",
                        "label": "سال ساخت",
                        "type": "int",
                        "is_required": false,
                        "data": {
                                    "max": 1600,
                                    "min": 1300
                                },
                        "category": 19
                    },
                    {
                        "id": 7,
                        "key": "apartment-sale-floor",
                        "label": "طبقه",
                        "type": "int",
                        "is_required": false,
                        "data": {
                                    "max": 200,
                                    "min": -2
                                },
                        "category": 19
                    }
                ]
                this fields use for creating ads, updating ads and filters
                '''
                'endpoint: /ad/api/v1/category/{category_slug}/fields/'
                'Examples:\n'
                '- /ad/api/v1/category/apartment-sale/fields/\n'
        ),
        manual_parameters=[category_slug_param], tags=['Category']
    )
    def get(self, request, category_slug, *args, **kwargs):
        qs = CategoryField.objects.filter(category__slug=category_slug)
        serializer = CategoryFieldSerializer(qs, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
