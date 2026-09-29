
from django.contrib import admin

from django.shortcuts import render
from django.urls import path, include

from accounts.models import Event
def homepage(request):
    events = Event.objects.order_by("date", "id")
    return render(request, "accounts/home.html", {"events": events})
def Tech(request):
    return render(request,'/accounts/Tech.html')
def Sports(request):
    return render(request,'/accounts/Sports.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('',homepage)
 
]



# http://localhost:8000/accounts