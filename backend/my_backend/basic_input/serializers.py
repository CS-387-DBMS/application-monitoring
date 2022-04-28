from rest_framework import serializers
from basic_input.models import Machine

class MachineSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Machine.objects.create(**validated_data)

    class Meta:
        model = Machine
        # fields = ['id','MachineName', 'MachineIP', 'RAM_usage', 'CPU_usage', 'Disk_usage']
        fields = '__all__'