# Makefile

# The default target (what happens if you just type 'make')
all: install run run-frontend test

# Installation: Upgrades pip, installs audit tool, installs app deps
install:
	python -m pip install --upgrade pip setuptools wheel
# 	pip install pip-audit
# 	pip install -r requirements.txt
	pip install -e ".[dev]"

run:
	uvicorn src.routes:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	streamlit run ./frontend.py

# Testing: Runs pytest
test-unit:
	pytest 

test-api:
	@echo "Starting isolated API Test Server on port 8001..."
	@# 1. Start server in background and save PID
	DATABASE_URL="sqlite+aiosqlite:///:memory:" \
	uvicorn src.routes:app --host 127.0.0.1 --port 8001 > server_test.log 2>&1 & \
	echo $$! > ./tests/api/test_server.pid; \
	\
	echo "Waiting for test server to initialize..."; \
	sleep 5; \
	\
	echo "Running Newman tests..."; \
	# 2. Run Newman inside an IF statement to handle success/fail correctly
	if newman run ./tests/api/devsecops01-project.postman_collection.json \
		-e ./tests/api/env.json \
		--env-var "baseUrl=http://localhost:8001" \
		--working-dir .; then \
		echo "✅ Tests passed! Shutting down test server..."; \
		kill $$(cat ./tests/api/test_server.pid); \
		rm ./tests/api/test_server.pid; \
	else \
		echo "❌ Tests failed. Cleaning up server..."; \
		kill $$(cat ./tests/api/test_server.pid); \
		rm ./tests/api/test_server.pid; \
		exit 1; \
	fi

test-e2e:
	@echo "🚀 Setting up E2E environment..."
	@# 1. Start Backend (In-Memory DB) on Port 8002
	DATABASE_URL="sqlite+aiosqlite:///:memory:" \
	uvicorn src.routes:app --host 127.0.0.1 --port 8002 > e2e_api.log 2>&1 & \
	echo $$! > .e2e_api.pid
	
	@echo "⏳ Waiting for Backend to initialize..."
	@sleep 5

	@# 2. Start Frontend on Port 8502, pointing to Backend 8002
	API_URL="http://localhost:8002" \
	streamlit run ./frontend.py --server.port 8502 --server.headless true > e2e_st.log 2>&1 & \
	echo $$! > .e2e_st.pid
	
	@echo "⏳ Waiting for Frontend to initialize..."
	@sleep 5

	@# 3. Run Playwright Tests
	@echo "🎥 Running Playwright Tests..."
	# We pass the Streamlit URL to the tests via an env var (or pytest.ini)
	BASE_URL="http://localhost:8502" \
	pytest tests/e2e || \
	(echo "❌ E2E Tests Failed. Cleaning up..." && \
	 kill $$(cat .e2e_api.pid) && rm .e2e_api.pid && \
	 kill $$(cat .e2e_st.pid) && rm .e2e_st.pid && \
	 exit 1)

	@# 4. Success Cleanup
	@echo "✅ E2E Tests Passed! Cleaning up..."
	@kill $$(cat .e2e_api.pid) && rm .e2e_api.pid
	@kill $$(cat .e2e_st.pid) && rm .e2e_st.pid	

# Auditing: Runs the security audit
# adding the "." path so that pi-audit treats it path as the project source:
# For projects using pyproject.toml (following PEP 621 or PEP 518),
# pip-audit will attempt to resolve the dependencies listed in the [project].dependencies section 
# of the pyproject.toml
audit:
	pip-audit --strict .

# Runs audit without strict mode. This is just for logging/display.
# It won't crash the build if it finds something.
audit-report:
	pip-audit .

# Clean up: Removes cache files (optional but nice to have)
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache

delete-db:
	rm -rf test.db