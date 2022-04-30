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
                {"machine_name": "M1", "data": [random.random()+3.5 for i in range(60)]},
                {"machine_name": "M2", "data": [random.random()+4.5 for i in range(60)]},
            ]
        },
        {
            "name" : "RAM Usage",
            "alert_timestamps": [], # seconds at which we have alerts 
            "data" :
            [
                {"machine_name": "M1", "data": [random.random()+5 for i in range(60)]},
                {"machine_name": "M2", "data": [random.random()+5.5 for i in range(60)]},
            ]
        }
    ]
    return HttpResponse(json.dumps(MyDict))


def getAlertData(request):

    MyDict = [
        {
            "time_stamp":"", # time at which the alert occurs
            "alert_type":"", # One of RAM, CPU or DISK
            "machine_name":"", # From the machines on the network
            "value":"", # Value of the attribute which exceeds the threshold
        },
    ]

    x =         {
            "time_stamp":3, # time at which the alert occurs
            "alert_type":"DISK", # One of RAM, CPU or DISK
            "machine_name":"M3", # From the machines on the network
            "value":"1.5", # Value of the attribute which exceeds the threshold
        }

    tmp_dict = [
        {
            "time_stamp":"1", # time at which the alert occurs
            "alert_type":"CPU", # One of RAM, CPU or DISK
            "machine_name":"M1", # From the machines on the network
            "value":"1.0", # Value of the attribute which exceeds the threshold
        },
        {
            "time_stamp":"2", # time at which the alert occurs
            "alert_type":"RAM", # One of RAM, CPU or DISK
            "machine_name":"M2", # From the machines on the network
            "value":"2.0", # Value of the attribute which exceeds the threshold
        },
        {
            "time_stamp":3, # time at which the alert occurs
            "alert_type":"DISK", # One of RAM, CPU or DISK
            "machine_name":"M3", # From the machines on the network
            "value":"1.5", # Value of the attribute which exceeds the threshold
        },

    ]
    global counter

    counter += 1
    x["time_stamp"] = counter
    y = x.copy()
    tmp_dict.append(x)

    return HttpResponse(json.dumps(tmp_dict))