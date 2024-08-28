dev:
	docker compose up --build --force-recreate --detach

db-revision:
	alembic revision --autogenerate -m "$(name)"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-upgrade-test:
	DATABASE_URL="postgresql+psycopg2://postgres:postgres@postgres:5432/postgres-test" alembic upgrade head

db-downgrade-test:
	DATABASE_URL="postgresql+psycopg2://postgres:postgres@postgres:5432/postgres-test" alembic downgrade -1

test:
	docker compose run --rm --service-ports test
