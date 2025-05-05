from django.db import models
from core.models.timestamp import TimeStampedModel
from core.models.ride import Ride

class RideEvent(TimeStampedModel):
    id_ride_event = models.AutoField(primary_key=True)
    id_ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='ride_events')
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Event {self.id_ride_event} for Ride {self.id_ride}: {self.description}"