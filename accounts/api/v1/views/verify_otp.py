from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from ..serializers import VerifyOTPSerializer
from ....models import OTP

User = get_user_model()



from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='Login/Register',
        operation_description=(
                '''
                Verify OTP and login/register user
                '''
                'endpoint: /account/api/v1/auth/verify-otp/\n\n'
                '''
                Example:\n
                    {
                        "phone": char 6 digit,
                        "code": code
                    }    
                '''
        ), tags=['Authentication']
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        try:
            with transaction.atomic():
                otp = OTP.objects.select_for_update().filter(
                    phone=phone,
                    code=code,
                    is_used=False
                ).latest('id')

                if otp.expires_at < now():
                    return Response(
                        {'success': False, 'message': 'کد منقضی شده'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                otp.is_used = True
                otp.save()

        except OTP.DoesNotExist:
            return Response(
                {'success': False, 'message': 'کد اشتباه است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, created = User.objects.get_or_create(phone=phone)

        if not user.is_verified:
            user.is_verified = True
            user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'success': True,
                'message': 'تایید موفق' if created else 'ورود موفق',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id
                    # 'phone': user.phone,
                    # 'first_name': user.profile.phone,
                    # 'last_name': user.profile.phone
                }
            },
            status=status.HTTP_200_OK
        )
