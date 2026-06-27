from rest_framework import views
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from chat.models import AdChat, AdMessage
from ..serializers import ChatCreateSerializer

from ad.models import Ad

class ChatCreateAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatCreateSerializer

    def post(self, request, ad_id):
        # check if chat is created or not
        ad = Ad.objects.get(id=ad_id)
        chat = AdChat.objects.filter(sender_id=request.user.id, ad_id=ad_id)
        if chat.first():
            return Response({'detail': 'چت تکراری است'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # create chat
            text = request.data.get('text')
            if text:
                if ad.user.id == request.user.id:
                    return Response(data={
                        'detail': 'نمیتوانید با خودتان چت کنید',
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    chat = AdChat.objects.create(sender_id=request.user.id, ad_id=ad_id)
                    AdMessage.objects.create(chat_id=chat.id,sender_id=request.user.id, text=text)
                    return Response(data={
                        'detail': 'چت ساخته شد',
                        'chat_id': chat.id,
                        'chat_uuid': chat.uuid,
                        'message':text
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response(data={
                    'detail': 'حتما پیام ارسال شود.'
                }, status=status.HTTP_400_BAD_REQUEST)
