from rest_framework import serializers

from ad.models import Category


class CategoryChoiceSerializer(serializers.ModelSerializer):
    children = serializers.ListField(child=serializers.DictField(), read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'icon', 'children', 'is_special', 'is_payable']
