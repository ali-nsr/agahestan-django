from rest_framework import serializers
from django.db import transaction

from ad.models import Ad, Gallery, AdAttribute



class AdUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = [
            "title", "description", "price", "is_negotiable"
        ]


# class AdAttributeSerializer(serializers.ModelSerializer):
#     label = serializers.ReadOnlyField(source='category_field.label')
#
#     class Meta:
#         model = AdAttribute
#         fields = ['category_field', 'label', 'value']
#
#
# class AdUpdateDestroySerializer(serializers.ModelSerializer):
#     ad_attributes = AdAttributeSerializer(many=True)
#
#     # gallery = GallerySerializer(many=True, allow_null=True)
#
#     class Meta:
#         model = Ad
#         fields = ['title', 'description', 'latitude', 'longitude', 'created_at', 'ad_attributes']
#
#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         # qs = instance.gallery.all()
#         # rep['gallery'] = GallerySerializer(qs, many=True).data
#         return rep
#
#     def update(self, instance, validated_data):
#         attrs_data = validated_data.pop("ad_attributes", [])
#         imgs_data = validated_data.pop("gallery", [])
#
#         instance.title = validated_data.get("title", instance.title)
#         instance.description = validated_data.get("description", instance.description)
#         instance.save()
#
#         # --- Update attributes ---
#         existing_attr_ids = [a.id for a in instance.ad_attributes.all()]
#         sent_attr_ids = [a.get("id") for a in attrs_data if a.get("id")]
#
#         # حذف attributeهایی که حذف شدن
#         for attr_id in existing_attr_ids:
#             if attr_id not in sent_attr_ids:
#                 AdAttribute.objects.filter(id=attr_id).delete()
#
#         # آپدیت یا ایجاد
#         for attr in attrs_data:
#             attr_id = attr.get("id")
#             if attr_id:
#                 AdAttribute.objects.filter(id=attr_id).update(**attr)
#             else:
#                 AdAttribute.objects.create(ad=instance, **attr)
#
#         # --- Update images به همین شکل ---
#         existing_img_ids = [i.id for i in instance.gallery.all()]
#         sent_img_ids = [i.get("id") for i in imgs_data if i.get("id")]
#
#         for img_id in existing_img_ids:
#             if img_id not in sent_img_ids:
#                 Gallery.objects.filter(id=img_id).delete()
#
#         for img in imgs_data:
#             img_id = img.get("id")
#             if img_id:
#                 Gallery.objects.filter(id=img_id).update(**img)
#             else:
#                 Gallery.objects.create(ad=instance, **img)
#
#         return instance
