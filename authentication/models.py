from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import secrets
import string

User = get_user_model()


class OtpCode(models.Model):
    """Modelo para armazenar códigos OTP para recuperação de senha."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    @staticmethod
    def generate_otp(length=6):
        """Gera um código OTP aleatório."""
        characters = string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    def save(self, *args, **kwargs):
        """Define a expiração do OTP ao salvar."""
        if not self.pk:  # Apenas para novos OTPs
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)  # Expira em 10 minutos
            self.code = self.generate_otp()
        super().save(*args, **kwargs)

    def is_valid(self):
        """Verifica se o OTP é válido (não usado e não expirado)."""
        return not self.is_used and timezone.now() <= self.expires_at


class ResetPasswordToken(models.Model):
    """Modelo para tokens de redefinição de senha."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Define a expiração do token ao salvar."""
        if not self.pk:  # Apenas para novos tokens
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)  # Expira em 1 hora
        super().save(*args, **kwargs)

    def is_valid(self):
        """Verifica se o token é válido (não expirado)."""
        return timezone.now() <= self.expires_at