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
