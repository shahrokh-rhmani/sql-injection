from django.urls import path
from .views import listview, register, login, logout

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('', listview, name='home'),
]