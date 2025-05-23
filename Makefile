#
# See `make help` for a list of all available commands.

# https://www.howtogeek.com/782514/how-to-use-set-and-pipefail-in-bash-scripts-on-linux/
SHELL=/bin/bash -eu -o pipefail

IMAGE_NAME := ghcr.io/tursodatabase/libsql-server:latest
CONTAINER_NAME := libsql-server_latest

UV := $(shell command -v uv)

deps:
ifeq ($(UV),)
	$(error uv is not available. Please install the Python tool uv)
endif

.PHONY: first-start
first-start:  ## Run a new container 'CONTAINER_NAME' using the image IMAGE_NAME
	mkdir -p sqld-data
	docker run -p 8081:8080 --name $(CONTAINER_NAME) -v `pwd`/sqld-data:/var/lib/sqld -d $(IMAGE_NAME)

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
playing-with-libsql: deps ## Run a simple script to test the database
	uv run --script playing-with-libsql.py

.PHONY: generate-jsw
generate-jsw: deps ## Run a simple script to generate an ED25519 key pairs and JWT token. Test the last one with and without expiration time.
	uv run --script generate-jsw.py 

.PHONY: help
help:
	@echo -e "Available make commands:"
	@echo -e ""
	@echo "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sort | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\1:\2/' | \
		awk -v c="$(CONTAINER_NAME)" -v i="$(IMAGE_NAME)" -F: \
		'{ gsub("CONTAINER_NAME", c); gsub("IMAGE_NAME", i); printf "%-25s %s\n", $$1, $$2 }')"

.DEFAULT_GOAL := help
