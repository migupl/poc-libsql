#
# See `make help` for a list of all available commands.

# https://www.howtogeek.com/782514/how-to-use-set-and-pipefail-in-bash-scripts-on-linux/
SHELL=/bin/bash -eu -o pipefail

IMAGE_NAME := ghcr.io/tursodatabase/libsql-server:latest

ifeq (,$(wildcard ./sqld-data/public.pub))
	CONTAINER_NAME := libsql-server_latest
else
	CONTAINER_NAME := secure-libsql-server_latest
	ENV_FILE := --env-file .env
endif

UV := $(shell command -v uv)

deps:
ifeq ($(UV),)
	$(error uv is not available. Please install the Python tool uv)
endif

.PHONY: first-start
first-start:  ## Run a new container 'CONTAINER_NAME' using the image IMAGE_NAME
	mkdir -p sqld-data
	docker run -p 8080:8080 --name $(CONTAINER_NAME) $(ENV_FILE) -v `pwd`/sqld-data:/var/lib/sqld -d $(IMAGE_NAME)

.PHONY: start
start:  ## Run the container 'CONTAINER_NAME'
	docker start $(CONTAINER_NAME)

.PHONY: alive
alive:  ## Run `sqld -help` on the container 'CONTAINER_NAME' to check it is alive
	docker exec -it $(CONTAINER_NAME) /bin/sqld --help

.PHONY: stop
stop:  ## Stop the container 'CONTAINER_NAME'
	docker stop $(CONTAINER_NAME)

.PHONY: playing-with-libsql
playing-with-libsql: deps ## Run a simple script to test the database. When JWT_TOKEN variable exists then the secure server is used.
	uv run --script playing-with-libsql.py $(JWT_TOKEN)

.PHONY: generate-jwt
generate-jwt: deps ## Run a simple script to generate an ED25519 key pairs and JWT token. Test the last one with and without expiration time.
	uv run --script generate-jwt.py

.PHONY: help
help:
	@echo -e "Available make commands:"
	@echo -e ""
	@echo "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sort | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\1:\2/' | \
		awk -v c="$(CONTAINER_NAME)" -v i="$(IMAGE_NAME)" -F: \
		'{ gsub("CONTAINER_NAME", c); gsub("IMAGE_NAME", i); printf "%-25s %s\n", $$1, $$2 }')"

.DEFAULT_GOAL := help
