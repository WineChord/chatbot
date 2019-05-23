from django.contrib import admin

# Register your models here.

from .models import ChatSession, ChatSessionMember, ChatSessionMessage


admin.site.register((ChatSession, ChatSessionMember, ChatSessionMessage))