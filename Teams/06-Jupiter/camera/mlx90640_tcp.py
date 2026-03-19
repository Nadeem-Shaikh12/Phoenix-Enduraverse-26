"""
camera/mlx90640_tcp.py
=======================
TCP reader for the DreamVision ESP32-S3 Firmware.

Wire protocol (per the firmware in firmware/src/main.cpp):
  [0–1]  : 0xAA 0xBB  – magic bytes
  [2–5]  : uint32 LE  – payload length in bytes (always 768 * 4 = 3072)
  [6–7]  : 0x00 0x00  – reserved
  [8 …]  : 768 × float32 LE – raw MLX90640 temperatures in °C (row-major, 32×24)

Total frame = 8 (header) + 3072 (payload) = 3080 bytes.

Usage:
    cam = MLX90640TCPCamera("10.37.50.209", 5000)
    cam.open()
    frame_celsius = cam.next_frame()   # np.ndarray float32, shape=(24, 32)
    cam.close()
"""

import socket
import struct
import threading
import queue
import time
import logging
import numpy as np
from typing import Optional

import camera.config as cfg

logger = logging.getLogger("dreamvision.mlx90640_tcp")

# Frame constants matching firmware
MAGIC          = b"\xAA\xBB"
HEADER_SIZE    = 8       # 2 magic + 4 length + 2 reserved
PAYLOAD_FLOATS = 768     # 32 × 24
PAYLOAD_BYTES  = PAYLOAD_FLOATS * 4   # float32 = 4 bytes each
TOTAL_FRAME    = HEADER_SIZE + PAYLOAD_BYTES   # 3080 bytes


class MLX90640TCPCamera:
    """
    Connects to the ESP32-S3 firmware TCP server and reads real thermal frames.
    Thread-safe: a background reader thread fills a queue; next_frame() pops from it.
    """

    def __init__(self, host: str = None, port: int = None, timeout: float = 10.0):
        self.host    = host or cfg.ESP32_HOST
        self.port    = port or cfg.ESP32_PORT
        self.timeout = timeout

        self._sock: Optional[socket.socket] = None
        self._queue: queue.Queue = queue.Queue(maxsize=3)
        self._stop   = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._open   = False

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _recv_exact(self, n: int) -> Optional[bytes]:
        """Read exactly n bytes from socket; returns None on disconnect/timeout."""
        buf = bytearray()
        while len(buf) < n:
            try:
                chunk = self._sock.recv(n - len(buf))
            except (socket.timeout, OSError) as e:
                logger.warning("[MLX TCP] Socket read error: %s", e)
                return None
            if not chunk:
                logger.warning("[MLX TCP] Connection closed by ESP32.")
                return None
            buf.extend(chunk)
        return bytes(buf)

    def _sync_header(self) -> Optional[int]:
        """
        Scan the TCP stream byte-by-byte until the 0xAA 0xBB magic is found,
        then read the 4-byte length and 2 reserved bytes.
        Returns payload length or None on error.
        """
        b1 = self._recv_exact(1)
        if b1 is None:
            return None

        while True:
            if b1 == b"\xAA":
                b2 = self._recv_exact(1)
                if b2 is None:
                    return None
                if b2 == b"\xBB":
                    # Found magic – read rest of header
                    rest = self._recv_exact(6)  # 4 length + 2 reserved
                    if rest is None:
                        return None
                    payload_len = struct.unpack_from("<I", rest, 0)[0]
                    return payload_len
                else:
                    b1 = b2  # continue scanning
            else:
                b1 = self._recv_exact(1)
                if b1 is None:
                    return None

    def _connect(self) -> bool:
        """Attempt TCP connection to ESP32. Returns True on success."""
        while not self._stop.is_set():
            try:
                logger.info("[MLX TCP] Connecting to %s:%d …", self.host, self.port)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
                sock.connect((self.host, self.port))
                self._sock = sock
                logger.info("[MLX TCP] ✓ Connected to ESP32-S3 at %s:%d", self.host, self.port)
                return True
            except OSError as e:
                logger.warning("[MLX TCP] Connection failed: %s – retrying in 3 s …", e)
                try:
                    sock.close()
                except Exception:
                    pass
                time.sleep(3)
        return False

    def _reader_loop(self):
        """Background thread: keeps reading frames and pushing them to the queue."""
        while not self._stop.is_set():
            if not self._connect():
                break

            logger.info("[MLX TCP] Reader thread active – streaming MLX90640 frames.")
            while not self._stop.is_set():
                payload_len = self._sync_header()
                if payload_len is None:
                    logger.warning("[MLX TCP] Header sync lost – reconnecting …")
                    break

                if payload_len != PAYLOAD_BYTES:
                    logger.warning("[MLX TCP] Unexpected payload len %d (expected %d) – resyncing",
                                   payload_len, PAYLOAD_BYTES)
                    continue  # try to re-sync

                raw = self._recv_exact(payload_len)
                if raw is None:
                    logger.warning("[MLX TCP] Payload read failed – reconnecting …")
                    break

                # Decode 768 float32 → 24×32 numpy array
                temperatures = np.frombuffer(raw, dtype=np.float32).reshape(24, 32).copy()

                # Drop oldest frame if queue is full (keep latency low)
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    pass
                self._queue.put(temperatures)

            # Close socket and retry
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    # ── Public interface ──────────────────────────────────────────────────────

    def open(self) -> None:
        """Start background reader thread. Blocks until first frame arrives (max 15 s)."""
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._reader_loop, daemon=True, name="mlx-tcp-reader"
        )
        self._thread.start()

        # Wait for first frame
        deadline = time.time() + 15.0
        while time.time() < deadline:
            if not self._queue.empty():
                self._open = True
                logger.info("[MLX TCP] ✓ First frame received — real thermal stream active!")
                return
            time.sleep(0.1)

        self.close()
        raise ConnectionError(
            f"No frames from ESP32-S3 at {self.host}:{self.port} within 15 s. "
            "Check that the ESP32 is powered, connected to the same WiFi, and "
            "the firmware is running."
        )

    def next_frame(self) -> Optional[np.ndarray]:
        """Return the latest thermal frame (24×32 float32 °C array), or None on timeout."""
        try:
            return self._queue.get(timeout=self.timeout)
        except queue.Empty:
            logger.warning("[MLX TCP] No frame received within %g s", self.timeout)
            return None

    def close(self) -> None:
        logger.info("[MLX TCP] Shutting down …")
        self._stop.set()
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=5)
        self._open = False
        logger.info("[MLX TCP] Closed.")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()
