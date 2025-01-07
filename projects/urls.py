from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('start/', views.StartView.as_view(), name='start'),
    path('new-project/', views.CreateProjectView.as_view(), name='new-project'),
    path('join-project/', views.JoinProjectView.as_view(), name='join-project'),
    path('main/<uuid:project_id>/', views.ProjectMainView.as_view(), name='main'),
    path('create-task/<uuid:project_id>/', views.TaskCreateView.as_view(), name='create-task'),
    path('backlog/<uuid:project_id>/', views.BacklogView.as_view(), name='backlog'),
    path('task-detail/<uuid:task_id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('task-delete/<uuid:task_id>/', views.TaskDeleteView.as_view(), name='task-delete'),
    path('task-update/<uuid:task_id>/', views.TaskUpdateView.as_view(), name='task-update'),
    path('task-logtime/<uuid:task_id>/', views.TimeLogView.as_view(), name='task-logtime'),
    path('task/create-comment/', views.CreateCommentView.as_view(), name='create-comment'),
    path('board/<uuid:project_id>/', views.ProjectBoardView.as_view(), name='board'),
    path('charts/<uuid:project_id>/', views.ChartsView.as_view(), name='charts'),
]
