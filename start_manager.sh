#!/bin/bash

# Detecta diretório base do projeto (onde este script está)
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"
LOG_FILE="$LOG_DIR/manager.log"
DJANGO_PORT=7000
STATIC_DIR="$APP_DIR/static"

CELERY_WORKER="celery -A core worker --loglevel=info --logfile=$LOG_DIR/celery_worker.log --detach"
CELERY_BEAT="celery -A core beat --loglevel=info --logfile=$LOG_DIR/celery_beat.log --detach"

export DJANGO_SETTINGS_MODULE=core.settings

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

mkdir -p "$LOG_DIR"
chmod 775 "$LOG_DIR"
touch "$LOG_FILE"
chmod 664 "$LOG_FILE"

# Ativa o ambiente virtual
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo -e "${RED}Erro: Virtualenv não encontrado em $VENV_DIR${NC}"
    exit 1
fi

# Verifica .env
if ! python3 -c "from decouple import config; assert config('SECRET_KEY', default=None)" 2>/dev/null; then
    echo -e "${RED}Erro: SECRET_KEY não está definido no .env ou está vazio.${NC}"
    exit 1
fi

# Verifica se Docker está instalado e ativo
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker não está instalado.${NC}"
        exit 1
    fi
    if ! docker info &> /dev/null; then
        echo -e "${RED}Docker não está em execução. Use: sudo systemctl start docker${NC}"
        exit 1
    fi
}

# Detecta comando válido: docker compose ou docker-compose
get_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null; then
        echo "docker compose"
    else
        echo -e "${RED}Erro: docker-compose ou plugin docker compose não encontrado.${NC}"
        exit 1
    fi
}

start_docker_services() {
    COMPOSE_CMD=$(get_compose_cmd)

    echo "Verificando serviços Redis e Flower via docker-compose..."
    docker ps | grep veloma_redis > /dev/null && \
    docker ps | grep veloma_flower > /dev/null && \
    echo -e "${GREEN}Redis e Flower já estão rodando.${NC}" && return 0

    echo "Iniciando serviços com docker-compose..."
    $COMPOSE_CMD -f "$APP_DIR/docker-compose.yml" up -d
    sleep 3

    docker ps | grep veloma_redis > /dev/null && \
    docker ps | grep veloma_flower > /dev/null && \
    echo -e "${GREEN}Containers iniciados com sucesso.${NC}" || \
    { echo -e "${RED}Erro ao iniciar containers. Verifique docker-compose.yml${NC}"; exit 1; }
}

prepare_static() {
    echo "Executando collectstatic..."
    python3 manage.py collectstatic --noinput >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}collectstatic executado com sucesso.${NC}"
    else
        echo -e "${RED}Erro ao executar collectstatic. Verifique $LOG_FILE.${NC}"
        exit 1
    fi
}

check_port() {
    if netstat -tuln | grep ":$DJANGO_PORT " > /dev/null; then
        echo -e "${RED}Erro: Porta $DJANGO_PORT já está em uso.${NC}"
        exit 1
    fi
}

stop_process() {
    local pattern="$1"
    local name="$2"
    local pids
    pids=$(pgrep -f "$pattern")

    if [ -z "$pids" ]; then
        echo "$name não estava rodando."
        return 0
    fi

    echo "Parando $name..."
    kill $pids
    sleep 2

    pids=$(pgrep -f "$pattern")
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}$name ainda ativo. Forçando com kill -9...${NC}"
        kill -9 $pids
        sleep 1

        if pgrep -f "$pattern" > /dev/null; then
            echo -e "${RED}Erro: Falha ao parar $name mesmo com kill -9.${NC}"
            return 1
        fi
    fi

    echo -e "${GREEN}$name parado com sucesso.${NC}"
}

start() {
    echo "Iniciando serviços..."
    cd "$APP_DIR" || { echo -e "${RED}Erro ao acessar $APP_DIR${NC}"; exit 1; }

    check_docker
    start_docker_services
    check_port
    prepare_static

    if pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null; then
        echo "Django já está rodando na porta $DJANGO_PORT."
    else
        nohup python3 manage.py runserver 0.0.0.0:$DJANGO_PORT >> "$LOG_FILE" 2>&1 &
        sleep 2
        pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null && \
            echo -e "${GREEN}Django iniciado na porta $DJANGO_PORT.${NC}" || \
            { echo -e "${RED}Erro ao iniciar Django. Verifique $LOG_FILE.${NC}"; exit 1; }
    fi

    if pgrep -f "celery -A core worker" > /dev/null; then
        echo "Celery Worker já está rodando."
    else
        $CELERY_WORKER
        sleep 2
        pgrep -f "celery -A core worker" > /dev/null && \
            echo -e "${GREEN}Celery Worker iniciado.${NC}" || \
            { echo -e "${RED}Erro ao iniciar Celery Worker.${NC}"; exit 1; }
    fi

    if pgrep -f "celery -A core beat" > /dev/null; then
        echo "Celery Beat já está rodando."
    else
        $CELERY_BEAT
        sleep 2
        pgrep -f "celery -A core beat" > /dev/null && \
            echo -e "${GREEN}Celery Beat iniciado.${NC}" || \
            { echo -e "${RED}Erro ao iniciar Celery Beat.${NC}"; exit 1; }
    fi
}

stop() {
    echo "Parando serviços..."
    stop_process "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" "Django"
    stop_process "celery -A core worker" "Celery Worker"
    stop_process "celery -A core beat" "Celery Beat"

    echo "Parando containers docker (Redis e Flower)..."
    COMPOSE_CMD=$(get_compose_cmd)
    $COMPOSE_CMD -f "$APP_DIR/docker-compose.yml" down
}

restart() {
    echo "Reiniciando serviços..."
    stop
    sleep 3
    start
}

status() {
    echo "Status dos serviços:"
    pgrep -f "python3 manage.py runserver 0.0.0.0:$DJANGO_PORT" > /dev/null && echo -e "${GREEN}Django: Rodando${NC}" || echo -e "${RED}Django: Parado${NC}"
    pgrep -f "celery -A core worker" > /dev/null && echo -e "${GREEN}Celery Worker: Rodando${NC}" || echo -e "${RED}Celery Worker: Parado${NC}"
    pgrep -f "celery -A core beat" > /dev/null && echo -e "${GREEN}Celery Beat: Rodando${NC}" || echo -e "${RED}Celery Beat: Parado${NC}"
    docker ps | grep veloma_redis > /dev/null && echo -e "${GREEN}Redis (Docker): Rodando${NC}" || echo -e "${RED}Redis (Docker): Parado${NC}"
    docker ps | grep veloma_flower > /dev/null && echo -e "${GREEN}Flower (Docker): Rodando${NC}" || echo -e "${RED}Flower (Docker): Parado${NC}"
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) restart ;;
    status) status ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
