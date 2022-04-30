from django.contrib import admin
from django.urls import path, include
from send_data.views import getStreamingData, getAlertData

urlpatterns = [
    path('getdata/', getStreamingData),
    path('getalertdata/', getAlertData),
]
