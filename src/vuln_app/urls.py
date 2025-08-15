from django.urls import path
from .views import listview, register

urlpatterns = [
    path('register/', register, name='register'),
    path('', listview, name='home'),
]