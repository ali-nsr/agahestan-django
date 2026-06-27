from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.core.cache import cache



# class UserNoDeleteQS(models.query.QuerySet):
#     def delete(self):
#         return self.filter(is_deleted=False)


class UserManager(BaseUserManager):
    # def get_queryset(self):
    #     return UserNoDeleteQS(self.model, using=self._db).filter(is_deleted=False)

    def create_user(self, phone, password):
        if not phone:
            raise ValueError('enter phone')
        user = self.model(phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password):
        user = self.create_user(phone, password)
        user.is_verified = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_user(self, user_id):
        from ad.models import Ad
        # from social.models import Follow

        cache_key = f'user:{user_id}'

        res = cache.get(cache_key)

        if res is not None:
            return res

        user = self.model.objects.get(id=user_id)

        data = {
            'id': user.id,
            'phone': user.phone,
            'email': user.profile.email if user.profile and user.profile.email else None,
            'image': user.profile.image.url if user.profile and user.profile.image else None,
            'full_name': user.full_name(),
            'ads_count': Ad.objects.filter(user_id=user.id).count(),
            # 'followers_count': Follow.objects.filter(following_id=user.id).all().count(),
            # 'following_count': Follow.objects.filter(follower_id=user.id).all().count(),
        }
        print(data)
        res = cache.set(cache_key, data, timeout=28800)
        return res