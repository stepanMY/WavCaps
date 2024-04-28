SHELL=/bin/bash

build:
	docker compose build
up:
	docker compose up &> ./logs/servicelog.log