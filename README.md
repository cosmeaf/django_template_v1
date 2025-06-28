# Django Template V1

🎯 **Template inicial profissional para projetos Django**

Este repositório é um projeto base completo com Django + DRF, estruturado de forma profissional para iniciar rapidamente novos projetos web ou APIs REST em produção ou desenvolvimento.

## 🧱 Funcionalidades incluídas

- ✅ Autenticação JWT com recuperação de senha via OTP
- ✅ Sistema assíncrono de envio de e-mails com Celery + Redis
- ✅ Suporte a múltiplos provedores de e-mail (SMTP, SendGrid, Mailgun)
- ✅ Templates HTML para e-mails (com design dourado)
- ✅ Painel administrativo customizado (com grupos e permissões)
- ✅ Swagger com `drf-spectacular`
- ✅ Sistema de configuração global com `django-constance`
- ✅ Suporte a múltiplos bancos de dados via painel admin
- ✅ Suporte a arquivos estáticos e mídia com MinIO (compatível com S3)
- ✅ Serviço de IP com fallback automático
- ✅ Controle de ambiente com `.env` e `python-decouple`
- ✅ Estrutura desacoplada e orientada a objetos (POO)
- ✅ Monitoramento de tarefas com Celery + Flower

## 📁 Estrutura de diretórios

veloma_crm/
├── core/
│ ├── settings.py
│ ├── urls.py
│ └── database.py
├── services/
│ ├── utils/
│ ├── models/
│ ├── admin/
│ ├── views/
│ └── tasks/
├── authentication/
├── templates/
├── static/
├── docker-compose.yml
├── start_server.sh
└── .env


## 🚀 Como executar

### Requisitos

- Python 3.11+
- Redis
- PostgreSQL ou SQLite
- Docker (opcional)

### Passo a passo

```bash
git clone git@github.com:cosmeaf/django_template_v1.git
cd django_template_v1
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
./start_server.sh
🌐 Documentação da API
Swagger: /api/docs/

Schema (YAML): /api/schema/

📦 Tecnologias
Tecnologia	Descrição
Django 5	Framework web principal
Django REST Framework	Construção de APIs REST
SimpleJWT	Autenticação segura com JWT
Celery + Redis	Execução assíncrona de tarefas
django-constance	Configuração dinâmica pelo admin
drf-spectacular	Documentação automática das APIs
python-decouple	Separação de variáveis de ambiente
django-anymail	Integração com provedores de e-mail externos
MinIO	Armazenamento de arquivos (S3-like)

✉️ Templates de e-mail
Local: templates/emails/

Design elegante em tons dourados

Variáveis substituíveis

HTML + texto simples

Para eventos como:

Recuperação de senha

Redefinição

Boas-vindas

🔐 Autenticação
Registro com senha forte

Login com JWT

Recuperação com OTP

Redefinição via link com token

Envio automático de e-mails

📜 Licença
Distribuído sob a licença MIT.

🤝 Autor
Cosme Alves
📫 cosme.alex@gmail.com
🔗 github.com/cosmeaf