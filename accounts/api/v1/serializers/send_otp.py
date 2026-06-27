from rest_framework import serializers


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, required=True, error_messages={
        'required': 'وارد کردن شماره موبایل الزامی است',
        'blank': 'شماره موبایل نمی‌تواند خالی باشد',
        'null': 'شماره موبایل نمی‌تواند خالی باشد',
        'max_length': 'شماره موبایل باید ۱۱ رقم باشد',
    })

    def validate_phone(self, value):
        request = self.context.get('request')

        if request.user.is_authenticated:
            raise serializers.ValidationError('کاربر لاگین است')

        if not value.startswith('09'):
            raise serializers.ValidationError('شماره موبایل معتبر نیست')

        return value
