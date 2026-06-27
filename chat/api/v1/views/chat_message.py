from django.db.models import Q

from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from chat.models import AdChat, AdMessage
from ..serializers import ChatMessageSerializer


class ChatMessageAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def get(self, request, chat_uuid):
        qs = AdMessage.objects.filter(Q(chat__uuid=chat_uuid) |
                                      Q(chat__sender_id=request.user.id) | Q(chat__ad__user_id=request.user.id))
        serializer = ChatMessageSerializer(qs, many=True)

        return Response(data=serializer.data)
