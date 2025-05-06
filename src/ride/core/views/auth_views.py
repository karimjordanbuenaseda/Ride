from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User as CustomUser

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and return JWT tokens
    """
    username = request.data.get('first_name', '') + request.data.get('last_name', '')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'rider')  # Default role is rider
    
    if not username or not email or not password:
        return Response(
            {'error': 'Please provide username(first & last name), email, and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'User with this email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    cu = CustomUser.objects.create(
        id_user=user.id,
        role=role,
        first_name=request.data.get('first_name', ''),
        last_name=request.data.get('last_name', ''),
        email=email,
        phone_number=request.data.get('phone_number', '')
    )
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': getattr(cu, 'role', None)
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)