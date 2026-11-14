from ipaddress import ip_address

from django.conf import settings
from django.core.exceptions import DisallowedHost

from .views import error_response


class RequestPolicyMiddleware:
    """Validate hosts even on health routes; do not return debug/error data."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.get_host()
            if settings.LOCAL_MODE:
                try:
                    local_peer = ip_address(request.META.get("REMOTE_ADDR", "")).is_loopback
                except ValueError:
                    local_peer = False
                if not local_peer:
                    raise DisallowedHost("Local mode requires a loopback peer.")
        except DisallowedHost:
            response = error_response("bad_request", 400)
        else:
            response = self.get_response(request)
        if response.status_code >= 400 and not response.get("Content-Type", "").startswith("application/json"):
            original = response
            response = error_response({400: "bad_request", 403: "forbidden", 404: "not_found", 405: "method_not_allowed"}.get(original.status_code, "server_error"), original.status_code)
            if original.has_header("Allow"):
                response["Allow"] = original["Allow"]
        response["Cache-Control"] = "no-store"
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["Referrer-Policy"] = "no-referrer"
        response["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response["Content-Security-Policy"] = "; ".join([
            "default-src 'self'", "script-src 'self'", "style-src 'self'", "font-src 'self'",
            "img-src 'self' data:", "connect-src 'self'", "object-src 'none'",
            "base-uri 'self'", "frame-ancestors 'none'", "form-action 'self'",
        ])
        return response
