from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    path('<uuid:room_id>/', views.chat_room, name='chat_room'),
]
