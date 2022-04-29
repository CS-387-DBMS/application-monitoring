from rest_framework import serializers
from send_data.models import ChartData

class ChartDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChartData
        fields = '__all__'