from django.urls import path

# /api/music/ POST 插入一条music
# /api/music/name POST 修改music的name
from Music.api_views import MusicView, ConsiderView

urlpatterns = [
    path('list', MusicView.as_view()),
    path('recommend', MusicView.as_view()),
    path('update', MusicView.as_view()),
    path('consider', ConsiderView.as_view())
    # path('list', MusicListView.as_view())
    # path('name', MusicNameView.)
]