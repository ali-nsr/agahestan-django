from rest_framework.response import Response
from rest_framework import views
from django.shortcuts import get_object_or_404
from ad.models import AdReportReason, Ad,AdReport
from ...serializers.ad.ad_report import AdReportSerializer, AdReportReasonSerializer


class AdReportAPIView(views.APIView):
    serializer_class = AdReportSerializer


    def post(self, request,ad_id, *args, **kwargs):

        ad = get_object_or_404(Ad, id=ad_id)
        report = AdReport.objects.filter(ad_id=ad.id).first()
        if report:
            return Response(data={"detail":"درخواست تکراری"})

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class AdReportReasonsAPIView(views.APIView):
    serializer_class = AdReportReasonSerializer

    def get(self, request, *args, **kwargs):
        qs = AdReportReason.objects.all()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)
