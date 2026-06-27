from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .....models import Profile
from ...serializers import ProfileSerializer

User = get_user_model()


from drf_yasg.utils import swagger_auto_schema

class ProfileApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]


    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    http_method_names = ['get', 'put', 'head', 'options']

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user_id=self.request.user.id)
        return obj

    @swagger_auto_schema(
        operation_summary='User profile',
        operation_description=(
                '''
                Get user profile \n
                Example:\n
                    {
                      "user_id": id,
                      "first_name": "",
                      "last_name": "",
                      "email": "",
                      "image": null,
                      "phone": ""
                    }
                '''
        ), tags=['Profile']
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(data=serializer.data,status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='User profile update',
        operation_description=(
                '''
                Update user profile \n
                Example:\n
                    {
                      "first_name": "",
                      "last_name": "",
                      "email": "",
                      "image": null
                    }
                '''
        ), tags=['Profile']
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)