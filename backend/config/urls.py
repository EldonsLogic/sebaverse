from django.urls import path, re_path

from modules.core import views
from modules.access import views as access_views

urlpatterns = [
    path("api/v1/account/csrf/", access_views.csrf_token, name="csrf-token"),
    path("api/v1/access/resources/<uuid:resource_id>/", access_views.resource_scope, name="resource-scope"),
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
