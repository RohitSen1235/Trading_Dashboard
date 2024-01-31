from django.urls import path,include
from app import views

urlpatterns = [
    path('', views.index,name="index"),
    path('save-db/',views.save_sector_db, name="save_db"),
    path('dashboard/', views.dashboard,name="dashboard"),
    # 
    path('get-hit-ratio/', views.get_overall_hitratio,name="hit_ratio"),
    path('get-monthly-pnl/', views.get_overall_monthly_profitloss,name="get_monthly_pnl"),
    path('get-drawdown/', views.get_drawdown_analysis,name="get_drawdown"),
    path('get-sector-pnl/', views.get_overall_sector_profitloss,name="get_sector_pnl"),
    # 
    path('dashboard/intraday-stats/', views.intraday_stats,name="intraday_stats"),
    path('dashboard/swing-stats/', views.swing_stats,name="swing_stats"),

    # 
    path('get-hit-ratio/<str:segment>/', views.get_segment_hitratio,name="segment_hit_ratio"),
    path('get-monthly-pnl/<str:segment>/', views.get_segment_monthly_profitloss,name="segment_monthly_pnl"),
    path('get-sector-pnl/<str:segment>/', views.get_segment_sector_profitloss,name="segment_sector_pnl"),
]