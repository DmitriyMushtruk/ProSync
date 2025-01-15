import pytest
from django.urls import reverse
from django.test import Client
from users.models import User
from projects.forms import ProjectCreateForm, JoinProjectForm
from projects.models import Project


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpassword')


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
@pytest.mark.parametrize("form_data", [
    {'name': 'Test Project 1', 'description': 'Test Description 1'},
    {'name': 'Another Project', 'description': 'Another Description'},
    {'name': 'Simple Name', 'description': 'Simple Description'},
    {'name': 'Project X', 'description': 'A very detailed description'},
    {'name': 'Short Name', 'description': 'Short description'},
])
def test_form_valid_data(user, form_data):
    form = ProjectCreateForm(data=form_data, owner=user)
    assert form.is_valid()

    project = form.save(commit=False)
    assert project.name == form_data['name']
    assert project.description == form_data['description']
    assert project.owner == user


@pytest.mark.django_db
@pytest.mark.parametrize("form_data", [
    {'name': '', 'description': 'Valid Description'},
    {'name': '', 'description': ''},
    {'name': ' ' * 5, 'description': 'Valid Description'},
])
def test_form_invalid_data(user, form_data):
    form = ProjectCreateForm(data=form_data, owner=user)
    assert not form.is_valid()
    assert 'name' in form.errors or 'description' in form.errors


@pytest.mark.django_db
def test_save_method_sets_owner(user):
    form_data = {
        'name': 'Test Project',
        'description': 'Test Description',
    }
    form = ProjectCreateForm(data=form_data, owner=user)
    project = form.save(commit=False)
    assert project.owner == user


@pytest.mark.django_db
def test_save_method_committed(user):
    form_data = {
        'name': 'Test Project',
        'description': 'Test Description',
    }
    form = ProjectCreateForm(data=form_data, owner=user)
    project = form.save(commit=True)
    assert Project.objects.filter(id=project.id).exists()


@pytest.mark.django_db
def test_project_create_view(client, user):
    client.login(username='testuser', password='testpassword')

    url = reverse('projects:new-project')
    data = {
        'name': 'New Project',
        'description': 'New Project Description',
    }
    response = client.post(url, data)

    assert response.status_code == 200
    project = Project.objects.get(name='New Project')
    assert project.description == 'New Project Description'
    assert project.owner == user


@pytest.mark.django_db
def test_project_create_view_invalid_data(client, user):
    client.login(username='testuser', password='testpassword')

    url = reverse('projects:new-project')
    data = {
        'name': '',
        'description': '',
    }
    response = client.post(url, data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_join_project_form_valid_data():
    form_data = {
        'access_key': 'validaccesskey12345',
    }
    form = JoinProjectForm(data=form_data)
    assert form.is_valid()


@pytest.mark.django_db
def test_join_project_form_invalid_data():
    form_data = {
        'access_key': '',
    }
    form = JoinProjectForm(data=form_data)
    assert not form.is_valid()
    assert 'access_key' in form.errors


@pytest.mark.django_db
def test_join_project_form_invalid_max_length():
    form_data = {
        'access_key': 'a' * 51,
    }
    form = JoinProjectForm(data=form_data)
    assert not form.is_valid()
    assert 'access_key' in form.errors
