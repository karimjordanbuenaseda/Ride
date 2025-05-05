from rest_framework import serializers
from core.serializers.core_serializers import CoreModelSerializer
from core.models.ride_event import RideEvent
from core.models.ride import Ride
from core.models.user import User

class RideEventSerializer(CoreModelSerializer):

    id_ride = serializers.PrimaryKeyRelatedField(queryset=Ride.objects.all(), source='ride')
    
    class Meta:
        model = RideEvent
        fields = ('id_ride_event', 'id_ride', 'description')