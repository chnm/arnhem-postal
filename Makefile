mm :
	poetry run python3 manage.py makemigrations

migrate :
	poetry run python3 manage.py migrate

preview :
	poetry run python3 manage.py runserver

check : 
	poetry run python3 manage.py check

test : 
	poetry run python3 manage.py test

loadlocations :
	poetry run python manage.py load_locations --filepath="~/Downloads/arnhemv2.xlsx" --sheet="Database ready"

loadlanguages :
	poetry run python manage.py loaddata languages.yaml

loadtranscriptions : 
	poetry run python manage.py load_transcriptions --filepath="~/Downloads/arnhemv2.xlsx" --sheet="Database ready"

loadtags :
	poetry run python manage.py load_tags --filepath="~/Downloads/arnhemv2.xlsx" --sheet="Database ready"

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

docs : 
	poetry run sphinx-build -b html docs/source/ docs/build/

# Docker helpers
docker-up : 
	docker-compose up -d

docker-down : 
	docker-compose down

rebuild : 
	docker-compose down
	docker-compose build
	docker-compose up

.PHONY : preview loadobjects loadtags loadimages loadtags loadlanguages loadtranscriptions dumpdata docker-up docker-down docker-build
