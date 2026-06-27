from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser,FileUploadParser

from drf_yasg.utils import swagger_auto_schema

from ...serializers import AdAttributeUpdateSerializer
from .....models import Ad




class AdAttributeUpdateView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Ad attribute create/update',
        operation_description=(
                '''
                Create or update ad attributes \n
                '''
                'endpoint: /ad/api/v1/ads/{ad_id}/create-ad-attributes/'
                
                '''
                Exaample \n\n
                
                {
                "attributes": [
                        {
                            "category_field_id": 1,
                            "value": "yes"
                        },
                        {
                            "category_field_id": 2,
                            "value": "yes"
                        }
                    ]
                }
                '''
        ), tags=['Ad']
    )
    def put(self, request, ad_id):
        ad = get_object_or_404(Ad, id=ad_id, user=request.user)

        # category = ad.category
        # if ad.category.categoryfield_set.all():
        #     return Response({'category_field':'این آگهی به اتریبیوت نیاز دارد'})

        if ad.user != request.user:
            raise PermissionDenied('شما مالک این آگهی نیستید')

        serializer = AdAttributeUpdateSerializer(
            instance=ad,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ad = serializer.save()

        return Response(data={
            'status': True,
            'message': 'اتریبیوت ها آپدیت شد',
            'ad_id': ad.id,
            'ad_uuid': ad.uuid
        })