from rest_framework import serializers

from .models import goal, task

class GoalSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source="user.email")
    tasks = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="task-details"
    )
    class Meta:
        model = goal
        fields='__all__'


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    goal = serializers.ReadOnlyField(source="goal.title")

    class Meta:
        model = task
        fields="__all__"
