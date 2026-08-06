from django.shortcuts import reverse
from rest_framework import serializers

from ad.models import Category

class CategorySuggestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields=['id','title']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        name = self.context.get('name')
        rep['ads_in_category_count'] = instance.category_ads.filter(title__icontains=name).count()
        rep['link'] = reverse('ad:api:ad-detail', kwargs={'slug':instance.slug})
        return rep
