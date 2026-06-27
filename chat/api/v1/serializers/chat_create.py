from rest_framework import serializers

from chat.models import AdChat, AdMessage


class ChatCreateSerializer(serializers.Serializer):
    ad_id = serializers.IntegerField(read_only=True)
    text = serializers.CharField(write_only=True)

