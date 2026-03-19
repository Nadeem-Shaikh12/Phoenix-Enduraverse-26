"""
run_dreamvision.py
==================
One-command launcher for the entire DreamVision system.

Usage:
    python run_dreamvision.py

Core Flow:
  1. Aggressively kills any processes listening on ports 3000 and 8002
  2. Starts Express API and waits for http://localhost:3000 to be ready (max 15s)
  3. Starts FastAPI Edge Server and waits for http://localhost:8002 to be ready (max 15s)
  4. Opens browser to the Dashboard
  5. ONLY launches Python Live Feed app if both servers started correctly.
"""

import subprocess
import sys
import os
import time
import webbrowser
import socket
import signal
import threading
import urllib.request

ROOT    = os.path.dirname(os.path.abspath(__file__))
EXPRESS = os.path.join(ROOT, "express_backend")
EDGE    = os.path.join(ROOT, "edge_server")

PROCESSES = []

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def info(msg):  print(f"{CYAN}[DreamVision]{RESET} {msg}")
def ok(msg):    print(f"{GREEN}[  OK  ]{RESET} {msg}")
def warn(msg):  print(f"{YELLOW}[ WARN ]{RESET} {msg}")
def err(msg):   print(f"{RED}[ ERR  ]{RESET} {msg}")

# ── Port killer ───────────────────────────────────────────────────────────────
def kill_port(port: int):
    sys.stdout.write(f"Killing any process on port {port}...")
    sys.stdout.flush()
    if sys.platform == "win32":
        # First use netstat to find PID, then taskkill
        cmd = f"for /f \"tokens=5\" %a in ('netstat -ano ^| findstr :{port} ^| findstr LISTENING') do taskkill /F /PID %a >nul 2>&1"
        os.system(cmd)
    else:
        os.system(f"fuser -k {port}/tcp >/dev/null 2>&1")
    print(f" {GREEN}Cleared!{RESET}")

# ── HTTP Health Check ─────────────────────────────────────────────────────────
def wait_for_http(url: str, label: str, max_wait: float = 15.0) -> bool:
    deadline = time.time() + max_wait
    sys.stdout.write(f"   Waiting for {label} ({url}) ")
    sys.stdout.flush()
    
    while time.time() < deadline:
        try:
            req = urllib.request.urlopen(url, timeout=1.0)
            if req.getcode() == 200 or req.getcode() == 404: 
                # Either way, the HTTP server responded, meaning it is alive
                print(f" {GREEN}ready!{RESET}")
                return True
        except Exception:
            pass
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1.0)
        
    print(f" {RED}Timeout (15s)!{RESET}")
    err(f"{label} failed to start within 15 seconds. Check logs above for crash details.")
    return False

# ── Subprocess Runner ─────────────────────────────────────────────────────────
def launch(cmd: list, cwd: str, label: str) -> subprocess.Popen:
    info(f"Starting {label} …")
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    PROCESSES.append((label, p))
    return p

# ── Log Streamer ──────────────────────────────────────────────────────────────
def _stream(proc: subprocess.Popen, prefix: str):
    def _reader(pipe, is_err):
        try:
            for line in iter(pipe.readline, b""):
                txt = line.decode(errors="replace").rstrip()
                if txt:
                    if is_err:
                        print(f"  {RED}[{prefix}/ERR]{RESET} {txt}")
                    else:
                        print(f"  {YELLOW}[{prefix}/OUT]{RESET} {txt}")
        except Exception:
            pass

    t1 = threading.Thread(target=_reader, args=(proc.stdout, False), daemon=True)
    t2 = threading.Thread(target=_reader, args=(proc.stderr, True), daemon=True)
    t1.start()
    t2.start()

# ── Shutdown Hook ─────────────────────────────────────────────────────────────
def shutdown(sig=None, frame=None):
    print(f"\n{YELLOW}[DreamVision]{RESET} Shutting down all processes …")
    for label, p in PROCESSES:
        try:
            if sys.platform == "win32":
                p.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                p.terminate()
        except: pass
    time.sleep(1)
    for label, p in PROCESSES:
        try: p.kill()
        except: pass
    ok("All processes stopped. Goodbye!")
    sys.exit(0)

signal.signal(signal.SIGINT,  shutdown)
signal.signal(signal.SIGTERM, shutdown)


def main():
    print(f"""{BOLD}{CYAN}
 ██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗██╗  ██╗ ██╗███████╗██╗ ██████╗ ███╗   ██╗
 ██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗ ████║██║  ██║ ██║██╔════╝██║██╔═══██╗████╗  ██║
 ██║  ██║██████╔╝█████╗  ███████║██╔████╔██║╚██╗██╔╝ ██║███████╗██║██║   ██║██╔██╗ ██║
 ██║  ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║ ╚███╔╝  ██║╚════██║██║██║   ██║██║╚██╗██║
 ██████╔╝██║  ██║███████╗██║  ██║██║ ╚═╝ ██║  ██║    ██║███████║██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝    ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
{RESET}
  {BOLD}DreamVision: Sequential Launcher (Express -> FastAPI -> UI){RESET}
""")

    info("Step 1: Terminating any Zombie Servers on ports 3000 & 8002...")
    kill_port(3000)
    kill_port(8002)
    time.sleep(1)

    print("")
    info("Step 2: Starting Express Backend Data API...")
    node_cmd = ["node", "index.js"]
    express_proc = launch(node_cmd, EXPRESS, "Express API (port 3000)")
    _stream(express_proc, "Express")

    if not wait_for_http("http://127.0.0.1:3000", "Express API"):
        err("Express Backend failed to start. Cannot continue. Shutting down.")
        shutdown()

    print("")
    info("Step 3: Starting FastAPI Edge Processor...")
    uvicorn_cmd = [
        sys.executable, "-m", "uvicorn",
        "api.server:app",
        "--host", "0.0.0.0",
        "--port", "8002",
        "--reload"
    ]
    edge_proc = launch(uvicorn_cmd, EDGE, "FastAPI Edge Server (port 8002)")
    _stream(edge_proc, "FastAPI")

    if not wait_for_http("http://127.0.0.1:8002/docs", "FastAPI Edge"):
        err("FastAPI Edge Server failed to start. Cannot continue. Shutting down.")
        shutdown()

    print("")
    info("Step 4: Bootstrapping Desktop & Web UIs...")
    time.sleep(1) # tiny beat to ensure logs printed

    dashboard_url = "http://localhost:3000"
    info(f"Opening browser to Dashboard: {dashboard_url}")
    webbrowser.open(dashboard_url)

    live_feed_script = os.path.join(ROOT, "live_feed_app.py")
    if os.path.exists(live_feed_script):
        feed_proc = launch([sys.executable, live_feed_script], ROOT, "Live Feed Tkinter App")
        _stream(feed_proc, "LiveFeed")
        ok("Desktop Live Feed App launched.")
    else:
        warn("live_feed_app.py missing — skipping desktop app.")

    print(f"""
{GREEN}{'═'*60}{RESET}
{BOLD}  🚀 DreamVision Fully Initialized!{RESET}

  {BOLD}Dashboard:{RESET}       http://localhost:3000
  {BOLD}FastAPI Docs:{RESET}    http://localhost:8002/docs
  {BOLD}Camera Feed:{RESET}     ESP32 must be connected via WiFi

  Press {BOLD}Ctrl+C{RESET} to stop everything cleanly.
{GREEN}{'═'*60}{RESET}
""")

    try:
        while True:
            for label, p in PROCESSES:
                if p.poll() is not None and label != "Live Feed Tkinter App":
                    # Tkinter app is allowed to exit via Q or X button 
                    err(f"{label} crashed abruptly! (Exit code {p.returncode})")
                    shutdown()
            time.sleep(3)
    except KeyboardInterrupt:
        shutdown()

if __name__ == "__main__":
    main()
