from django.urls import path, re_path

from modules.core import views

urlpatterns = [
    path("api/v1/health/", views.health, name="health"),
    path("api/v1/ready/", views.ready, name="ready"),
    path("", views.shell, name="shell"),
    re_path(r"^(?:materials|practice|progress)/?$", views.shell),
    path("assets/<path:asset_path>", views.frontend_asset, {"namespace": "assets"}),
    path("brand/<path:asset_path>", views.frontend_asset, {"namespace": "brand"}),
    re_path(r"^.*$", views.not_found),
]
handler400 = views.bad_request
handler403 = views.forbidden
handler404 = views.not_found
handler500 = views.server_error
