from django.contrib.auth.models import User

from rest_framework import serializer


class UserSerializer(serializer.HyperlinkedModelSerializer):
    
    goals = serializer.HyperlinkedRelatedField(many=True, view_name="goal-details")
    
    class Meta:
        model=User
        fields="__all__"