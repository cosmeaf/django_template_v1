from django.db import models

class EmailProvider(models.Model):
    PROVIDER_CHOICES = [
        ('smtp', 'SMTP Manual'),
        ('mailgun', 'Mailgun'),
        ('sendgrid', 'SendGrid'),
    ]

    name = models.CharField(max_length=100, verbose_name="Nome de exibição")
    provider_type = models.CharField(max_length=20, choices=PROVIDER_CHOICES, verbose_name="Tipo de Provedor")
    default_sender = models.EmailField(verbose_name="E-mail do Remetente Padrão")

    # Configurações SMTP
    host = models.CharField(max_length=255, blank=True, null=True, verbose_name="Servidor SMTP")
    port = models.PositiveIntegerField(blank=True, null=True, verbose_name="Porta SMTP")
    username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Usuário SMTP")
    password = models.CharField(max_length=255, blank=True, null=True, verbose_name="Senha SMTP")
    use_tls = models.BooleanField(default=True, verbose_name="Usar TLS")
    use_ssl = models.BooleanField(default=False, verbose_name="Usar SSL")

    # API Key (Mailgun / SendGrid)
    api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="API Key")

    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Provedor de E-mail"
        verbose_name_plural = "Provedores de E-mail"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.provider_type})"
