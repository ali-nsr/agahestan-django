from rest_framework import serializers
from django.utils.timezone import localtime

from chat.models import AdChat


class AdChatListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='sender.id')
    name = serializers.CharField(source='sender.phone')  # یا sender.username
    last_message = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    has_new = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = AdChat
        fields = ['id', 'name', 'last_message', 'time', 'has_new', 'absolute_url']

    def get_lastMessage(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        return last_msg.text if last_msg else ''

    def get_time(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            # فقط ساعت و دقیقه
            return localtime(last_msg.timestamp).strftime('%H:%M')
        return ''

    def get_hasNew(self, obj):
        request = self.context.get('request')  # safer
        if request:
            return obj.messages.filter(is_seen=False).exclude(sender=request.user).exists()
        return False

    def get_absolute_url(self, obj):
        return f'http://127.0.0.1:8000/chat/api/v1/{obj.uuid}/'
