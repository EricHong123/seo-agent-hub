.PHONY: start stop reset logs status install docker-build docker-up docker-down

start:
	@echo "Starting SEO Agent Hub..."
	PYTHONPATH=apps/seo-agent python3 -m uvicorn interfaces.api.main:app --host 127.0.0.1 --port 8000 &
	@sleep 2
	PYTHONPATH=apps/seo-agent:apps/dashboard python3 apps/dashboard/server.py &
	@sleep 1
	cd apps/social-upload && python3 web_server.py &
	@sleep 1
	@echo ""
	@echo "Dashboard:    http://127.0.0.1:3000"
	@echo "SEO Agent:    http://127.0.0.1:8000"
	@echo "Social Upload: http://127.0.0.1:8001"

stop:
	pkill -f "dashboard/server.py" || true
	pkill -f "web_server.py" || true
	pkill -f "uvicorn interfaces.api.main" || true
	@echo "SEO Agent Hub stopped."

start-full:
	@echo "Starting SEO Agent Hub (full)..."
	docker compose --profile full up -d
	@echo "Dashboard:    http://127.0.0.1:3000"
	@echo "SEO Agent:    http://127.0.0.1:8000"
	@echo "Social Upload: http://127.0.0.1:8001"

reset:
	rm -rf apps/seo-agent/data/*
	rm -rf apps/social-upload/data/*
	@echo "Data reset."

logs:
	@tail -f apps/seo-agent/data/logs/agent.log 2>/dev/null || echo "No logs yet."

status:
	@curl -s http://127.0.0.1:8000/health 2>/dev/null || echo "SEO Agent: offline"
	@curl -s http://127.0.0.1:8001/health 2>/dev/null || echo "Social Upload: offline"

install:
	@echo "Installing dependencies..."
	cd apps/seo-agent && pip install -r requirements.txt
	cd apps/social-upload && pip install -r requirements.txt
	@echo "Done. Run 'make start' to begin."

docker-build:
	@echo "Building Docker images..."
	docker compose build
	@echo "Done. Run 'make docker-up' to start."

docker-up:
	@echo "Starting SEO Agent Hub (Docker)..."
	docker compose up -d
	@echo ""
	@echo "Dashboard: http://localhost:3000"
	@echo "SEO Agent: http://localhost:8000"

docker-up-full:
	@echo "Starting SEO Agent Hub full stack (Docker)..."
	docker compose --profile full up -d
	@echo "Dashboard:    http://localhost:3000"
	@echo "SEO Agent:    http://localhost:8000"
	@echo "SAU Web:      http://localhost:8001"

docker-down:
	docker compose down
	@echo "SEO Agent Hub stopped."
