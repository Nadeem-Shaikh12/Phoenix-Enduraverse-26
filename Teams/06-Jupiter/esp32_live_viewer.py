"""
esp32_live_viewer.py
=====================
Standalone live camera viewer for the ESP32-S3 N16R8.

Connects to the ESP32 camera HTTP MJPEG stream and shows it
in a fullscreen OpenCV window. Press 'q' to quit, 's' to snapshot.

Usage:
    python esp32_live_viewer.py                     # auto-detects stream URL
    python esp32_live_viewer.py --ip 10.37.50.209  # specify IP
    python esp32_live_viewer.py --url http://10.37.50.209:81/stream
"""

import argparse
import sys
import time
import os
from datetime import datetime

import cv2
import requests
import numpy as np

# ── Common ESP32 Camera streaming URL patterns ──────────────────────────────
# The ESP32-S3 with Arduino CameraWebServer firmware typically uses one of these:
DEFAULT_STREAM_URLS = [
    "http://{ip}:81/stream",
    "http://{ip}/stream",
    "http://{ip}:80/stream",
    "http://{ip}:8080/stream",
    "http://{ip}/mjpeg/1",
    "http://{ip}:81/mjpeg",
    "http://{ip}/video",
    "http://{ip}:4747/video",   # DroidCam
]

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "data", "snapshots")


def find_stream(ip: str) -> str | None:
    """Probe common ESP32 MJPEG URL patterns and return the first working one."""
    print(f"[*] Auto-detecting stream at {ip} ...")
    for pattern in DEFAULT_STREAM_URLS:
        url = pattern.format(ip=ip)
        try:
            r = requests.get(url, stream=True, timeout=2)
            ct = r.headers.get("Content-Type", "")
            if r.status_code == 200 and ("multipart" in ct or "jpeg" in ct or "octet" in ct):
                print(f"[✓] Found stream at: {url}  (Content-Type: {ct})")
                r.close()
                return url
            r.close()
        except Exception:
            pass
        print(f"     {url} — no response")
    return None


def read_mjpeg_stream(url: str):
    """
    Generator that yields decoded BGR frames from an MJPEG HTTP stream.
    Works with both OpenCV VideoCapture (fast) and requests byte-parsing (fallback).
    """
    print(f"[*] Connecting to: {url}")

    # Method 1: OpenCV native (fastest, handles any MJPEG stream)
    cap = cv2.VideoCapture(url)
    if cap.isOpened():
        print("[✓] OpenCV stream opened successfully.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[!] Frame dropped — reconnecting ...")
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(url)
                continue
            yield frame
        cap.release()
        return

    # Method 2: requests byte-by-byte MJPEG parser (fallback)
    print("[~] OpenCV direct open failed, trying byte-stream parser ...")
    while True:
        try:
            r = requests.get(url, stream=True, timeout=10)
            buf = b""
            for chunk in r.iter_content(chunk_size=4096):
                buf += chunk
                start = buf.find(b"\xff\xd8")  # JPEG start
                end   = buf.find(b"\xff\xd9")  # JPEG end
                if start != -1 and end != -1 and end > start:
                    jpg_data = buf[start:end + 2]
                    buf = buf[end + 2:]
                    frame = cv2.imdecode(np.frombuffer(jpg_data, np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        yield frame
        except Exception as e:
            print(f"[!] Stream error: {e} — retrying in 2 s ...")
            time.sleep(2)


def run_viewer(url: str):
    """Main viewer loop — shows live feed in OpenCV window."""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    WIN = "ESP32-S3 Live Camera — press Q to quit, S to snapshot"
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN, 960, 720)

    fps_t   = time.time()
    fps_cnt = 0
    fps     = 0.0

    print("\n" + "═" * 55)
    print("  ESP32-S3  ⬤  Live Camera Feed")
    print(f"  Stream : {url}")
    print("  Q = quit   S = save snapshot")
    print("═" * 55 + "\n")

    for frame in read_mjpeg_stream(url):
        # FPS counter
        fps_cnt += 1
        elapsed = time.time() - fps_t
        if elapsed >= 1.0:
            fps = fps_cnt / elapsed
            fps_cnt = 0
            fps_t = time.time()

        # Overlay FPS + timestamp
        overlay = frame.copy()
        ts  = datetime.now().strftime("%H:%M:%S")
        txt = f"LIVE  {ts}  |  {fps:.1f} FPS"
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 28), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        cv2.putText(frame, txt, (8, 19),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 120), 1, cv2.LINE_AA)

        cv2.imshow(WIN, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("[*] Quit.")
            break
        elif key == ord("s"):
            fn  = datetime.now().strftime("snap_%Y%m%d_%H%M%S.jpg")
            path = os.path.join(SNAPSHOT_DIR, fn)
            cv2.imwrite(path, frame)
            print(f"[✓] Snapshot saved: {path}")

    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="ESP32-S3 Live Camera Viewer")
    parser.add_argument("--ip",  default="10.37.50.209", help="ESP32 IP address")
    parser.add_argument("--url", default=None,           help="Full stream URL (skips auto-detect)")
    args = parser.parse_args()

    if args.url:
        url = args.url
    else:
        url = find_stream(args.ip)
        if not url:
            print("\n[✗] Could not find a live stream on any common endpoint.")
            print("     Make sure the ESP32-S3 has the CameraWebServer firmware flashed.")
            print("     Common stream URLs to try manually:")
            for p in DEFAULT_STREAM_URLS[:4]:
                print(f"       python esp32_live_viewer.py --url {p.format(ip=args.ip)}")
            sys.exit(1)

    run_viewer(url)


if __name__ == "__main__":
    main()
