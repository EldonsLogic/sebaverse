.PHONY: foundation-check dependency-check
foundation-check:
	python3 tools/model_economics.py
	python3 tools/validate_project.py
	python3 tools/check_foundation.py
	python3 -m unittest discover -s tools/tests -p 'test_*.py'

dependency-check:
	python3 tools/check_dependencies.py

.PHONY: backend-check smoke-local
backend-check:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests -q -k 'not postgres_integration'
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python backend/manage.py check

smoke-local:
	python3 tools/smoke_local.py

.PHONY: test-contracts test-authorization test-consent test-ingestion test-content-isolation
test-contracts:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python tools/export_curriculum_schema.py --check
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/curriculum -q

test-authorization:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/authorization -q

test-consent:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/consent -q

test-ingestion:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/ingestion -q

test-content-isolation: test-contracts test-authorization

.PHONY: test-resilience
test-resilience:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/resilience -q

.PHONY: test-publication-preflight test-retrieval-preflight test-learning-ledger-preflight test-tutor-state-preflight test-parent-privacy-preflight
test-publication-preflight:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/curriculum/test_publication_preflight.py -q

test-retrieval-preflight:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/retrieval/test_retrieval_preflight.py -q
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python evals/retrieval/run_preflight_eval.py

test-learning-ledger-preflight:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/learning/test_learning_ledger.py -q

test-tutor-state-preflight:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/tutoring/test_tutor_state.py -q

test-parent-privacy-preflight:
	SEBAVERSE_ENV=local DJANGO_DEBUG=1 backend/.venv/bin/python -m pytest backend/tests/operations/test_parent_privacy_preflight.py -q
