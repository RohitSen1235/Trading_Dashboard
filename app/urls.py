from django.urls import path,include
from app import views

urlpatterns = [
    path('', views.index,name="index"),
    path('dashboard/', views.dashboard,name="dashboard"),
    path('dashboard/get-hit-ratio/', views.get_hitratio,name="hit_ratio"),
    path('dashboard/get-monthly-pnl/', views.get_monthly_profitloss,name="get_monthly_pnl"),
    path('dashboard/get-drawdown/', views.get_drawdown_analysis,name="get_drawdown"),

]