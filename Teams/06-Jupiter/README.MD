# 🏭 DreamVision: Smart Factory Thermal Inspection Platform

**DreamVision** is an end-to-end, real-time thermal monitoring and AI-powered visual inspection system designed for automotive manufacturing and industrial quality control. 

By seamlessly bridging physical embedded hardware (ESP32-S3) with an intelligent Local Edge Processor (Python/FastAPI) and a Cloud-Ready web dashboard (Node.js/Express), DreamVision automatically tracks, analyzes, and categorizes component thermal defects with mathematical precision.

---

## 🏗️ 1. High-Level Architecture & Microservices

The DreamVision ecosystem is strictly decoupled into four intelligent tiers:

1. **Hardware Layer (ESP32-S3 Firmware):** A C++ RTOS environment running an MLX90614 non-contact infrared temperature sensor and an OV3660 camera module.
2. **Edge Vision Layer (Python Tkinter/OpenCV App):** An aggressive local software gateway (`live_feed_app.py`). It captures MJPEG video streams, dynamicly parses thermal telemetry, paints bounding boxes around active hotspots, and possesses a **Simulation Override Sandbox** to seamlessly test maximum telemetry load capacities.
3. **Database Routing Layer (Express.js):** A lightweight, lightning-fast Node.js API serving local Web assets, routing telemetry securely into MongoDB Atlas, and broadcasting Server-Sent Events (SSE).
4. **Supervisor Dashboard Layer (HTML/Vanilla JS):** A highly-responsive, real-time web dashboard plotting component health with a native 2000ms DOM-throttle for buttery-smooth visual monitoring.

---

## 🌊 2. System Data Flow Pipeline

```mermaid
graph TD
    A[ESP32-S3 Camera + MLX90614] -->|Port 80: /stream| B(Edge: Python Tkinter App)
    B -->|OpenCV: Real-Time Bounding Box| C[Hotspot Extractor & Simulator]
    C -->|POST /api/inspection| D((Express.js Node API))
    D -->|Upsert Document| E[(MongoDB Atlas)]
    C -->|Writes cv2.imwrite()| F[Local Disk: /public/snapshots]
    D -->|Broadcasts SSE| G[Supervisor Web Dashboard]
    F -->|Serves static Image| G
```

### The Hotspot Simulation Override Loop
To physically protect the single-threaded physical ESP32 from network denial-of-service, the Python Edge App physically captures `self.current_frame` via OpenCV and silently drops it onto the Express server's local storage (`/public/snapshots/live_simulator_feed.jpg`). The Dashboard fetches the latest physical image directly from Node.js, allowing massive scale across multiple viewing browsers without ever touching or disturbing the ESP32's native Wi-Fi connection.

---

## 🧠 3. Control Logic & Defect Engine

DreamVision categorizes component safety into three absolute strict states based on localized mapping thresholds:

*   **OK (Green):** Operating effectively within designated thermal specs.
*   **WARNING (Yellow):** Exceeds maximum standard threshold, approaching critical boundary.
*   **NOK (Red - Not OK):** Catastrophic failure boundary breached. Part is rejected.

### Component Threshold Matrix
The Node.js Express server calculates these dynamically globally via the following pre-compiled dictionary:
```json
{
  "crankcase": { "max": 80, "critical": 140, "failure": 180 },
  "cylinder_head": { "max": 150, "critical": 250, "failure": 300 },
  "engine_cover": { "max": 70, "critical": 120, "failure": 150 },
  "clutch_housing": { "max": 90, "critical": 160, "failure": 200 }
}
```
*If a component's temperature natively eclipses the `critical` numeric range, it is brutally forcefully flagged as `NOK` and uploaded.*

---

## 📂 4. Detailed Codebase Breakdown

### A. The Master Launcher (`run_dreamvision.py`)
A single-click orchestration Python script. It utilizes pure `subprocess` threading and `Get-WmiObject` (on Windows systems) to aggressively kill orphaned ports (3000, 8002), synchronously spin up the **Express Node API**, wait until an HTTP `200 OK` health check is detected, boot up the **FastAPI uvicorn server**, and finally launch the **Tkinter Live Feed UI** and automatically open the supervisor dashboard.

### B. Python Edge Vision App (`live_feed_app.py`)
- Built using native **Tkinter** and **OpenCV** (`cv2`). 
- Establishes a raw HTTP stream (`urllib.request.urlopen`) to the ESP32's `/stream` MJPEG boundary.
- Generates dynamic synthetic telemetry via `_fetch_stats` for frontend sandbox load-testing ("Cold", "Normal", "Hot" dropdown temperature toggles).
- Posts completely synchronized payloads directly to `/inspection`.
- Listens to the 'S' keybinding to execute formal system audits.

### C. Node.js Express Backend (`express_backend/index.js`)
- Protects the MongoDB Database URI via `MongoClient` pooling.
- **SSE Logic (`GET /stream`)**: Maintains unclosing HTTP connections utilizing `text/event-stream` headers, pushing instantaneous event frames to vanilla Javascript hooks.
- **CSV Data Export (`GET /dashboard/report/csv`)**: Features a programmatic mapping loop natively formatting millions of possible MongoDB NoSQL document nodes into a downloadable, UTF-8 encoded comma-separated `.csv` payload for Supervisor auditing.

### D. Supervisor Web Dashboard (`frontend/public/` directory)
- Connected securely to the Express backend routing layer.
- **Anti-Thrashing System**: Implements a precise mathematical `2000ms` timestamp throttle `if (now - lastSseTime > 2000)` surrounding the Server-Sent Event `onmessage` socket. This inherently guarantees the HTML `table` DOM rendering doesn't flicker maliciously under heavy Python telemetry data loads.
- Modal interface popups seamlessly load HTML `img` `src` addresses resolving to the local pipeline.

---

## 🚀 5. Getting Started & Installation

### Requirements
- Python 3.9+
- Node.js v16+
- ESP32-S3 Hardware Board + OV3660 + Local 2.4Ghz Wi-Fi Connection
- An active Internet connection to successfully hit MongoDB Atlas.

### Boot Sequence
1. Clone the repository natively.
2. Install Python dependency wheels:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the specific frontend Node modules inside the backend folder:
   ```bash
   cd express_backend
   npm install cors express mongodb dotenv
   ```
4. Return to the root directory and explicitly run the master unified start script:
   ```bash
   python run_dreamvision.py
   ```

*(The script will elegantly launch all microservices in the absolutely correct chronological sequence, and automatically deploy the Dashboard to your default Chrome/Edge browser!)*

---

### 🛡️ License & Maintenance
DreamVision Core Architecture is finalized for production Edge-AI demonstrations. 
**Push thoroughly validated feature branches only.**