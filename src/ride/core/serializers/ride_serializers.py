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
    ride_events = RideEventSerializer(many=True, read_only=True)
    todays_ride_events = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = (
            'id_ride', 'status', 'id_rider', 'id_driver', 
            'rider', 'driver',
            'pickup_latitude', 'pickup_longitude', 
            'dropoff_latitude', 'dropoff_longitude', 
            'pickup_time', 'ride_events', 'todays_ride_events'
        )


    def get_todays_ride_events(self, obj):
        # This method will be used by the viewset to optimize the query
        # The actual implementation will depend on prefetched data
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        events = obj.ride_events.filter(created_at__gte=twenty_four_hours_ago)
        return RideEventSerializer(events, many=True).data