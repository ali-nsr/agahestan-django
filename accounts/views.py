from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login as ln, logout as lo, authenticate

from .models import User

def login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if User.objects.filter(phone__iexact=phone).exists():
            if not authenticate(username=phone, password=password):
                messages.warning(request, f'موبایل یا رمز عبور اشتباه است')
                return redirect(request.META['HTTP_REFERER'])
            else:
                user = authenticate(request, username=phone, password=password)
                ln(request, user)
                messages.success(request, f'خوش آمدید')
                return redirect('/')
        else:
            messages.warning(request, f'موبایل یا رمز عبور اشتباه است')
            return redirect(request.META['HTTP_REFERER'])

    return render(request, 'accounts/auth/login.html')


def logout(request):
    lo(request)
    messages.success(request, 'با موفقیت از حساب خود خارج شدید')
    return redirect('accounts:login')