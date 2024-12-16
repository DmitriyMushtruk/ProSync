from django.forms import model_to_dict
from django.views.generic import ListView, DetailView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProjectCreateForm, JoinProjectForm, TaskForm
from .models import Project, Team, TeamMember, Task
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect

from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy


class StartView(TemplateView):
    template_name = 'projects/start.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['projects'] = Project.objects.filter(
            team__members__user=user
        ).distinct()
        return context


@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectCreateForm(request.POST, owner=request.user)
        if form.is_valid():
            project = form.save()
            team = Team.objects.create(project=project)
            team.members.create(user=request.user, role='owner')
            return JsonResponse({'success': True, 'project_id': project.id})
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def join_project_view(request):
    if request.method == 'POST':
        form = JoinProjectForm(request.POST)
        if form.is_valid():
            access_key = form.cleaned_data['access_key']
            try:
                project = Project.objects.get(access_key=access_key)
                TeamMember.objects.get_or_create(
                    team=project.team,
                    user=request.user,
                    defaults={'role': 'member'}
                )
                messages.success(request, f"You've successfully joined {project.name}.")
                return redirect('project_detail', project_id=project.id)
            except Project.DoesNotExist:
                form.add_error('access_key', "Invalid access key.")
    else:
        form = JoinProjectForm()
    return render(request, 'projects/join_project.html', {'form': form})

@login_required
def project_main_view(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    members = get_list_or_404(TeamMember, team=project.team)
    tasks = Task.objects.filter(project=project)

    print(request.path)
    return render(
        request,
        'projects/main.html',
        {
            'project': project,
            'members': members,
            'tasks': tasks,
            'status_choices': Task.STATUS_CHOICES,
            'priority_choices': Task.PRIORITY_CHOICES,
        }
    )

def create_task_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.project = project
            task.save()
            return HttpResponseRedirect(f'/projects/main/{project_id}/')
    else:
        form = TaskForm()

    return render(request, 'projects/main.html', {'project': project, 'form': form})

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/main.html'

    def form_valid(self, form):
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        form.instance.project = project
        form.instance.user = self.request.user
        form.instance.remaining_estimate = form.instance.original_estimate
        messages.success(self.request, f'Task successfully created.')
        return super().form_valid(form)

    def get_success_url(self):
        project_id = self.kwargs['project_id']
        return reverse_lazy('projects:main', kwargs={'project_id': project_id})


class BacklogView(ListView):
    model = Task
    template_name = 'projects/backlog.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        queryset = Task.objects.filter(project_id=project_id)

        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        user_filter = self.request.GET.get('user')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if user_filter:
            queryset = queryset.filter(user__username=user_filter)

        sort_by = self.request.GET.get('sort_by', 'created_at')
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        context['project'] = Project.objects.get(id=project_id)
        context['members'] = TeamMember.objects.filter(team=context['project'].team)

        context['current_status'] = self.request.GET.get('status', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['current_user'] = self.request.GET.get('user', '')
        return context


class TaskDetailView(DetailView):
    model = Task

    def get_object(self, queryset=None):
        task_id = self.kwargs.get('task_id')
        return get_object_or_404(Task, id=task_id)

    @staticmethod
    def format_time(decimal_time):
        """Convert decimal time to 'Xh Ym' format."""
        hours = int(decimal_time)
        minutes = int((decimal_time - hours) * 60)
        return f"{hours}h {minutes}m"

    def get(self, request, *args, **kwargs):
        task = self.get_object()

        task_data = model_to_dict(task)
        task_data['id'] = task.id
        task_data['user'] = {
            'id': task.user.id,
            'username': task.user.username,
            'email': task.user.email,
        }
        task_data['created_at'] = task.created_at.strftime('%d.%m.%y at %H:%M')
        task_data['updated_at'] = task.updated_at.strftime('%d.%m.%y at %H:%M')
        task_data['original_estimate'] = self.format_time(task_data['original_estimate'])
        task_data['remaining_estimate'] = self.format_time(task_data['remaining_estimate'])
        return JsonResponse(task_data)


class TaskDeleteView(DeleteView):
    model = Task
    pk_url_kwarg = 'task_id'

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task_id = task.id
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return JsonResponse({'message': 'Task deleted successfully!', 'task_id': task_id})
