from django.shortcuts import render
from send_data.models import ChartData
from send_data.serializers import ChartDataSerializer
from django.http import HttpResponse, JsonResponse

# Create your views here.
streaming_data = []
counter = 0

def getStreamingData(request):

    global counter

    counter += 1
    streaming_data.append(counter)

    if counter == 3:
        counter -= 10

    x = ChartData(n = counter)
    x.save()

    l_data = ChartData.objects.all()

    serializer = ChartDataSerializer(l_data,many=True)
    return JsonResponse(serializer.data, safe=False)
