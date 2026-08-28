from _distutils_hack import override
from rest_framework import serializers

from ad.models import Category


class CategoryChoiceSerializer(serializers.ModelSerializer):
    children = serializers.ListField(child=serializers.DictField(), read_only=True)
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'icon', 'children', 'is_special', 'is_payable']


    # def to_representation(self, instance):
    #     rep = super(CategoryChoiceSerializer, self).to_representation(instance)
    #     rep['image'] = instance.icon.url if instance.icon else None
    #     return rep
    def get_icon(self, obj):
        # چون ورودی سریالایزر دیکشنری است، obj یک دیکشنری خواهد بود
        request = self.context.get('request', None)
        icon_url = obj.get('icon')
        if request:
            return request.build_absolute_uri(icon_url)
        return icon_url