from django.shortcuts import render
from django.views import generic
from .models import *

# Create your views here.
class listm1(generic.list.ListView):
    model = m1
    context_object_name = 'listm1'
    template_name = 'listm1.html'

class addm1(generic.edit.CreateView):
    model = m1
    fields = ['f']    
    template_name = 'addm1.html'
