from django.contrib import admin
from django.urls import path
from newUser import views

urlpatterns = [
    path('', views.landing, name="newUser"),
]