from django.urls import path
from .views import listview

urlpatterns = [
    path('', listview, name='home'),
]