from django.urls import path, re_path
from .views import UsersListView, UserRegisterView, UserLoginView, LogoutView

urlpatterns = [
    path('user/register', UserRegisterView.as_view(), name='user_register'),
    path('user/login', UserLoginView.as_view(), name='user_login'),
    path('user/logout', LogoutView.as_view(), name='user_logout'),

    path('users/', UsersListView.as_view(), name='users_list'),

]