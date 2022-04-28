from django.contrib import admin
from django.urls import path, include
from basic_input.views import createMachine

urlpatterns = [
    path('addmachine/', createMachine),
]
