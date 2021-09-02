from django.shortcuts import render,redirect,reverse
from goals.forms import GoalForm, TaskForm
from random import randint
# Create your views here.

def landing(request):
    if request.method=="GET":
        request.session["newUser"]=True
        goals = [
            {
                "id":1111,
                "title": "Set your very first goal",
                "description":"Set a new goal to get use to, or to start your adventure. Press on the name of the goal to see all the tasks",
                "start_date":"2021-01-01 00:00:00",
                "end_date":"2021-02-01 00:00:00",
                "tasks":[
                    {   
                        "id":1111,
                        "content":"Create first goal by pressing add from the goals page",
                        "done":False
                    },
                        {   
                            "id":1110,
                            "content":"Finish your first task by pressing done next to the task",
                            "done":False
                        },
                        {   
                            "id":1112,
                            "content":"Edit first goal by pressing edit on the top left side of this page",
                            "done":False
                        },
                        {   
                            "id":1113,
                            "content":"Create first task by pressing add task",
                            "done":False
                        },
                        {   
                            "id":1114,
                            "content":"Edit first task by pressing edit next to the task",
                            "done":False
                        },
                        {   
                            "id":1115,
                             "content":"Delete first task by pressing delete next to the tast",
                            "done":False
                        },
                        {   
                            "id":1115,
                            "content":"Delete first goal by pressing delete on the top right side of the page",
                            "done":False
                        }
                        ]
                    }
                ]
        request.session["goals"] = goals
        template="goals/goals.html"
        content={
            "goals":goals,
        }
        return render(request, template, content)
    if request.method=="POST":
        title = request.POST.get("title") 
        description = request.POST.get("description")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        content = request.POST.get("content") 
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
        goals = request.session['goals']
        goals.append(newUserGoal)
        request.session["goals"]=goals
        return redirect(reverse("goals"))
