.PHONY: start stop reset logs status install

start:
	@echo "Starting ContentEngine..."
	PYTHONPATH=apps/seo-agent python3 -m uvicorn interfaces.api.main:app --host 127.0.0.1 --port 8000 &
	@sleep 2
	PYTHONPATH=apps/seo-agent:apps/dashboard python3 apps/dashboard/server.py &
	@sleep 1
	@echo ""
	@echo "Dashboard:    http://127.0.0.1:3000"
	@echo "SEO Agent:    http://127.0.0.1:8000"
	@echo "Docs:         http://127.0.0.1:3000/docs"

start-full:
	@echo "Starting ContentEngine (full)..."
	docker compose --profile full up -d
	@echo "Dashboard:    http://127.0.0.1:3000"
	@echo "SEO Agent:    http://127.0.0.1:8000"
	@echo "Social Upload: http://127.0.0.1:8001"

stop:
	pkill -f "dashboard/server.py" || true
	pkill -f "uvicorn interfaces.api.main" || true
	docker compose down 2>/dev/null || true
	@echo "ContentEngine stopped."

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
