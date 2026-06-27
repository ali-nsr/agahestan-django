from rest_framework import serializers

from chat.models import AdChat,AdMessage
from utils.mixins import PersianTimeMixin



class ChatMessageSerializer(PersianTimeMixin,serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.phone')  # یا sender.username
    time = serializers.SerializerMethodField()

    class Meta:
        model = AdMessage
        fields = ['sender','text','time','is_seen']

    def get_time(self, obj):
        return self.persian_timesince(obj.timestamp)