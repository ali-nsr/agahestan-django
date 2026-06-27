from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


from ...serializers import AdCreateSerializer


class AdCreateView(views.APIView):
    permission_classes = [IsAuthenticated]

    category_slug_param = openapi.Parameter(name='category_slug',
                                            in_=openapi.IN_QUERY,
                                            description='category slug: apartment-sale',
                                            type=openapi.TYPE_STRING,
                                            required=True,
                                            example='apartment-sale', )

    @swagger_auto_schema(
        operation_summary='Create an Ad depends on category',
        operation_description=(
                '''
                for creating an ad depends on a category first step is getting category fields.\n
                to get category fields you can request: /ad/api/v1/ads/{category}/fields/\n
                after getting category fields we render fields of attributes of ad.\n
                
                '''
                'endpoint: /ad/api/v1/ads/{category}/create-ad/\n\n'
                'Example: \n\n'
                '''
                {
                    "title": char (required),
                    "description": text (required),
                    "price": int (required),
                    "province": id int (required),
                    "city": id int (required),
                    "neighborhood": id int (not required),
                    "address": text (required),
                    "latitude": float (not required),
                    "longitude": float (not required),
                    "is_negotiable": bool
                }
                '''
        ),
        manual_parameters=[category_slug_param], tags=['Ad']
    )
    def post(self, request, category_slug):

        serializer = AdCreateSerializer(
            data=request.data,
            context={
                'user_id': request.user.id,
                'category_slug': category_slug,
            }
        )
        serializer.is_valid(raise_exception=True)
        ad = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'آگهی ساخته شد',
                'ad_id': ad.id,
                'ad_uuid':ad.uuid
            },
            status=201
        )
