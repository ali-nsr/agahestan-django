from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q


def notify_user(user_id, payload):
    """ارسال event به گروه NotificationConsumer یک کاربر."""
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f'notif_user_{user_id}',
        {
            'type': 'notify',
            'payload': payload,
        },
    )


def notify_chat_participants(chat, exclude_user_id=None):
    """
    شمارش جدید رو به هر دو طرف چت بفرست.
    (خریدار = chat.sender، فروشنده = chat.ad.user)
    """
    from .models import AdMessage

    for uid in (chat.sender_id, chat.ad.user_id):
        if exclude_user_id and uid == exclude_user_id:
            continue

        unread = AdMessage.objects.filter(
            is_seen=False,
        ).filter(
            Q(chat__ad__user_id=uid) | Q(chat__sender_id=uid)
        ).exclude(
            sender_id=uid
        ).count()

        notify_user(uid, {
            'type': 'unread_count',
            'count': unread,
        })