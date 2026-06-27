from rest_framework import serializers

from ad.models import AdReport,AdReportReason



class AdReportReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdReportReason
        fields = '__all__'




class AdReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdReport
        fields = ['reason','ad','reporter','description']

