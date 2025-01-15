from django import forms
from projects.models import Project, Task


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        self.owner = owner

    def save(self, commit=True):
        project = super().save(commit=False)
        project.owner = self.owner
        if commit:
            project.save()
        return project


class JoinProjectForm(forms.Form):
    access_key = forms.CharField(max_length=50, label="Access Key")


class TaskForm(forms.ModelForm):
    original_estimate = forms.CharField(
        required=True,
        help_text="Minutes must be an integer.",
        initial='0h 0m',
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'original_estimate']

    def clean_original_estimate(self):
        original_estimate = self.cleaned_data.get('original_estimate', '0h 0m')

        hours, minutes = 0, 0
        if 'h' in original_estimate:
            try:
                hours = int(original_estimate.split('h')[0].strip())
            except ValueError:
                raise forms.ValidationError("Hours must be an integer.")
        if 'm' in original_estimate:
            try:
                minutes = int(original_estimate.split('m')[0].split('h')[-1].strip())
            except ValueError:
                raise forms.ValidationError("Minutes must be an integer.")

        return hours + (minutes / 60)


class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'user']
