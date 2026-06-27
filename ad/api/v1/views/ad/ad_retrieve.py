from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema

from ...serializers import AdDetailSerializer
from ad.models import Ad, AdViews


class AdRetrieveAPIView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AdDetailSerializer

    @swagger_auto_schema(
        operation_summary='Ad detail',
        operation_description=(
                '''
                Ad detail \n
                '''
                'endpoint: /ad/api/v1/ads/{ad_uuid}/'
        ), tags=['Ad']
    )
    def get(self, request, uuid):
        try:
            ad = Ad.objects.get(uuid=uuid)
            serializer = self.serializer_class(ad, context={'request': request, 'user': request.user})

            # add views
            remote_addr = request.META.get('REMOTE_ADDR')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = remote_addr
            user_agent = request.headers.get('User-Agent')
            views = AdViews.objects.filter(ip=ip, user_agent__exact=user_agent, ad_id=ad.id)

            if not views.exists():
                AdViews.objects.create(ip=ip, user_agent=user_agent, ad_id=ad.id)
                ad.views_count += 1
                ad.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ad.DoesNotExist:
            return Response(data={'detail': 'آکهی یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
