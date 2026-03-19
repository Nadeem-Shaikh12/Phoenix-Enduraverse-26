/* ================================================================
   DreamVision Supervisor Dashboard — script.js  (v3 - fully fixed)
   All data → Express API (localhost:3000 / MongoDB)
   Assessments → FastAPI Edge (localhost:8002)
   ================================================================ */

// ── API Endpoints ───────────────────────────────────────────────
const API_BASE      = "http://localhost:3000";   // Express (MongoDB) — ALL dashboard data
const EDGE_API_BASE = "http://localhost:8002";   // FastAPI (SQLite edge) — only /inspect POST

// ── Component Thresholds ────────────────────────────────────────
const COMPONENT_THRESHOLDS = {
    crankcase:        { label: "Crankcase",        normal_min:  60, normal_max: 120, critical: 140 },
    exhaust_manifold: { label: "Exhaust Manifold", normal_min: 200, normal_max: 400, critical: 450 },
    brake_rotor:      { label: "Brake Rotor",      normal_min:  50, normal_max: 250, critical: 300 },
    cylinder_head:    { label: "Cylinder Head",    normal_min:  80, normal_max: 130, critical: 150 },
    battery_pack:     { label: "Battery Pack",     normal_min:  20, normal_max:  45, critical:  55 }
};

// ── State ───────────────────────────────────────────────────────
let currentModalUid = null;
let chartInstance   = null;
let toastTimer      = null;

// ── Toast Notification ──────────────────────────────────────────
function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.className   = `toast ${type}`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toast.className = "toast hidden"; }, 3500);
}

// ── Animated stat value ─────────────────────────────────────────
function animateValue(el, newVal) {
    if (!el) return;
    el.style.transform  = "scale(1.12)";
    el.style.transition = "transform 0.2s";
    el.textContent = newVal;
    setTimeout(() => { el.style.transform = ""; }, 200);
}

// ── Fetch Stats (MongoDB via Express) ───────────────────────────
async function fetchStats() {
    try {
        const res  = await fetch(`${API_BASE}/stats`);
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();

        animateValue(document.getElementById("stat-total"),       data.total_inspections  ?? 0);
        animateValue(document.getElementById("stat-ok-rate"),     `${data.yield_percent   ?? 0}%`);
        animateValue(document.getElementById("stat-defect-rate"), `${data.defect_percent  ?? 0}%`);
        animateValue(document.getElementById("stat-warning"),     data.warning_count      ?? 0);

        updateChart(data);
    } catch (e) {
        console.warn("Stats offline:", e);
    }
}

// ── Status Pill ─────────────────────────────────────────────────
function statusPill(status) {
    const map = {
        OK:      { cls: "ok",     icon: "✅" },
        WARNING: { cls: "warn",   icon: "⚠️" },
        NOK:     { cls: "danger", icon: "❌" },
    };
    const s = map[status] ?? { cls: "", icon: "❓" };
    return `<span class="status-pill ${s.cls}">${s.icon} ${status}</span>`;
}

// ── Fetch & Render Feed (MongoDB via Express) ───────────────────
async function fetchFeed(query = "") {
    try {
        const url  = query
            ? `${API_BASE}/results?search=${encodeURIComponent(query)}`
            : `${API_BASE}/results`;
        const res  = await fetch(url);
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();
        renderTable(data);
    } catch (e) {
        console.warn("Feed offline:", e);
        renderTable([]);
    }
}

function renderTable(data) {
    const tbody = document.getElementById("tableBody");
    if (!tbody) return;

    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="7">
                    <div class="empty-state">
                        <span>🌡️</span>
                        <p>No inspections yet. Run an assessment to populate data.</p>
                    </div>
                </td>
            </tr>`;
        return;
    }

    tbody.innerHTML = "";
    data.forEach(row => {
        if (typeof updateDigitalTwin === "function") updateDigitalTwin(row.status);

        const tr = document.createElement("tr");
        
        let rowColor = "";
        if (row.status === "OK") rowColor = "background-color: rgba(34, 197, 94, 0.1);";
        else if (row.status === "WARNING") rowColor = "background-color: rgba(245, 158, 11, 0.1);";
        else if (row.status === "NOK") rowColor = "background-color: rgba(239, 68, 68, 0.1);";

        tr.style = rowColor;
        
        tr.innerHTML = `
            <td style="font-family:monospace;color:#94a3b8;font-size:.78rem">${row.part_uid ?? "—"}</td>
            <td style="font-weight:600;color:#e5e7eb">${row.component_name ?? "—"}</td>
            <td style="color:#f59e0b;font-weight:700">${Number(row.temperature ?? 0).toFixed(1)}</td>
            <td style="color:#38bdf8;font-weight:600">${row.variance !== undefined ? Number(row.variance).toFixed(2) : "—"}</td>
            <td>${statusPill(row.status)}</td>
            <td><span class="verified-badge">${row.verified_status ?? "Pending"}</span></td>
            <td style="color:#64748b;font-size:.78rem">${row.timestamp ?? "—"}</td>
            <td><button id="detail-btn-${row.part_uid}" onclick="openModal('${row.part_uid}')">Details</button></td>
        `;
        tbody.appendChild(tr);
    });
}

// ── Search ──────────────────────────────────────────────────────
let searchDebounce = null;
function searchInspections() {
    clearTimeout(searchDebounce);
    const q = document.getElementById("searchInput")?.value ?? "";
    searchDebounce = setTimeout(() => fetchFeed(q), 300);
}
function resetSearch() {
    const inp = document.getElementById("searchInput");
    if (inp) inp.value = "";
    fetchFeed();
}

// ── Open Detail Modal (MongoDB via Express) ─────────────────────
async function openModal(uid) {
    try {
        // Fetch from Express → MongoDB  (NOT the edge FastAPI server)
        const res = await fetch(`${API_BASE}/dashboard/inspection/${uid}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        currentModalUid = uid;

        document.getElementById("modal-uid").textContent       = data.part_uid        ?? uid;
        document.getElementById("modal-component").textContent = data.component_name  ?? "—";
        document.getElementById("modal-temp").textContent      = Number(data.temperature ?? 0).toFixed(1);
        document.getElementById("modal-ambient").textContent   = data.ambient_temp !== undefined ? Number(data.ambient_temp).toFixed(1) : "—";
        document.getElementById("modal-var").textContent       = data.variance !== undefined ? Number(data.variance).toFixed(2) : "—";
        document.getElementById("modal-time").textContent      = data.timestamp       ?? "—";
        document.getElementById("modal-verified").textContent  = data.verified_status ?? "Pending";

        const statusEl = document.getElementById("modal-status");
        const colorMap = { OK: "#22c55e", WARNING: "#f59e0b", NOK: "#ef4444" };
        statusEl.textContent        = data.status ?? "—";
        statusEl.style.background   = colorMap[data.status] ?? "#64748b";
        statusEl.style.color        = "#fff";
        statusEl.style.padding      = "2px 10px";
        statusEl.style.borderRadius = "20px";

        const imgEl = document.getElementById("modal-img");
        if (data.image_path) {
            if (data.image_path.startsWith("http")) {
                imgEl.src = data.image_path; // Absolute URL (ESP32 natively)
            } else {
                imgEl.src = `${API_BASE}/${data.image_path}`; // Relative URL (Express uploads endpoint)
            }
            imgEl.style.display = "block";
        } else {
            imgEl.src = "";
            imgEl.style.display = "none";
        }

        document.getElementById("detailModal").style.display = "block";
    } catch (e) {
        showToast("⚠️ Could not load inspection details.", "warn");
        console.error("openModal error:", e);
    }
}

function closeModal() {
    document.getElementById("detailModal").style.display = "none";
    currentModalUid = null;
}

// Close modal on backdrop click
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("detailModal")?.addEventListener("click", (e) => {
        if (e.target === e.currentTarget) closeModal();
    });
    if (typeof buildDigitalTwin === "function") buildDigitalTwin();
});

// ── Supervisor Verification (MongoDB via Express) ───────────────
async function submitVerification() {
    if (!currentModalUid) return;
    const status = document.getElementById("verify-select")?.value;
    const user   = document.getElementById("logged-user")?.textContent ?? "Supervisor";

    try {
        const res = await fetch(`${API_BASE}/dashboard/verify/${currentModalUid}`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ verified_status: status, verified_by: user })
        });
        if (res.ok) {
            showToast(`✅ Marked as ${status} by ${user}`, "ok");
            closeModal();
            fetchFeed();
        } else {
            showToast("❌ Verification save failed.", "err");
        }
    } catch (e) {
        showToast("🌐 Network error during verification.", "err");
    }
}

// ── Chart.js Donut ──────────────────────────────────────────────
function updateChart(data) {
    const canvas = document.getElementById("defectChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["OK", "WARNING", "NOK"],
            datasets: [{
                data: [data.ok_count ?? 0, data.warning_count ?? 0, data.nok_count ?? 0],
                backgroundColor: ["#22c55e", "#f59e0b", "#ef4444"],
                borderColor:     ["#16a34a", "#d97706", "#dc2626"],
                borderWidth: 2,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            cutout:     "68%",
            animation:  { duration: 600, easing: "easeOutQuart" },
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#94a3b8", font: { size: 11, family: "Inter" }, padding: 14, usePointStyle: true }
                }
            }
        }
    });
}

// ── Trigger Assessment (FastAPI Edge → saves to SQLite + syncs to MongoDB) ──
async function triggerAssessment() {
    const comp = document.getElementById("component-select")?.value;
    const rule = COMPONENT_THRESHOLDS[comp];
    const btn  = document.getElementById("assess-btn");

    // Simulate realistic temperature
    let temp;
    if (rule) {
        const rand = Math.random();
        if (rand < 0.70)      temp = rule.normal_min + Math.random() * (rule.normal_max - rule.normal_min);
        else if (rand < 0.90) temp = rule.normal_max + Math.random() * (rule.critical - rule.normal_max);
        else                  temp = rule.critical   + Math.random() * 20;
    } else {
        temp = 50 + Math.random() * 100;
    }

    if (btn) {
        btn.classList.add("loading");
        btn.innerHTML = `<span class="btn-icon">⏳</span> Assessing...`;
    }

    try {
        // Step 1: Send to FastAPI edge (processes + saves to SQLite)
        const edgeRes = await fetch(`${EDGE_API_BASE}/inspect`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({
                device_id:             "Supervisor-Dashboard",
                timestamp:             new Date().toISOString(),
                component_name:        comp,
                simulated_temperature: temp
            })
        });

        if (edgeRes.ok) {
            const edgeData = await edgeRes.json();

            // Step 2: Also push to MongoDB via Express so dashboard sees it immediately
            await fetch(`${API_BASE}/inspection`, {
                method:  "POST",
                headers: { "Content-Type": "application/json" },
                body:    JSON.stringify({
                    part_uid:       edgeData.part_uid       ?? `SIM-${Date.now()}`,
                    component_name: edgeData.component_name ?? comp,
                    temperature:    edgeData.temperature    ?? temp,
                    status:         edgeData.status         ?? "OK",
                    device_id:      "Supervisor-Dashboard",
                    timestamp:      edgeData.timestamp      ?? new Date().toISOString(),
                    verified_status: "Pending"
                })
            });

            showToast(`⚡ ${rule?.label ?? comp} @ ${temp.toFixed(1)}°C → ${edgeData.status ?? "OK"}`, "ok");
            fetchFeed();
            fetchStats();
        } else {
            showToast("❌ Assessment failed. Check edge server.", "err");
        }
    } catch (e) {
        showToast("🌐 Edge server offline — check that uvicorn is running.", "err");
        console.error("Assessment error:", e);
    } finally {
        if (btn) {
            btn.classList.remove("loading");
            btn.innerHTML = `<span class="btn-icon">⚡</span> Assess Component`;
        }
    }
}

// ── SSE (Real-time from Express) ────────────────────────────────
let lastSseTime = 0;
try {
    const evtSource = new EventSource(`${API_BASE}/stream`);
    evtSource.onmessage = () => {
        const now = Date.now();
        if (now - lastSseTime > 2000) { // Throttle intense simulator bursts from Python
            if (!document.getElementById("searchInput")?.value && !currentModalUid) {
                fetchFeed();
                fetchStats();
                lastSseTime = now;
            }
        }
    };
    evtSource.onerror = () => evtSource.close();
} catch (_) {}

// ── Polling fallback (5s) ───────────────────────────────────────
setInterval(() => {
    const now = Date.now();
    if (now - lastSseTime > 4000) { // Only poll if SSE is completely dead
        if (!document.getElementById("searchInput")?.value && !currentModalUid) {
            fetchStats();
            fetchFeed();
        }
    }
}, 5000);

// ── Initial Load ────────────────────────────────────────────────
fetchStats();
fetchFeed();
