from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from rest_framework import serializers

from datetime import timedelta

from ad.models import Ad, Category
from accounts.models import User


class AdCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ad
        fields = [
            "title", "description", "price",
            "province", "city", "neighborhood", "address",
            "latitude", "longitude", "is_negotiable",
        ]

    def create(self, validated_data):
        user_id = self.context["user_id"]
        category_slug = self.context["category_slug"]

        with transaction.atomic():
            category = get_object_or_404(Category, slug=category_slug)
            if Ad.objects.filter(user_id=user_id, status=Ad.Status.DRAFT).exists():
                raise serializers.ValidationError({"detail": "کاربر آگهی پیش‌نویس دارد"})
            else:
                ad = Ad.objects.create(
                    user_id=user_id,
                    category_id=category.id,
                    status=Ad.Status.WAIT_TO_PAY if category.is_payable else Ad.Status.REVIEW,  # همیشه ایجاد میشه به عنوان پیش‌نویس
                    expires_at=timezone.now() + timedelta(days=2),
                    **validated_data
                )

                return ad
