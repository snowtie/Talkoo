import threading
import time
import webbrowser
import urllib.request
import urllib.error
import sys
import uvicorn
from talkoo import Talkoo
from talkoo_api import app
from config import load_config
from pathlib import Path


def read_host_port(file_name="HP.txt"):
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent
    file_path = base_dir / file_name

    try:
        with file_path.open("r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            host = lines[0] if len(lines) > 0 else "127.0.0.1"
            port = int(lines[1]) if len(lines) > 1 else 8000
            if not (1 <= port <= 65535):
                port = 8000
            return host, port
    except (FileNotFoundError, ValueError):
        return "127.0.0.1", 8000


def wait_and_open_browser(url: str, timeout_sec: int = 20, interval_sec: float = 0.3):
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    webbrowser.open(url.rsplit("/health", 1)[0])
                    return
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            pass
        time.sleep(interval_sec)


if __name__ == "__main__":
    HOST, PORT = read_host_port("HP.txt")
    BASE_URL = f"http://{HOST}:{PORT}"
    HEALTH_URL = f"{BASE_URL}/health"

    talkoo_translator = Talkoo()
    app.state.tokenizer = talkoo_translator.tokenizer
    app.state.base_model = talkoo_translator.base_model
    app.state.device = talkoo_translator.actual_device

    load_config()
    
    threading.Thread(
        target=wait_and_open_browser,
        args=(HEALTH_URL,),
        daemon=True
    ).start()

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
