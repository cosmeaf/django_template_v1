import logging
from django.conf import settings
from django.template.loader import render_to_string
from services.tasks.email_tasks import send_email_task

logger = logging.getLogger(__name__)

class EmailService:
    """
    Serviço de envio de e-mails via Celery, com logging profissional.
    """
    def __init__(self, subject=None, to_email=None, template_name=None, context=None,
                 from_email=None, cc=None, bcc=None, attachments=None):
        self.subject = subject or "Sem Assunto"
        self.to_email = to_email if isinstance(to_email, list) else [to_email]
        self.template_name = template_name
        self.context = self._prepare_context(context)
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        self.cc = cc or []
        self.bcc = bcc or []
        self.attachments = attachments or []

    def _prepare_context(self, context):
        if not context:
            return {}
        return {
            key: str(value) if hasattr(value, '__dict__') else value
            for key, value in context.items()
        }

    def send(self):
        try:
            send_email_task.delay(
                self.subject,
                self.to_email,
                self.template_name,
                self.context,
                self.from_email,
                self.cc,
                self.bcc,
                self.attachments
            )
            logger.info(
                f"E-mail agendado com sucesso: para {self.to_email} usando template {self.template_name}.",
                extra={"subject": self.subject, "context": self.context}
            )
        except Exception as e:
            logger.error(
                f"Falha ao agendar envio de e-mail: {e}",
                exc_info=True,
                extra={
                    "to_email": self.to_email,
                    "template": self.template_name,
                    "context": self.context
                }
            )
