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

def createLogger(machine_obj):
    "Logic to ssh and create logger"
    # TODO other options : threshold etc
    cmd =  ["sshpass", "-p", machine_obj.passwrd, "ssh", "-o", "StrictHostKeyChecking=no", "root@"+machine_obj.MachineIP, "-f", "python3", "/root/logger.py"]
    cmd += ["--ip", str(machine_obj.MachineIP)]
    cmd += ["--port", str(machine_obj.Port)]
    cmd += ["--cpu", str(machine_obj.CPU_usage)]
    cmd += ["--mem", str(machine_obj.RAM_usage)]
    cmd += ["--net", str(machine_obj.packet)]

    run(["sshpass", "-p", machine_obj.passwrd, "scp", "-o", "StrictHostKeyChecking=no", "../../logger/logger.py", "root@"+machine_obj.MachineIP+":/root/logger.py"], timeout=3)
    run(cmd, timeout=3)

def getLogs(machine_obj):
    """
    Logic to ssh and get logs: say they are stored in the variable 'logs'
    """
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
    if request.method == "GET":
        for idx, obj in enumerate(Machine.objects.all()):
            createLogger(obj)

            stop_events.append(Event())

            t = GetLogsThread(stop_events[idx], idx, getLogs, obj, 20)
            t.start()

        return HttpResponse(status=200)
    
    else:
        return HttpResponse(status=404)