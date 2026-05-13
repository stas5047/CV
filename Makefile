.PHONY: storage-bootstrap compose-config compose-config-gpu

storage-bootstrap:
	powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1

compose-config:
	docker compose --env-file .env.example config

compose-config-gpu:
	docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config

