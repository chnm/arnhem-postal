mm :
	poetry run python3 manage.py makemigrations

migrate :
	poetry run python3 manage.py migrate

preview :
	poetry run python3 manage.py runserver

check : 
	poetry run python3 manage.py check

loadlocations :
	poetry run python manage.py load_locations --filepath="~/Downloads/arnhemv2.xlsx" --sheet="Database ready"

loadlanguages :
	poetry run python manage.py loaddata languages.yaml

loadobjects :
	poetry run python manage.py load_objects --filepath="~/Downloads/arnhemv2.xlsx" --sheet="Database ready"

loadimages : 
	poetry run python manage.py populate_images

dumpdata : 
# Dump the data
	pg_dump arnhem > arnhem_data.sql
# Zip the static files
	zip -r static.zip media
# Zip the collectstatic files
	zip -r collectstatic.zip staticfiles

graph_illustrate :
	poetry run python3 manage.py graph_models -a -g -o models.png

# Docker helpers
docker-up : 
	docker-compose up -d

docker-down : 
	docker-compose down

rebuild : 
	docker-compose down
	docker-compose build
	docker-compose up

# Django helpers
createsuper : 
	docker-compose exec web poetry run python manage.py createsuperuser

.PHONY : preview graph_illustrate docker-up docker-down docker-build
