# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from projects.models import Project
# from .models import ChatRoom, ChatParticipant
# from django.utils.timezone import now
#
# from django.db import transaction
#
# @receiver(post_save, sender=Project)
# def create_chat_room(sender, instance, created, **kwargs):
#     if created:
#         def create_chat_and_participants():
#             chat_room = ChatRoom.objects.create(project=instance)
#             team_members = instance.team.members.all()
#
#             participants = [
#                 ChatParticipant(room=chat_room, user=member.user, last_active=now())
#                 for member in team_members
#             ]
#             ChatParticipant.objects.bulk_create(participants)
#
#         transaction.on_commit(create_chat_and_participants)

