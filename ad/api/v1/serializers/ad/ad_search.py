from rest_framework import serializers

from ad.models import Category

class CategorySuggestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields=['id','title']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        name = self.context.get('name')
        # rep['link'] = f'http://127.0.0.1:8000/ad/api/v1/iran/{instance.slug}/'
        rep['link'] = f'https://django-main.liara.run//ad/api/v1/iran/{instance.slug}/'
        rep['ads_in_category_count'] = instance.category_ads.filter(title__icontains=name).count()
        return rep
