from django.db import transaction
from rest_framework import serializers

from ad.models import Ad, AdAttribute, CategoryField


class AdAttributeSerializer(serializers.Serializer):
    category_field_id = serializers.IntegerField()
    value = serializers.JSONField()

class AdAttributeUpdateSerializer(serializers.Serializer):
    attributes = AdAttributeSerializer(many=True)

    def validate(self, attrs):
        for attr in attrs['attributes']:
            field = CategoryField.objects.get(id=attr['category_field_id'])

            if field.type == 'boolean' and not isinstance(attr['value'], bool):
                raise serializers.ValidationError("boolean expected")

            if field.type == 'multi' and not isinstance(attr['value'], list):
                raise serializers.ValidationError("list expected")

        return attrs

    def update(self, instance, validated_data):
        attrs = validated_data['attributes']
        print(attrs)
        if attrs:
            with transaction.atomic():
                # پاک‌سازی قبلی
                instance.ad_attributes.all().delete()

                # ثبت جدید
                for attr in attrs:
                    category_field = CategoryField.objects.filter(id=attr['category_field_id'])

                    if category_field.exists():
                        value = attr['value']
                        if isinstance(value, bool):
                            value = "دارد" if value else "ندارد"
                        elif isinstance(value, list):
                            value = ",".join(value)

                        AdAttribute.objects.create(
                            ad=instance,
                            category_field_id=attr['category_field_id'],
                            value=value
                        )
                    else:
                        raise serializers.ValidationError(
                            {'category_field_id': f'id {attr["category_field_id"]} is wrong'})
                return instance
        else:
            # raise serializers.ValidationError({'attributes': 'این فیلد مورد نیاز است'})
            pass