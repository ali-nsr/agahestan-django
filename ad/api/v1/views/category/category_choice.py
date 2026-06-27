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
        serializer = self.get_serializer(tree, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def build_tree(self, categories):
        """
        دسته‌ها رو درختی می‌سازه بدون Query اضافی
        """
        category_map = {c.id: {"id": c.id, "title": c.title, "slug": c.slug, "is_payable": c.is_payable, "children": []}
                        for c in categories}

        roots = []
        for cat in categories:
            if cat.parent_id:
                parent = category_map.get(cat.parent_id)
                if parent:
                    parent["children"].append(category_map[cat.id])
            else:
                roots.append(category_map[cat.id])
        return roots
