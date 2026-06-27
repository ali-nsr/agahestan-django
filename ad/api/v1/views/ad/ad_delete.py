from rest_framework.response import Response
from rest_framework import views

from drf_yasg.utils import swagger_auto_schema

from ad.models import Ad



class AdDeleteAPIView(views.APIView):

    @swagger_auto_schema(
        operation_summary='Ad delete',
        operation_description=(
                '''
                Ad delete \n
                '''
                'endpoint: /account/api/v1/user-ads/{ad_uuid}/'
        ), tags=['Ad']
    )
    def delete(self, request,ad_id, *args, **kwargs):
        ad = Ad.objects.get(id=ad_id)
        ad.delete()

        return Response(data={'detail':'آکهی پاک شد'},status=204)
