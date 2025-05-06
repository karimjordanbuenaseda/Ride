from rest_framework import viewsets, renderers
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.decorators import action

from core.serializers import *
from core.models import *

class IsAdminRole(BasePermission):
    """
    Custom permission to only allow users with 'admin' role.
    """
    message = "Only users with admin role are allowed to perform this action."
    
    def has_permission(self, request, view):
        # Allow GET requests for authenticated users (optional)
        # if request.method in ['GET'] and request.user.is_authenticated:
        #     return True
            
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
            
        # Try to find the corresponding custom User model with admin role
        try:
            custom_user = User.objects.get(email=request.user.email)
            return custom_user.role == 'admin'
        except User.DoesNotExist:
            return False

class RideViewSet(viewsets.ModelViewSet):

    serializer_class = RideSerializer
    permission_classes = [IsAdminRole]
    queryset = Ride.objects.all()

    def get_renderers(self):
        return [renderers.JSONRenderer()]