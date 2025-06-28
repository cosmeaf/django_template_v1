from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from authentication.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserRecoverySerializer,
    OtpVerifySerializer,
    ResetPasswordSerializer
)


class UserRegisterView(APIView):
    """View para registro de novos usuários."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.create(serializer.validated_data)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """View para login de usuários."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRecoveryView(APIView):
    """View para iniciar a recuperação de senha."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRecoverySerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Código OTP enviado para o e-mail."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpVerifyView(APIView):
    """View para verificar o código OTP."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OtpVerifySerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """View para redefinir a senha."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
