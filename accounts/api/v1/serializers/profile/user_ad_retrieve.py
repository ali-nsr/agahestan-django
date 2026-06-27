from django.db import transaction
from rest_framework import serializers

from ad.models import Ad, Gallery, AdAttribute, Category, AdViews
from location.models import City


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'image', 'is_main']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title', 'slug']


class UserAdRetrieveSerializer(serializers.ModelSerializer):
    attributes = serializers.ReadOnlyField(source='get_field_values')
    ad_price_status = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ['id', 'uuid', 'title', 'description', 'price', 'is_negotiable', 'address', 'created_at', 'attributes',
                  'views_count', 'ad_price_status']
        read_only_fields = ['created_at', 'views_count', 'uuid']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        qs = instance.gallery.all()
        rep['gallery'] = GallerySerializer(qs, many=True).data
        rep['city'] = CitySerializer(instance.city).data
        rep['category'] = CategorySerializer(instance.category).data
        return rep

    def get_ad_price_status(self, obj):
        return {
            'is_paid': obj.is_paid,
            'price_to_pay': obj.category.price if obj.category.is_payable else 0
        }

    def update(self, instance, validated_data):

        """
        Expected input:
        {
            "title": "test",
            "description": "test",
            "price": 1000,
            "province": 1,
            "city": 1,
            "latitude": 1,
            "longitude": 1,
            "attributes": [{"category_field_id":1, "value":200},
                           {"category_field_id":2, "value":2}],
            "images": []
        }
        """

        with transaction.atomic():
            attrs_data = validated_data.pop('attributes', [])
            images_data = validated_data.pop('images', [])

            # فیلدهای ساده را آپدیت می‌کنیم
            for key, value in validated_data.items():
                setattr(instance, key, value)
            instance.save()

            # --- Attributes ---
            # اول همه‌ی attr های قدیمی پاک بشه
            AdAttribute.objects.filter(ad=instance).delete()

            # دوباره همه attr های جدید ساخته بشن
            for attr in attrs_data:
                AdAttribute.objects.create(
                    ad=instance,
                    category_field_id=attr['category_field_id'],
                    value=attr['value']
                )

            # --- Images ---
            # اگر خواستی جایگزین کنی، این بخش را فعال می‌کنیم
            if images_data:
                Gallery.objects.filter(ad=instance).delete()
                for img in images_data:
                    Gallery.objects.create(ad=instance, **img)

            # ساختن attributes_cache مثل create
            attrs_data_clean = []
            attrs = AdAttribute.objects.filter(ad=instance)

            for attr in attrs:
                attrs_data_clean.append({
                    "label": attr.category_field.label,
                    "value": attr.value
                })

            instance.attributes_cache = attrs_data_clean
            instance.save()

            return instance
