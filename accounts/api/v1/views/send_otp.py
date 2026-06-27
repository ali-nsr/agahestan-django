from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.timezone import now, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random

from ..serializers import SendOTPSerializer
from ....models import OTP
from django.contrib.auth import get_user_model
from ....tasks import send_otp_sms_async
from rest_framework.permissions import AllowAny

User = get_user_model()


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



class SendOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='Login/Register',
        operation_description=(
                '''
                get description of login page
                '''
        ), tags=['Authentication']
    )
    def get(self, request):
        data = {
            'title_1': 'ورود به حساب کاربری',
            'title_2': 'لطفا شماره همراه خود را وارد کنید',
            'description': 'برای ثبت آگهی رایگان ایتدا به حساب کاربری وارد شوید'
        }
        return Response(data=data)

    @swagger_auto_schema(
        operation_summary='Create an Ad depends on category',
        operation_description=(
                '''
                Send OTP to phone number
                after sending phone number to backend, if user get a verification code
                '''
                'endpoint: /account/api/v1/auth/send-otp/\n\n'
                'Example: \n\n'
                '''
                {
                    "phone": "char 11 digit"
                }
                '''
        ), tags=['Authentication']
    )
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']

        # ساخت یا گرفتن کاربر
        user, _ = User.objects.get_or_create(phone=phone)

        # محدودیت ارسال (مثلاً 60 ثانیه)
        otp = OTP.objects.filter(
            phone=phone,
            expires_at__gte=now() - timedelta(seconds=60)
        ).order_by('created_at')

        if otp.first():
            return Response(
                {
                    'detail': 'لطفاً کمی بعد دوباره تلاش کنید',
                    'code_expires_at': otp.first().expires_at.strftime('%H:%M:%S'),
                    'remaining_time': otp.first().expires_at - (now() - (otp.first().expires_at - otp.first().created_at)),
                    'remaining_time2': (now() - otp.first().expires_at),
                    'code': otp.first().code,
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        code = f'{random.randint(100000, 999999)}'

        send_otp_sms_async(phone, code)

        return Response(
            {
                'success': True,
                'message': 'کد تایید ارسال شد',
                'code': code
            },
            status=status.HTTP_200_OK
        )
