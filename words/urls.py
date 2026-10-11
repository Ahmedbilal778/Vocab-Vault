from django.urls import path
from . import views as v
urlpatterns = [
    path("", v.dashboard, name="dashboard"),
    path("vocabulary/", v.vocabulary, name="vocabulary"),
    path("add/", v.add_word, name="add_word"),
    path("delete/<int:pk>/", v.delete_word, name="delete_word"),
    path("practice/", v.zone, name="zone"),
    path("revision/", v.revision, name="revision"),
    path("practice/play/", v.play, name="play"),
    path("progress/", v.progress, name="progress"),
    path("speaking/", v.speaking, name="speaking"),
    path("ai/word/", v.ai_word, name="ai_word"),
    path("ai/conversation/", v.conversation, name="conversation"),
    path("ai/chat/", v.ai_chat, name="ai_chat"),
    path("achievements/", v.achievements, name="achievements"),
    path("settings/", v.settings_page, name="settings"),
]
