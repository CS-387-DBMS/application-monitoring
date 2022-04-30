from itertools import count
import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from httplib2 import Response
from rest_framework.parsers import JSONParser
from basic_input.models import Machine
from basic_input.serializers import MachineSerializer
from basic_input.my_thread import GetLogsThread
from threading import Event
from subprocess import run
from json import loads
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
import pandas as pd

# Create your views here.

stop_events = []
is_monitoring = False

def createLogger(machine_obj):
    "Logic to ssh and create logger"
    print('creating logger', machine_obj.MachineIP)
    # TODO other options : threshold etc
    cmd =  ["sshpass", "-p", machine_obj.passwrd, "ssh", "-o", "StrictHostKeyChecking=no", "root@"+machine_obj.MachineIP, "-f", "python3", "/root/logger.py"]
    cmd += ["--ip", str(machine_obj.MachineIP)]
    cmd += ["--port", str(machine_obj.Port)]
    cmd += ["--cpu", str(machine_obj.CPU_usage)]
    cmd += ["--mem", str(machine_obj.RAM_usage)]
    cmd += ["--net", str(machine_obj.packet)]
    cmd += ["--interval", str(0.5)]

    run(["sshpass", "-p", machine_obj.passwrd, "scp", "-o", "StrictHostKeyChecking=no", "../../logger/logger.py", "root@"+machine_obj.MachineIP+":/root/logger.py"], timeout=3)
    run(cmd, timeout=3)

def getLogs(machine_obj):
    """
    Logic to ssh and get logs: say they are stored in the variable 'logs'
    """
    print('get logger', machine_obj.MachineIP)
    ip = machine_obj.MachineIP
    pswd = machine_obj.passwrd

    option = ["-o", "StrictHostKeyChecking=no"]
    run(["sshpass", "-p", pswd, "scp"]+option+["root@"+ip+":/root/host.log", "/tmp/host.log"], timeout=3)
    run(["sshpass", "-p", pswd, "scp"]+option+["root@"+ip+":/root/http.log", "/tmp/http.log"], timeout=3)
    run(["sshpass", "-p", pswd, "scp"]+option+["root@"+ip+":/root/alert.log", "/tmp/alert.log"], timeout=3)

    run(["sshpass", "-p", pswd, "ssh"]+option+["root@"+ip, "cp", "/dev/null", "/root/host.log"], timeout=3)
    run(["sshpass", "-p", pswd, "ssh"]+option+["root@"+ip, "cp", "/dev/null", "/root/http.log"], timeout=3)
    run(["sshpass", "-p", pswd, "ssh"]+option+["root@"+ip, "cp", "/dev/null", "/root/alert.log"], timeout=3)
    # pray()

    # read csv log files, insert into infux
    client = influxdb_client.InfluxDBClient(
        url="http://localhost:8086",
        token=os.environ["influxdb_token"],
        org=os.environ["influxdb_org"]
    )
    write_api=client.write_api(write_options=SYNCHRONOUS)

    columns=['timestamp', 'type', 'cpu_used', 'total_cpu_used', 'mem_used', 'total_mem_used', 'total_swap_used', 'disk_read', 'disk_write', 'total_disk_read', 'total_disk_write', 'bytes_sent', 'bytes_recv', 'total_bytes_sent', 'total_bytes_recv', 'total_packets_sent', 'total_packets_recv', 'total_dropin', 'total_dropout']
    data=pd.read_csv("/tmp/host.log", names=columns)
    for col in columns[2:]:
        data[col]=data[col].astype("float")
    data.rename(columns={"timestamp":"_time"}, inplace=True)
    print(data)
    data = data[data['_time'].notna()]
    data["_time"]=data["_time"].apply(lambda x: datetime.datetime.fromtimestamp(x).astimezone())
    data=data.set_index("_time")
    data.drop(columns=['type'], inplace=True, axis=1)
    print(data)
    write_api.write(bucket=os.environ["influxdb_bucket"], record=data, data_frame_measurement_name=ip)

    # columns = ['timestamp', 'type', 'alert', 'value']
    # data=pd.read_csv("/tmp/alert.log", names=columns)
    # data['value']=data['value'].astype("float")
    # data.rename(columns={"timestamp":"_time"}, inplace=True)
    # print(data)
    # data = data[data['_time'].notna()]
    # data["_time"]=data["_time"].apply(lambda x: datetime.datetime.fromtimestamp(x).astimezone())
    # data=data.set_index("_time")
    # data.drop(columns=['type'], inplace=True, axis=1)

    return True


@csrf_exempt
def createMachine(request,id=None):
    if request.method == "POST":
        data = JSONParser().parse(request)
        serializer = MachineSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == "GET":
        machines = Machine.objects.all()
        serializer = MachineSerializer(machines,many=True)
        return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def deleteMachine(request):
    if request.method == "POST":
        data = JSONParser().parse(request)
        id = data['id']
        Machine.objects.filter(id=id).delete()

        return HttpResponse(status=204)


@csrf_exempt
def StartMonitoring(request):
    if request.method == "GET" and not is_monitoring:
        for idx, obj in enumerate(Machine.objects.all()):
            print('loooooooooooooop', obj.MachineIP)
            createLogger(obj)

            stop_events.append(Event())

            t = GetLogsThread(stop_events[idx], idx, getLogs, obj, 2)
            t.start()

        return HttpResponse(status=200)
    
    else:
        return Response({"status": ["Monitoring has already begun."]}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def StopMonitoring(request):

    if request.method == "GET" and is_monitoring:

        ## command to stop monitoring by stopping logger scripts
        for machine_obj in Machine.objects.all():
            run(["sshpass", "-p", machine_obj.passwrd, \
                "ssh", "-o", "StrictHostKeyChecking=no", "root@"+machine_obj.MachineIP, \
                "kill", "-9", "'$(cat /root/logger.pid)'"], timeout=3)

        is_monitoring = False
        return HttpResponse(status=200)
    
    else:
        return Response({"status": ["Monitoring has not begun."]}, status=status.HTTP_400_BAD_REQUEST)        


    #     for idx, obj in enumerate(Machine.objects.all()):
    #         createLogger(obj)

    #         stop_events.append(Event())

    #         t = GetLogsThread(stop_events[idx], idx, getLogs, obj, 100000)
    #         t.start()

    #     return HttpResponse(status=200)
    
    # else:
    #     return HttpResponse(status=404)


from django.shortcuts import render
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

