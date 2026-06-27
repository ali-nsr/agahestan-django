from rest_framework.response import Response
from rest_framework import views
from rest_framework import generics

from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema

from ad.models import Gallery

from utils.permissions import IsAdOwner,IsGalleryOwner

class GalleryImageDeleteAPIView(views.APIView):
    # permission_classes = [IsGalleryOwner]

    @swagger_auto_schema(
        operation_summary='Gallery delete',
        operation_description=(
                '''
                Delete each ad gallery \n
                '''
                'endpoint: /ad/api/v1/ads/{gallery_id}/gallery-delete/'
        ), tags=['Ad']
    )
    def delete(self, request,gallery_id, *args, **kwargs):
        image = get_object_or_404(Gallery, id=gallery_id)
        if image.ad.user != request.user:
            return Response(data={'message': 'درخواست نامعتبر'}, status=400)

        image.delete()
        print('ok')
        return Response(data={'message':'فایل گالری پاک شد'},status=204)
