# from rest_framework import serializers
#
# from django.contrib.auth import get_user_model
# from django.core.cache import cache
# from django.contrib.auth import login
#
# import random
#
#
# from ...models import Profile
# from ...tasks import send_verify_sms_async,send_forgot_password_sms_async
# from rest_framework import serializers
# from django.db import transaction
# from ad.models import Ad,AdAttribute,Gallery
# from ad.api.v1.serializers import GallerySerializer
#
# User = get_user_model()
#
#
#
#
# class RegisterSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(max_length=128, write_only=True)
#
#     class Meta:
#         model = User
#         fields = ['phone', 'password', 'confirm_password']
#
#     def validate(self, attrs):
#         if attrs['password'] != attrs['confirm_password']:
#             raise serializers.ValidationError({'password': 'رمز عبور با تایید رمز عبور مغایرت دارد'})
#         if User.objects.filter(phone=attrs['phone'], is_verified=True).exists():
#             raise serializers.ValidationError({'phone': 'کاربر وجود دارد'})
#         return super().validate(attrs)
#
#     # def create(self, validated_data):
#     #     validated_data.pop('confirm_password', None)
#     #     user = User.objects.create_user(**validated_data)
#     #     # send verification sms
#     #     otp = str(random.randint(1000, 9999))
#     #     cache.set(f'otp:{user.phone}', otp, timeout=60)
#     #
#     #     send_verify_sms_async(user_phone=user.phone, otp_code=otp)
#     #
#     #     return user
#
#
# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(required=True, max_length=128, write_only=True)
#     new_password = serializers.CharField(required=True, max_length=128, write_only=True)
#     confirm_new_password = serializers.CharField(required=True, max_length=128, write_only=True)
#
#     def validate(self, attrs):
#         new_password = attrs['new_password']
#         confirm_new_password = attrs['confirm_new_password']
#
#         if new_password != confirm_new_password:
#             raise serializers.ValidationError({'confirm new password': 'رمز عبور با تکرار رمز عبور یکی نیست'})
#
#         return super().validate(attrs)
#
#
#
#
# class VerifySerializer(serializers.Serializer):
#     user_otp = serializers.CharField(write_only=True)
#
#
#
# class ResendVerifyCodeSerializer(serializers.Serializer):
#     phone = serializers.CharField(write_only=True)
#
#     def validate(self, attrs):
#         user_otp = attrs['user_otp']
#
#         real_otp = cache.get(f'otp:{user_otp}')
#
#         if real_otp != user_otp:
#             serializers.ValidationError({'phone': 'کد یکبار مصرف اشتباه است'})
#
#         return super().validate(attrs)
#
#
# class ForgotPasswordSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=11, write_only=True)
#
#
#     def validate(self, attrs):
#         validated_date = super().validate(attrs)
#
#         phone = attrs['phone']
#         user = User.objects.filter(phone=phone)
#         if not user.exists():
#             raise serializers.ValidationError({'phone': 'کاربری یافت نشد'})
#
#         return validated_date
#
#
# class ResetPasswordSerializer(serializers.Serializer):
#     code = serializers.IntegerField(write_only=True)
#     new_password = serializers.CharField(max_length=255, write_only=True)
#     confirm_new_password = serializers.CharField(max_length=255, write_only=True)
#
#     def validate(self, attrs):
#         new_password = attrs['new_password']
#         confirm_new_password = attrs['confirm_new_password']
#
#
#         if new_password != confirm_new_password:
#             raise serializers.ValidationError({'confirm new password': 'رمز عبور با تکرار رمز عبور یکی نیست'})
#
#
#         return super().validate(attrs)
#
#
#
# # jwt serializer
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
#
#
# class CustomTokenObtainPairViewSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         validated_date = super().validate(attrs)
#         # if not self.user.is_verified:
#         #     raise serializers.ValidationError({'detail': 'user is not verified'})
#         validated_date['user_id'] = self.user.id
#         return validated_date
#
# # end jwt serializer
#
#
# # profile
#
#
# class AdListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ad
#         fields = '__all__'
#
# class AdDetailSerializer(serializers.ModelSerializer):
#     field_values = serializers.ReadOnlyField(source='get_field_values')
#
#     class Meta:
#         model = Ad
#         fields = ['title', 'category', 'city', 'created_at', 'field_values']
#
#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         qs = instance.gallery.all()
#         rep['gallery'] = GallerySerializer(qs, many=True).data
#         return rep
#
#
# class AdAttributeItemSerializer(serializers.Serializer):
#     category_field = serializers.IntegerField()
#     value = serializers.CharField(allow_blank=True)
#
# class AdAttributesSyncSerializer(serializers.Serializer):
#     """
#         Example:
#
#             {
#               "items": [
#                 {"category_field": 1, "value": "سند دارد"},
#                 {"category_field": 2, "value": "شخصی"},
#                 {"category_field": 3, "value": "دوخوابه"}
#               ]
#             }
#
#     """
#
#     items = AdAttributeItemSerializer(many=True)
#
#     def save(self, **kwargs):
#         ad = self.context['ad']
#         items = self.validated_data['items']
#
#         with transaction.atomic():
#             existing_qs = AdAttribute.objects.select_for_update().filter(ad=ad)
#             existing_by_cf = {e.category_field_id: e for e in existing_qs}
#
#             incoming_cf_ids = {i['category_field'] for i in items}
#             to_create, to_update, to_delete_ids = [], [], []
#
#             for item in items:
#                 cf_id = item['category_field']
#                 val = item['value']
#                 if cf_id in existing_by_cf:
#                     obj = existing_by_cf[cf_id]
#                     if obj.value != val:
#                         obj.value = val
#                         to_update.append(obj)
#                 else:
#                     to_create.append(
#                         AdAttribute(ad=ad, category_field_id=cf_id, value=val)
#                     )
#
#             for cf_id, obj in existing_by_cf.items():
#                 if cf_id not in incoming_cf_ids:
#                     to_delete_ids.append(obj.id)
#
#             if to_update:
#                 AdAttribute.objects.bulk_update(to_update, ['value'])
#             if to_create:
#                 AdAttribute.objects.bulk_create(to_create)
#             if to_delete_ids:
#                 AdAttribute.objects.filter(id__in=to_delete_ids).delete()
#
#         return {
#             'created': len(to_create),
#             'updated': len(to_update),
#             'deleted': len(to_delete_ids),
#         }
#
#
# class GalleryItemSerializer(serializers.Serializer):
#     id = serializers.IntegerField(required=False)
#     image = serializers.ImageField(required=False)
#     ordering = serializers.IntegerField(required=False, default=0)
#
# class GallerySyncSerializer(serializers.Serializer):
#     items = GalleryItemSerializer(many=True, required=False)
#
#     def save(self, **kwargs):
#         ad = self.context['ad']
#         items = self.validated_data.get('items', [])
#
#         with transaction.atomic():
#             existing_qs = Gallery.objects.select_for_update().filter(ad=ad)
#             existing_by_id = {g.id: g for g in existing_qs}
#
#             incoming_ids = {i['id'] for i in items if 'id' in i}
#             to_create, to_update, to_delete_ids = [], [], []
#
#             # ایجاد یا آپدیت
#             for item in items:
#                 img_id = item.get('id')
#                 if img_id and img_id in existing_by_id:
#                     g = existing_by_id[img_id]
#                     new_order = item.get('ordering', g.ordering)
#                     new_image = item.get('image')
#                     changed = False
#
#                     if g.ordering != new_order:
#                         g.ordering = new_order
#                         changed = True
#                     if new_image:
#                         g.image = new_image
#                         changed = True
#
#                     if changed:
#                         to_update.append(g)
#                 else:
#                     if 'image' in item:
#                         to_create.append(
#                             Gallery(ad=ad, image=item['image'], ordering=item.get('ordering', 0))
#                         )
#
#             # حذف مواردی که در payload نیستند
#             for gid, g in existing_by_id.items():
#                 if gid not in incoming_ids:
#                     to_delete_ids.append(gid)
#
#             if to_update:
#                 Gallery.objects.bulk_update(to_update, ['image', 'ordering'])
#             if to_create:
#                 Gallery.objects.bulk_create(to_create)
#             if to_delete_ids:
#                 Gallery.objects.filter(id__in=to_delete_ids).delete()
#
#         return {
#             'created': len(to_create),
#             'updated': len(to_update),
#             'deleted': len(to_delete_ids),
#         }