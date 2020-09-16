basedir = $(realpath .)
projdir = $(basedir)/face_recognizer

bin = $(basedir)/venv/bin
python = PYTHONPATH=$(basedir) $(bin)/python
gunicorn = $(python) $(bin)/gunicorn
pytest = cd $(projdir) && $(python) $(bin)/pytest

run:
	$(gunicorn) -w 1 "face_recognizer.web:make_app()"

run_tests:
	$(pytest) tests

run_containers:
	docker-compose -f services/docker-compose.yaml up --no-recreate -d

prune_containers:
	docker-compose -f services/docker-compose.yaml down

run_tests_container:
	docker-compose -f services/docker-compose.tests.yaml up --no-recreate
