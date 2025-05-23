## Task Prompt: Implement Doctor Health Check Route

### Goal

Create a `/healthz/doctor` endpoint that provides comprehensive system health information for debugging and monitoring.

### Implementation Steps

#### 1. Create Route File

```python
# src/instabids/api/routes/health.py
from fastapi import APIRouter, Depends
from typing import Dict, Any, List
import sys
import os
import pkg_resources
from datetime import datetime
import asyncio

from google import genai
from instabids.db.client import SupabaseClient
from instabids.agents import AgentFactory

router = APIRouter(
    prefix="/healthz",
    tags=["health"]
)


@router.get("/doctor")
async def doctor_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Returns system status including:
    - Python environment
    - Installed packages
    - Available models
    - Database connectivity
    - Agent readiness
    - Configuration status
    """
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
        "issues": []
    }
    
    # Python environment
    health_data["environment"] = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": sys.platform,
        "cwd": os.getcwd()
    }
    
    # Package versions
    critical_packages = [
        "google-adk",
        "google-genai",
        "supabase",
        "fastapi",
        "pydantic"
    ]
    
    health_data["packages"] = {}
    for package in critical_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            health_data["packages"][package] = version
        except Exception:
            health_data["packages"][package] = "NOT INSTALLED"
            health_data["issues"].append(f"Package {package} not found")
    
    # Model availability
    try:
        models = [m.name for m in genai.discovery.list_models()]
        health_data["checks"]["models"] = {
            "status": "ok",
            "available_models": models,
            "flash_model_present": any("flash" in m for m in models)
        }
    except Exception as e:
        health_data["checks"]["models"] = {
            "status": "error",
            "error": str(e)
        }
        health_data["status"] = "degraded"
    
    # Database connectivity
    try:
        client = SupabaseClient.get_client()
        # Simple query to test connection
        result = await asyncio.to_thread(
            lambda: client.table('projects').select('count').limit(1).execute()
        )
        health_data["checks"]["database"] = {
            "status": "ok",
            "connection": "established"
        }
    except Exception as e:
        health_data["checks"]["database"] = {
            "status": "error",
            "error": str(e)
        }
        health_data["status"] = "unhealthy"
    
    # Agent availability
    try:
        factory = AgentFactory()
        available_agents = factory.list_agents()
        health_data["checks"]["agents"] = {
            "status": "ok",
            "available": available_agents,
            "count": len(available_agents)
        }
    except Exception as e:
        health_data["checks"]["agents"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Environment variables
    required_env_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "GOOGLE_API_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        health_data["checks"]["environment_vars"] = {
            "status": "error",
            "missing": missing_vars
        }
        health_data["status"] = "unhealthy"
    else:
        health_data["checks"]["environment_vars"] = {
            "status": "ok",
            "all_present": True
        }
    
    # ADK cache status
    cache_path = os.path.expanduser("~/.cache/adk/model_catalog.json")
    health_data["checks"]["adk_cache"] = {
        "exists": os.path.exists(cache_path),
        "path": cache_path
    }
    
    # Overall status
    if health_data["status"] == "healthy" and not health_data["issues"]:
        health_data["message"] = "All systems operational"
    elif health_data["status"] == "degraded":
        health_data["message"] = "System operational with reduced functionality"
    else:
        health_data["message"] = "System experiencing issues"
    
    return health_data


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Simple ping endpoint for basic health check."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe for Kubernetes/container orchestration.
    
    Returns 200 if system is ready to accept traffic.
    Returns 503 if system is not ready.
    """
    try:
        # Quick checks only
        client = SupabaseClient.get_client()
        factory = AgentFactory()
        
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

#### 2. Register Route in Main API

```python
# src/instabids/api/main.py
from fastapi import FastAPI
from instabids.api.routes import health, projects, agents

app = FastAPI(
    title="InstaBids API",
    version="0.1.0",
    description="AI-Driven Multi-Agent Bidding Platform"
)

# Register routes
app.include_router(health.router)
app.include_router(projects.router)
app.include_router(agents.router)
```

#### 3. Add Middleware for Metrics

```python
# src/instabids/api/middleware/metrics.py
import time
from fastapi import Request
from typing import Callable


async def metrics_middleware(request: Request, call_next: Callable):
    """Add response time headers."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response
```

#### 4. Create Tests

```python
# tests/api/test_health.py
import pytest
from fastapi.testclient import TestClient
from instabids.api.main import app


class TestHealthEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_ping(self, client):
        """Test basic ping endpoint."""
        response = client.get("/healthz/ping")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    def test_doctor_endpoint(self, client):
        """Test comprehensive health check."""
        response = client.get("/healthz/doctor")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
        assert "environment" in data
        assert "packages" in data
        
        # Verify package checks
        assert "google-adk" in data["packages"]
        assert "google-genai" in data["packages"]
    
    def test_readiness(self, client):
        """Test readiness probe."""
        response = client.get("/healthz/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data
        assert "timestamp" in data
```

### Usage Examples

```bash
# Check system health
curl http://localhost:8001/healthz/doctor | jq .

# Simple ping
curl http://localhost:8001/healthz/ping

# Readiness check (for k8s)
curl http://localhost:8001/healthz/ready
```

### Response Example

```json
{
  "status": "healthy",
  "timestamp": "2025-05-23T10:30:00Z",
  "message": "All systems operational",
  "environment": {
    "python_version": "3.12.0",
    "platform": "linux"
  },
  "packages": {
    "google-adk": "1.0.0",
    "google-genai": "1.16.1",
    "supabase": "2.0.0"
  },
  "checks": {
    "models": {
      "status": "ok",
      "available_models": ["gemini-2.0-flash-exp"],
      "flash_model_present": true
    },
    "database": {
      "status": "ok",
      "connection": "established"
    },
    "agents": {
      "status": "ok",
      "available": ["homeowner", "bidcard"],
      "count": 2
    }
  },
  "issues": []
}
```

### Monitoring Integration

```python
# For Prometheus/Grafana
@router.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    return PlainTextResponse(
        content=generate_metrics(),
        media_type="text/plain"
    )
```

### Success Criteria

- [ ] Endpoint returns 200 OK
- [ ] All system checks included
- [ ] Response time < 1 second
- [ ] Proper error handling
- [ ] Tests pass
- [ ] Documentation updated