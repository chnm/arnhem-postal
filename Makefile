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

# Data importing
loadlanguages :
	poetry run python manage.py loaddata languages.yaml

loadlocations :
	poetry run python manage.py load_locations --filepath="./arnhemv2.xlsx" --sheetname="Database ready"


loadtranscriptions : 
	poetry run python manage.py load_transcriptions --filepath="./arnhemv2.xlsx" --sheetname="Database ready"

loadtags :
	poetry run python manage.py load_tags --filepath="./arnhemv2.xlsx" --sheetname="Database ready"

loadobjects :
	poetry run python manage.py load_objects --filepath="./arnhemv2.xlsx" --sheetname="Database ready"

loadimages : 
	poetry run python manage.py populate_images

loaddocuments : 
	poetry run python manage.py load_documents --filepath="./arnhemv2.xlsx" --sheetname="Documents Database Ready"

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
