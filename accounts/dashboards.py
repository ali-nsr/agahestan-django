from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from ad.models import (
    Ad, Category, CategoryField, AdAttribute, Gallery
)
from location.models import Province, City, Neighborhood

def dashboard(request):
    return render(request, 'accounts/dashboard/index.html')
