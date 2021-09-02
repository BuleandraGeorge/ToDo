from django.contrib import admin
from django.urls import path
from userProfile import views

urlpatterns = [
    path('', views.userProfile, name="profile"),
    path('checkout/', views.checkout, name='checkout'),
    path('update_subscription/', views.update_subscription, name='update_sub'),
    path('reactivate_subscription/', views.reactivate_subscription, name='reactivate_sub'),
    path('cancel_subscription/<str:sub_id>/<int:now>/', views.subscription_cancel, name='cancel_sub'),
    path('success/<int:sub_id>/', views.subscription_success, name="success"),
    path('update_payment_details/', views.payment, name='payment_details'),
    path('delete_card/<str:id_pm>/', views.delete_card, name="delete_pm"),
    path('webhook/', views.webhook_received, name='wh')
]