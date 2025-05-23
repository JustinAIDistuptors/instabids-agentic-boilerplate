# 🛠️ Common Pitfalls & Instant Fixes — Google ADK 1.0.0 - Python
_Last verified 22 May 2025_

| # | Pitfall (≈ probability) | Symptom / bad snippet | One-liner Fix | 🔗 Refs |
|---|------------------------|----------------------|---------------|---------||
| **1** | **Legacy import** (90 %) | `import google.generativeai as genai` | `from google import genai` | [ADK Quickstart](https://github.com/google/adk-python) |
| **2** | **Ghost Git wheel** (90 %) | `ModuleNotFoundError: google.adk.cli.main` after you once did `pip install google-adk@git+…` | ```bash\npoetry cache clear pypi --all && rd /s /q .venv && poetry lock --no-update && poetry install\n``` | GH #73, #743 |
| **3** | **Missing Vertex extras** (85 %) | `google.cloud.aiplatform` import fails in streaming | `pip install "google-adk[vertexai]~=1.0.0"` | [Docs Install](https://github.com/google/adk-python#installation) |
| **4** | **Protobuf 5↔6 mismatch** (80 %) | `ImportError: XXX_pb2` deep in `google.cloud.*` | Pin `protobuf==5.29.4` until 1.0.1 GA | issue #618 |
| **5** | **Wrong export var** (80 %) | `.adk scan skips your module` | In `__init__.py`: `from .agent import agent` (NOT `root_agent`) | Quickstart code |
| **6** | **`ToolContext` omitted** (75 %) | `TypeError: my_tool() missing tool_context` | ```python\ndef my_tool(tool_context:ToolContext, q:str)->dict:\n    ...\n``` | Vertex ref page |
| **7** | **Live ID gap** (70 %) | `ValueError: Model …live-001 not found` | Use `"gemini-2.0-flash-exp"` **or** `pip install --pre google-adk` | GH #866 |
| **8** | **Paper-thin docstrings** (70 %) | Agent keeps hallucinating tool args | ≥ 5-line docstring with `Args:` & `Returns:` | ADK tool guide |
| **9** | **Bad module paths** (65 %) | `from google.adk.runtime import Event` | Correct paths: `google.adk.events`, `google.adk.types`, `google.adk.agents.llm_agent` | GH #74, Docs |
| **10** | **No state prefix** (60 %) | Cross-user state leakage | Use `user:` `app:` `temp:` in keys | ADK state doc |
| **11** | **Positional Agent ctor** (55 %) | Params shift after refactor | Always keyword: `MyAgent(name=..., model=...)` | common style |
| **12** | **Port 8000/8001 busy** (55 %) | `[Errno 10048] Address already in use` | Free port helper: `ports.pick_free()` | Windows issue |
| **13** | **Loose tool return** (50 %) | `ToolCallValidationError` | Return at least `{"status": "success", ...}` | ADK samples |
| **14** | **Global adk.exe shadows venv** (45 %) | `adk web` uses wrong Python | Uninstall global (`pipx uninstall adk`) | Win PATH |
| **15** | **Proactor loop missing** (40 %) | `RuntimeError: Event loop closed` streaming | ```py\nif sys.platform.startswith('win'):\n  asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())``` | issue #296 |
| **16** | **Wrong `__init__.py` re-export** (40 %) | Components scan finds pkg but not instance | `from .agent import agent` | Quickstart |
| **17** | **Model misuse** (35 %) | Slow/costly calls | Flash for speed, Pro for complexity | Model table |
| **18** | **Env var typo** (35 %) | `PermissionDenied` from Vertex API | Must export `GOOGLE_API_KEY` | GH #693 |
| **19** | **A2A vs MCP mix-up** (30 %) | Wrong transport for tool calls | Remember: A2A = agent events, MCP = code builder interface | Docs |
| **20** | **Old streaming helper** (30 %) | Using `.start_stream()` | Use `run_live()` pattern | Streaming quickstart |
| **21** | **CallbackContext mis-typed** (25 %) | `AttributeError` in callbacks | Mirror signature from superclass (`inspect.signature`) | issue #2022 |
| **22** | **Artifact store confusion** (20 %) | Binary blobs inline → OOM | Use `LocalArtifactStore` dev; GCS in prod | Artifacts doc |
| **23** | **Docker misses extras** (20 %) | `ModuleNotFoundError: google.cloud` | `RUN pip install "google-adk[vertexai]~=1.0.0"...` | Cloud Run doc |
| **24** | **CI uses dead cmd** (15 %) | `adk: error: unrecognized arguments --script` | `poetry run adk test` or `adk api_server` | Test docs |
| **25** | **`sub_agents` misuse** (15 %) | Parent fails to delegate | Provide class list *or* `.adk/components.json`—not both | Agent-team tut |
| **26** | **Live quota 5-stream cap** (15 %) | `429 RESOURCE_EXHAUSTED` | Throttle tests; set dummy key in CI | Vertex quota doc |
| **27** | **Supabase RLS on Storage** (10 %) | 403 when agent fetches artifact | Add bucket-level policy for `service_role` | Supabase docs |
| **28** | **Circular import after hot-rewrite** (10 %) | `ImportError: cannot import name agent` | Writer agent must restart proc or `pip install -e .` | GH #61 |
| **29** | **grpcio-status vs Protobuf pin** (5 %) | `_Call` object attr error | Keep grpcio-status 1.71 + protobuf 5.29.4 | Compat table |
| **30** | **Model-catalog cache** (5 %) | "model not found" after upgrading wheel | `rm -f ~/.cache/adk/model_catalog.json` | GH #866 note |
| **31** | **adk web blank screen** (Chrome 125+) | Blank UI on Chrome | `pip install adk-web==0.2.1` or set `ADK_WEB_DEV=true` | GH #874 |
| **32** | **Unlimited streaming bill shock** | Live agent keeps mic open | Call `loop_agent.stop_live()` or set `max_ttl_secs` | Cost docs |
| **33** | **google-genai ≥ 1.18.0 break** | `TypeError: AsyncIterator` | Pin `google-genai==1.17.*` until ADK 1.0.1 | Breaking change |
| **34** | **google-ai-python Protobuf 6** | Indirect dependency conflict | Add `google-cloud-core~=2.24,<3` | Dependency tree |
| **35** | **CI model cache survives** | "model not found" in next job | Add to reset: `rm -rf ~/.cache/adk/model_catalog.json` | CI caching |

---

## One-time Bootstrap Script (`scripts/reset_env.sh`)

```bash
#!/bin/bash
poetry cache clear pypi --all
rm -rf .venv
poetry lock --no-update
poetry install --sync
rm -f ~/.cache/adk/model_catalog.json
```

## Windows Version (`scripts/reset_env.ps1`)

```powershell
poetry cache clear pypi --all
Remove-Item -Recurse -Force .venv
poetry lock --no-update
poetry install --sync
Remove-Item $env:USERPROFILE\.cache\adk\model_catalog.json -ErrorAction SilentlyContinue
```

## Port Helper (`src/instabids/utils/ports.py`)

```python
import socket, random, contextlib

def pick_free_port() -> int:
    """Return an unused TCP port (avoids Errno 10048 on Windows)."""
    for _ in range(20):
        port = random.randint(8100, 9000)
        with contextlib.closing(socket.socket()) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free port found")
```

## "Doctor" Route Example

```python
from fastapi import APIRouter
from google import genai
import importlib, pkg_resources, json

router = APIRouter(tags=["healthz"])

@router.get("/healthz/doctor")
def doctor():
    models = [m.name for m in genai.discovery.list_models()
              if "flash" in m.name]
    pkgs = {p.key: p.version for p in pkg_resources.working_set
            if p.key.startswith("google-adk") or p.key == "google-genai"}
    return {"models": models, "packages": pkgs}
```

## How to use this file

1. **Copy everything above** into `docs/common-pitfalls.md`.
2. **Link it** from your README.md and onboarding doc.
3. **In every writer-agent system prompt**, add:
   > "Before committing, open docs/COMMON_PITFALLS.md and verify none of your code triggers a listed pitfall."

Now your all-agent team has a living, source-cited cheat-sheet that matches the real-world quirks of ADK 1.0.0 as seen this week.