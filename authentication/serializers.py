from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from django.conf import settings
from authentication.models import OtpCode, ResetPasswordToken
from services.utils.emails.email_service import EmailService
import re

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializador para registro de usuários com validação e geração de tokens JWT."""
    first_name = serializers.CharField(required=True, max_length=50)
    last_name = serializers.CharField(required=True, max_length=50)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'password2']

    def validate_email(self, value):
        """Valida se o e-mail já está em uso."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return value.lower()

    def validate_password(self, value):
        """Valida a força da senha."""
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um caractere especial.")
        return value

    def validate(self, data):
        """Valida se as senhas coincidem."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return data

    def create(self, validated_data):
        """Cria um novo usuário e retorna tokens JWT."""
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )

        # Adiciona o grupo padrão "user"
        default_group, _ = Group.objects.get_or_create(name='user')
        user.groups.add(default_group)

        refresh = RefreshToken.for_user(user)
        groups = user.groups.values_list('name', flat=True)

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": groups[0] if groups else "user",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class UserLoginSerializer(serializers.Serializer):
    """Serializador para login de usuários e geração de tokens JWT."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Valida as credenciais do usuário."""
        email = data.get("email").lower()
        password = data.get("password")
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Credenciais inválidas.")

        refresh = RefreshToken.for_user(user)
        groups = user.groups.values_list('name', flat=True)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": groups[0] if groups else "user"
            },
        }


class UserRecoverySerializer(serializers.Serializer):
    """Serializador para iniciar o processo de recuperação de senha."""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Valida se o e-mail existe e envia o código OTP."""
        try:
            user = User.objects.get(email=value.lower())
        except User.DoesNotExist:
            raise serializers.ValidationError("E-mail não encontrado.")

        otp_code = OtpCode.objects.create(user=user)
        email_service = EmailService(
            subject="Código de Recuperação de Senha",
            to_email=[value.lower()],
            template_name="emails/recovery_email.html",
            context={"otp_code": otp_code.code, "user": user}
        )
        email_service.send()

        return value.lower()


class OtpVerifySerializer(serializers.Serializer):
    """Serializador para validar o código OTP e gerar um token de redefinição."""
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        """Valida o código OTP e gera um link temporário para redefinição de senha."""
        try:
            otp = OtpCode.objects.filter(code=data['code'], is_used=False).latest('created_at')
        except OtpCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Código inválido ou expirado."})

        if not otp.is_valid():
            otp.delete()
            raise serializers.ValidationError({"code": "Código expirado."})

        user = otp.user
        otp.delete()  # Apaga o OTP após validação

        reset_token = ResetPasswordToken.objects.create(user=user)
        domain = getattr(settings, 'SITE_URL', "http://127.0.0.1")
        reset_url = f"{domain}/auth/reset-password/?token={reset_token.token}"

        return {"reset_url": reset_url}


class ResetPasswordSerializer(serializers.Serializer):
    """Serializador para redefinir a senha com um token."""
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value):
        """Valida a força da nova senha."""
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("A senha deve conter pelo menos um caractere especial.")
        return value

    def validate(self, data):
        """Valida o token e se as senhas coincidem."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})

        try:
            reset_token = ResetPasswordToken.objects.get(token=data['token'])
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Token inválido ou expirado.")

        if not reset_token.is_valid():
            raise serializers.ValidationError("Token expirado.")

        return data

    def save(self):
        """Redefine a senha do usuário e envia uma confirmação por e-mail."""
        reset_token = ResetPasswordToken.objects.get(token=self.validated_data['token'])
        user = reset_token.user
        user.set_password(self.validated_data['password'])
        user.save()

        reset_token.delete()

        email_service = EmailService(
            subject="Sua senha foi alterada",
            to_email=[user.email],
            template_name="emails/password_changed.html",
            context={"user": user}
        )
        email_service.send()

        return {"message": "Senha redefinida com sucesso!"}