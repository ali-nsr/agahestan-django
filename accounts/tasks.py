from celery import shared_task
from django.utils.timezone import timedelta, now
from .models import OTP

@shared_task(queue='celery:1', autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def send_verify_sms_async(user_phone, otp_code):
    print(f'phone: {user_phone} , otp code: {otp_code}')


@shared_task(queue='celery:1', autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def send_forgot_password_sms_async(user_phone, otp_code):
    print(f'phone: {user_phone} , otp code: {otp_code}')

@shared_task(queue='celery:1', autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def send_otp_sms_async(phone, code):
    OTP.objects.create(
        phone=phone,
        code=code,
        created_at=now(),
        expires_at=now() + timedelta(seconds=60),
    )
