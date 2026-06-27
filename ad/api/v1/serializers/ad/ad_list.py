from rest_framework import serializers

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

    def get_absolute_url(self, obj):
        url = 'http://127.0.0.1:8000/ad/api/v1/ads/{}/'.format(obj.uuid)
        # url = 'https://django-main.liara.run/ad/api/v1/ads/{}/'.format(obj.uuid)
        return url

    def get_time(self, obj):
        return self.persian_timesince(obj.created_at)

    def to_representation(self, instance):
        rep = super(AdListSerializer, self).to_representation(instance)
        rep['category'] = CategorySerializer(instance.category).data
        rep['city'] = AdCitySerializer(instance.city).data

        if instance.thumbnail:
            # rep['thumbnail'] = 'http://127.0.0.1:8000'+instance.thumbnail.url
            rep['thumbnail'] = 'https://django-main.liara.run' + instance.thumbnail.url
        else:
            rep['thumbnail'] = 'https://django-main.liara.run/static/image/default.jpg'
            # rep['thumbnail'] = 'http://127.0.0.1:8000/static/image/default.jpg'
        return rep
