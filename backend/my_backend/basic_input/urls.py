from django.contrib import admin
from django.urls import path, include
from basic_input.views import createMachine, deleteMachine, StartMonitoring

urlpatterns = [
    path('addmachine/', createMachine),    
    path('delmachine/', deleteMachine),
    path('monitor/', StartMonitoring),
]
