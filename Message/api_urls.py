from django.urls import path

from Message.api_views import MessageView

urlpatterns = [
    path('', MessageView.as_view())
]
