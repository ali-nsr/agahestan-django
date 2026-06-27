from rest_framework import generics
from rest_framework.response import Response

from ...serializers import UserAdListSerializer
from utils.paginations import DefaultPagination
from utils.permissions import IsAdOwner
from ad.models import Ad, AdAttribute


from drf_yasg.utils import swagger_auto_schema

class UserAdListAPIView(generics.GenericAPIView):

    permission_classes = [IsAdOwner]
    serializer_class = UserAdListSerializer

    def get_queryset(self):
        request = self.request
        qs = Ad.objects.filter(user_id=request.user.id).select_related('category', 'province', 'city', 'neighborhood')
        return qs

    @swagger_auto_schema(
        operation_summary='User Ads list',
        operation_description=(
                '''
                User Ads list \n
                '''
                'endpoint: /account/api/v1/user-ads/'
        ), tags=['Profile']
    )
    def get(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)

        return Response(data=serializer.data)
