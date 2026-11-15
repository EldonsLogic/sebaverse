"""Validate startup configuration without opening a connection or reading files."""
from collections.abc import Mapping

from django.core.exceptions import ImproperlyConfigured

LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "[::1]"}
LOCAL_SECRET = "local-synthetic-only-not-for-deployment-" + "0" * 48


def _boolean(value: str, name: str) -> bool:
    if value.lower() not in {"0", "1", "false", "true"}:
        raise ImproperlyConfigured(f"{name} must be 0, 1, false or true.")
    return value.lower() in {"1", "true"}


def load_environment(env: Mapping[str, str]) -> dict:
    mode = env.get("SEBAVERSE_ENV", "production")
    if mode not in {"local", "production"}:
        raise ImproperlyConfigured("SEBAVERSE_ENV must be local or production.")
    local = mode == "local"
    debug = _boolean(env.get("DJANGO_DEBUG", "0"), "DJANGO_DEBUG")
    if debug and not local:
        raise ImproperlyConfigured("Debug is permitted only in explicit local mode.")

    hosts = [host.strip() for host in env.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()]
    if local and not hosts:
        hosts = sorted(LOOPBACK_HOSTS)
    if not hosts or any("*" in host or "/" in host or "://" in host for host in hosts):
        raise ImproperlyConfigured("Explicit allowed hosts are required; wildcard hosts are forbidden.")
    if local and not set(hosts).issubset(LOOPBACK_HOSTS):
        raise ImproperlyConfigured("Local mode permits only loopback allowed hosts.")

    secret = env.get("DJANGO_SECRET_KEY", "")
    if not secret and local and debug:
        secret = LOCAL_SECRET
    if not secret.strip() or len(secret) < 50 or (not local and (secret == LOCAL_SECRET or secret.startswith("django-insecure-"))):
        raise ImproperlyConfigured("Provide an independent DJANGO_SECRET_KEY of at least 50 characters.")

    names = ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST")
    parts = {name: env.get(name, "") for name in names}
    configured = any(parts.values()) or bool(env.get("POSTGRES_PORT"))
    if configured:
        if not all(parts.values()):
            raise ImproperlyConfigured("PostgreSQL configuration must supply DB, USER, PASSWORD and HOST together.")
        try:
            port = int(env.get("POSTGRES_PORT", "5432"))
        except ValueError:
            raise ImproperlyConfigured("POSTGRES_PORT must be a valid TCP port.") from None
        if not 1 <= port <= 65535:
            raise ImproperlyConfigured("POSTGRES_PORT must be a valid TCP port.")
        if local and parts["POSTGRES_HOST"] not in {"localhost", "127.0.0.1", "::1"}:
            raise ImproperlyConfigured("Local PostgreSQL host must be an explicit loopback endpoint.")
        if local and env.get("PSYCOPG_IMPL") != "python":
            raise ImproperlyConfigured("Local database use requires PSYCOPG_IMPL=python after native pre-use checks.")
        database = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parts["POSTGRES_DB"],
            "USER": parts["POSTGRES_USER"],
            "PASSWORD": parts["POSTGRES_PASSWORD"],
            "HOST": parts["POSTGRES_HOST"],
            "PORT": str(port),
            "CONN_MAX_AGE": 0,
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": ({"connect_timeout": 3, "sslmode": "disable", "gssencmode": "disable", "require_auth": "scram-sha-256"}
                        if local else {"connect_timeout": 3, "sslmode": "verify-full"}),
        }
    elif local:
        database = {"ENGINE": "django.db.backends.dummy"}
    else:
        raise ImproperlyConfigured("Production mode requires explicit PostgreSQL configuration.")

    return {"local": local, "debug": debug, "hosts": hosts, "secret": secret, "database": database}
