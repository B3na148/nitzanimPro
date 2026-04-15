from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT_DIR = Path(__file__).resolve().parent.parent
SERVER_DIR = ROOT_DIR / "server"
SERVER_SCRIPT = SERVER_DIR / "server.py"
HISTORY_DIR = SERVER_DIR / "history_data"
REPORT_PATH = SERVER_DIR / "final_report.json"
SAVE_HISTORY_URL = "http://localhost:5000/save-history"


def _import_local_analyzer():
    """Import analyzer lazily so this module stays lightweight on import."""
    if str(SERVER_DIR) not in sys.path:
        sys.path.insert(0, str(SERVER_DIR))
    from categorization import LocalAnalyzer  # type: ignore

    return LocalAnalyzer


def _is_server_alive(url: str = SAVE_HISTORY_URL, timeout: float = 0.8) -> bool:
    probe_url = url.rsplit("/", 1)[0]
    try:
        request.urlopen(probe_url, timeout=timeout)
    except error.HTTPError:
        # The server is alive even if route returns 404
        return True
    except Exception:
        return False
    return True


def _wait_for_server(url: str = SAVE_HISTORY_URL, timeout_seconds: float = 10.0) -> bool:
    end = time.time() + timeout_seconds
    while time.time() < end:
        if _is_server_alive(url):
            return True
        time.sleep(0.25)
    return False


def _start_server_process(python_executable: str | None = None) -> subprocess.Popen:
    py = python_executable or sys.executable
    return subprocess.Popen(
        [py, str(SERVER_SCRIPT)],
        cwd=str(SERVER_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )


def _post_history_to_server(history_payload: Any, url: str = SAVE_HISTORY_URL, timeout: float = 10.0) -> dict:
    payload = json.dumps(history_payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url=url,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _latest_history_file() -> Path:
    if not HISTORY_DIR.exists():
        raise FileNotFoundError(f"History directory not found: {HISTORY_DIR}")
    files = sorted(HISTORY_DIR.glob("history_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No history files found in: {HISTORY_DIR}")
    return files[0]


def run_big_button(
    history_payload: Any | None = None,
    *,
    start_server_if_needed: bool = True,
    run_ai_analysis: bool = True,
    model_name: str = "qwen2.5:0.5b",
    output_report_path: str | Path | None = None,
) -> dict:
    """
    Orchestrator for your interface button:
      1) Ensures backend server is available (optional)
      2) Sends extension-like history payload to /save-history (optional)
      3) Runs AI categorization on latest saved history (optional)

    Returns a status dictionary you can show in the interface.
    """
    status: dict[str, Any] = {
        "server_started_by_button": False,
        "server_ready": False,
        "history_saved": False,
        "history_file": None,
        "analysis_ran": False,
        "report_file": None,
    }

    if start_server_if_needed and not _is_server_alive():
        _start_server_process()
        status["server_started_by_button"] = True

    status["server_ready"] = _wait_for_server() if start_server_if_needed else _is_server_alive()
    if not status["server_ready"]:
        raise RuntimeError("Server is not reachable on http://localhost:5000")

    if history_payload is not None:
        response = _post_history_to_server(history_payload)
        status["history_saved"] = True
        status["server_response"] = response

    history_file = _latest_history_file()
    status["history_file"] = str(history_file)

    if run_ai_analysis:
        LocalAnalyzer = _import_local_analyzer()
        output_path = Path(output_report_path) if output_report_path else REPORT_PATH
        analyzer = LocalAnalyzer(model_name=model_name)
        analyzer.run_analysis(str(history_file), str(output_path))
        status["analysis_ran"] = True
        status["report_file"] = str(output_path)

    return status
