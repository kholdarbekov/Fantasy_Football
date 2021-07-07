from rest_framework import generics, status, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models import User
from .serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer


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
        token, created = Token.objects.get_or_create(user=serializer.instance)
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
