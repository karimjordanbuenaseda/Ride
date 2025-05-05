from rest_framework import serializers
from core.serializers.core_serializers import CoreModelSerializer
from core.models.user import User


class UserSerializer(CoreModelSerializer):

    class Meta:
        model = User
        fields = (
            'id_user',
            'role',
            'first_name',
            'last_name',
            'email',
            'phone_number'
        )