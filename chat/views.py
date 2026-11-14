from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as djmessages
from django.db.models import Q
from .models import AdChat, AdMessage
from ad.models import Ad
from accounts.models import User
from django.http import Http404


def chatroom(request, room_name):
    return render(request, 'chat/chat_room.html', {'room_name': room_name})

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import AdChat, AdMessage
from ad.models import Ad

@login_required
@require_POST
def start_chat(request, ad_uuid):
    ad = get_object_or_404(Ad, uuid=ad_uuid)

    if ad.user_id == request.user.id:
        return JsonResponse({'ok': False, 'error': 'نمی‌توانید با خودتان چت کنید.'}, status=400)

    text = (request.POST.get('text') or '').strip()
    if not text:
        return JsonResponse({'ok': False, 'error': 'متن پیام خالی است.'}, status=400)

    chat, created = AdChat.objects.get_or_create(ad=ad, sender=request.user)

    # اگه چت جدید ساخته شد یا پیام جدید اومد، ذخیره کن
    AdMessage.objects.create(chat=chat, sender=request.user, text=text[:2000])
    chat.save()

    return JsonResponse({
        'ok': True,
        'redirect_url': f'/chat/{chat.uuid}/',
        'is_new': created,
    })

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@login_required
def chat_detail(request, chat_uuid):
    chat = get_object_or_404(
        AdChat.objects.select_related('ad', 'ad__user', 'sender'),
        uuid=chat_uuid,
    )

    if chat.sender_id != request.user.id and chat.ad.user_id != request.user.id:
        return redirect('chat:chat-list')

    other_user = chat.sender if chat.ad.user_id == request.user.id else chat.ad.user

    # ═══ Mark unseen as seen + broadcast ═══
    unseen_qs = (
        AdMessage.objects
        .filter(chat=chat, is_seen=False)
        .exclude(sender=request.user)
    )
    seen_ids = list(unseen_qs.values_list('id', flat=True))
    if seen_ids:
        unseen_qs.update(is_seen=True)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'adchat_{chat_uuid}',
            {
                'type': 'messages_seen',
                'message_ids': seen_ids,
                'user_id': request.user.id,
            }
        )

    chat_messages = chat.messages.select_related('sender').order_by('timestamp')

    return render(request, 'chat/chat_detail.html', {
        'chat': chat,
        'chat_messages': chat_messages,
        'other_user': other_user,
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, OuterRef, Subquery
from .models import AdChat, AdMessage
from ad.models import Ad
from accounts.models import User


@login_required
def chat_list(request):
    user = request.user

    last_msg = AdMessage.objects.filter(chat=OuterRef('pk')).order_by('-timestamp')

    chats = (
        AdChat.objects
        .filter(Q(ad__user=user) | Q(sender=user))
        .select_related('ad', 'sender', 'ad__user')
        .annotate(
            last_text=Subquery(last_msg.values('text')[:1]),
            last_at=Subquery(last_msg.values('timestamp')[:1]),
            last_sender_id=Subquery(last_msg.values('sender_id')[:1]),
            unread_count=Count(
                'messages',
                filter=Q(messages__is_seen=False) & ~Q(messages__sender=user),
            ),
        )
        .order_by('-updated_at')
    )

    chat_data = []
    for chat in chats:
        other_user = chat.sender if chat.ad.user_id == user.id else chat.ad.user
        chat_data.append({
            'chat': chat,
            'other_user': other_user,
            'is_mine': chat.last_sender_id == user.id,
            'unread_count': chat.unread_count,
        })

    return render(request, 'chat/chat_list.html', {
        'chat_data': chat_data,
        'total_unread': sum(c['unread_count'] for c in chat_data),
    })