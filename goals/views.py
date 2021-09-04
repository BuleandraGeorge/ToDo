from django.shortcuts import render, redirect,reverse, get_object_or_404
from goals.forms import GoalForm,TaskForm
from goals.models import goal, task
from userProfile.models import profile, subscription
from django.conf import settings
from random import randint
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.views.generic import ListView


def goals(request):
    active_services=request.session.get("active_services", [])
    if request.user.is_authenticated:
        profile=request.user.profile
        exists_sub=subscription.objects.filter(profile=profile, service__name="Goals")
        if "Goals" in active_services:
            active_services.remove('Goals')
        if exists_sub:
            the_sub = exists_sub[0]
            if the_sub.is_active():
                active_services.append('Goals')
        goals=goal.objects.filter(owner=profile)
        request.session['active_services']=active_services
    else:
        if not "Goals" in request.session.get("active_services", []):
            active_services.append('Goals')
            request.session['active_services']=active_services
        goals=request.session.get('goals', [])
        if not goals:
            return redirect(reverse('newUser'))
    context={
            "goalform":GoalForm,
            "taskform":TaskForm,
            "goals":goals,
            'active_services':active_services
        }
    template="goals/goals.html"
    return render(request,template, context)

def goalDetails(request, pk):
    if not "Goals" in request.session.get('active_services',[]):
       return redirect(reverse('profile'))
    if request.user.is_authenticated:
        profile=request.user.profile
        thegoal=get_object_or_404(goal, owner=profile, pk=pk)
        tasks= thegoal.task_set.all()
    else:
        goals = request.session.get("goals")
        for x in goals:
            if x["id"] == pk:
                thegoal = x
                break
        tasks=[]
        tasks.extend(thegoal["tasks"])
    template="goals/goal_details.html"
    context={
        "goal": thegoal,
        "tasks":tasks,
    }
    return render(request, template, context)

def goalAdd(request):
    if not "Goals" in request.session.get("active_services", []):
        return redirect(reverse('profile'))
    if request.session["newUser"]:
        template="newUser/landingPage.html"
        content={
            "taskForm":TaskForm,
            "goalForm":GoalForm,
        }
        request.session['newUser']=False
        return render(request, template, content)
    if request.method=="GET":
        context={
            "goalform":GoalForm,
            "taskform":TaskForm,
        }
        template="goals/addGoal.html"
        return render(request,template, context)

    if request.method=="POST":
        if request.user.is_authenticated:
            title = request.POST.get("title") 
            description = request.POST.get("description")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            newGoal = goal(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                owner=request.user.profile
                )
            newGoal.save()
            content = request.POST.get("content") 
            done = request.POST.get("done") != None
            newTask=task(
                content=content,
                done=done,
                goal=newGoal
            )
            newTask.save()
            goal_id=newGoal.id
        else:
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
            goals = request.session["goals"]
            goals.append(newUserGoal)
            request.session["goals"] = goals
            goal_id=newUserGoal['id']
        return redirect(reverse("goalDetails", args=[goal_id]))

def editGoal(request, goal_id):
    if not "Goals" in request.session['active_services']:
        return redirect(reverse('profile'))
    if request.method == "GET":
        if request.user.is_authenticated:
            profile=request.user.profile
            theGoal = get_object_or_404(goal, owner=profile, pk=goal_id)
            theForm = GoalForm(instance=theGoal)
        else:
            goals = request.session.get('goals')
            for x in goals:
                if x["id"] == goal_id:
                    theGoal = x
                    break
            data={
                "title":theGoal['title'],
                "description":theGoal['description'],
                "start_date":theGoal['start_date'],
                "end_date":theGoal['end_date']
            }
            theForm=GoalForm(data)
        context={
            "goalform":theForm,
            "goal":theGoal,
        }
        template="goals/editGoal.html"
        return render(request, template, context)
    if request.method == "POST":
        if request.user.is_authenticated:
            profile=request.user.profile
            theGoal = get_object_or_404(goal, owner=profile, pk=goal_id)
            theGoal = GoalForm(request.POST, instance = theGoal)
            theGoal.save()
        else:
            goals = request.session.get('goals')
            for x in goals:
                if x["id"] == goal_id:
                    theGoal = x
                    break
            title = request.POST.get("title") 
            description = request.POST.get("description")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            theGoal.update({
                "title": title,
                "description":description,
                "start_date":start_date,
                "end_date":end_date
                })
            for x in goals:
                if x["id"] == goal_id:
                    x=theGoal
                    request.session['goals']=goals
                    break
        return redirect(reverse(goalDetails, args=[goal_id]))

def goalDelete(request, goal_id):
    if not "Goals" in request.session['active_services']:
        return redirect(reverse('profile'))
    if request.user.is_authenticated:
        profile=request.user.profile
        thegoal = get_object_or_404(goal,owner=profile,pk=goal_id)
        thegoal.delete()
    else:
        goals = request.session.get("goals")
        for x in goals:
            if x["id"] == goal_id:
                goals.remove(x)
                request.session["goals"]=goals
                break
    return redirect("goals")

def addTask(request, goal_id):
    if not "Goals" in request.session['active_services']:
        return redirect(reverse('profile'))
    if request.method=="POST":
        if request.user.is_authenticated:
            content = request.POST.get("content") 
            done = request.POST.get("done") != None
            profile=request.user.profile
            Goal = get_object_or_404(goal,owner=profile,pk=goal_id)
            newTask=task(
                content=content,
                done=done,
                goal=Goal
            )
            newTask.save()
        else:
            goals = request.session["goals"]
            for x in goals:
                if x["id"] == goal_id:
                    theGoal = x
            content = request.POST.get("content") 
            done = request.POST.get("done") != None
            Tasks = theGoal["tasks"]
            Tasks.append({
            "id":randint(1, 1000),
            "content":content,
            "done":False
            })
            theGoal["tasks"]=Tasks
            for x in goals:
                if x["id"] == goal_id:
                    x=theGoal
            request.session["goals"]=goals
        return redirect(reverse('goalDetails', args=[goal_id]))
    if request.method=="GET":
        if request.user.is_authenticated:
            profile=request.user.profile
            Goal = get_object_or_404(goal,owner=profile,pk=goal_id)
            Goal=goal.objects.get(pk=goal_id)
            Tasks=Goal.task_set.all()
        else:
            goals = request.session["goals"]
            for x in goals:
                if x["id"] == goal_id:
                    Goal = x
            Tasks = Goal["tasks"]
        template="goals/addTask.html"
        context={
                "taskform":TaskForm,
                "goal":Goal,
                "tasks":Tasks
            }
        return render(request, template, context)

def updateTask(request, task_id, status):
    if not "Goals" in request.session['active_services']:
        return redirect(reverse('profile'))
    if request.user.is_authenticated:
        from goals.models import task
        Task=task.objects.get(pk=task_id)
        goal_id=Task.goal.id
        if status == "done":
            Task.done=True
            Task.save()
        elif status == "undone":
            Task.done=False
            Task.save()
        else:
            Task.delete()
    else:
        goals = request.session['goals']
        for goal in goals:
            for task in goal['tasks']:
                if task_id == task['id']:
                    Task = task
                    goal_id=goal['id']
                    break
        if status == "done":
            Task["done"]=True
            for goal in goals:
                for task in goal['tasks']:
                    if task_id == task['id']:
                        task = Task
                        request.session['goals']=goals
                        break
        elif status == "undone":
            Task["done"]=False
            for goal in goals:
                for task in goal['tasks']:
                    if task_id == task['id']:
                        task = Task
                        request.session['goals']=goals
                        break
        else:
            for goal in goals:
                for task in goal['tasks']:
                    if task_id == task['id']:
                        goal['tasks'].remove(task)
                        request.session['goals']=goals
                        break
    return redirect(reverse('goalDetails', args=[goal_id]))


def editTask(request, task_id):
    if not "Goals" in request.session['active_services']:
        return redirect(reverse('profile'))
    if request.method == "GET":
        if request.user.is_authenticated:
            from .models import task
            theTask = get_object_or_404(task, pk=task_id)
            theForm = TaskForm(instance=theTask)
            theGoal = theTask.goal
        else:
            goals = request.session['goals']
            for goal in goals:
                for task in goal['tasks']:
                    if task_id == task['id']:
                        theTask = task
                        theGoal=goal
                        theForm=TaskForm(data={
                            "content":theTask['content'],
                            "done":theTask['done']
                        })
                        break
        context={
            "taskform":theForm,
            "goal": theGoal,
            "task": theTask,
        }
        template="goals/editTask.html"  
        return render(request, template, context)
    if request.method == "POST":
        if request.user.is_authenticated:
            from .models import task
            theTask = get_object_or_404(task, pk=task_id)
            theForm = TaskForm(request.POST, instance = theTask)
            theForm.save()
            goal_id = theTask.goal.id
        else:
            goals = request.session['goals']
            for goal in goals:
                for task in goal['tasks']:
                    if task_id == task['id']:
                        goal_id=goal['id']
                        task['content']=request.POST['content']
                        task['done'] =  None
                        request.session['goals']=goals
                        break
        return redirect(reverse(goalDetails, args=[goal_id]))