from rest_framework import serializers

from ad.models import Ad, Gallery
from jalali_date import datetime2jalali


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['image']


class UserAdListSerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ['id', 'uuid', 'title', 'category', 'price', 'absolute_url',
                  'created_date', 'address', 'status'
                  ]

    def get_status(self, obj):
        return obj.get_status_display()

    def get_absolute_url(self, obj):
        # url = 'http://127.0.0.1:8000/api/v1/ads/{}/detail/'.format(obj.id)
        url = 'https://django-main.liara.run/api/v1/ads/{}/detail/'.format(obj.uuid)
        return url

    def get_created_date(self, obj):
        res = datetime2jalali(obj.created_at).strftime('%y/%m/%d _ %H:%M:%S')
        return res

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        ad_images = instance.gallery.all()
        if ad_images:
            img = ad_images.filter(is_main=True).first()
            rep['thumbnail'] = GallerySerializer(img).data
        else:
            rep['thumbnail'] = 'https://django-main.liara.run/static/image/default.jpg'
            # rep['thumbnail'] = 'http://127.0.0.1:8000/static/image/default.jpg'
        return rep
