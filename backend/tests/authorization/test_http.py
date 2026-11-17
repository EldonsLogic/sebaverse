from uuid import uuid4
from django.test import Client


def test_anonymous_session_cannot_resolve_guessed_resource():
    c = Client(HTTP_HOST='localhost', enforce_csrf_checks=True)
    response = c.get('/api/v1/access/resources/'+str(uuid4())+'/')
    assert response.status_code == 401
    assert response.json()['error']['code'] == 'unauthenticated'


def test_csrf_bootstrap_deliberately_returns_masked_token_and_httponly_cookie():
    c = Client(HTTP_HOST='localhost', enforce_csrf_checks=True)
    response = c.get('/api/v1/account/csrf/')
    assert response.status_code == 200
    assert len(response.json()['csrf_token']) == 64
    assert response.cookies['csrftoken']['httponly'] is True
    assert response['Cache-Control'] == 'no-store'


def test_write_without_csrf_is_blocked_before_any_resource_or_database_access():
    c = Client(HTTP_HOST='localhost', enforce_csrf_checks=True)
    response = c.post('/api/v1/access/resources/'+str(uuid4())+'/', data={'role': 'guardian', 'paid': True})
    assert response.status_code == 403


def test_valid_csrf_does_not_create_a_write_capability():
    c = Client(HTTP_HOST='localhost', enforce_csrf_checks=True)
    token = c.get('/api/v1/account/csrf/').json()['csrf_token']
    response = c.post('/api/v1/access/resources/'+str(uuid4())+'/', HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 405
