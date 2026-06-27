from django.shortcuts import get_object_or_404
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied

from drf_yasg.utils import swagger_auto_schema

from ...serializers import Ad,GallerySerializer
from utils.permissions import IsAdOwner

class GalleryCreateView(views.APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary='Gallery create',
        operation_description=(
                '''
                Create or update ad gallery \n
                each image has 2 data, "image" and "is_main"\n
                "image" is the image file, type of "image" is file (multipart)\n
                "is_main" is the main image, type of "is_main" is bool\n
                NOTE: only 1 image has "is_main" with "true" value\n"
                Example:\n
                    data = {
                        'image': image file,
                        'is_main': bool
                    }
                '''
                'endpoint: /ad/api/v1/ads/{ad_id}/create-ad-gallery/'
        ), tags=['Ad']
    )
    def post(self, request, ad_id):
        ad = get_object_or_404(Ad, id=ad_id)

        # دریافت همه فایل‌ها
        images = request.FILES.getlist('image')

        created_ids = []

        if ad.user != request.user:
            raise PermissionDenied('شما مالک این آگهی نیستید')

        if images:
            for idx, img in enumerate(images):
                # برای هر عکس، کلید is_main مربوطه را بررسی می‌کنیم
                # Front-end می‌تواند بفرستد: is_main_0, is_main_1, is_main_2
                key = f'is_main_{idx}'
                is_main_value = request.data.get(key, 'false').lower() in ('true', '1')

                data = {
                    'image': img,
                    'is_main': is_main_value
                }

                serializer = GallerySerializer(data=data, context={'ad': ad})
                serializer.is_valid(raise_exception=True)
                gallery = serializer.save()
                created_ids.append(gallery.id)

            return Response(
                {
                    'success': True,
                    'message': 'گالری با موفقیت ثبت شد',
                    'data': {'ids': created_ids},
                    'ad_id': ad.id,
                    'ad_uuid': ad.uuid
                },
                status=201
            )
        else:
            pass