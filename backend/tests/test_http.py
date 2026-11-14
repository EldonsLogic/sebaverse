import logging
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

from django.db import OperationalError
from django.test import Client, override_settings
from django.urls import path
import pytest

from modules.core.logging import MetadataOnlyFormatter


def test_liveness_is_small_json_without_db_or_session_write(client):
    with patch("modules.core.views.connection") as connection:
        response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert not response.cookies
    connection.cursor.assert_not_called()


@pytest.mark.parametrize("route", ["/api/v1/health/", "/api/v1/ready/"])
@pytest.mark.parametrize("method", ["post", "put", "delete", "options", "head"])
def test_health_routes_only_allow_get(client, route, method):
    with patch("modules.core.views.connection") as connection:
        response = getattr(client, method)(route)
    assert response.status_code == 405
    assert response["Allow"] == "GET"
    connection.cursor.assert_not_called()


def test_unconfigured_readiness_fails_without_db_connection(client):
    with patch("modules.core.views.connection") as connection:
        response = client.get("/api/v1/ready/")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "not_ready"
    connection.cursor.assert_not_called()


@pytest.mark.parametrize("outcome", [(1,), (0,), OperationalError("synthetic-password-host-private")])
def test_readiness_success_and_failure_use_db_probe_without_exposing_error(client, outcome):
    fake = MagicMock()
    cursor = fake.cursor.return_value.__enter__.return_value
    if isinstance(outcome, Exception):
        fake.cursor.side_effect = outcome
    else:
        cursor.fetchone.return_value = outcome
    scoped = SimpleNamespace(DATABASES={"default": {"ENGINE": "django.db.backends.postgresql"}})
    with patch("modules.core.views.connection", fake), patch("modules.core.views.settings", scoped):
        response = client.get("/api/v1/ready/")
    assert response.status_code == (200 if outcome == (1,) else 503)
    assert "synthetic-password-host-private" not in response.content.decode()
    if outcome == (1,):
        cursor.execute.assert_called_once_with("SELECT 1")
        assert response.json() == {"status": "ready"}


def test_invalid_host_is_denied_on_liveness_too(client):
    response = client.get("/api/v1/health/", HTTP_HOST="untrusted.invalid")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"
    assert "untrusted.invalid" not in response.content.decode()


def test_unsafe_request_without_csrf_has_generic_json_error():
    client = Client(HTTP_HOST="localhost", enforce_csrf_checks=True)
    response = client.post("/api/v1/health/", {"sensitive": "synthetic-child-like-value"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "csrf_failed"
    assert "synthetic-child-like-value" not in response.content.decode()


def test_response_security_headers_and_no_store(client):
    response = client.get("/api/v1/health/")
    assert response["Cache-Control"] == "no-store"
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
    assert response["Referrer-Policy"] == "no-referrer"
    assert "microphone=()" in response["Permissions-Policy"]
    assert "frame-ancestors 'none'" in response["Content-Security-Policy"]
    assert "'unsafe-inline'" not in response["Content-Security-Policy"]


def test_unknown_api_never_returns_spa_or_debug_route_dump(client):
    response = client.get("/api/v1/not-implemented/")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert "urlpatterns" not in response.content.decode()


def test_error_response_and_logging_do_not_expose_exception_message(client):
    urls = ModuleType("synthetic_failure_urls")
    def explode(request):
        raise RuntimeError("synthetic-sensitive-exception")
    urls.urlpatterns = [path("api/v1/explode/", explode)]
    with override_settings(ROOT_URLCONF=urls):
        response = Client(HTTP_HOST="localhost", raise_request_exception=False).get("/api/v1/explode/")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "server_error"
    assert "synthetic-sensitive-exception" not in response.content.decode()
    record = logging.LogRecord("django.request", logging.ERROR, __file__, 1, "private message", (), (RuntimeError, RuntimeError("private trace"), None))
    assert MetadataOnlyFormatter().format(record) == "ERROR django.request"


@pytest.fixture
def frontend(tmp_path):
    root = tmp_path / "dist"
    (root / "assets").mkdir(parents=True)
    (root / "brand").mkdir()
    (root / "index.html").write_text("<!doctype html><html lang='ar' dir='rtl'>synthetic shell</html>")
    (root / "assets" / "app.js").write_text("console.log('synthetic asset')")
    (root / "brand" / "logo.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    (root / "brand" / "OFL-test.txt").write_text("synthetic notice fixture")
    with override_settings(WEB_DIST_DIR=root):
        yield root


@pytest.mark.parametrize("route", ["/", "/materials", "/practice", "/progress", "/progress/"])
def test_only_explicit_shell_routes_serve_local_build(client, frontend, route):
    response = client.get(route)
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    assert response.streaming is False
    assert b"synthetic shell" in response.content


@pytest.mark.parametrize("route", ["/assets/app.js", "/brand/logo.svg", "/brand/OFL-test.txt"])
def test_approved_assets_can_be_served(client, frontend, route):
    response = client.get(route)
    assert response.status_code == 200
    assert response["X-Content-Type-Options"] == "nosniff"
    assert response.streaming is False
    response.close()


@pytest.mark.parametrize("route", ["/README.md", "/.env", "/config/settings.py", "/unknown-page", "/api/v1/unknown/", "/assets/app.js.map", "/assets/private.tsx", "/brand/private.txt", "/assets/../index.html", "/assets/%2e%2e/%2e%2e/README.md", "/assets/sub%5cprivate.js"])
def test_arbitrary_files_routes_and_maps_are_not_served(client, frontend, route):
    response = client.get(route)
    assert response.status_code == 404
    assert response["Content-Type"].startswith("application/json")


def test_outside_symlink_is_not_served(client, frontend):
    outside = frontend.parent / "outside.js"
    outside.write_text("synthetic private content")
    (frontend / "assets" / "escape.js").symlink_to(outside)
    response = client.get("/assets/escape.js")
    assert response.status_code == 404
    assert "synthetic private content" not in response.content.decode()


def test_missing_frontend_is_resumable_error_not_source_exposure(client, tmp_path):
    with override_settings(WEB_DIST_DIR=tmp_path / "not-built"):
        response = client.get("/")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "frontend_unavailable"
    assert str(tmp_path) not in response.content.decode()


def test_local_build_serving_is_not_enabled_for_production(client, frontend):
    with override_settings(LOCAL_MODE=False):
        assert client.get("/").status_code == 404
        assert client.get("/assets/app.js").status_code == 404


def test_shell_and_assets_do_not_accept_unsafe_methods(client, frontend):
    assert client.post("/").status_code == 405
    assert client.post("/assets/app.js").status_code == 405


def test_local_mode_rejects_remote_peer_even_with_forged_loopback_host(client):
    response = client.get("/api/v1/health/", REMOTE_ADDR="192.0.2.10", HTTP_HOST="localhost")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"
    assert "192.0.2.10" not in response.content.decode()


@pytest.mark.parametrize("route,filename", [("/", "index.html"), ("/assets/app.js", "assets/app.js")])
def test_local_files_have_a_bounded_read_and_safe_oversize_failure(client, frontend, route, filename):
    from modules.core.views import MAX_LOCAL_FILE_BYTES
    (frontend / filename).write_bytes(b"x" * (MAX_LOCAL_FILE_BYTES + 1))
    response = client.get(route)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "frontend_unavailable"
    assert len(response.content) < 200


def test_built_shell_under_async_request_uses_nonstreaming_response(frontend):
    import asyncio
    from django.test import AsyncClient
    response = asyncio.run(AsyncClient(HTTP_HOST="localhost").get("/"))
    assert response.status_code == 200
    assert response.streaming is False
    assert b"synthetic shell" in response.content


@pytest.mark.parametrize("route", ["/assets/%00bad.js", "/brand/OFL%00.txt", "/assets/%1fbad.js", "/assets/%7fbad.js"])
def test_control_characters_are_rejected_before_file_resolution(client, frontend, route):
    response = client.get(route)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert str(frontend) not in response.content.decode()
