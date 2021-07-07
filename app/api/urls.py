from django.urls import path, re_path
from .views import UsersListView, UserRegisterView, UserLoginView, LogoutView, TeamDetailView, TeamUpdateView, PlayerUpdateView

urlpatterns = [
    path('user/register', UserRegisterView.as_view(), name='user_register'),
    path('user/login', UserLoginView.as_view(), name='user_login'),
    path('user/logout', LogoutView.as_view(), name='user_logout'),

    path('user/team', TeamDetailView.as_view(), name='user_team_details'),
    path('user/team/update', TeamUpdateView.as_view(), name='user_team_update'),
    path('user/player/update', PlayerUpdateView.as_view(), name='team_player_update'),

    path('users/', UsersListView.as_view(), name='users_list'),

]