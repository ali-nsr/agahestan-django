from rest_framework import serializers

from ad.models import Ad, Gallery, AdAttribute, CategoryField, Category

from utils.mixins import PersianTimeMixin
from chat.models import AdChat
from social.models import Follow


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'image', 'is_main']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']


class CategoryFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryField
        fields = ['label']


class AdAttributeSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='category_field.label')
    value = serializers.CharField()

    class Meta:
        model = AdAttribute
        fields = ['label', 'value']

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep['catfield'] = CategoryFieldSerializer(instance.category_field.label).data
    #     return rep


class AdOwnerContactSerializer(serializers.Serializer):
    phone = serializers.CharField(default='aaa')

    # message = serializers.CharField()

    class Meta:
        model = Ad
        fields = ['phone']


from ...serializers.ad.ad_list import AdListSerializer


class AdDetailSerializer(PersianTimeMixin, serializers.ModelSerializer):
    ad_attributes = AdAttributeSerializer(many=True, read_only=True)
    gallery = GallerySerializer(many=True, allow_null=True, read_only=True)
    time = serializers.SerializerMethodField(method_name='get_time')
    full_address = serializers.ReadOnlyField(source='get_full_address')
    contact = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    related_ads = serializers.SerializerMethodField()
    has_chat = serializers.SerializerMethodField()
    is_ad_owner = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = ['id', 'uuid', 'title', 'description', 'latitude', 'longitude', 'time', 'price',
                  'full_address',
                  'ad_attributes', 'gallery', 'contact', 'seller', 'related_ads', 'has_chat','is_ad_owner']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['categories'] = CategorySerializer(instance.category).data
        return rep

    def get_time(self, obj):
        return self.persian_timesince(obj.created_at)

    # --- contact ---
    def get_contact(self, obj):
        return {
            "phone": obj.user.phone,
            "message": "ارسال پیام"
        }

    def get_seller(self, obj):
        user_followers = Follow.objects.filter(following_id=obj.user.id).count()
        user_followings = Follow.objects.filter(follower_id=obj.user.id).count()
        user_ads_count = Ad.objects.filter(user_id=obj.user.id).count()

        return {
            'id': obj.user.id,
            'name': obj.user.phone,
            'join_date': self.persian_timesince(obj.user.created_at),
            'avatar': obj.user.profile.image.url if obj.user.profile.image else None,
            'followers_count': user_followers,
            'followings_count': user_followings,
            'ads_count': user_ads_count
        }

    def get_related_ads(self, obj):
        qs = Ad.objects.get_related_ads(obj.category.id).exclude(id=obj.id)[:8]
        return AdListSerializer(qs, many=True).data

    def get_has_chat(self, obj):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return {
                'has_chat': False,
                'chat_uuid': None
            }

        user = request.user

        # کاربر صاحب آگهی است
        if obj.user_id == user.id:
            return {
                'has_chat': False,
                'chat_uuid': None
            }

        chat = AdChat.objects.filter(
            ad=obj,
            sender=user
        ).only('uuid').first()

        if chat:
            return {
                'has_chat': True,
                'chat_uuid': chat.uuid
            }

        return {
            'has_chat': False,
            'chat_uuid': None
        }

    def get_is_ad_owner(self, obj):
        request = self.context.get('request')
        if obj.user.id == request.user.id:
            return True
        return False
