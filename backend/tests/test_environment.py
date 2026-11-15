import pytest
from django.core.exceptions import ImproperlyConfigured

from config.environment import LOCAL_SECRET, load_environment


def local(**extra):
    return {"SEBAVERSE_ENV": "local", "DJANGO_DEBUG": "1", **extra}


def production(**extra):
    return {
        "DJANGO_SECRET_KEY": "synthetic-not-a-live-key-" + "x" * 60,
        "DJANGO_ALLOWED_HOSTS": "example.invalid",
        "POSTGRES_DB": "synthetic",
        "POSTGRES_USER": "synthetic",
        "POSTGRES_PASSWORD": "synthetic-not-live",
        "POSTGRES_HOST": "db.invalid",
        **extra,
    }


def test_no_ambient_configuration_fails_closed():
    with pytest.raises(ImproperlyConfigured):
        load_environment({})


def test_explicit_local_debug_without_db_is_dummy_not_sqlite():
    config = load_environment(local())
    assert config["secret"] == LOCAL_SECRET
    assert config["hosts"] == ["127.0.0.1", "[::1]", "localhost"]
    assert config["database"] == {"ENGINE": "django.db.backends.dummy"}


@pytest.mark.parametrize("env", [
    {"SEBAVERSE_ENV": "local"},
    {"DJANGO_DEBUG": "1"},
    local(DJANGO_ALLOWED_HOSTS="0.0.0.0"),
    local(DJANGO_ALLOWED_HOSTS="*"),
    local(DJANGO_ALLOWED_HOSTS="localhost,example.invalid"),
    local(DJANGO_DEBUG="sometimes"),
    local(SEBAVERSE_ENV="typo"),
    local(POSTGRES_DB="partial"),
    local(POSTGRES_PORT="5432"),
    production(DJANGO_SECRET_KEY=LOCAL_SECRET),
    production(DJANGO_SECRET_KEY=" " * 60),
    production(DJANGO_SECRET_KEY="short"),
    production(DJANGO_DEBUG="1"),
    production(DJANGO_ALLOWED_HOSTS="*"),
    production(POSTGRES_PASSWORD=""),
    production(POSTGRES_PORT="bad"),
    production(POSTGRES_PORT="0"),
    production(POSTGRES_PORT="65536"),
])
def test_unsafe_or_partial_configuration_is_rejected_without_echoing_values(env):
    env = dict(env)
    env.setdefault("SYNTHETIC_PRIVATE_VALUE", "do-not-echo-this-value")
    with pytest.raises(ImproperlyConfigured) as failure:
        load_environment(env)
    assert "do-not-echo-this-value" not in str(failure.value)
    assert env.get("POSTGRES_PASSWORD", "a value never printed") not in str(failure.value) or not env.get("POSTGRES_PASSWORD")


def test_production_postgres_configuration_is_explicit_tls_required():
    config = load_environment(production())
    assert config["debug"] is False and config["local"] is False
    assert config["database"]["ENGINE"] == "django.db.backends.postgresql"
    assert config["database"]["OPTIONS"] == {"connect_timeout": 3, "sslmode": "verify-full"}
    assert config["database"]["CONN_MAX_AGE"] == 0


@pytest.mark.parametrize("host", ["db.example.invalid", "192.0.2.10", "localhost,db.example.invalid"])
def test_local_rejects_complete_remote_postgres_configuration(host):
    env = production(SEBAVERSE_ENV="local", DJANGO_DEBUG="1", DJANGO_ALLOWED_HOSTS="localhost", POSTGRES_HOST=host)
    with pytest.raises(ImproperlyConfigured, match="explicit loopback") as failure:
        load_environment(env)
    assert host not in str(failure.value)
    assert env["POSTGRES_PASSWORD"] not in str(failure.value)


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "::1"])
def test_local_postgres_accepts_only_explicit_loopback_configuration(host):
    config = load_environment(production(SEBAVERSE_ENV="local", DJANGO_DEBUG="1", DJANGO_ALLOWED_HOSTS="localhost", POSTGRES_HOST=host, PSYCOPG_IMPL="python"))
    assert config["database"]["HOST"] == host
    assert config["database"]["OPTIONS"] == {
        "connect_timeout": 3, "sslmode": "disable", "gssencmode": "disable", "require_auth": "scram-sha-256"
    }


@pytest.mark.parametrize("implementation", [None, "binary", "c", "PYTHON"])
def test_local_database_requires_explicit_python_binding(implementation):
    env = production(SEBAVERSE_ENV="local", DJANGO_DEBUG="1", DJANGO_ALLOWED_HOSTS="localhost", POSTGRES_HOST="127.0.0.1")
    if implementation is not None:
        env["PSYCOPG_IMPL"] = implementation
    with pytest.raises(ImproperlyConfigured, match="PSYCOPG_IMPL=python"):
        load_environment(env)


def test_unconfigured_local_dummy_does_not_require_or_load_a_db_binding():
    config = load_environment(local(PSYCOPG_IMPL="binary"))
    assert config["database"] == {"ENGINE": "django.db.backends.dummy"}
