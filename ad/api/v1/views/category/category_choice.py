from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ...serializers import CategoryChoiceSerializer
from .....models import Category

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class CategoryChoiceAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategoryChoiceSerializer

    def get_queryset(self):
        # فقط برای امنیت — ولی عملاً از queryset در build_tree استفاده نمی‌کنیم
        return Category.objects.none()

    @swagger_auto_schema(
        operation_summary='List of all categories with children',
        tags=['Category']
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        categories = Category.objects.all().select_related('parent')
        tree = self.build_tree(categories)
        serializer = self.get_serializer(tree, many=True, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def build_tree(self, categories, request=None):
        """
        دسته‌ها رو درختی می‌سازه بدون Query اضافی
        """
        category_map = {}

        for c in categories:
            # ساخت آدرس کامل برای آیکون
            icon_url = None
            if c.icon:
                if request:
                    icon_url = request.build_absolute_uri(c.icon.url)
                else:
                    icon_url = c.icon.url

            category_map[c.id] = {
                'id': c.id,
                'title': c.title,
                'slug': c.slug,
                'icon': icon_url,  # اضافه شدن آیکون
                'is_payable': c.is_payable,
                'is_special': c.is_special,  # اضافه شدن فیلد اختصاصی که در سریالایزر هست
                'children': []
            }

        roots = []
        for cat in categories:
            if cat.parent_id:
                parent = category_map.get(cat.parent_id)
                if parent:
                    parent['children'].append(category_map[cat.id])
            else:
                # این شرط باید دقیقا معادل نبودن parent_id باشد
                roots.append(category_map[cat.id])

        return roots
