from django.urls import path, re_path
from .views import UsersListView, UserRegisterView, UserLoginView, LogoutView, TeamDetailView, TeamUpdateView, \
    PlayerUpdateView, SetPlayerToTransferList, TransferListView, BuyTransferView, UserUpdateView, UserDeleteView, \
    TeamListView, TeamCreateView, TeamDeleteView, PlayerCreateView, PlayerListView, PlayerDelete

urlpatterns = [
    path('user/register', UserRegisterView.as_view(), name='user_register'),
    path('user/login', UserLoginView.as_view(), name='user_login'),
    path('user/logout', LogoutView.as_view(), name='user_logout'),

    path('team/create', TeamCreateView.as_view(), name='team_create'),  # only for admin
    path('team/list', TeamListView.as_view(), name='team_list'),  # only for admin
    path('team/update', TeamUpdateView.as_view(), name='team_update'),
    path('team/delete', TeamDeleteView.as_view(), name='team_delete'),  # only for admin
    path('team/details', TeamDetailView.as_view(), name='team_details'),

    path('player/create', PlayerCreateView.as_view(), name='player_create'),  # only for admin
    path('player/list', PlayerListView.as_view(), name='player_list'),  # only for admin
    path('player/update', PlayerUpdateView.as_view(), name='player_update'),
    path('player/delete', PlayerDelete.as_view(), name='player_delete'),  # only for admin

    path('transfer/set', SetPlayerToTransferList.as_view(), name='set_player_to_transfer_list'),
    path('transfer/list', TransferListView.as_view(), name='transfer_list'),
    path('transfer/buy', BuyTransferView.as_view(), name='transfer_buy'),

    # only admin apis
    path('users/', UsersListView.as_view(), name='users_list'),
    path('user/update', UserUpdateView.as_view(), name='user_update'),
    path('user/delete', UserDeleteView.as_view(), name='user_delete'),



]
