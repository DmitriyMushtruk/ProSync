from django.shortcuts import render

from django.shortcuts import render, get_object_or_404

from projects.models import Project
from .models import ChatRoom

def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    project = Project.objects.get(id=room.project_id)
    chat_messages = room.messages.order_by('created_at')
    current_user = request.user
    return render(
        request,
        'chats/chat.html',
        {
            'chat_room': room,
            'project': project,
            'chat_messages': chat_messages,
            'current_user': current_user,
        }
    )
