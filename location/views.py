from django.shortcuts import redirect
from location.services import clear_selected_cities


def clear_cities(request):
    clear_selected_cities(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))