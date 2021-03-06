from django.contrib import admin
from django.urls import path, include
from basic_input.views import createMachine, deleteMachine, StartMonitoring, StopMonitoring, getAlertData, getStreamingData

urlpatterns = [
    path('stoppp/',StopMonitoring),
    path('addmachine/', createMachine),    
    path('delmachine/', deleteMachine),
    path('monitor/', StartMonitoring),
    path('getdata/', getStreamingData),
    path('getalertdata/', getAlertData),
]
