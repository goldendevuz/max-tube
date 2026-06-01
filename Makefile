env:
	python3 -m venv env && . env/bin/activate
migration:
	python3 manage.py makemigrations
makemigrations:
	python3 manage.py makemigrations youtube
migrate:
	python3 manage.py migrate
collectstatic:
	python3 manage.py collectstatic --noinput
run:
	python3 manage.py runserver 0.0.0.0:8000
cru:
	python manage.py createsuperuser --username=goldendev --email=goldendevuz@gmail.com
i:
	pip install -r requirements.txt
freeze:
	pip freeze > requirements.txt
