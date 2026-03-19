"""

Controls:
    +  / =   →  raise min pore size  (less noise)
    -        →  lower min pore size  (more detections)
    E        →  toggle edge map overlay
    B        →  toggle binary mask panel
    I        →  toggle defect ID labels
    S        →  save frame
    Q / ESC  →  quit
"""
import cv2
import numpy as np
import time
import os
import platform
from datetime import datetime


P = {
    "blur_kernel":     7,
    "clahe_clip":      2.0,
    "clahe_tile":      8,
    "bottomhat_ksize": 21,
    "canny_low":       30,
    "canny_high":      90,
    "close_ksize":     9,
    "min_area":        500,
    "max_area":        120_000,
    "min_circularity": 0.30,
    "min_solidity":    0.55,
    "level_low":       0.3,
    "level_medium":    1.5,
    "level_high":      4.0,
}

SENS_STEPS = [200, 350, 500, 750, 1000, 1500, 2500, 4000]

SEVERITY_COLORS = {
    "OK":       (50,  210,  50),
    "LOW":      (0,   200, 200),
    "MEDIUM":   (0,   150, 255),
    "HIGH":     (0,    40, 255),
    "CRITICAL": (0,     0, 210),
}


def open_camera():
    OS = platform.system()

    # Pick backends in order of reliability per OS
    order = (
        [(cv2.CAP_DSHOW, "DirectShow"), (cv2.CAP_MSMF, "MSMF"), (cv2.CAP_ANY, "Auto")]
        if OS == "Windows" else
        [(cv2.CAP_ANY, "AVFoundation")]
        if OS == "Darwin" else
        [(cv2.CAP_V4L2, "V4L2"), (cv2.CAP_ANY, "Auto")]
    )

    for backend, name in order:
        for idx in range(4):
            try:
                cap = cv2.VideoCapture(idx, backend)
                if not cap.isOpened():
                    cap.release()
                    continue
                ok, f = cap.read()
                if ok and f is not None and f.size > 0:   # validate with actual frame
                    print(f"[Camera] Device {idx} via {name}")
                    return cap
                cap.release()
            except Exception:
                pass
    return None


def detect(frame, p):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # Boost local contrast to make pores stand out
    clahe    = cv2.createCLAHE(clipLimit=p["clahe_clip"],
                                tileGridSize=(p["clahe_tile"], p["clahe_tile"]))
    enhanced = clahe.apply(gray)

    # Smooth out surface grain/texture before thresholding
    k       = p["blur_kernel"] | 1          # force odd kernel size
    blurred = cv2.GaussianBlur(enhanced, (k, k), 0)

    # --- Channel A: Bottom-Hat (morphological dark-blob extractor) ---
    bh_k      = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                    (p["bottomhat_ksize"], p["bottomhat_ksize"]))
    bottomhat = cv2.morphologyEx(blurred, cv2.MORPH_BLACKHAT, bh_k)  # close(img) - img = dark spots

    # Adaptive threshold: keep only regions significantly darker than surroundings
    bh_mean, bh_std = cv2.meanStdDev(bottomhat)
    bh_thresh       = max(float(bh_mean[0][0]) + 1.5 * float(bh_std[0][0]), 12)
    _, mask_bh      = cv2.threshold(bottomhat, bh_thresh, 255, cv2.THRESH_BINARY)

    # --- Channel B: Canny edges → close loops → flood-fill interiors ---
    edges  = cv2.Canny(blurred, p["canny_low"], p["canny_high"])
    ck     = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (p["close_ksize"], p["close_ksize"]))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, ck)   # seal broken edge boundaries

    # Flood-fill from image border; invert → only enclosed interior regions remain
    flood = closed.copy()
    cv2.floodFill(flood, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    mask_edge = cv2.bitwise_not(flood)

    # Merge both detection channels
    combined = cv2.bitwise_or(mask_bh, mask_edge)

    # Open removes isolated noise pixels; Close fills micro-gaps inside pores
    open_k  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    close_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    cleaned = cv2.morphologyEx(combined, cv2.MORPH_OPEN,  open_k)
    cleaned = cv2.morphologyEx(cleaned,  cv2.MORPH_CLOSE, close_k)

    cnts, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pores = []
    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if not (p["min_area"] <= area <= p["max_area"]):
            continue

        # Circularity = 1 for perfect circle; filters scratches and lines
        peri = cv2.arcLength(cnt, True)
        circ = (4 * np.pi * area / peri ** 2) if peri > 0 else 0
        if circ < p["min_circularity"]:
            continue

        # Solidity = area / convex-hull area; rejects jagged/fragmented shapes
        hull     = cv2.convexHull(cnt)
        h_area   = cv2.contourArea(hull)
        solidity = (area / h_area) if h_area > 0 else 0
        if solidity < p["min_solidity"]:
            continue

        x, y, bw, bh2 = cv2.boundingRect(cnt)
        M  = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"]) if M["m00"] else x + bw // 2
        cy = int(M["m01"] / M["m00"]) if M["m00"] else y + bh2 // 2

        pores.append({
            "cnt": cnt, "area": area,
            "cx": cx,   "cy": cy,
            "bbox": (x, y, bw, bh2),
            "circ": round(circ, 3),
            "solidity": round(solidity, 3),
        })

    total_area = sum(pp["area"] for pp in pores)
    por_pct    = total_area / (h * w) * 100   # porosity as % of frame area

    lo, med, hi = p["level_low"], p["level_medium"], p["level_high"]
    if   por_pct < lo:      sev = "OK"
    elif por_pct < med:     sev = "LOW"
    elif por_pct < hi:      sev = "MEDIUM"
    elif por_pct < hi * 2:  sev = "HIGH"
    else:                   sev = "CRITICAL"

    return pores, round(por_pct, 3), sev, cleaned, edges


def draw_overlay(frame, pores, por_pct, sev, p, fps, show_ids):
    out   = frame.copy()
    color = SEVERITY_COLORS[sev]

    for i, pp in enumerate(pores):
        x, y, bw, bh = pp["bbox"]

        overlay = out.copy()
        cv2.drawContours(overlay, [pp["cnt"]], -1, color, -1)
        cv2.addWeighted(overlay, 0.30, out, 0.70, 0, out)   # semi-transparent fill
        cv2.drawContours(out, [pp["cnt"]], -1, color, 2)
        cv2.rectangle(out, (x, y), (x + bw, y + bh), color, 1)

        if show_ids:
            cv2.putText(out, f"#{i+1}  {pp['area']:.0f}px",
                        (x, max(y - 5, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1, cv2.LINE_AA)

    # Semi-transparent HUD background
    ov = out.copy()
    cv2.rectangle(ov, (0, 0), (300, 155), (10, 10, 10), -1)
    cv2.addWeighted(ov, 0.65, out, 0.35, 0, out)

    rows = [
        (f"Porosity : {por_pct:.3f} %",           color,         0.56),
        (f"Pores    : {len(pores)}",               (220,220,220), 0.52),
        (f"Severity : {sev}",                      color,         0.56),
        (f"Min area : {p['min_area']} px",         (150,150,150), 0.44),
        (f"Min circ : {p['min_circularity']:.2f}", (140,140,140), 0.44),
        (f"FPS      : {fps:.1f}",                  (120,120,120), 0.42),
    ]
    for i, (txt, col, sc) in enumerate(rows):
        cv2.putText(out, txt, (8, 22 + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, sc, col, 1, cv2.LINE_AA)

    # Severity badge top-right
    (tw, th), _ = cv2.getTextSize(sev, cv2.FONT_HERSHEY_SIMPLEX, 0.72, 2)
    bx = out.shape[1] - tw - 24
    ov2 = out.copy()
    cv2.rectangle(ov2, (bx-10, 6), (bx+tw+10, 6+th+14), (10,10,10), -1)
    cv2.addWeighted(ov2, 0.70, out, 0.30, 0, out)
    cv2.putText(out, sev, (bx, 6+th+8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.72, color, 2, cv2.LINE_AA)

    cv2.putText(out, "+/-=size  E=edges  B=mask  I=labels  S=save  Q=quit",
                (8, out.shape[0]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (130,130,130), 1, cv2.LINE_AA)

    return out


def make_binary_panel(binary, h, w):
    small = cv2.resize(binary, (w//2, h))
    b3    = cv2.cvtColor(small, cv2.COLOR_GRAY2BGR)
    b3[small > 0] = (0, 80, 255)
    cv2.putText(b3, "Cleaned mask", (6, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,200), 1)
    return b3


def make_edge_panel(edges, h, w):
    small = cv2.resize(edges, (w//2, h))
    e3    = cv2.cvtColor(small, cv2.COLOR_GRAY2BGR)
    e3[small > 0] = (80, 220, 80)
    cv2.putText(e3, "Canny edges", (6, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,200), 1)
    return e3


def main():
    print("\n╔═══════════════════════════════════════════════════╗")
    print("║  Metal Pore Detector  —  LIVE                     ║")
    print("║  Bottom-Hat + Canny Edge Segmentation             ║")
    print("╚═══════════════════════════════════════════════════╝\n")

    cap = open_camera()
    if cap is None:
        print("[Error] No webcam found. Close other apps using camera.")
        input("Press Enter to exit...")
        return

    # Try HD first, fall back to VGA
    for rw, rh in [(1280, 720), (640, 480)]:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  rw)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, rh)
        ok, f = cap.read()
        if ok and f is not None and f.size > 0:
            break

    for _ in range(8):                          # flush stale buffer frames
        cap.read(); time.sleep(0.03)

    cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[Camera] {cam_w}x{cam_h}")

    if platform.system() == "Linux":
        cv2.startWindowThread()                 # prevents frozen windows on Linux

    WIN = "Metal Pore Detector — LIVE  [click here first]"
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN, min(cam_w, 1280), min(cam_h, 720))

    os.makedirs("pore_captures", exist_ok=True)

    p          = P.copy()
    show_bin   = False
    show_edges = False
    show_ids   = True
    fail_count = 0
    fps        = 0.0
    fps_t      = time.perf_counter()
    frame_cnt  = 0
    last_disp  = None

    sens_idx = SENS_STEPS.index(min(SENS_STEPS, key=lambda v: abs(v - p["min_area"])))

    print("[App] CLICK the window, then use +/- to tune sensitivity.\n")

    while True:
        ret, frame = cap.read()

        if not ret or frame is None or frame.size == 0:
            fail_count += 1
            if fail_count > 50:                 # try to reconnect after sustained failure
                cap.release(); time.sleep(0.8)
                cap = open_camera()
                if cap is None: break
                fail_count = 0
            time.sleep(0.03)
            continue
        fail_count = 0

        pores, por_pct, sev, binary, edges = detect(frame, p)

        # Rolling FPS over 0.5-second window
        frame_cnt += 1
        now = time.perf_counter()
        if now - fps_t >= 0.5:
            fps = frame_cnt / (now - fps_t)
            frame_cnt = 0; fps_t = now

        annotated = draw_overlay(frame, pores, por_pct, sev, p, fps, show_ids)

        # Build side panel based on toggle state
        if show_edges and show_bin:
            side    = cv2.resize(np.vstack([make_edge_panel(edges, cam_h, cam_w),
                                            make_binary_panel(binary, cam_h, cam_w)]),
                                 (cam_w//2, cam_h))
            display = np.hstack([annotated, side])
        elif show_edges:
            display = np.hstack([annotated, make_edge_panel(edges, cam_h, cam_w)])
        elif show_bin:
            display = np.hstack([annotated, make_binary_panel(binary, cam_h, cam_w)])
        else:
            display = annotated

        last_disp = display.copy()
        cv2.imshow(WIN, display)

        key = cv2.waitKey(1) & 0xFF             # waitKey(1) keeps window responsive

        if key in (ord('q'), 27):
            break
        elif key in (ord('+'), ord('=')):
            sens_idx = min(sens_idx + 1, len(SENS_STEPS) - 1)
            p["min_area"] = SENS_STEPS[sens_idx]
            print(f"[App] Min area → {p['min_area']} px²  (stricter)")
        elif key == ord('-'):
            sens_idx = max(sens_idx - 1, 0)
            p["min_area"] = SENS_STEPS[sens_idx]
            print(f"[App] Min area → {p['min_area']} px²  (looser)")
        elif key == ord('e'):
            show_edges = not show_edges
            cv2.resizeWindow(WIN, min(cam_w * (1 + int(show_edges) + int(show_bin)), 1800), min(cam_h, 720))
            print(f"[App] Edge view {'ON' if show_edges else 'OFF'}")
        elif key == ord('b'):
            show_bin = not show_bin
            cv2.resizeWindow(WIN, min(cam_w * (1 + int(show_edges) + int(show_bin)), 1800), min(cam_h, 720))
            print(f"[App] Binary mask {'ON' if show_bin else 'OFF'}")
        elif key == ord('i'):
            show_ids = not show_ids
        elif key == ord('s'):
            fname = f"pore_captures/pore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(fname, last_disp)
            print(f"[App] Saved → {fname}")

    cap.release()
    cv2.destroyAllWindows()
    print("[App] Done.")


if __name__ == "__main__":
    main()
