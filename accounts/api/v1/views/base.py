# from django.shortcuts import get_object_or_404
# from django.contrib.auth import get_user_model
# from django.core.cache import cache
# from django.contrib.auth import login
# from django.utils.timezone import timedelta, now
#
# from rest_framework.response import Response
# from rest_framework import generics
# from rest_framework import views
# from rest_framework.views import APIView
# from rest_framework import status
# from rest_framework_simplejwt.tokens import RefreshToken
# import random
#
#
# from ...tasks import send_verify_sms_async, send_forgot_password_sms_async, send_otp_sms_async
# from ...models import Profile, OTP
# from ad.models import Ad
#
# User = get_user_model()
# from ad.api.v1.mixins import BaseResponseMixin









# jwt codes
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
# from .serializers import CustomTokenObtainPairViewSerializer
#
#
# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairViewSerializer
#     queryset = Profile.objects.all()

# end jwt codes

# profile
# from rest_framework import generics
# from rest_framework import views
# from rest_framework.response import Response
# from rest_framework import status
# from django.shortcuts import get_object_or_404
# from django.db import transaction
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
# from .serializers import AdListSerializer,AdDetailSerializer,AdAttributesSyncSerializer,AdAttributeItemSerializer,GallerySyncSerializer
# from ad.models import Ad, AdAttribute
#
#
# class UserAdsApiView(views.APIView):
#     def get(self, request):
#         ads = Ad.objects.filter(user_id=request.user.id)
#         serializer = AdListSerializer(ads, many=True)
#         return Response(serializer.data)

# class UserAdDetailApiView(generics.RetrieveUpdateAPIView):
#     serializer_class = AdDetailSerializer
#
#     def get_object(self):
#         obj = get_object_or_404(Ad, pk=self.kwargs['pk'])
#         return obj
#
#
# class AdAttributesUpdateAPIView(views.APIView):
#
#     def get(self, request,pk=None):
#         qs = AdAttribute.objects.filter(ad_id=pk)
#         serializer = AdAttributeItemSerializer(qs, many=True)
#         return Response(serializer.data)
#
#
#     def put(self, request, pk):
#         ad = get_object_or_404(Ad, pk=pk, user=request.user)
#         ser = AdAttributesSyncSerializer(data=request.data, context={'ad': ad})
#         ser.is_valid(raise_exception=True)
#         result = ser.save()
#         return Response(result, status=status.HTTP_200_OK)
#
# class AdGallerySyncView(views.APIView):
#     parser_classes = (MultiPartParser, FormParser, JSONParser)
#
#     def put(self, request, ad_id):
#         ad = get_object_or_404(Ad, pk=ad_id, user=request.user)
#         serializer = GallerySyncSerializer(data=request.data, context={"ad": ad})
#         serializer.is_valid(raise_exception=True)
#         result = serializer.save()
#         return Response(result, status=status.HTTP_200_OK)


# maybe need these endpoints in future


# class ResendVerifyCodeApiView(APIView):
#     def post(self, request):
#         # real_otp = request.session.get('register_otp')
#         # if real_otp:
#         #     return Response(data={'detail': f'{real_otp} exists'}, status=status.HTTP_400_BAD_REQUEST)
#         # else:
#
#         if request.user.is_authenticated:
#             otp = str(random.randint(1000, 9999))
#             request.session['register_otp'] = otp
#             request.session['register_phone'] = request.user.phone
#
#             send_verify_sms_async(user_phone=request.user.phone, otp_code=otp)
#             data = {
#                 'otp': request.session['register_otp'],
#                 'phone': request.user.phone
#             }
#             return Response(data=data, status=status.HTTP_200_OK)
#         else:
#             return Response(data={'detail': 'ابتدا به حساب کاربری وارد شوید'}, status=status.HTTP_400_BAD_REQUEST)


# class VerifyApiView(generics.GenericAPIView):
#     serializer_class = VerifySerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#
#         serializer.is_valid(raise_exception=True)
#
#         user_opt = serializer.validated_data.get('user_otp')
#         real_otp = request.session.get('register_otp')
#         user_phone = request.session.get('register_phone')
#
#         if real_otp and user_phone:
#             if int(real_otp) == int(user_opt):
#                 user = User.objects.get(phone=user_phone)
#                 if not user.is_verified:
#                     user.is_verified = True
#                     user.save()
#
#                     del request.session['register_otp']
#                     del request.session['register_phone']
#
#                     return Response(status=status.HTTP_200_OK)
#                 else:
#                     return Response(data={'detail': 'کاربر قعال است'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response(data={'detail': f'{real_otp} != {user_opt}'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(data={'detail': 'otp does not exists'}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class RegisterApiView(generics.GenericAPIView):
#     serializer_class = RegisterSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = RegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             user = User.objects.create_user(phone=serializer.validated_data['phone'],
#                                             password=serializer.validated_data['password'])
#             # send verification sms
#             otp = str(random.randint(1000, 9999))
#
#             request.session['register_otp'] = otp
#             request.session['register_phone'] = user.phone
#
#             send_verify_sms_async(user_phone=user.phone, otp_code=otp)
#
#             data = {
#                 'phone': serializer.validated_data['phone'],
#                 'otp': otp
#             }
#
#             return Response(data=data, status=status.HTTP_201_CREATED)
#
#         return Response(data={
#             "success": False,
#             "message": "user exists",
#             "error": None
#         }, status=status.HTTP_400_BAD_REQUEST)

# class ChangePasswordApiView(generics.GenericAPIView):
#     serializer_class = ChangePasswordSerializer
#
#     def get_object(self):
#         obj = self.request.user
#         return obj
#
#     def put(self, request, *args, **kwargs):
#         self.object = self.get_object()
#
#         serializer = ChangePasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             if not self.object.check_password(serializer.validated_data.get('old_password')):
#                 return Response({'old_password': 'wrong password'})
#             self.object.set_password(serializer.validated_data.get('new_password'))
#             self.object.save()
#             return Response({'detail': 'password changed successfully'}, status=status.HTTP_200_OK)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ForgotPasswordApiView(generics.GenericAPIView):
#     """
#     Insert phone number. after validation a 6 digit code will send to this phone number.
#     then use this code in verify endpoint
#     {
#         "phone": ""
#     }
#     """
#     serializer_class = ForgotPasswordSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user_phone = serializer.validated_data['phone']
#         otp = str(random.randint(100000, 999999))
#         request.session['forgot_otp'] = otp
#         request.session['forgot_phone'] = user_phone
#
#         send_forgot_password_sms_async(user_phone=user_phone, otp_code=otp)
#
#         data = {
#             "success": True,
#             "message": "کد فراموشی رمز عبور ارسال شد",
#             "otp": otp,
#             "user_phone": user_phone
#         }
#         return Response(data=data, status=status.HTTP_200_OK)


# class ResetPasswordApiView(generics.GenericAPIView):
#     serializer_class = ResetPasswordSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         code = serializer.validated_data['code']
#         new_password = serializer.validated_data['new_password']
#         real_code = request.session.get('forgot_otp')
#         user_phone = request.session.get('forgot_phone')
#         if real_code is None:
#             return Response({'detail': 'code is wrong'})
#
#         user = User.objects.filter(phone=user_phone)
#         if not user.exists():
#             return Response({'detail': 'user is not found'})
#
#         if int(real_code) != int(code):
#             return Response({'detail': 'code is wrong'})
#
#         user = user[0]
#         user.set_password(new_password)
#         user.save()
#
#         return Response(serializer.data, status=status.HTTP_200_OK)
