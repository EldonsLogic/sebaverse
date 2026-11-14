from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.db import DatabaseError, connection
from django.http import HttpResponse, JsonResponse
from django.utils._os import safe_join

MAX_LOCAL_FILE_BYTES = 2 * 1024 * 1024

ASSET_TYPES = {
    ".js": "text/javascript",
    ".css": "text/css",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
}


def error_response(code, status, message="The request could not be completed."):
    return JsonResponse({"error": {"code": code, "message": message}}, status=status)


def _get_only(request):
    if request.method != "GET":
        response = error_response("method_not_allowed", 405)
        response["Allow"] = "GET"
        return response
    return None


def health(request):
    denied = _get_only(request)
    return denied if denied is not None else JsonResponse({"status": "ok"})


def ready(request):
    denied = _get_only(request)
    if denied is not None:
        return denied
    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.dummy":
        return error_response("not_ready", 503)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone() != (1,):
                return error_response("not_ready", 503)
    except DatabaseError:
        return error_response("not_ready", 503)
    return JsonResponse({"status": "ready"})


def _built_file_response(path, content_type):
    # Local F2 assets are small. Bound memory and avoid sync streaming under ASGI.
    try:
        with path.open("rb") as source:
            content = source.read(MAX_LOCAL_FILE_BYTES + 1)
    except OSError:
        return error_response("frontend_unavailable", 503)
    if len(content) > MAX_LOCAL_FILE_BYTES:
        return error_response("frontend_unavailable", 503)
    return HttpResponse(content, content_type=content_type)


def shell(request):
    denied = _get_only(request)
    if denied is not None:
        return denied
    if not settings.LOCAL_MODE:
        return error_response("not_found", 404)
    root = Path(settings.WEB_DIST_DIR)
    index = root / "index.html"
    if root.is_symlink() or not index.is_file() or index.is_symlink():
        return error_response("frontend_unavailable", 503)
    return _built_file_response(index, "text/html; charset=utf-8")


def frontend_asset(request, namespace, asset_path):
    denied = _get_only(request)
    if denied is not None:
        return denied
    if not settings.LOCAL_MODE:
        return error_response("not_found", 404)
    if any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in asset_path):
        return error_response("not_found", 404)
    parts = PurePosixPath(asset_path)
    if len(asset_path) > 500 or "\\" in asset_path or parts.is_absolute() or any(p in {".", ".."} for p in asset_path.split("/")):
        return error_response("not_found", 404)
    content_type = ASSET_TYPES.get(parts.suffix.lower())
    if namespace == "brand" and parts.suffix.lower() == ".txt" and parts.name.startswith("OFL"):
        content_type = "text/plain; charset=utf-8"
    if content_type is None:
        return error_response("not_found", 404)
    configured_root = Path(settings.WEB_DIST_DIR)
    if configured_root.is_symlink():
        return error_response("not_found", 404)
    root = configured_root.resolve()
    try:
        target = Path(safe_join(root, namespace, asset_path)).resolve()
    except SuspiciousFileOperation:
        return error_response("not_found", 404)
    if not target.is_relative_to(root / namespace) or not target.is_file():
        return error_response("not_found", 404)
    return _built_file_response(target, content_type)


def not_found(request, exception=None, **kwargs):
    return error_response("not_found", 404)


def csrf_failure(request, reason=""):
    return error_response("csrf_failed", 403)


def bad_request(request, exception=None):
    return error_response("bad_request", 400)


def server_error(request):
    return error_response("server_error", 500)


def forbidden(request, exception=None):
    return error_response("forbidden", 403)
