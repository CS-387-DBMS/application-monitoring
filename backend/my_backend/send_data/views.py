from django.shortcuts import render
from send_data.models import ChartData
from send_data.serializers import ChartDataSerializer
from django.http import HttpResponse, JsonResponse

import random
import json

# Create your views here.
streaming_data = []
counter = 0

def getStreamingData(request):
    MyDict = [
        {
            "name" : "CPU Usage",
            "alert_timestamps": [], # seconds at which we have alerts 
            "data" :
            [
                {"machine_name": "M1", "data": [random.random() for i in range(60)]},
                {"machine_name": "M2", "data": [random.random()+5 for i in range(60)]},
            ]
        },
        {
            "name" : "RAM Usage",
            "alert_timestamps": [], # seconds at which we have alerts 
            "data" :
            [
                {"machine_name": "M1", "data": [random.random()+3 for i in range(60)]},
                {"machine_name": "M2", "data": [random.random()+8 for i in range(60)]},
            ]
        }
    ]
    return HttpResponse(json.dumps(MyDict))


def getAlertData(request):

    MyDict = [
        [{
            "time_stamp":"", # time at which the alert occurs
            "alert_type":"", # One of RAM, CPU or DISK
            "machine_name":"", # From the machines on the network
            "value":"", # Value of the attribute which exceeds the threshold
        },]
    ]

    return HttpResponse(json.dumps(MyDict))