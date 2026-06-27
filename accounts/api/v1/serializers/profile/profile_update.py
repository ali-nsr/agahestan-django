from rest_framework import serializers

from .....models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    phone = serializers.ReadOnlyField(source='user.phone')
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Profile
        fields = ['user_id', 'first_name', 'last_name', 'email', 'image', 'phone']
