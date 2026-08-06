from rest_framework import serializers
from django.urls import reverse

from ad.models import Ad, Category, Gallery
from location.models import City
from jalali_date import datetime2jalali, date2jalali
from utils.mixins import PersianTimeMixin


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']


class AdCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name']


class DateSerializer(serializers.Serializer):
    date = serializers.DateTimeField()


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['image']


class AdListSerializer(PersianTimeMixin, serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ['title', 'category', 'city', 'price', 'absolute_url', 'time']

    def get_host(self, obj):
        request = self.context.get('request')
        path = reverse('ad-detail', kwargs={'uuid': str(obj.uuid)})
        # مثال path: /ad/api/v1/ads/<uuid>/

        if request is None:
            # fallback: آدرس نسبی برگردون
            return path

        return request.build_absolute_uri(path)

    def get_absolute_url(self, obj):
        request = self.context.get('request')
        path = reverse('ad:api:ad-detail', kwargs={'uuid': str(obj.uuid)})

        return request.build_absolute_uri(path) if request else path

    def get_time(self, obj):
        return self.persian_timesince(obj.created_at)

    def to_representation(self, instance):
        rep = super(AdListSerializer, self).to_representation(instance)
        rep['category'] = CategorySerializer(instance.category).data
        rep['city'] = AdCitySerializer(instance.city).data

        request = self.context.get('request')

        if instance.thumbnail:
            url = instance.thumbnail.url
        else:
            url = '/static/image/default.jpg'

        rep['thumbnail'] = request.build_absolute_uri(url) if request else url
        return rep
