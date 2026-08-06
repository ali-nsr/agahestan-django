from _distutils_hack import override
from rest_framework import serializers

from ad.models import Category


class CategoryChoiceSerializer(serializers.ModelSerializer):
    children = serializers.ListField(child=serializers.DictField(), read_only=True)

    # icon = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'icon', 'children', 'is_special', 'is_payable']

    # def get_icon(self, obj):
    #     request = self.context.get('request', None)
    #     if obj.icon:
    #         # در صورتی که شیء request در context وجود داشته باشد، آدرس کامل ساخته می‌شود
    #         if request is not None:
    #             return request
    #         # در غیر این صورت، مسیر نسبی رسانه برگردانده می‌شود
    #         return request
    #     return None
