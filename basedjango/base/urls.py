from django.urls import path
from . import views

urlpatterns = [
    path('listm1/', views.listm1.as_view(), name='listm1'),
    path('addm1/', views.addm1.as_view(), name='addm1'),
]
