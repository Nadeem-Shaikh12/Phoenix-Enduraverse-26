import cv2
import urllib.request
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from PIL import Image, ImageTk
import io
import os
import time
import uuid
from datetime import datetime

COMPONENT_THRESHOLDS = {
    "crankcase": {"max": 80, "critical": 140, "failure": 180},
    "gearbox_housing": {"max": 60, "critical": 110, "failure": 140},
    "cylinder_head": {"max": 150, "critical": 250, "failure": 300},
    "engine_cover": {"max": 70, "critical": 120, "failure": 150},
    "cam_cover": {"max": 60, "critical": 110, "failure": 140},
    "oil_pump_housing": {"max": 80, "critical": 120, "failure": 150},
    "clutch_housing": {"max": 90, "critical": 160, "failure": 200}
}

# ── Config ──────────────────────────────────────────
ESP32_IP = "10.37.50.209"
STREAM_URL = f"http://{ESP32_IP}/stream"
SNAPSHOT_URL = f"http://{ESP32_IP}/snapshot"
STATUS_URL = f"http://{ESP32_IP}/status"
API_URL = "http://localhost:3000"
SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "express_backend", "public", "snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

class DreamVisionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DreamVision - Live Camera Feed")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0f172a")
        
        # Key Bindings
        self.root.bind('<s>', lambda e: self.take_snapshot())
        self.root.bind('<S>', lambda e: self.take_snapshot())
        self.root.bind('<q>', lambda e: self.root.quit())
        self.root.bind('<Q>', lambda e: self.root.quit())

        self.running = False
        self.stream_thread = None
        self.current_frame = None  # To hold the latest frame for snapshots
        
        # Data for video overlay and snapshots
        self.overlay_data = {
            "part_uid": "--",
            "temperature": "--",
            "ambient_temp": "--",
            "variance": "--",
            "status": "UNKNOWN"
        }

        self.build_ui()
        self.update_stats()

    def build_ui(self):
        # ── Title ──
        title = tk.Label(self.root, text="DreamVision Live Feed",
                        font=("Arial", 20, "bold"),
                        bg="#0f172a", fg="#38bdf8")
        title.pack(pady=10)

        # ── Status bar ──
        self.status_var = tk.StringVar(value="Disconnected (Press S to Snapshot, Q to Quit)")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                             font=("Arial", 10),
                             bg="#1e293b", fg="#94a3b8",
                             padx=10, pady=5)
        status_bar.pack(fill=tk.X, padx=20)

        # ── Main frame ──
        main_frame = tk.Frame(self.root, bg="#0f172a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ── Left — camera feed ──
        left_frame = tk.Frame(main_frame, bg="#1e293b",
                             relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))

        cam_title = tk.Label(left_frame, text="Live Camera Feed",
                            font=("Arial", 12, "bold"),
                            bg="#1e293b", fg="#38bdf8")
        cam_title.pack(pady=8)

        self.camera_label = tk.Label(left_frame, bg="#0f172a",
                                    text="Camera feed will appear here\n(Press Start Stream)",
                                    fg="#64748b", font=("Arial", 11))
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ── Right — stats + controls ──
        right_frame = tk.Frame(main_frame, bg="#0f172a", width=280)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        # Component Selection
        comp_frame = tk.Frame(right_frame, bg="#1e293b", relief=tk.RAISED, bd=1)
        comp_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(comp_frame, text="Active Component", font=("Arial", 11, "bold"),
                 bg="#1e293b", fg="#38bdf8").pack(pady=6)
        
        self.components = list(COMPONENT_THRESHOLDS.keys())
        self.comp_var = tk.StringVar(value=self.components[0])
        self.comp_dropdown = ttk.Combobox(comp_frame, textvariable=self.comp_var, values=self.components, state="readonly")
        self.comp_dropdown.pack(pady=(5, 10), padx=10, fill=tk.X)

        tk.Label(comp_frame, text="Thermal Range", font=("Arial", 11, "bold"),
                 bg="#1e293b", fg="#38bdf8").pack(pady=(5, 6))
        
        self.ranges = ["Cold", "Normal", "Hot"]
        self.range_var = tk.StringVar(value=self.ranges[1])
        self.range_dropdown = ttk.Combobox(comp_frame, textvariable=self.range_var, values=self.ranges, state="readonly")
        self.range_dropdown.pack(pady=(0, 10), padx=10, fill=tk.X)

        # Stats
        stats_frame = tk.Frame(right_frame, bg="#1e293b", relief=tk.RAISED, bd=1)
        stats_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(stats_frame, text="MongoDB Cloud Stats", font=("Arial", 11, "bold"),
                bg="#1e293b", fg="#38bdf8").pack(pady=6)
        self.total_var   = tk.StringVar(value="Total: --")
        self.ok_var      = tk.StringVar(value="OK: --")
        self.warning_var = tk.StringVar(value="Warning: --")
        self.nok_var     = tk.StringVar(value="NOK: --")
        stat_colors = ["#cbd5e1", "#22c55e", "#f59e0b", "#ef4444"]
        for var, color in zip([self.total_var, self.ok_var,
                               self.warning_var, self.nok_var], stat_colors):
            tk.Label(stats_frame, textvariable=var, font=("Arial", 10, "bold"),
                    bg="#1e293b", fg=color).pack(pady=3)

        # Latest inspection
        latest_frame = tk.Frame(right_frame, bg="#1e293b", relief=tk.RAISED, bd=1)
        latest_frame.pack(fill=tk.X, pady=(0,10))
        tk.Label(latest_frame, text="Latest Inspection", font=("Arial", 11, "bold"),
                bg="#1e293b", fg="#38bdf8").pack(pady=6)
        self.latest_part_var  = tk.StringVar(value="Part: --")
        self.latest_temp_var  = tk.StringVar(value="Object Temp: --")
        self.latest_ambient_var = tk.StringVar(value="Ambient Temp: --")
        self.latest_var_var = tk.StringVar(value="Variance: --")
        self.latest_status_var = tk.StringVar(value="Status: --")
        tk.Label(latest_frame, textvariable=self.latest_part_var,
                font=("Arial", 9), bg="#1e293b", fg="#cbd5e1").pack(pady=2)
        tk.Label(latest_frame, textvariable=self.latest_temp_var,
                font=("Arial", 9), bg="#1e293b", fg="#cbd5e1").pack(pady=2)
        tk.Label(latest_frame, textvariable=self.latest_ambient_var,
                font=("Arial", 9), bg="#1e293b", fg="#cbd5e1").pack(pady=2)
        tk.Label(latest_frame, textvariable=self.latest_var_var,
                font=("Arial", 9), bg="#1e293b", fg="#cbd5e1").pack(pady=2)
        self.latest_status_label = tk.Label(latest_frame,
                textvariable=self.latest_status_var,
                font=("Arial", 12, "bold"), bg="#1e293b", fg="#22c55e")
        self.latest_status_label.pack(pady=4)

        # Snapshot button
        snap_btn = tk.Button(right_frame, text="Take Snapshot (S)",
                            font=("Arial", 10, "bold"),
                            bg="#0ea5e9", fg="white",
                            relief=tk.FLAT, padx=10, pady=6,
                            command=self.take_snapshot)
        snap_btn.pack(fill=tk.X, pady=(0,5))

        # Start/Stop button
        self.stream_btn = tk.Button(right_frame, text="Start Stream",
                                   font=("Arial", 10, "bold"),
                                   bg="#22c55e", fg="white",
                                   relief=tk.FLAT, padx=10, pady=6,
                                   command=self.toggle_stream)
        self.stream_btn.pack(fill=tk.X)

    def toggle_stream(self):
        if self.running:
            self.running = False
            self.stream_btn.config(text="Start Stream", bg="#22c55e")
            self.status_var.set("Stream stopped")
        else:
            self.running = True
            self.stream_btn.config(text="Stop Stream", bg="#ef4444")
            self.status_var.set(f"Connecting to {STREAM_URL}...")
            self.stream_thread = threading.Thread(
                target=self.stream_camera, daemon=True)
            self.stream_thread.start()

    def draw_overlay(self, frame):
        h, w = frame.shape[:2]
        
        # --- OpenCV Hotspot Tracking ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(blurred)

        # Draw glowing hotspot target
        cv2.circle(frame, maxLoc, 30, (0, 0, 255), 2)
        cv2.putText(frame, "HOTSPOT", (maxLoc[0] - 35, maxLoc[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2, cv2.LINE_AA)

        status = str(self.overlay_data.get("status", "UNKNOWN")).strip().upper()
        
        # --- Draw Overlays ---
        color = (180, 180, 180) # Gray
        if status == "OK": color = (50, 200, 80) # Green
        elif status == "WARNING": color = (0, 200, 255) # Yellow format BGR
        elif status == "NOK": color = (40, 40, 220) # Red
        
        # Draw translucent background bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 70), (w, h), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Text
        uid_text = f"UID: {self.overlay_data['part_uid']}"
        temp_text = f"Obj: {self.overlay_data['temperature']}C  Amb: {self.overlay_data['ambient_temp']}C"
        var_text = f"Variance: {self.overlay_data['variance']}"
        
        # Scale text down slightly and position dynamically
        cv2.putText(frame, uid_text, (10, h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, temp_text, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, var_text, (int(w / 2) + 20, h - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"STATUS: {status}", (int(w / 2) + 20, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA)

        return frame

    def stream_camera(self):
        import requests
        import numpy as np
        try:
            url = STREAM_URL
            r = requests.get(url, stream=True, timeout=5)
            if r.status_code != 200:
                raise Exception(f"HTTP {r.status_code}")
                
            self.status_var.set(f"Streaming live from {ESP32_IP}...")
            
            bytes_data = b''
            for chunk in r.iter_content(chunk_size=4096):
                if not self.running:
                    break
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8')
                b = bytes_data.find(b'\xff\xd9')
                
                # Extract ESP32 Header Telemetry (Temporarily Disabled for Dummy Simulation Override)
                if a != -1:
                    header_block = bytes_data[:a].decode('utf-8', errors='ignore')
                    for line in header_block.split('\r\n'):
                        if line.startswith('X-Ambient-Temp:'):
                            self.overlay_data['ambient_temp'] = line.split(':')[1].strip()

                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        self.current_frame = frame.copy()
                        frame = self.draw_overlay(frame)
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(rgb)
                        img = img.resize((640, 480), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(image=img)

                        self.camera_label.config(image=photo, text="")
                        self.camera_label.image = photo

        except Exception as e:
            self.status_var.set(f"Stream error: {str(e)}")
            self.running = False
            self.stream_btn.config(text="Start Stream", bg="#22c55e")

    def take_snapshot(self):
        if self.current_frame is None:
            self.status_var.set("Snapshot failed: No live frame available. Start stream first.")
            return

        # Prepare new UUID
        ts = datetime.now()
        ts_fn = ts.strftime("%Y%m%d_%H%M%S")
        ts_iso = ts.isoformat()
        uid = f"ESP32-{ts_fn}-{uuid.uuid4().hex[:6].upper()}"
        
        filename = f"{uid}.jpg"
        filepath = os.path.join(SNAPSHOT_DIR, filename)

        try:
            resp = urllib.request.urlopen(SNAPSHOT_URL, timeout=3)
            img_arr = np.array(bytearray(resp.read()), dtype=np.uint8)
            img = cv2.imdecode(img_arr, -1)
            cv2.imwrite(filepath, img)
        except Exception as e:
            print(f"Warning: /snapshot failed, using stream frame. Error: {e}")
            cv2.imwrite(filepath, self.current_frame)

        # Post to MongoDB using the exact calculated values and current component
        status = self.overlay_data.get("status", "UNKNOWN")
        comp = self.comp_var.get()
        
        try: temp_val = float(self.overlay_data.get("temperature", 0))
        except (ValueError, TypeError): temp_val = 0.0
        
        try: amb_val = float(self.overlay_data.get("ambient_temp", 0))
        except (ValueError, TypeError): amb_val = 0.0
        
        try: var_val = float(self.overlay_data.get("variance", 0))
        except (ValueError, TypeError): var_val = 0.0

        payload = {
            "part_uid": uid,
            "component_name": comp,
            "temperature": temp_val,
            "ambient_temp": amb_val,
            "variance": var_val,
            "status": status,
            "device_id": "ESP32S3-CAM-01",
            "timestamp": ts_iso,
            "verified_status": "Pending",
            "image_path": f"snapshots/{filename}"
        }

        self.status_var.set("Uploading snapshot...")
        try:
            r = requests.post(f"{API_URL}/inspection", json=payload, timeout=3)
            if r.status_code in (200, 201):
                self.status_var.set(f"✅ Snapshot synced directly to MongoDB! UID: {uid}")
            else:
                self.status_var.set(f"❌ Snapshot saved but Mongo upload failed: HTTP {r.status_code}")
        except Exception as e:
            self.status_var.set(f"❌ Snapshot saved locally. MongoDB unreachabe: {e}")

    def update_stats(self):
        threading.Thread(target=self._fetch_stats, daemon=True).start()
        self.root.after(500, self.update_stats)  # Poll every 500ms for real-time temp

    def _fetch_stats(self):
        import random
        import time
        # --- FAST DUMMY DATA GENERATOR ---
        range_mode = self.range_var.get()
        if range_mode == "Cold":
            dummy_t = round(random.uniform(6.0, 11.0), 1)
            dummy_status = "OK"
        elif range_mode == "Hot":
            dummy_t = round(random.uniform(150.0, 300.0), 1)
            dummy_status = "NOK"
        else: # Normal
            dummy_t = round(random.uniform(20.0, 40.0), 1)
            dummy_status = "OK"

        self.overlay_data["temperature"] = dummy_t
        self.overlay_data["status"] = dummy_status

        # Save a continuous live dummy frame to prevent hitting the ESP32 single-thread limit
        dummy_img_path = "snapshots/live_simulator_feed.jpg"
        try:
            if self.current_frame is not None:
                save_path = os.path.join(SNAPSHOT_DIR, "live_simulator_feed.jpg")
                cv2.imwrite(save_path, self.current_frame)
        except:
            pass

        # FORCE THIS DUMMY DATA INTO MONGODB CONSTANTLY TO OVERRIDE ESP32!
        try:
            payload = {
                "part_uid": self.overlay_data.get("part_uid", f"SIM-{int(time.time())}"),
                "component_name": self.comp_var.get(),
                "temperature": dummy_t,
                "ambient_temp": self.overlay_data.get("ambient_temp", 26.5),
                "variance": self.overlay_data.get("variance", 0.0),
                "status": dummy_status,
                "device_id": "PYTHON-SIMULATOR",
                "image_path": dummy_img_path
            }
            requests.post(f"{API_URL}/inspection", json=payload, timeout=1)
        except:
            pass

        # MongoDB stats (total, OK, warning, NOK counts)
        try:
            r = requests.get(f"{API_URL}/stats", timeout=3)
            if r.status_code == 200:
                data = r.json()
                self.total_var.set(f"Total: {data.get('total_inspections', 0)}")
                self.ok_var.set(f"OK: {data.get('ok_count', 0)}")
                self.warning_var.set(f"Warning: {data.get('warning_count', 0)}")
                self.nok_var.set(f"NOK: {data.get('nok_count', 0)}")
        except:
            pass

        # ── LIVE Telemetry: Polling the ESP32 /status endpoint has been completely 
        # disabled here to prevent crashing the physical microcontroller's networking 
        # stack while the video feed socket is aggressively streaming.

        # Part UID from MongoDB (last inspected part)
        try:
            r = requests.get(f"{API_URL}/results", timeout=3)
            if r.status_code == 200:
                results = r.json()
                if results and len(results) > 0:
                    self.overlay_data["part_uid"] = results[0].get("part_uid", "--")
        except:
            pass

        # Latest inspection updates (local updates from OpenCV & Header Stream)
        try:
            self.latest_part_var.set(f"Part: {self.overlay_data.get('part_uid', '--')}")
            self.latest_temp_var.set(f"Object Temp: {self.overlay_data.get('temperature', '--')}C")
            self.latest_ambient_var.set(f"Ambient Temp: {self.overlay_data.get('ambient_temp', '--')}C")
            self.latest_var_var.set(f"Variance: {self.overlay_data.get('variance', '--')}")
            
            status = self.overlay_data.get('status', 'UNKNOWN')
            self.latest_status_var.set(f"Status: {status}")
            color = {"OK": "#22c55e", "WARNING": "#f59e0b", "NOK": "#ef4444"}.get(status, "#cbd5e1")
            self.latest_status_label.config(fg=color)
        except Exception as e:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DreamVisionApp(root)
    root.mainloop()
