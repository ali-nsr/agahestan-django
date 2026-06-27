from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ...serializers import UserAdListSerializer
from utils.paginations import DefaultPagination
from utils.permissions import IsAdOwner
from ad.models import Ad, AdAttribute


from drf_yasg.utils import swagger_auto_schema

class UserBookmarksApiView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAdListSerializer

    @swagger_auto_schema(
        operation_summary='User bookmarks list',
        operation_description=(
                '''
                User can see bookmarks list \n
                '''
                'endpoint: /account/api/v1/user-bookmarks/'
        ), tags=['Profile']
    )
    def get(self, request):
        qs = Ad.objects.filter(bookmarks__user_id=request.user.id).select_related('category', 'province', 'city',
                                                                                  'neighborhood')

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
