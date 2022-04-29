from django.contrib import admin
from django.urls import path, include
from send_data.views import getStreamingData

urlpatterns = [
    path('getdata/', getStreamingData),
]
