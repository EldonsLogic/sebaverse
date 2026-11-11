.PHONY: foundation-check dependency-check
foundation-check:
	python3 tools/model_economics.py
	python3 tools/validate_project.py
	python3 tools/check_foundation.py
	python3 -m unittest discover -s tools/tests -p 'test_*.py'

dependency-check:
	python3 tools/check_dependencies.py
