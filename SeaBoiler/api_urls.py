from django.urls import include, path

urlpatterns = [
    path('base/', include('Base.api_urls')),
    path('music/', include('Music.api_urls')),
]
