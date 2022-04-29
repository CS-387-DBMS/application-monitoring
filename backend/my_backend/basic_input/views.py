from itertools import count
from os import stat
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

# Create your views here.

stop_events = []

def createLogger(machine_obj):
    "Logic to ssh and create logger"
    # TODO other options : threshold etc
    cmd =  ["sshpass", "-p", machine_obj.passwrd,  "root@"+machine_obj.MachineIP, "nohup", "python3", "/root/logger.py"]
    cmd += ["--port", str(machine_obj.Port)]
    cmd += ["--cpu", str(machine_obj.CPU_usage)]
    cmd += ["--mem", str(machine_obj.RAM_usage)]
    cmd += ["--net", str(machine_obj.packet)]

    run(["sshpass", "-p", machine_obj.passwrd, "scp", "../../../logger/logger.py", "root@"+ip+":/root/logger.py"], timeout=3)
    run(cmd, timeout=3)

def getLogs(machine_obj):
    """
    Logic to ssh and get logs: say they are stored in the variable 'logs'
    """
    ip = machine_obj.MachineIP
    pswd = machine_obj.passwrd
    run(["sshpass", "-p", pswd, "scp", "root@"+ip+":/root/host.log", "/tmp/host.log"], timeout=3)
    run(["sshpass", "-p", pswd, "scp", "root@"+ip+":/root/http.log", "/tmp/http.log"], timeout=3)
    run(["sshpass", "-p", pswd, "scp", "root@"+ip+":/root/alert.log", "/tmp/alert.log"], timeout=3)

    run(["sshpass", "-p", pswd, "root@"+ip, "cp", "/dev/null", "/root/host.log"], timeout=3)
    run(["sshpass", "-p", pswd, "root@"+ip, "cp", "/dev/null", "/root/http.log"], timeout=3)
    run(["sshpass", "-p", pswd, "root@"+ip, "cp", "/dev/null", "/root/alert.log"], timeout=3)
    # pray()

    # read csv log files, insert into infux
    
    return logs, httplog


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
        cmd = [
            "python3",
            "request_log.py",
            "--ip_addresses"
        ] + list_of_ip_addresses
        + ["--tokens"]
        + list_of_tokens
        + ["--orgs"]
        + orgs
        + ["--buckets"]
        + buckets
        + ["--ports"]
        + ports
        + [
            "--control_ip_address", my_ip,
            "--control_token", my_token,
            "--control_org", my_org,
            "--control_bucket", my_bucket,
            "--control_port", my_port
        ]

        run(cmd)

        return HttpResponse(status=200)
        
    #     for idx, obj in enumerate(Machine.objects.all()):
    #         createLogger(obj)

    #         stop_events.append(Event())

    #         t = GetLogsThread(stop_events[idx], idx, getLogs, obj, 100000)
    #         t.start()

    #     return HttpResponse(status=200)
    
    # else:
    #     return HttpResponse(status=404)