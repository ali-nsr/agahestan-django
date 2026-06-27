from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ad.models import Ad, Category


class PayAdPrice(APIView):
    def get(self, request, ad_uuid, *args, **kwargs):
        ad = get_object_or_404(Ad, uuid=ad_uuid)
        return Response(data={
            'ad_title': ad.title,
            'ad_id': ad.id,
            'ad_uuid': ad.uuid,
            'is_paid': ad.is_paid,
            'price_to_pay':ad.category.price if ad.category.is_payable else 0
        })

    def post(self, request, ad_uuid, *args, **kwargs):
        ad = get_object_or_404(Ad, uuid=ad_uuid)
        return Response({'ad': ad})
