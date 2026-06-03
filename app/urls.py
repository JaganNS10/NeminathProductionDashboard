from django.urls import path
from . import views
from app.views import (production_update, after_assembly, work_done_today)
urlpatterns = [
    path('',views.base,name='base'),
    path('apps_tasks/',views.apps_tasks,name='apps_tasks'),
    path('apps_tasks_seen/<int:id>/',views.apps_tasks_seen,name='apps_tasks_id'),
    path('apps_tasks_update/<int:id>/',views.apps_tasks_update,name='apps_tasks_update'),
    path('employee/<str:username>/', views.dashboard, name='dashboard'),
    path('Employeelogin/', views.employee_login, name='employee_login'),
    path('auth_login_minimal/',views.auth_login_minimal,name='auth_login_minimal'),
    path('logout/',views.logout_view,name='logout'),
    path('leads_create/',views.leads_create,name='leads_create'),
    path('leads_view/',views.leads_view,name='leads_view'), 
    path('leads_view/<int:id>/',views.leads_view,name='leads_view'),   
    path('leads/',views.leads,name='leads'),
    path('leads_update/<int:employee_id>/',views.leads_update,name='leads_update'),
    path('leads_delete/<int:employee_id>/',views.leads_delete,name='leads_delete'),
    path('Employeeoverallperformance/',views.leaderboard_view,name='leaderboard'),
    path('production-update/', production_update, name='production_update'),
    path('after-assembly/', after_assembly, name='after_assembly'),
    path('work-done-today/', work_done_today, name='work_done_today'),
    path('sheet/<slug:slug>/', views.process_sheet, name='process_sheet'),
]
