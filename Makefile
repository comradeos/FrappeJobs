.PHONY: build up rebuild down clean logs test ps

build:
	docker compose build

up:
	docker compose up -d

rebuild:
	docker compose down
	docker compose up -d --build

down:
	docker compose down

clean:
	docker compose down -v --remove-orphans

logs:
	docker compose logs -f --tail=200

test:
	docker compose ps

ps:
	docker compose ps
