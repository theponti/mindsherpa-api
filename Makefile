dev:
	docker compose run --rm --service-ports fastapi

db-revision:
	alembic revision --autogenerate -m "$(name)"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1
