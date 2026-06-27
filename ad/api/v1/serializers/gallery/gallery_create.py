from django.db import transaction
from rest_framework import serializers

from ad.models import Ad, Gallery
from ad.tasks import update_ad_thumbnail_async

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['image', 'is_main']


    def create(self, validated_data):
        ad = self.context['ad']

        with transaction.atomic():
            gallery = Gallery.objects.create(ad=ad, **validated_data)

            return gallery
