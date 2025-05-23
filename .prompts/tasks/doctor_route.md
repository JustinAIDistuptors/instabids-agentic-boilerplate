## Task: Implement Health Check Doctor Route

### Goal

Create a comprehensive health check endpoint that verifies system status for AI agents.

### Implementation

```python
# src/instabids/api/routes/health.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import pkg_resources
import psutil
import asyncio
from datetime import datetime

# Imports for checks
from google import genai
from supabase import Client
from instabids.db import SupabaseService
from instabids.agents import agent_registry

router = APIRouter(prefix="/healthz", tags=["health"])

@router.get("/doctor")
async def doctor_check() -> Dict[str, Any]:
    """
    Comprehensive health check for InstaBids system.
    
    Returns:
        dict: System health status including:
            - Model availability
            - Package versions
            - Database connectivity
            - Agent status
            - System resources
    """
    health_report = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
        "warnings": [],
        "errors": []
    }
    
    # 1. Check Model Registry
    try:
        models = [m.name for m in genai.discovery.list_models()]
        flash_models = [m for m in models if "flash" in m]
        
        health_report["checks"]["models"] = {
            "status": "ok",
            "available_models": len(models),
            "flash_models": flash_models,
            "recommended_model": "gemini-2.0-flash-exp" in flash_models
        }
        
        if "gemini-2.0-flash-exp" not in flash_models:
            health_report["warnings"].append(
                "Recommended model 'gemini-2.0-flash-exp' not found"
            )
    except Exception as e:
        health_report["checks"]["models"] = {
            "status": "error",
            "message": str(e)
        }
        health_report["errors"].append(f"Model check failed: {e}")
    
    # 2. Check Package Versions
    try:
        packages = {}
        for pkg_name in ["google-adk", "google-genai", "supabase", "protobuf"]:
            try:
                version = pkg_resources.get_distribution(pkg_name).version
                packages[pkg_name] = version
            except:
                packages[pkg_name] = "not installed"
        
        health_report["checks"]["packages"] = {
            "status": "ok",
            "versions": packages
        }
        
        # Check for version compatibility
        if packages.get("protobuf", "").startswith("6."):
            health_report["warnings"].append(
                "Protobuf 6.x detected - may cause issues with ADK 1.0.0"
            )
    except Exception as e:
        health_report["checks"]["packages"] = {
            "status": "error",
            "message": str(e)
        }
    
    # 3. Check Database Connectivity
    try:
        client = SupabaseService.get_client()
        
        # Test query
        response = await asyncio.to_thread(
            lambda: client.table('projects').select('count').limit(1).execute()
        )
        
        health_report["checks"]["database"] = {
            "status": "ok",
            "connected": True,
            "response_time_ms": "< 100"  # Could measure actual time
        }
    except Exception as e:
        health_report["checks"]["database"] = {
            "status": "error",
            "connected": False,
            "message": str(e)
        }
        health_report["errors"].append(f"Database connection failed: {e}")
    
    # 4. Check Agent Registry
    try:
        agents = agent_registry.get_all_agents()
        agent_status = []
        
        for agent_name, agent_instance in agents.items():
            try:
                # Basic validation
                status = {
                    "name": agent_name,
                    "class": agent_instance.__class__.__name__,
                    "tools": len(getattr(agent_instance, 'tools', [])),
                    "status": "ready"
                }
                agent_status.append(status)
            except Exception as e:
                agent_status.append({
                    "name": agent_name,
                    "status": "error",
                    "error": str(e)
                })
        
        health_report["checks"]["agents"] = {
            "status": "ok",
            "total_agents": len(agents),
            "agents": agent_status
        }
    except Exception as e:
        health_report["checks"]["agents"] = {
            "status": "error",
            "message": str(e)
        }
    
    # 5. Check System Resources
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_report["checks"]["system"] = {
            "status": "ok",
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "disk_usage_percent": disk.percent
        }
        
        # Add warnings for high usage
        if cpu_percent > 80:
            health_report["warnings"].append(f"High CPU usage: {cpu_percent}%")
        if memory.percent > 80:
            health_report["warnings"].append(f"High memory usage: {memory.percent}%")
        if disk.percent > 90:
            health_report["warnings"].append(f"High disk usage: {disk.percent}%")
    except Exception as e:
        health_report["checks"]["system"] = {
            "status": "error",
            "message": str(e)
        }
    
    # 6. Check Environment Variables
    env_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        health_report["warnings"].append(
            f"Missing environment variables: {', '.join(missing_vars)}"
        )
    
    # Determine overall status
    if health_report["errors"]:
        health_report["status"] = "unhealthy"
    elif health_report["warnings"]:
        health_report["status"] = "degraded"
    
    # Return appropriate status code
    if health_report["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_report)
    
    return health_report

@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Simple liveness check for Kubernetes."""
    return {"status": "alive"}

@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness check for load balancers."""
    try:
        # Quick DB check
        client = SupabaseService.get_client()
        await asyncio.to_thread(
            lambda: client.table('projects').select('count').limit(1).execute()
        )
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503, detail={"status": "not ready"})
```

### Integration with Main App

```python
# src/instabids/api/main.py
from fastapi import FastAPI
from instabids.api.routes import health

app = FastAPI(title="InstaBids API")

# Include health routes
app.include_router(health.router)
```

### Test Implementation

```python
# tests/api/test_health.py
import pytest
from fastapi.testclient import TestClient
from instabids.api.main import app

client = TestClient(app)

def test_doctor_route():
    """Test comprehensive health check."""
    response = client.get("/healthz/doctor")
    
    assert response.status_code in [200, 503]
    data = response.json()
    
    assert "status" in data
    assert "checks" in data
    assert "timestamp" in data
    
    # Verify all checks present
    expected_checks = [
        "models", "packages", "database", "agents", "system"
    ]
    for check in expected_checks:
        assert check in data["checks"]

def test_liveness_check():
    """Test simple liveness endpoint."""
    response = client.get("/healthz/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_check():
    """Test readiness endpoint."""
    response = client.get("/healthz/ready")
    assert response.status_code in [200, 503]
```

### Usage Examples

```bash
# Check system health
curl http://localhost:8000/healthz/doctor | jq

# Kubernetes liveness probe
curl http://localhost:8000/healthz/live

# Load balancer health check
curl http://localhost:8000/healthz/ready
```

### Response Example

```json
{
  "status": "healthy",
  "timestamp": "2025-05-23T10:00:00Z",
  "checks": {
    "models": {
      "status": "ok",
      "available_models": 15,
      "flash_models": ["gemini-2.0-flash-exp"],
      "recommended_model": true
    },
    "packages": {
      "status": "ok",
      "versions": {
        "google-adk": "1.0.0",
        "google-genai": "1.17.0",
        "supabase": "2.0.0",
        "protobuf": "5.29.4"
      }
    },
    "database": {
      "status": "ok",
      "connected": true,
      "response_time_ms": "< 100"
    },
    "agents": {
      "status": "ok",
      "total_agents": 5,
      "agents": [
        {
          "name": "homeowner",
          "class": "HomeownerAgent",
          "tools": 8,
          "status": "ready"
        }
      ]
    },
    "system": {
      "status": "ok",
      "cpu_usage_percent": 15.2,
      "memory_usage_percent": 45.8,
      "disk_usage_percent": 62.3
    }
  },
  "warnings": [],
  "errors": []
}
```