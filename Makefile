dev:
	docker compose up --build --force-recreate --detach

db-revision:
	alembic revision --autogenerate -m "$(name)"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

# Define variables at the top of your Makefile
DB_USER := postgres
DB_PASSWORD := postgres
DB_HOST := localhost
DB_PORT := 5432
TEST_DB_NAME := test_db
POSTGRES_CONTAINER := postgres  # Assuming 'db' is your PostgreSQL container name

# Function to run a command in the PostgreSQL container
define run_in_postgres
	docker-compose exec -T $(POSTGRES_CONTAINER) psql -U $(DB_USER) -c "$(1)"
endef

test:
	# @echo "Creating test database..."
	docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS test_db;"
	docker-compose exec postgres psql -U postgres -c "CREATE DATABASE test_db;"

	# @echo "Running migrations..."
	# DATABASE_URL="postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(TEST_DB_NAME)" alembic upgrade head

	@echo "Running tests..."
	ENVIRONMENT=test \
	SUPABASE_URL="http://supabase:3000" \
	SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF0Z2R2cW10YmJ0aWZ2Z2N0Z3Z3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTYzMjI4MjQsImV4cCI6MjAxMTg5ODgyNH0.i9QWzUY21Y4q0sZ57YB5489J7x089g64vj9229111" \
	DATABASE_URL="postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(TEST_DB_NAME)" pytest tests/ -v

	@echo "Cleaning up test database..."
	docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS test_db;"

.PHONY: test
