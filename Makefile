COMPOSE=docker compose -f docker-compose.dev.yml

.DEFAULT_GOAL := wizard
## Run wizard
wizard:
	python3 main.py action=wizard

## Connect to EnedisGateway container : DEV
debug:
	$(COMPOSE) stop myelectricaldata_import
	$(COMPOSE) rm -f myelectricaldata_import
	python3 main.py action=debug

## Connect to EnedisGateway container : DEV
run:
	$(COMPOSE) stop myelectricaldata_import
	$(COMPOSE) rm -f myelectricaldata_import
	python3 main.py action=run

## Start docker conatiners for dev
up:
	@echo "Start docker container for dev"
	$(COMPOSE) up -d
	@echo ""
	@echo "\033[0;33mMQTT Explorer:\033[0m    \033[0;32mhttp://127.0.0.1:4000\033[0m    Auth info: (host: mosquitto)"
	@echo "\033[0;33mInflux DB:    \033[0m    \033[0;32mhttp://127.0.0.1:8086\033[0m    Auth info: (user: enedisgateway2mqtt, pawword: enedisgateway2mqtt)"
	
## Stop docker conatiners for dev
down:
	@echo "Start docker conatiner for dev"
	$(COMPOSE) down

## Start in app
start:
	$(COMPOSE) exec myelectricaldata_import python -u /app/main.py
	
## Connect to enedisgateway2mqtt container
bash:
	$(COMPOSE) exec myelectricaldata_import bash

## Create git branch
version=
git_branch:
	git branch $(version) || true
	git checkout $(version) || true
	echo -n $(version) > app/VERSION

## Create add/commit/push
current_version := $(shell cat app/VERSION)
comment=
.PHONY: git_push
git_push:
	set -x
	@(echo "git add --all")
	git add --all
	@if [ "$(comment)" = "" ]; then comment="maj"; fi; \
    echo "git commit -m '$${comment}'"
	git commit -m "$${comment}"
	@(echo "git push origin $(current_version)")
	git push origin $(current_version)


## Generate requirements.txt
generate-dependencies:
	cd app; pip-compile -o requirements.txt pyproject.toml; cd -

## Create github pre release (dev)
create-release-dev:
	python3 main.py action=create_pre_release

## Create github release (prod)
create-release:
	python3 main.py action=create_release