# jwt codes
from rest_framework.request import Request
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from rest_framework import serializers

from ....models import Profile
from accounts.models import User

# jwt serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class CustomTokenObtainPairViewSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        validated_date = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError({'detail': 'user is not verified'})
        validated_date['user_id'] = self.user.id
        validated_date['phone'] = self.user.phone
        validated_date['first_name'] = self.user.first_name
        validated_date['last_name'] = self.user.last_name
        return validated_date


# end jwt serializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairViewSerializer
    queryset = Profile.objects.all()

    @swagger_auto_schema(
        operation_summary='JWT create token',
        tags=['Authentication']
    )
    def post(self, request: Request, *args, **kwargs):
        pass


# views.py یا api/views.py
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.response import Response
from rest_framework import status


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    @swagger_auto_schema(
        operation_summary='JWT refresh token',
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {"error": "توکن نامعتبر است"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # دریافت توکن جدید
        access_token = serializer.validated_data['access']

        # استخراج اطلاعات از توکن
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(access_token)
        user_id = token['user_id']

        user = User.objects.get(id=user_id)
        # ساخت پاسخ سفارشی
        data = {
            'access': str(access_token),
            'user_id': user_id,
            'phone': user.phone,
            'first_name': user.profile.first_name,
            'last_name': user.profile.last_name,
            'message': 'توکن با موفقیت رفرش شد'
        }

        return Response(data, status=status.HTTP_200_OK)


class CustomTokenVerifyView(TokenVerifyView):

    @swagger_auto_schema(
        operation_summary='JWT verify token',
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        pass
