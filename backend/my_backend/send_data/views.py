from django.shortcuts import render
from backend.my_backend.basic_input.models import Machine
from send_data.models import ChartData
from send_data.serializers import ChartDataSerializer
from django.http import HttpResponse, JsonResponse
import argparse
from http import client
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
from matplotlib.pyplot import axis
import pandas as pd
import os

import random
import json

# Create your views here.
streaming_data = []
counter = 0

def get_data(query_api, org, bucket, ip, field, yield_name="mean"):
    query='from(bucket: "'+bucket+'")\
            |> range(start: -10m)\
            |> filter(fn: (r) => r["_measurement"] == "'+ip+'")\
            |> filter(fn: (r) => r["_field"] == "'+field+'")\
            |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)\
            |> yield(name: "'+yield_name+'")'
    result=query_api.query(org=org, query=query)
    for table in result:
        data=pd.DataFrame([row.values for row in table])
        data.drop(columns=["result","table", "_start", "_stop", "_field", "_measurement"], inplace=True, axis=1)
        data.set_index("_time", inplace=True)
        data.rename(columns={"_value":field}, inplace=True)
        return (data[-60:][field].tolist())

def getStreamingData(request):
    MyDict=[]
    org=os.environ["influxdb_org"]
    bucket=os.environ["influxdb_bucket"]
    client=influxdb_client.InfluxDBClient(
        url="http://localhost:8086",
        token=os.environ["influxdb_token"],
        org=os.environ["influxdb_org"]
    )
    query_api=client.query_api()
    fields=['timestamp', 'type', 'cpu_used', 'total_cpu_used', 'mem_used', 'total_mem_used', 'total_swap_used', 'disk_read', 'disk_write', 'total_disk_read', 'total_disk_write', 'bytes_sent', 'bytes_recv', 'total_bytes_sent', 'total_bytes_recv', 'total_packets_sent', 'total_packets_recv', 'total_dropin', 'total_dropout']
    for field in fields[2:]:
        d={"name":field, "alert_timestamps":[], "data":[]}
        for obj in Machine.objects.all():
            d["data"].append({"machine_name":obj.MachineName, "data":get_data(query_api, org, bucket, obj.MachineIP, field)})
        MyDict.append(d)


    # MyDict = [
    #     {
    #         "name" : "CPU Usage",
    #         "alert_timestamps": [], # seconds at which we have alerts 
    #         "data" :
    #         [
    #             {"machine_name": "M1", "data": [random.random() for i in range(60)]},
    #             {"machine_name": "M2", "data": [random.random()+5 for i in range(60)]},
    #         ]
    #     },
    #     {
    #         "name" : "RAM Usage",
    #         "alert_timestamps": [], # seconds at which we have alerts 
    #         "data" :
    #         [
    #             {"machine_name": "M1", "data": [random.random()+3 for i in range(60)]},
    #             {"machine_name": "M2", "data": [random.random()+8 for i in range(60)]},
    #         ]
    #     }
    # ]
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