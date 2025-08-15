from django.urls import path
from .views import listview, register, login

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('', listview, name='home'),
]