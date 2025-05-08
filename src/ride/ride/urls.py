"""
URL configuration for ride project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from core.views import *
import debug_toolbar

admin.autodiscover()

router = routers.SimpleRouter()
# Register your viewsets here
router.register(r'rides', RideViewSet, basename='rides')
router.register(r'users', UserViewSet)
router.register(r'ride-events', RideEventViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),

    # jwt authentication and generation
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # user registration
    path('api/register/', register_user, name='register_user'),
    path('__debug__/', include(debug_toolbar.urls)),

    re_path(r'^api/', include(router.urls)),
]
