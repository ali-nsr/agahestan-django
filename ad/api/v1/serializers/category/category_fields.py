from rest_framework import serializers

from ad.models import CategoryField


class CategoryFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryField
        fields = '__all__'
