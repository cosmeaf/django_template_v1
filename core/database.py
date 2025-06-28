import os
from pathlib import Path
from decouple import config
import logging

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

ENGINE_MAP = {
    'postgresql': 'django.db.backends.postgresql',
    'mysql': 'django.db.backends.mysql',
    'sqlite3': 'django.db.backends.sqlite3',
    'oracle': 'django.db.backends.oracle',
    'mssql': 'mssql',  # requer pacote: django-mssql-backend
}

REQUIRED_FIELDS = {
    'postgresql': ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT'],
    'mysql':      ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT'],
    'oracle':     ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT'],
    'mssql':      ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT'],
}

def validate_env_vars(engine_key: str) -> bool:
    """Valida se todas as variáveis obrigatórias estão presentes para o banco escolhido."""
    required_keys = REQUIRED_FIELDS.get(engine_key, [])
    missing = [key for key in required_keys if not config(key, default='')]

    if missing:
        logger.error(f"[DATABASE] Variáveis ausentes para o banco '{engine_key}': {missing}")
        return False
    return True

def get_database_config():
    engine_key = config('DB_ENGINE', default='sqlite3').lower()
    engine = ENGINE_MAP.get(engine_key)

    if not engine:
        logger.warning(f"[DATABASE] DB_ENGINE '{engine_key}' não reconhecido. Usando SQLite.")
        engine = ENGINE_MAP['sqlite3']
        engine_key = 'sqlite3'

    if engine_key == 'sqlite3':
        # Verifica se DB_NAME foi definido; se não, usa o padrão absoluto
        db_name = (
            str(BASE_DIR / 'db.sqlite3')
            if not config('DB_NAME', default=None)
            else config('DB_NAME')
        )

        logger.info(f"[DATABASE] Usando SQLite como backend → {db_name}")
        return {
            'default': {
                'ENGINE': engine,
                'NAME': db_name,
            }
        }

    # Para outros bancos, validar campos obrigatórios
    if not validate_env_vars(engine_key):
        logger.warning(f"[DATABASE] Fallback para SQLite devido a configuração incompleta de '{engine_key}'.")
        return {
            'default': {
                'ENGINE': ENGINE_MAP['sqlite3'],
                'NAME': str(BASE_DIR / 'db.sqlite3'),
            }
        }

    logger.info(f"[DATABASE] Usando banco '{engine_key}' com engine '{engine}'.")

    return {
        'default': {
            'ENGINE': engine,
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }

# Exporta para uso direto no settings.py
DATABASES = get_database_config()
