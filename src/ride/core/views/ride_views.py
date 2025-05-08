from rest_framework import viewsets, renderers, filters
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from core.serializers import *
from core.models import *
from core.utils.location_helpers import calculate_distance_annotation

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    # Add this method to ensure pagination is being respected
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class IsAdminRole(BasePermission):
    """
    Custom permission to only allow users with 'admin' role.
    """
    message = "Only users with admin role are allowed to perform this action."
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
            
        try:
            custom_user = User.objects.get(email=request.user.email)
            return custom_user.role == 'admin'
        except User.DoesNotExist:
            return False

class RideViewSet(viewsets.ModelViewSet):

    serializer_class = RideSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['pickup_time', 'distance_to_pickup']
    permission_classes = [IsAdminRole]

    def get_queryset(self):

        queryset = Ride.objects.select_related('id_rider', 'id_driver')

        # getting today events
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        queryset = queryset.prefetch_related(Prefetch(
            'ride_events',
            queryset=RideEvent.objects.filter(created_at__gte=twenty_four_hours_ago),
            to_attr='prefetched_todays_events'
        ))

        # apply filters based on email if provided
        email = self.request.query_params.get('rider_email', None)
        if email:
            try:
                user = User.objects.get(email=email)
                queryset = queryset.filter(id_rider=user.id_user)
            except User.DoesNotExist:
                return Ride.objects.none()


        # Check if we need to sort by distance to a specific location
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        
        if latitude and longitude:
            try:
                # Validate coordinates
                lat_float = float(latitude)
                lon_float = float(longitude)
                
                if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
                    # Add distance annotation for sorting
                    distance_annotation = calculate_distance_annotation(lat_float, lon_float)
                    queryset = queryset.annotate(distance_to_pickup=distance_annotation)
                    
                    # Let the ordering filter handle this
                    if self.request.query_params.get('ordering') == 'distance_to_pickup':
                        queryset = queryset.order_by('distance_to_pickup')
            except (ValueError, TypeError):
                # If coordinates are invalid, just continue without distance annotation
                pass
        
        # Default ordering if no specific ordering is requested
        ordering = self.request.query_params.get('ordering')
        if not ordering:
            queryset = queryset.order_by('-pickup_time')

        return queryset

    def get_renderers(self):
        if 'html' in self.request.query_params:
            return [renderers.BrowsableAPIRenderer()]
        return [renderers.JSONRenderer()]
    
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Only users with admin privileges can access this viewset.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]

class RideEventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ride events to be viewed or edited.
    Only users with admin privileges can access this viewset.
    """
    queryset = RideEvent.objects.all()
    serializer_class = RideEventSerializer
    permission_classes = [IsAdminRole]