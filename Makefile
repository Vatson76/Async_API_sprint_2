setup:
	docker-compose exec admin python manage.py migrate	
	docker-compose exec admin python manage.py collectstatic --no-input

admin:
	docker-compose exec admin python manage.py createsuperuser

load_data:
	docker-compose exec admin python manage.py migrate_data

locale:
	docker-compose exec admin python manage.py compilemessages -l en -l ru

redis:
	docker-compose exec redis redis-cli

setup_auth:
	docker-compose exec auth flask db upgrade
