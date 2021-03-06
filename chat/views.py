
from django.contrib.auth import get_user_model
from .models import (ChatSession, ChatSessionMember, ChatSessionMessage, deserialize_user)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from django.shortcuts import render

from notifications.signals import notify
# generate response module 
from . import geneRes
import re

# Create your views here.

class ChatSessionView(APIView):
  """Manage Chat sessions."""
  permission_classes = (permissions.IsAuthenticated,)
  def post(self, request, *args, **kwargs):
    """create a new chat session."""
    user = request.user
    chat_session = ChatSession.objects.create(owner=user)
    return Response({
      'status': 'SUCCESS', 'uri': chat_session.uri,
      'message': 'New chat session created'
    })

  def patch(self, request, *args, **kwargs):
    """Add a user to a chat session."""
    User = get_user_model()
    uri = kwargs['uri']
    username = request.data['username']
    user = User.objects.get(username=username)

    chat_session = ChatSession.objects.get(uri=uri)
    owner = chat_session.owner

    if owner != user:
      chat_session.members.get_or_create(
        user=user, chat_session=chat_session
      )

    owner = deserialize_user(owner)
    members = [
      deserialize_user(chat_session.user)
      for chat_session in chat_session.members.all()
    ]
    members.insert(0, owner) # Make the owner the first member

    return Response({
      'status': 'SUCCESS', 'members':members,
      'message': '%s joined that chat' % user.username,
      'user': deserialize_user(user)
    })

class ChatSessionMessageView(APIView):
  """Create/Get Chat session message."""
  permission_classes = (permissions.IsAuthenticated,)
  def get(self, request, *args, **kwargs):
    """return all messages in a chat session."""
    uri = kwargs['uri']
    chat_session = ChatSession.objects.get(uri=uri)
    messages = [chat_session_message.to_json()
        for chat_session_message in chat_session.messages.all()]

    return Response({
      'id': chat_session.id, 'uri': chat_session.uri,
      'messages': messages
    })

  def post(self, request, *args, **kwargs):
    """create a new message in a chat session."""
    print("entering post...")
    uri = kwargs['uri']
    message = request.data['message']
    print(message)

    user = request.user
    chat_session = ChatSession.objects.get(uri=uri)

    chat_session_message = ChatSessionMessage.objects.create(
      user=user, chat_session=chat_session, message=message
    )

    notif_args = {
      'source': user,
      'source_display_name': user.get_full_name(),
      'category': 'chat', 'action': 'Sent',
      'obj': chat_session_message.id,
      'short_description': 'You have a new message', 'silent': True,
      'extra_data': {
        'uri': chat_session.uri,
        'message': chat_session_message.to_json()
      }
    }
    notify.send(
      sender=self.__class__, **notif_args, channels=['websocket']
    )
    # customize ->_->
    # if re.search(r'.*', message) != None:
      # geneRes.gRes(uri)

    # generate response in
    if str(user) != 'hubot' and message[0] == '/':
      print('preparing generate response...')
      geneRes.geneResponse(message, uri)

    return Response({
      'status': 'SUCCESS', 'uri': chat_session.uri, 'message': message,
      'user': deserialize_user(user)
    })
