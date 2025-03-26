from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('search/', views.search, name='search'),
    path('get_charts/', views.get_charts, name='get_charts'),
    path('music/', views.music_page, name='music_page'),
    path('artist/<int:artist_id>/', views.artist_profile, name='artist_profile'),
    path('play_track/<int:track_id>/', views.play_track, name='play_track'),
]