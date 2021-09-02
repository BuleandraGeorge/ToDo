from django.forms import ModelForm, Textarea
from django import forms
from goals.models import goal, task

class GoalForm(ModelForm):
    class Meta:
        model=goal
        fields=['title', 'description', 'start_date', 'end_date' ]
        widgets={
            'description': forms.Textarea(attrs={
                'class': "w-100 rounded-2"
            })
        }

class TaskForm(ModelForm):
    class Meta:
        model=task
        fields=['content', 'done']
        widgets={
            'content':  forms.Textarea(attrs={
                'class':"w-100 rounded-2 border-success",
            })
        }
        