import json

from django.contrib.contenttypes.models import ContentType
from django.views.generic import ListView, DetailView, DeleteView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from users.models import User
from chats.models import ChatRoom, ChatParticipant
from .forms import ProjectCreateForm, JoinProjectForm, TaskForm
from .models import Project, Team, TeamMember, History, Comment
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views import View
from .models import Task
from django.core.exceptions import ObjectDoesNotExist

from .services.history_service import HistoryService
from django.utils.timezone import now
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect


class StartView(TemplateView):
    template_name = 'projects/start.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['projects'] = Project.objects.filter(
            team__members__user=user
        ).distinct()
        return context


class CreateProjectView(LoginRequiredMixin, CreateView):
    def post(self, request, *args, **kwargs):
        form = ProjectCreateForm(request.POST, owner=request.user)

        if form.is_valid():
            project = form.save()
            team = Team.objects.create(project=project)
            team.members.create(user=request.user, role='owner')
            chat_room = ChatRoom.objects.create(project=project)

            participants = [
                ChatParticipant(room=chat_room, user=member.user, last_active=now())
                for member in team.members.all()
            ]
            ChatParticipant.objects.bulk_create(participants)

            HistoryService.create_history_entry(
                project=project,
                user=request.user,
                action='create',
                description=f"Project '{project.name}' was created.",
                content_object=project
            )

            return JsonResponse({'success': True, 'project_id': project.id})
        return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)

# TODO update redirect here ->
class JoinProjectView(LoginRequiredMixin, View):
    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        access_key = request.POST.get('access_key')

        if not access_key:
            return JsonResponse({'error': 'Access key is required.'}, status=400)

        try:
            project = Project.objects.get(access_key=access_key)

            created, _ = TeamMember.objects.get_or_create(
                team=project.team,
                user=request.user,
                defaults={'role': 'member'}
            )

            HistoryService.create_history_entry(
                project=project,
                user=self.request.user,
                action='join',
                description=f"{self.request.user} has been joined",
                content_object=project
            )

            if created:
                messages.success(self.request, f"You've successfully joined {project.name}.")
            else:
                messages.info(self.request, f"You are already a member of {project.name}.")

            project_main_url = reverse('projects:main', kwargs={'project_id': project.id})
            return HttpResponseRedirect(project_main_url)

        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Invalid access key.'}, status=404)

class ProjectMainView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/main.html'
    pk_url_kwarg = 'project_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        members = TeamMember.objects.filter(team=project.team)
        tasks = Task.objects.filter(project=project)
        history_items = project.history.all().order_by('timestamp')
        chat_room = ChatRoom.objects.get(project=project)
        print(chat_room.id)


        context['members'] = members
        context['tasks'] = tasks
        context['status_choices'] = Task.STATUS_CHOICES
        context['priority_choices'] = Task.PRIORITY_CHOICES
        context['history_items'] = history_items
        context['chat_room'] = chat_room

        return context


class ProjectBoardView(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return render(request, 'projects/main.html', {'error': 'Project not found'})

        members = TeamMember.objects.filter(team=project.team)
        filter_user_id = request.GET.get('filter', 'all')

        if filter_user_id == 'all':
            tasks = Task.objects.filter(project=project).order_by('updated_at')
        else:
            try:
                user = User.objects.get(id=filter_user_id)
                tasks = Task.objects.filter(project=project, user=user).order_by('updated_at')
            except User.DoesNotExist:
                tasks = Task.objects.none()

        chat_room = ChatRoom.objects.get(project=project)

        priority_icons = {
            "trivial": 1,
            "low": 2,
            "medium": 3,
            "high": 4,
        }

        context = {
            'project': project,
            'tasks': tasks,
            'members': members,
            'selected_filter': filter_user_id,
            "priority_icons": priority_icons,
            'chat_room': chat_room
        }
        return render(request, 'projects/board.html', context)


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
        response = super().form_valid(form)
        HistoryService.create_history_entry(
            project=project,
            user=self.request.user,
            action='create',
            description=f"Task was created",
            content_object=self.object
        )
        messages.success(self.request, f'Task successfully created.')
        return response

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
        context['chat_room'] = ChatRoom.objects.get(project_id=project_id)
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

        comments = task.comments.select_related('user').all()
        comments_data = [
            {
                'type': 'comment',
                'timestamp': comment.timestamp.strftime('%d.%m.%y at %H:%M:%S'),
                'user': comment.user.username,
                'description': comment.description,
            }
            for comment in comments
        ]

        history_entries = History.objects.filter(
            content_type=ContentType.objects.get_for_model(Task),
            object_id=str(task.id)
        ).select_related('user')

        history_data = [
            {
                'type': 'history',
                'timestamp': history.timestamp.strftime('%d.%m.%y at %H:%M:%S'),
                'user': history.user.username if history.user else "System",
                'description': history.description,
            }
            for history in history_entries
        ]

        combined_data = sorted(
            comments_data + history_data,
            key=lambda x: x['timestamp']
        )

        task_data = {
            'id': task.id,
            'user': {
                'id': task.user.id,
                'username': task.user.username,
            },
            'status': task.status,
            'priority': task.priority,
            'created_at': task.created_at.strftime('%d.%m.%y at %H:%M'),
            'updated_at': task.updated_at.strftime('%d.%m.%y at %H:%M'),
            'original_estimate': self.format_time(task.original_estimate),
            'remaining_estimate': self.format_time(task.remaining_estimate),
            'title': task.title,
            'description': task.description,
            'comments_and_history': combined_data,
        }

        return JsonResponse(task_data)


class TaskDeleteView(DeleteView):
    model = Task
    pk_url_kwarg = 'task_id'

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task_id = task.id
        project = Project.objects.get(id=task.project.id)
        HistoryService.create_history_entry(
            project=project,
            user=self.request.user,
            action='delete',
            description=f"Task was deleted",
            content_object=task
        )
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return JsonResponse({'message': 'Task deleted successfully!', 'task_id': task_id})


class TaskUpdateView(View):
    # noinspection PyMethodMayBeStatic
    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        project = Project.objects.get(id=task.project.id)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.status = data.get('status', task.status)
        task.priority = data.get('priority', task.priority)

        user_username = data.get('user')
        if user_username:
            user = get_object_or_404(User, username=user_username)
            task.user = user

        task.save()

        HistoryService.create_history_entry(
            project=project,
            user=self.request.user,
            action='update',
            description=f"Task was updated",
            content_object=task
        )
        messages.success(request, 'Task updated successfully!')
        return JsonResponse({'success': True, 'message': 'Task updated successfully.'})

class TimeLogView(View):
    # noinspection PyMethodMayBeStatic
    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        project = Project.objects.get(id=task.project.id)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

        hours = int(data.get('worked').split('h')[0].strip())
        minutes = int(data.get('worked').split('m')[0].split('h')[-1].strip())
        worked = hours + (minutes / 60)

        task.remaining_estimate -= worked
        task.time_spent += worked

        task.save()

        HistoryService.create_history_entry(
            project=project,
            user=self.request.user,
            action='update',
            description=f" Worked on task {data.get('worked')}: {data.get('description')}",
            content_object=task
        )

        messages.success(request, 'Time successfully was logged!')
        return JsonResponse({'success': True, 'message': 'Time successfully was logged.'})



class CreateCommentView(View):
    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)  # Распарсить JSON из тела запроса
            task_id = data.get('task_id')
            description = data.get('description')
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

        if not task_id or not description:
            return JsonResponse({'error': 'Task ID and description are required.'}, status=400)

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found.'}, status=404)

        comment = Comment.objects.create(
            task=task,
            user=request.user,
            description=description
        )
        messages.success(request, 'Comment created successfully!')
        return JsonResponse({'message': 'Comment created successfully.', 'comment': comment.description})


class ChartsView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/charts.html'
    pk_url_kwarg = 'project_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        members = TeamMember.objects.filter(team=project.team)
        tasks = Task.objects.filter(project=project)
        history_items = project.history.all().order_by('timestamp')
        chat_room = ChatRoom.objects.get(project=project)

        task_data = tasks.values('status', 'priority')
        task_status_chart = {
            'in progress': 0,
            'to do': 0,
            'on hold': 0,
            'done': 0,
            'backlog': 0,
            'trivial': 0,
            'low': 0,
            'medium': 0,
            'high': 0,
        }

        for task in task_data:
            status = task['status']
            priority = task['priority']
            if status in task_status_chart:
                task_status_chart[status] += 1
            if priority == task_status_chart:
                task_status_chart[priority] += 1

        context['members'] = members
        context['tasks'] = json.dumps(list(task_data))
        context['status_choices'] = Task.STATUS_CHOICES
        context['priority_choices'] = Task.PRIORITY_CHOICES
        context['history_items'] = history_items
        context['chat_room'] = chat_room
        context['status_counts'] = task_status_chart

        return context

