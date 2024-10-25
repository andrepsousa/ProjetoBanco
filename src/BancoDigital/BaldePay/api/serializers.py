from BaldePay.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ('id', 'name', 'email', 'password', 'date_birth', 'phone')

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
