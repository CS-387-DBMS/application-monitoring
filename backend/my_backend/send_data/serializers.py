from rest_framework import serializers
from send_data.models import ChartData

class ChartDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChartData
        fields = '__all__'

class DataFrontend(serializers.Serializer):

    cpu_usage = serializers.DecimalField(decimal_places=2,max_digits=3)