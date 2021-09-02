from django import template
register = template.Library()

def progress(tasks):
    taskDone=0
    for task in tasks:
        if task.done:
            taskDone+=1
    if len(tasks)==0:
        return 0.0
    else:
        return (format((taskDone/len(tasks))*100, ".1f"))

register.filter("progress", progress)