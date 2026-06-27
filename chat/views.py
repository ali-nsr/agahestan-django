from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
# from django.contrib import messages as djmessages
from django.db.models import Q
from .models import AdChat, AdMessage
from ad.models import Ad
from accounts.models import User
from django.http import Http404


def chatroom(request, room_name):
    return render(request, 'chat/chat_room.html', {'room_name': room_name})

@login_required
def start_chat(request, ad_id):
    if request.method == "POST":
        ad = get_object_or_404(Ad, id=ad_id)
        if request.user == ad.user:
            # messages.messages(request, 'با خودتان نمیتوانید چت کنید')
            return redirect('/')
        chat, created = AdChat.objects.get_or_create(ad=ad, sender=request.user)
        AdMessage.objects.get_or_create(chat_id=chat.id, sender=request.user, text=request.POST['text'])
        return redirect('chat:chat-detail', chat_uuid=chat.uuid)


@login_required
def chat_detail(request, chat_uuid):
    chat = get_object_or_404(AdChat, uuid=chat_uuid)

    # فقط کسانی که مجازند ببینن (خریدار یا فروشنده)
    if chat.sender != request.user and chat.ad.user != request.user:
        return redirect('chat:inbox')

    messages = chat.messages.all().order_by('timestamp')
    return render(request, 'chat/chat_detail.html', {
        'chat': chat,
        'messages': messages,
    })


@login_required
def chat_list(request):
    chats = AdChat.objects.filter(Q(ad__user=request.user)|Q(sender=request.user)).select_related('ad', 'sender')

    return render(request, 'chat/chat_list.html', {
        'chats': chats,
    })
