from django.db.models import Q
from rest_framework import views
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from chat.models import AdChat, AdMessage
from ..serializers import AdChatListSerializer


class ChatListAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdChatListSerializer

    def get(self, request, *args, **kwargs):
        chats = AdChat.objects.filter(Q(ad__user=request.user) | Q(sender=request.user)).select_related('ad', 'sender')
        serializer = self.serializer_class(chats, many=True, context={'request': request})

        return Response(data=serializer.data)
