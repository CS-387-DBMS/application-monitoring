from rest_framework import serializers
from basic_input.models import Machine

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['machine_name', 'machine_ip', 'ram_threshold', 'cpu_threshold', 'disk_threshold']