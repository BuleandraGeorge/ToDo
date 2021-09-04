from django.shortcuts import render,redirect,reverse
from goals.forms import GoalForm, TaskForm
from random import randint
from django.views import View
from django.views.generic.base import ContextMixin
from .default_goals import default_goals
# Create your views here.

class NewUserView(View):

    template_name= "goals/goals.html"

    def get(self, *args, **kwargs):
        self.request.session["newUser"]=True
        self.request.session["goals"] = default_goals
        return render(self.request, self.template_name)

    def post(self, *args, **kwargs):
        title = self.request.POST.get("title") 
        description = self.request.POST.get("description")
        start_date = self.request.POST.get("start_date")
        end_date = self.request.POST.get("end_date")
        content = self.request.POST.get("content") 
        newUserTasks=[]
        newUserTasks.append({
            "id":randint(1, 1000),
            "content":content,
            "done":False
        })
        newUserGoal={
            "id": randint(1, 1000),
            "title":title,
            "description":description,
            "start_date":start_date,
            "end_date":end_date,
            "tasks":newUserTasks
        }
        goals = self.request.session['goals']
        goals.append(newUserGoal)
        self.request.session["goals"]=goals
        return redirect(reverse("goals"))
