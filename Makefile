mm :
	poetry run python3 manage.py makemigrations

migrate :
	poetry run python3 manage.py migrate

preview :
	poetry run python3 manage.py runserver

# Compile TailwindCSS
tailwind :
	poetry run python3 manage.py tailwind start

graph_illustrate :
	poetry run python3 manage.py graph_models -a -g -o models.png

# Docker helpers
docker-up : 
	docker-compose up

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
