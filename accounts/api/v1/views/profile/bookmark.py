from django.shortcuts import get_object_or_404

from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from accounts.models import Bookmark
from ad.models import Ad


class BookmarkApiView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='Add or remove Bookmark',
        operation_description=(
                '''
                User can add an ad to its bookmark
                '''
                'endpoint: /account/api/v1/add-or-remove-bookmark/{ad_id}/\n\n'
        ), tags=['Profile']
    )
    def post(self, request, ad_id, *args, **kwargs):
        if request.user.is_authenticated:
            ad = get_object_or_404(Ad, id=ad_id)
            bookmark = Bookmark.objects.filter(user_id=request.user.id, ad_id=ad.id).first()
            if bookmark:
                bookmark.delete()
                return Response(data={"detail": "آگهی حذف شد"}, status=status.HTTP_204_NO_CONTENT)
            else:
                Bookmark.objects.create(user_id=request.user.id, ad_id=ad.id)
                return Response(data={"detail": "آگهی نشان شد"}, status=status.HTTP_201_CREATED)
        else:
            return Response(data={'detail': 'ابتدا وارد حساب کاربری شوید'}, status=status.HTTP_400_BAD_REQUEST)
