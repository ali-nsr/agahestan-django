from rest_framework import serializers

from ad.models import Ad

class AdUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = [
            "title", "description", "price","address", "is_negotiable"
        ]
