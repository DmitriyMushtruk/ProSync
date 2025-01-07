import uuid
from django.db import models
from users.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(
        'Project',
        on_delete=models.CASCADE,
        related_name='team'
    )

    def __str__(self):
        return f"Team for Project: {self.project.name}"


class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.username} in Team {self.team.id}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_owner")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    access_key = models.CharField(max_length=50, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.access_key:
            self.access_key = self.generate_access_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_access_key():
        return uuid.uuid4().hex[:10]

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('in progress', 'In progress'),
        ('to do', 'To do'),
        ('on hold', 'On hold'),
        ('done', 'Done'),
        ('backlog', 'Backlog'),
    ]

    PRIORITY_CHOICES = [
        ('trivial', 'Trivial'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='trivial')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    original_estimate = models.FloatField(default=0.0, help_text="Original time estimate in hours")
    remaining_estimate = models.FloatField(default=0.0, help_text="Remaining time estimate in hours")
    time_spent = models.FloatField(default=0.0, help_text="Time spent in hours")

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.task}"


class History(models.Model):
    ACTIONS = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('join', 'Join Member'),
        ('leave', 'Leave Member'),
        ('start', 'Start Project'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    action = models.CharField(max_length=20, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(null=True, blank=True, max_length=255)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'Histories'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} on {self.content_object} by {self.user}"
