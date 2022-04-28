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

def createLogger(ip, port):
    "Logic to ssh and create logger"
    # TODO other options : threshold etc
    run(["scp", "../../../logger/logger.py", "root@"+ip+":/root/logger.py"], timeout=3)
    run(["ssh", "root@"+ip, "nohup", "python3", "/root/logger.py", "--port", str(port)], timeout=3)

def getLogs(ip):
    """
    Logic to ssh and get logs: say they are stored in the variable 'logs'
    """
    run(["scp", "root@"+ip+":/root/host.log", "/tmp/host.log"], timeout=3)
    run(["scp", "root@"+ip+":/root/http.log", "/tmp/http.log"], timeout=3)
    run(["ssh", "root@"+ip, "cp", "/dev/null", "/root/host.log"], timeout=3)
    run(["ssh", "root@"+ip, "cp", "/dev/null", "/root/http.log"], timeout=3)
    # pray()

    f = open('/tmp/host.log', 'r')
    logs = [loads(x) for x in f.readlines()]
    f.close()
    h = open('/tmp/host.log', 'r')
    httplog = [loads(x) for x in h.readlines()]
    h.close()
    
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
        for idx, obj in enumerate(Machine.objects.all()):

            createLogger(obj.MachineIP, obj.Port) # TODO

            e = Event()
            stop_events.append(e)
            ip = None

            t = GetLogsThread(stop_events[idx], idx, getLogs, ip, 100000)
            t.start()

            pass
        pass
