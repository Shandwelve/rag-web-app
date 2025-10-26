help:
	@echo "Makefile"
	@echo "usage: make COMMAND"
	@echo ""
	@echo "Commands:"
	@echo "  db.make_migrations Generate migrations file"
	@echo "  db.up              Run migrations"
	@echo "  app.drop           Drop app"


db.make_migrations:
	@cd api && uv run alembic revision --autogenerate -m "$(m)"

db.up:
	@cd api && uv run alembic upgrade head

black.run:
	@cd api && uv run black app

ruff.run:
	@cd api && uv run ruff check app --fix && uv run ruff format app

mypy.run:
	@cd api && uv run mypy app

db.down:
	@cd api && uv run alembic downgrade base

app.start:
	@docker-compose up -d --build --force-recreate

app.stop:
	@docker stop $$(docker ps -aq)
	@docker rm $$(docker ps -aq)
