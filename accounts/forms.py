from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import authenticate

from .models import *


# this form is for adding user in admin panel
class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label='رمز عبور')
    password2 = forms.CharField(widget=forms.PasswordInput, label='تکرار رمز عبور')

    class Meta:
        model = User
        fields = ['phone']

    def clean_password2(self):
        data = self.cleaned_data
        if data['password2'] and data['password1'] and data['password2'] != data['password1']:
            raise forms.ValidationError('رمز عبور ها مغایرت دارند.')
        return data['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField

    class Meta:
        model = User
        fields = ['phone']

    def clean_password(self):
        return self.initial['password']


from django.core.validators import RegexValidator

# from services.utils import jalali_converter

# regex phone number
phone_number_validation = RegexValidator(
    regex=r'^[0][9]\d{9}$',
    message='لطفا یک شماره همراه معتبر وارد کنید.'
)


class RegisterForm(forms.Form):
    phone = forms.CharField(
        label='شماره همراه',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '*********09'
            }
        ),
        validators=[
            phone_number_validation
        ]
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'رمز عبور'
            }
        ),
        validators=[
            validators.MinLengthValidator(8)
        ]

    )
    confirm_password = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'تکرار رمز عبور'
            }
        ),
        validators=[
            validators.MinLengthValidator(8)
        ]
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(phone__exact=phone):
            raise forms.ValidationError('شماره وارد شده از قبل موجود است.')
        return phone

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise forms.ValidationError('کلمات عبور با هم مغایرت دارند. لطفا دوباره تلاش کنید.')
        return confirm_password


class LoginForm(forms.Form):
    phone = forms.CharField(
        label='شماره همراه',
        widget=forms.NumberInput(
            attrs={
                'id': 'emailContent',
                'class': 'form-control',
                'placeholder': 'شماره همراه',
                'style': 'direction: rtl'
            }
        ),
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(
            attrs={
                'id': 'passwordContent',
                'class': 'form-control',
                'placeholder': 'رمز عبور'
            }
        ),
    )

    def clean(self):
        phone = self.cleaned_data['phone']
        password = self.cleaned_data['password']
        if not authenticate(phone=phone, password=password):
            raise forms.ValidationError("شماره یا رمز عبور اشتباه است.")


class ResetPasswordEmailValidation(PasswordResetForm):
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'لطفا ایمیل خود را وارد نمایید.'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("کاربری با مشخصات وارد شده وجود ندارد.")
        return email


class VerifyRegistrationForm(forms.Form):
    code = forms.IntegerField(
        label='کد تایید',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'emailContent',
                'placeholder': 'کد تایید',
                'style': 'direction: rtl'
            }
        ))


class ForgotPasswordForm(forms.Form):
    phone = forms.CharField(
        label='شماره همراه',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'emailContent',
                'placeholder': 'شماره همراه',
                'style': 'direction: rtl'
            }
        ),
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not User.objects.filter(phone__iexact=phone, is_active=True).exists():
            raise forms.ValidationError("کاربری با مشخصات وارد شده وجود ندارد.")
        return phone


class VerifyResetPassword(forms.Form):
    reset_password_code = forms.IntegerField(
        label='کد تایید',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'emailContent',
                'placeholder': 'کد تایید'
            }
        ))
    reset_password_form = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'passwordContent',
                'placeholder': 'رمز عبور جدید'
            }
        ),
        validators=[
            validators.MinLengthValidator(8)
        ]

    )
    confirm_reset_password_form = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'passwordContent',
                'placeholder': 'تکرار رمز عبور جدید'
            }
        ),
        validators=[
            validators.MinLengthValidator(8)
        ]
    )

    def clean_confirm_reset_password_form(self):
        reset_password = self.cleaned_data['reset_password_form']
        confirm_reset_password = self.cleaned_data['confirm_reset_password_form']

        if reset_password != confirm_reset_password:
            raise forms.ValidationError('کلمات عبور با هم مغایرت دارند. لطفا دوباره تلاش کنید.')
        return confirm_reset_password


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='رمز عبور فعلی',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'رمز عبور فعلی'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    new_password = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'رمز عبور جدید'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )
    confirm_new_password = forms.CharField(
        label='تایید رمز عبور',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'تایید رمز عبور'
            }
        ),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )

    def clean_confirm_new_password(self):
        password = self.cleaned_data['new_password']
        confirm_password = self.cleaned_data['confirm_new_password']

        if password != confirm_password:
            raise forms.ValidationError('کلمات عبور با هم مغایرت دارند. لطفا دوباره تلاش کنید.')
        return confirm_password


# class UserInfoForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']


