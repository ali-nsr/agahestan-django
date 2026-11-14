from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

from .utils import notify_chat_participants



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

        # mark پیام‌های دیده‌نشده + broadcast
        seen_ids = await self.mark_messages_as_seen(self.chat_uuid, self.user.id)
        if seen_ids:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'messages_seen',
                'message_ids': seen_ids,
                'user_id': self.user.id,
            })

        await self.update_user_to_online(self.user.id)

    async def disconnect(self, close_code):
        await self.update_user_to_offline(self.user.id)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        message = (text_data or '').strip()
        if not message:
            return

        info = await self.save_message(self.user.id, message)

        # ارسال پیام
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': message,
            'sender_id': self.user.id,
            'sender_username': self.user.phone,
            'message_id': info['id'],
            'time': info['time'],
        })

        # ═══ اطلاع به گیرنده (طرف مقابل) ═══
        await self.notify_recipient()

    async def chat_message(self, event):
        await self.send(json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'message_id': event['message_id'],
            'time': event['time'],
        }))

        seen_ids = await self.mark_messages_as_seen(self.chat_uuid, self.user.id)
        if seen_ids:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'messages_seen',
                'message_ids': seen_ids,
                'user_id': self.user.id,
            })

        # ═══ اطلاع به NotificationConsumer هر دو طرف ═══
        await self.broadcast_unread_counts()

    async def messages_seen(self, event):
        await self.send(json.dumps({
            'type': 'messages_seen',
            'message_ids': event['message_ids'],
            'user_id': event['user_id'],
        }))

    async def broadcast_unread_counts(self):
        from .utils import notify_chat_participants
        from .models import AdChat
        from asgiref.sync import sync_to_async

        chat = await sync_to_async(AdChat.objects.select_related('ad').get)(uuid=self.chat_uuid)
        await sync_to_async(notify_chat_participants)(chat)

    async def notify_recipient(self):
        from .utils import notify_user
        from .models import AdChat, AdMessage
        from asgiref.sync import sync_to_async

        chat = await sync_to_async(
            AdChat.objects.select_related('ad').get
        )(uuid=self.chat_uuid)

        recipient_id = chat.sender_id if chat.ad.user_id == self.user.id else chat.ad.user_id

        # شمارش جدید برای گیرنده
        unread = await sync_to_async(
            lambda: AdMessage.objects.filter(
                is_seen=False,
            ).filter(
                chat__ad__user_id=recipient_id
            ).exclude(
                sender_id=recipient_id
            ).count() +
                    AdMessage.objects.filter(
                        is_seen=False,
                        chat__sender_id=recipient_id,
                    ).exclude(
                        sender_id=recipient_id
                    ).count()
        )()

        await sync_to_async(notify_user)(recipient_id, {
            'type': 'unread_count',
            'count': unread,
        })
    # ═════════════════════════════════════════════
    # DB helpers
    # ═════════════════════════════════════════════

    @database_sync_to_async
    def save_message(self, sender_id, message):
        from .models import AdChat, AdMessage
        chat = AdChat.objects.get(uuid=self.chat_uuid)
        msg = AdMessage.objects.create(
            chat=chat, sender_id=sender_id, text=message[:2000],
        )
        chat.save()
        return {
            'id': msg.id,
            'time': msg.timestamp.strftime('%H:%M'),
        }

    @database_sync_to_async
    def mark_messages_as_seen(self, chat_uuid, user_id):
        """پیام‌های طرف مقابل رو seen کن، IDها رو برگردون."""
        from .models import AdChat, AdMessage
        chat = AdChat.objects.get(uuid=chat_uuid)
        qs = (
            AdMessage.objects
            .filter(chat=chat, is_seen=False)
            .exclude(sender_id=user_id)
        )
        ids = list(qs.values_list('id', flat=True))
        if ids:
            qs.update(is_seen=True)
        return ids

    @database_sync_to_async
    def update_user_to_online(self, user_id):
        from accounts.models import User
        User.objects.filter(id=user_id).update(is_online=True)

    @database_sync_to_async
    def update_user_to_offline(self, user_id):
        from accounts.models import User
        User.objects.filter(id=user_id).update(is_online=False)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close(code=403)
            return

        self.group_name = f'notif_user_{user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # ارسال شمارش اولیه
        count = await self.get_unread_count(user.id)
        await self.send(json.dumps({
            'type': 'unread_count',
            'count': count,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        """سرور این رو صدا می‌زنه تا کلاینت آپدیت بشه."""
        await self.send(json.dumps(event['payload']))

    @database_sync_to_async
    def get_unread_count(self, user_id):
        from .models import AdMessage
        from django.db.models import Q

        return AdMessage.objects.filter(
            is_seen=False,
        ).filter(
            Q(chat__ad__user_id=user_id) | Q(chat__sender_id=user_id)
        ).exclude(
            sender_id=user_id
        ).count()