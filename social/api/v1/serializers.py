from rest_framework import serializers

from ...models import Follow

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


class SocialUserAdListSerializer(PersianTimeMixin, serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    social_data = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ['title', 'category', 'city', 'price', 'absolute_url', 'time', 'social_data']

    def get_absolute_url(self, obj):
        # url = 'http://127.0.0.1:8000/ad/api/v1/ads/{}/'.format(obj.id)
        url = 'https://django-main.liara.run/ad/api/v1/ads/{}/'.format(obj.id)
        return url

    def get_time(self, obj):
        res = datetime2jalali(obj.created_at).strftime('%y/%m/%d _ %H:%M:%S')
        return res

    def get_time(self, obj):
        return self.persian_timesince(obj.created_at)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['category'] = CategorySerializer(instance.category).data
        rep['city'] = AdCitySerializer(instance.city).data
        ad_images = instance.gallery.all()
        if ad_images:
            img = ad_images.filter(is_main=True).first()
            rep['thumbnail'] = GallerySerializer(img).data
        else:
            rep['thumbnail'] = 'https://django-main.liara.run/static/image/default.jpg'
            # rep['thumbnail'] = 'http://127.0.0.1:8000/static/image/default.jpg'
        return rep

    def get_social_data(self, obj):
        user_followers = Follow.objects.filter(following_id=obj.user.id).count()
        user_followings = Follow.objects.filter(follower_id=obj.user.id).count()
        user_ads_count = Ad.objects.filter(user_id=obj.user.id).count()

        return {
            'followers_count': user_followers,
            'followings_count':user_followings,
            'ads_count': user_ads_count
        }
