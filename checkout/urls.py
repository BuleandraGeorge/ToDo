from django.urls import path
urlpatterns=[
    path('', views.checkout, name='checkout'),
    path('success/', views.subscription_success, name="success"),
    path('cancel/', views.subscription_cancel, name="cancel"),
]