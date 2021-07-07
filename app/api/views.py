from rest_framework import generics, status, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models import User, Team, Player
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer, TeamSerializer, \
    TeamUpdateSerializer, PlayerSerializer


class UsersListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        users = User.objects.all()
        users_serializer = self.get_serializer(users, many=True)

        return Response(users_serializer.data)


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)

        Team.objects.generate_team(user)

        return Response({'token': token.key}, status=status.HTTP_201_CREATED, headers=headers)


class UserLoginView(ObtainAuthToken):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny, ]
    http_method_names = ['post', ]


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):

        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class TeamDetailView(generics.RetrieveAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        team = self.request.user.team
        return team


class TeamUpdateView(generics.UpdateAPIView):
    serializer_class = TeamUpdateSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_object(self):
        team = self.request.user.team
        return team


class PlayerUpdateView(generics.UpdateAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_object(self):
        player = Player.objects.get(id=self.request.data['id'])
        if player not in self.request.user.team.players.all():
            return None
        return player
