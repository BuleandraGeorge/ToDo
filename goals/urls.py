from django.contrib import admin
from django.urls import path
from goals import views

urlpatterns = [
    path('', views.goals, name="goals"),
    path('<int:pk>/', views.goalDetails, name="goalDetails"),
    path('delete/<int:goal_id>/', views.goalDelete, name="goalDelete"),
    path('addGoal/', views.goalAdd, name="goalAdd"),
    path('addTask/<int:goal_id>/', views.addTask, name="addTask"),
    path('updateTask/<int:task_id>/<str:status>/', views.updateTask, name="updateTask"),
    path('editTask/<int:task_id>/', views.editTask, name="editTask"),
    path('editGoal/<int:goal_id>/', views.editGoal, name="editGoal"),
]