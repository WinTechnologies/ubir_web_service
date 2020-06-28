from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenVerifySerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from .models import User
from .serializers import CreateUserSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except:
            return {'detail': 'Email or Password is incorrect.'}
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        super().validate(attrs)


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer


class MyTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        super().validate(attrs)


class MyTokenVerifyView(TokenVerifyView):
    serializer_class = MyTokenVerifySerializer


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)
