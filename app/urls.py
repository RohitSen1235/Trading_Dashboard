from django.urls import path,include
from app import views

urlpatterns = [
    path('', views.index,name="index"),
    path('dashboard/', views.dashboard,name="dashboard"),

]