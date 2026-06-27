from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache

import json

from accounts.models import User
from .models import AdChat, AdMessage
from ad.models import Ad
from asgiref.sync import sync_to_async




class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_uuid = None
        self.room_group_name = None
        self.user = None

    async def connect(self):
        self.chat_uuid = self.scope['url_route']['kwargs']['chat_uuid']
        self.room_group_name = f'adchat_{self.chat_uuid}'
        self.user = self.scope['user']

        # if self.user.is_anonymous:
        #     await self.close(code=403,reason='unauthorized')



        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # پیام‌های دیده‌نشده را اینجا seen کن
        await self.mark_messages_as_seen(self.chat_uuid, self.user.id)
        await self.update_user_to_online(self.user.id)

    async def disconnect(self, close_code):
        await self.update_user_to_offline(self.user.id)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data=None, bytes_data=None):
        """
        handle requests from frontend to backend.
        """
        message = text_data

        await self.save_message(self.user.id, message)

        # broadcast message to all channels of this group (room)
        # message must be dictionary
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message', # type is required and needs a handler method
            'message': message,
            'sender_username': self.user.phone
        })

    async def chat_message(self, event):
        """
        handler basically send data to frontend (client)
        its not a nessasary method but you should declare it even it returns nothing.
        but for showing data to client you should return data to client
        """

        send_data = {
            'message': event['message'],
            'sender_username': event['sender_username']
        }
        await self.send(json.dumps(send_data))
        # وقتی پیام جدید می‌رسد، کاربر آن را می‌بیند
        await self.mark_messages_as_seen(self.chat_uuid, self.user.id)




    @database_sync_to_async
    def save_message(self, sender_id, message):
        chat = AdChat.objects.get(uuid=self.chat_uuid)
        AdMessage.objects.create(chat=chat, sender_id=sender_id, text=message)
        chat.save()

    @database_sync_to_async
    def update_user_to_online(self, user_id):
        user = User.objects.get(id=user_id)
        user.is_online = True
        user.save()

    @database_sync_to_async
    def update_user_to_offline(self, user_id):
        user = User.objects.get(id=user_id)
        user.is_online = False
        user.save()

    @database_sync_to_async
    def mark_messages_as_seen(self, chat_uuid, user_id):
        chat = AdChat.objects.get(uuid=chat_uuid)

        # فقط پیام‌هایی که:
        # 1. فرستنده‌شان غیر از کاربر فعلی است
        # 2. دیده نشده‌اند
        unseen_messages = AdMessage.objects.filter(
            chat=chat,
            is_seen=False
        ).exclude(sender_id=user_id)

        unseen_messages.update(is_seen=True)



'''
class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_uuid = None
        self.room_group_name = None
        self.user = None

    async def connect(self):
        self.chat_uuid = self.scope['url_route']['kwargs']['chat_uuid']
        self.room_group_name = f'adchat_{self.chat_uuid}'
        self.user = self.scope['user']

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    async def receive(self, text_data=None, bytes_data=None):
        """
        handle requests from frontend to backend.
        """
        message = text_data
        sender_id = self.user.id

        await self.save_message(sender_id, message)

        # broadcast message to all channels of this group (room)
        # message must be dictionary
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message', # type is required and needs a handler method
            'message': message,
            'sender_id': sender_id,
        })

    async def chat_message(self, event):
        # sender = await database_sync_to_async(User.objects.get)(id=event['sender_id'])
        print(event)
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender_id'],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, message):
        chat = AdChat.objects.get(uuid=self.chat_uuid)
        AdMessage.objects.create(chat=chat, sender_id=sender_id, text=message)
        chat.save()
'''
