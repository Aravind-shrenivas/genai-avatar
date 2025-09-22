import os
import sys
import time
import uuid
import socket
import signal
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Config for defaults; override per-request
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000  # ensure unique port per spawn if running multiple
UI_PATH = "/ui"

app = FastAPI()

class LaunchRequest(BaseModel):
    config: str
    host: Optional[str] = None
    port: Optional[int] = None
    env: Optional[str] = None
    timeout_sec: int = 120

procs = {}  # pid -> metadata; simplistic in-memory tracking


def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def wait_for_ready(host: str, port: int, timeout: int) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(host, port):
            return True
        time.sleep(0.5)
    return False


def choose_free_port(start_port: int = DEFAULT_PORT, max_tries: int = 100) -> int:
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("No free port found")


@app.post("/spawn")
def spawn(request: LaunchRequest, http_req: Request):
    cfg_path = Path(request.config).expanduser().resolve()
    if not cfg_path.exists():
        raise HTTPException(status_code=400, detail=f"Config not found: {cfg_path}")

    host = request.host or DEFAULT_HOST
    port = request.port or choose_free_port()

    # Build command: replicate "uv run --active src/demo.py --config <abs>.yaml"
    # For portability, call python directly; adapt if 'uv' is mandatory in the environment.
    cmd = [
        sys.executable,
        "src/demo.py",
        "--host", host,
        "--port", str(port),
        "--config", str(cfg_path),
    ]
    if request.env:
        cmd += ["--env", request.env]

    # Inherit env; ensure PYTHONPATH includes project dir if needed
    env = os.environ.copy()

    # Start subprocess detached enough to not block; capture stdout/stderr for debugging
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        preexec_fn=os.setsid if hasattr(os, "setsid") else None,  # POSIX
    )

    sid = uuid.uuid4().hex
    procs[proc.pid] = {"sid": sid, "host": host, "port": port, "cfg": str(cfg_path), "start": time.time()}

    # Wait for server to listen on port
    if not wait_for_ready(host, port, request.timeout_sec):
        try:
            # Best-effort terminate if it failed to come up
            if hasattr(os, "killpg") and proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            pass
        raise HTTPException(status_code=504, detail="Timed out waiting for demo to start")

    # Build external URL from request headers (supports proxies)
    scheme = http_req.headers.get("x-forwarded-proto", http_req.url.scheme)
    host_hdr = http_req.headers.get("x-forwarded-host", http_req.headers.get("host"))
    base = f"{scheme}://{host_hdr}" if host_hdr else f"http://{host}:{port}"

    # If accessed directly, return local bind; if behind proxy, callers should reach via proxy host
    url = f"{base}{UI_PATH}" if host_hdr else f"http://{host}:{port}{UI_PATH}"
    return {"url": url, "pid": proc.pid, "sid": sid}


@app.post("/stop")
def stop(pid: int):
    if pid not in procs:
        raise HTTPException(status_code=404, detail="Unknown pid")
    try:
        if hasattr(os, "killpg"):
            os.killpg(os.getpgid(pid), signal.SIGTERM)
        else:
            os.kill(pid, signal.SIGTERM)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop {pid}: {e}")
    finally:
        procs.pop(pid, None)
    return {"stopped": pid}


@app.get("/healthz")
def health():
    return {"ok": True}
