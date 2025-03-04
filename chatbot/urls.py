from django.urls import path
from .views import ChatbotView, ChatbotSameThreadView

urlpatterns = [
    path("chatbot-home", ChatbotView.as_view(), name="chatbot-home" ),
    path("chatbot-samethread", ChatbotSameThreadView.as_view(), name="chatbot-home" ),
]