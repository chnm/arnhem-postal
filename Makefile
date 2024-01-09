mm :
	poetry run python3 manage.py makemigrations

migrate :
	poetry run python3 manage.py migrate

preview :
	poetry run python3 manage.py runserver

check : 
	poetry run python3 manage.py check

loadlocations :
	poetry run python manage.py loaddata locations.yaml

loadlanguages :
	poetry run python manage.py loaddata languages.yaml

loadobjects :
	poetry run python manage.py load_objects --filepath="~/Downloads/arnhem.xlsx" --sheet="Box 1 Folders I-VIII"

loadimages : 
	poetry run python manage.py populate_images

# Compile TailwindCSS
tailwind :
	poetry run python3 manage.py tailwind start

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

.PHONY : preview tailwind graph_illustrate docker-up docker-down docker-build
