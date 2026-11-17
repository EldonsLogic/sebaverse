from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from modules.core.views import error_response, _get_only
from .service import authorized_resource


@ensure_csrf_cookie
def csrf_token(request):
    denied = _get_only(request)
    if denied is not None:
        return denied
    return JsonResponse({'csrf_token': get_token(request)})


def resource_scope(request, resource_id):
    denied = _get_only(request)
    if denied is not None:
        return denied
    if not request.user.is_authenticated:
        return error_response('unauthenticated', 401)
    if request.GET:
        return error_response('bad_request', 400)
    resource = authorized_resource(request.user, resource_id)
    if resource is None:
        return error_response('not_found', 404)
    # Deliberately only a scope anchor: no content, answer key, identity or consent evidence.
    return JsonResponse({'id': str(resource.id), 'kind': resource.kind,
                         'edition_id': resource.edition_id, 'edition_version': resource.edition_version})
