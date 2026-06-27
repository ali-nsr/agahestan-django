from rest_framework.response import Response
from rest_framework import status
from rest_framework import views
from rest_framework import generics

from ...models import Follow
from .serializers import SocialUserAdListSerializer
from ad.models import Ad
from utils.paginations import DefaultPagination

class FollowUserApiView(views.APIView):

    def post(self, request,user_id, *args, **kwargs):
        # check if user is same
        if int(request.user.id) == int(user_id):
            return Response(data={'detail': 'درخواست نامعتبر'}, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.filter(follower_id=request.user.id, following_id=user_id)
        if follow.exists():
            follow.delete()
            return Response(data={'detail': 'آنفالو انجام شد'}, status=status.HTTP_204_NO_CONTENT)
        else:
            Follow.objects.create(follower_id=request.user.id, following_id=user_id)
            return Response(data={'detail': 'فالو انجام شد'}, status=status.HTTP_201_CREATED)


class UserAdsApiView(generics.ListAPIView):
    serializer_class = SocialUserAdListSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        qs = Ad.objects.filter(user_id=user_id).select_related('category', 'province', 'city', 'neighborhood')
        return qs