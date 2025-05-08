from rest_framework import serializers
from core.serializers.core_serializers import CoreModelSerializer
from django.utils import timezone
from datetime import timedelta
from core.models.ride import Ride
from core.serializers.user_serializers import UserSerializer
from core.serializers.ride_event_serializers import RideEventSerializer

class RideSerializer(CoreModelSerializer):

    rider = UserSerializer(source='id_rider', read_only=True)
    driver = UserSerializer(source='id_driver', read_only=True)
    todays_ride_events = serializers.SerializerMethodField()
    distance_to_pickup = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Ride
        fields = (
            'id_ride', 'status', 
            'rider', 'driver',
            'pickup_latitude', 'pickup_longitude', 
            'dropoff_latitude', 'dropoff_longitude', 
            'pickup_time', 'todays_ride_events', 'distance_to_pickup'
        )


    def get_todays_ride_events(self, obj):
        return RideEventSerializer(obj.prefetched_todays_events, many=True).data