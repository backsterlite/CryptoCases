# Makefile

# ––––– VARIABLES –––––
DC            := docker compose -f docker-compose.yml
DCT           := docker compose -f docker-compose.yml -f docker-compose.test.yml

# ––––– DEFAULT TARGET –––––
.DEFAULT_GOAL := help

# ––––– TASKS –––––

help: ## 🆘 Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## 🛠 Build all images
	$(DC) build

up: ## 🚀 Spin up all services in background
	$(DC) up -d

down: ## 🛑 Shut down all services
	$(DC) down

rebuild: ## 🔄 Rebuild and restart everything
	$(DC) build --no-cache
	$(DC) down
	$(DC) up -d

logs: ## 📜 Tail logs of all services
	$(DC) logs -f

test: ## ✅ Run the full test suite inside container
	$(DCT) run --rm backend  

clean: down ## 🧹 Alias for down, add volumes cleanup if needed
	@echo "Services stopped. To clear volumes, run 'docker volume rm cryptocases_mongo cryptocases_redis'"

.PHONY: registries
registries:
	@echo "1/6 Fetch raw data from Coingecko…"
	python3 scripts/fetch_raw_coin_data.py --delay 2.0
	@echo "2/6 Build network map…"
	python3 scripts/build_network_map.py
	@echo "3/6 Build asset registry…"
	python3 scripts/build_asset_registry.py
	@echo "4/6 Build coin registry…"
	python3 scripts/build_coin_registry.py
	@echo "5/6 Build chain registry…"
	python3 scripts/build_chain_registry.py
	@echo "6/6 Merge policy tokens…"
	python3 scripts/merge_policy.py
	@echo "✅ All registries up to date."