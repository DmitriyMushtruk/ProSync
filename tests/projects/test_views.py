import pytest
from django.urls import reverse
from users.models import User
from projects.models import Project, Team, TeamMember, Task, History
from chats.models import ChatRoom, ChatParticipant


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpassword')


@pytest.mark.django_db
def test_start_view_with_projects(user, client):
    project1 = Project.objects.create(
        name="Project 1",
        description="Description for Project 1",
        owner=user
    )

    team = Team.objects.create(project=project1)

    TeamMember.objects.create(team=team, user=user, role='member')

    client.login(username='testuser', password='testpassword')

    url = reverse('projects:start')
    response = client.get(url)

    assert response.status_code == 200
    assert 'projects' in response.context
    assert len(response.context['projects']) == 1
    assert response.context['projects'][0].name == 'Project 1'


@pytest.mark.django_db
def test_start_view_no_projects(user, client):
    client.login(username='testuser', password='testpassword')

    url = reverse('projects:start')
    response = client.get(url)

    assert response.status_code == 200
    assert 'projects' in response.context
    assert len(response.context['projects']) == 0


@pytest.mark.django_db
def test_create_project_integration(user, client):
    url = reverse('projects:new-project')
    data = {
        'name': 'Test Project',
        'description': 'Test Project Description',
    }
    client.login(username='testuser', password='testpassword')

    initial_project_count = Project.objects.count()
    initial_team_count = Team.objects.count()
    initial_chat_room_count = ChatRoom.objects.count()
    initial_chat_participant_count = ChatParticipant.objects.count()

    response = client.post(url, data)

    assert response.status_code == 200
    assert response.json()['success'] is True
    assert Project.objects.count() == initial_project_count + 1
    assert Team.objects.count() == initial_team_count + 1
    assert ChatRoom.objects.count() == initial_chat_room_count + 1
    assert ChatParticipant.objects.count() == initial_chat_participant_count + 1

    project = Project.objects.last()
    team = Team.objects.get(project=project)
    chat_room = ChatRoom.objects.get(project=project)

    assert team.members.count() == 1
    assert ChatParticipant.objects.filter(room=chat_room).count() == 1


@pytest.mark.django_db
def test_join_project_view_valid_key(user, client):
    client.login(username='testuser', password='testpassword')

    project = Project.objects.create(
        name='Test Project',
        description='Test Project Description',
        owner=user,
        access_key='validaccesskey12345'
    )
    Team.objects.create(project=project)

    url = reverse('projects:join-project')
    data = {
        'access_key': project.access_key,
    }
    response = client.post(url, data)
    expected_url = f'/projects/main/{project.id}/'

    assert response.status_code == 302
    assert response['Location'] == expected_url


@pytest.mark.django_db
def test_join_project_view_invalid_key(user, client):
    client.login(username='testuser', password='testpassword')

    Project.objects.create(name='Test Project', description='Test Project Description',
                           access_key='validaccesskey12345', owner=user)

    url = reverse('projects:join-project')
    data = {
        'access_key': 'wrongaccesskey111',
    }
    response = client.post(url, data)

    assert response.status_code == 404
    assert 'Invalid access key' in response.content.decode()


@pytest.mark.django_db
def test_task_delete_view_success(client, user):
    client.login(username='testuser', password='testpassword')

    project = Project.objects.create(
        name='Test Project',
        description='Test Description',
        owner=user,
    )

    task = Task.objects.create(
        title='Test Task',
        description='Test Task Description',
        project=project,
        user=user,
    )

    history_record = History.objects.create(
        project=project,
        user=user,
        action='delete',
        description="Task was deleted",
        content_object=task,
    )

    url = reverse('projects:task-delete', kwargs={'task_id': task.id})
    response = client.delete(url)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['message'] == 'Task deleted successfully!'
    assert response_data['task_id'] == str(task.id)
    assert history_record is not None
