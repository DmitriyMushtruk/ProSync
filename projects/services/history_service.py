# services/history_service.py
from projects.models import History

class HistoryService:
    @staticmethod
    def create_history_entry(project, user, action, description='', content_object=None):
        return History.objects.create(
            project=project,
            user=user,
            action=action,
            description=description,
            content_object=content_object
        )

    @staticmethod
    def filter_project_history(project):
        history = project.history.all()
        history_items = [{'description': history.first().description, 'position': 'center'}]

        for index, item in enumerate(history[1:], start=1):
            position = 'left' if index % 2 == 0 else 'right'
            history_items.append({'description': item.description, 'position': position})

        return history_items
