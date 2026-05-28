#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_DIR="${VENV_DIR:-.venv}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
MANAGE_PY="$ROOT_DIR/manage.py"
REQUIREMENTS="$ROOT_DIR/requirements.txt"

PYTHON_BIN=""

usage() {
    cat <<'EOF'
Usage:
  ./build.sh install              Create/use a virtualenv and install requirements
  ./build.sh check-env            Verify required local environment values exist
  ./build.sh check                Run local Django checks and migration checks
  ./build.sh deploy-check         Run deployment-oriented checks without changing data
  ./build.sh migrate              Apply database migrations
  ./build.sh collectstatic        Collect static assets
  ./build.sh runserver [host:port] Run the Django development server
  ./build.sh local                Install, check, migrate, then run the server
  ./build.sh help                 Show this help

Environment overrides:
  VENV_DIR=.venv                  Virtualenv directory used when no venv is active
  HOST=127.0.0.1                  Default runserver host
  PORT=8000                       Default runserver port
  PYTHON=python3                  Python executable used to create the virtualenv
EOF
}

log() {
    printf '\n==> %s\n' "$*"
}

warn() {
    printf 'Warning: %s\n' "$*" >&2
}

fail() {
    printf 'Error: %s\n' "$*" >&2
    exit 1
}

has_env_value() {
    local name="$1"
    local value="${!name:-}"

    if [[ -n "$value" ]]; then
        return 0
    fi

    if [[ -f "$ROOT_DIR/.env" ]] && grep -Eq "^[[:space:]]*${name}=.+[^[:space:]]" "$ROOT_DIR/.env"; then
        return 0
    fi

    return 1
}

select_python() {
    if [[ -n "${VIRTUAL_ENV:-}" && -x "$VIRTUAL_ENV/bin/python" ]]; then
        PYTHON_BIN="$VIRTUAL_ENV/bin/python"
    elif [[ -x "$ROOT_DIR/$VENV_DIR/bin/python" ]]; then
        PYTHON_BIN="$ROOT_DIR/$VENV_DIR/bin/python"
    else
        PYTHON_BIN="${PYTHON:-python3}"
    fi
}

ensure_manage_py() {
    [[ -f "$MANAGE_PY" ]] || fail "manage.py was not found at $MANAGE_PY"
}

ensure_project_files() {
    ensure_manage_py
    [[ -f "$REQUIREMENTS" ]] || fail "requirements.txt was not found at $REQUIREMENTS"
}

install_deps() {
    ensure_project_files

    if [[ -z "${VIRTUAL_ENV:-}" && ! -x "$ROOT_DIR/$VENV_DIR/bin/python" ]]; then
        log "Creating virtualenv at $ROOT_DIR/$VENV_DIR"
        "${PYTHON:-python3}" -m venv "$ROOT_DIR/$VENV_DIR"
    fi

    select_python
    log "Installing Python requirements with $PYTHON_BIN"
    "$PYTHON_BIN" -m pip install --upgrade pip
    "$PYTHON_BIN" -m pip install -r "$REQUIREMENTS"
}

check_env() {
    ensure_project_files

    local missing=()
    local required=(SECRET_KEY DATABASE_URL FIELD_ENCRYPTION_KEY)
    local optional=(CLOUDINARY_CLOUD_NAME CLOUDINARY_API_KEY CLOUDINARY_API_SECRET REDIS_URL)

    for name in "${required[@]}"; do
        if ! has_env_value "$name"; then
            missing+=("$name")
        fi
    done

    if (( ${#missing[@]} > 0 )); then
        printf 'Missing required environment values:\n' >&2
        printf '  - %s\n' "${missing[@]}" >&2
        printf '\nAdd them to %s/.env or export them before running this script.\n' "$ROOT_DIR" >&2
        if [[ " ${missing[*]} " == *" FIELD_ENCRYPTION_KEY "* ]]; then
            printf 'Generate FIELD_ENCRYPTION_KEY with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"\n' >&2
        fi
        return 1
    fi

    for name in "${optional[@]}"; do
        if ! has_env_value "$name"; then
            warn "$name is not set. This is OK for some local flows, but related integrations may not work."
        fi
    done

    log "Environment looks usable"
}

django() {
    ensure_manage_py
    select_python
    "$PYTHON_BIN" "$MANAGE_PY" "$@"
}

local_checks() {
    check_env
    log "Running Django system checks"
    django check

    log "Checking for unapplied migrations"
    django migrate --check --dry-run
}

deploy_checks() {
    check_env
    log "Running Django deployment checks"
    django check --deploy

    log "Checking static collection without writing files"
    django collectstatic --noinput --dry-run

    log "Checking for unapplied migrations"
    django migrate --check --dry-run
}

apply_migrations() {
    check_env
    log "Applying migrations"
    django migrate
}

collect_static() {
    check_env
    log "Collecting static files"
    django collectstatic --noinput
}

run_server() {
    check_env
    local bind="${1:-$HOST:$PORT}"
    log "Starting development server at http://$bind/"
    django runserver "$bind"
}

command="${1:-help}"
case "$command" in
    install)
        install_deps
        ;;
    check-env)
        check_env
        ;;
    check)
        local_checks
        ;;
    deploy-check)
        deploy_checks
        ;;
    migrate)
        apply_migrations
        ;;
    collectstatic)
        collect_static
        ;;
    runserver)
        shift || true
        run_server "${1:-}"
        ;;
    local)
        install_deps
        local_checks
        apply_migrations
        run_server
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        usage
        fail "Unknown command: $command"
        ;;
esac
