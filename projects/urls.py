from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('start/', views.StartView.as_view(), name='start'),
    path('new-project/', views.create_project_view, name='new-project'),
    path('main/<uuid:project_id>/', views.project_main_view, name='main'),
    path('create-task/<uuid:project_id>/', views.TaskCreateView.as_view(), name='create-task'),
    path('backlog/<uuid:project_id>/', views.BacklogView.as_view(), name='backlog'),
    path('task-detail/<uuid:task_id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('task-delete/<uuid:task_id>/', views.TaskDeleteView.as_view(), name='task-delete'),
]