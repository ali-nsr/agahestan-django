from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from ...serializers import AdUpdateSerializer
from ad.models import Ad
from utils.permissions import IsAdOwner


class AdUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAdOwner]
    serializer_class = AdUpdateSerializer
    http_method_names = ['put', 'head', 'options']

    def get_object(self):
        return get_object_or_404(Ad, pk=self.kwargs['pk'], user_id=self.request.user.id)

    @swagger_auto_schema(
        operation_summary='Ad update',
        operation_description=(
                '''
                Ad update \n
                '''
                'endpoint: /account/api/v1/user-ads/{ad_uuid}/'
        ), tags=['Ad']
    )
    def put(self, request, ad_uuid, *args, **kwargs):
        obj = self.get_object()
        serializer = AdUpdateSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
