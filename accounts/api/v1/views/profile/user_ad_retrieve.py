from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ...serializers import UserAdRetrieveSerializer
from utils.permissions import IsAdOwner
from ad.models import Ad

from drf_yasg.utils import swagger_auto_schema


class UserAdRetrieveApiView(generics.RetrieveAPIView):
    serializer_class = UserAdRetrieveSerializer
    permission_classes = [IsAdOwner]
    http_method_names = ['get', 'put', 'delete', 'head', 'options']

    def get_object(self):
        try:
            obj = get_object_or_404(Ad, uuid=self.kwargs['uuid'], user_id=self.request.user.id)
            return obj
        except Http404:
            raise Http404

    @swagger_auto_schema(
        operation_summary='User Ad detail',
        operation_description=(
                '''
                User Ads detail \n
                '''
                'endpoint: /account/api/v1/user-ads/{ad_uuid}/'
        ), tags=['Profile']
    )
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = UserAdRetrieveSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # @swagger_auto_schema(
    #     operation_summary='User Ad update',
    #     operation_description=(
    #             '''
    #             User Ads detail \n
    #             '''
    #             'endpoint: /account/api/v1/user-ads/{ad_uuid}/'
    #     ), tags=['Profile']
    # )
    # def put(self, request, ad_uuid, *args, **kwargs):
    #     obj = self.get_object()
    #     serializer = UserAdRetrieveSerializer(obj, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # @swagger_auto_schema(
    #     operation_summary='User Ad delete',
    #     operation_description=(
    #             '''
    #             User Ad delete \n
    #             '''
    #             'endpoint: /account/api/v1/user-ads/{ad_uuid}/'
    #     ), tags=['Profile']
    # )
    # def delete(self, request, *args, **kwargs):
    #     obj = self.get_object()
    #     obj.delete()
    #
    #     return Response(data={'detail': 'آکهی پاک شد'}, status=status.HTTP_204_NO_CONTENT)
