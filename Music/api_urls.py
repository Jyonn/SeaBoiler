from django.urls import path

# /api/music/ POST 插入一条music
# /api/music/name POST 修改music的name
from Music.api_views import RecommendView, MusicListView

urlpatterns = [
    path('recommend', RecommendView.as_view()),
    path('list', MusicListView.as_view())
    # path('name', MusicNameView.)
]