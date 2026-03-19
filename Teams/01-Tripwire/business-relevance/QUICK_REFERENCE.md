# ⚡ Endur-Cert Quick Reference Card

## 🚀 Getting Started (60 seconds)

```powershell
# Navigate to project
cd d:\2ndlife

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run app.py

# Open browser: http://localhost:8501
```

---

## 📊 The Three-Step Process

```
1. UPLOAD CSV → 2. RUN ASSESSMENT → 3. VIEW RESULTS
```

**CSV Format Required:**
```
Battery_ID,Predicted_RUL,Average_Operating_Temperature
BATT_001,2500,35.5
BATT_002,1800,40.0
```

---

## ⚙️ Core Formulas

### Health Score
$$SoH = \left(\frac{RUL}{3000}\right) \times 100$$

### Temperature Penalty (°C diff from 25°C)
$$Penalty = \frac{1}{2^{(T_{diff}/10)}}$$

### Blue Book Value
$$Value = (\text{Price} \times SoH\%) \times M_{app} \times P_{thermal}$$

---

## 🎯 Battery Grades

| Grade | SoH | Application | Value | |
|-------|-----|-------------|-------|---|
| A | >85% | High-Power Mobility | ₹ | 🟢 |
| B | 70-85% | Stationary Storage | ₹ (15% less) | 🟠 |
| C | <70% | Resource Recovery | ₹ (80% less) | 🔴 |

---

## 🌡️ Temperature Impact

| Temp | Factor | Impact |
|------|--------|--------|
| 15°C | 1.2 | ⚡ Bonus |
| 25°C | 1.0 | = Normal |
| 35°C | 0.56 | ⚠ Tax |
| 45°C | 0.31 | 🔥 Severe |

---

## 📁 File Organization

```
d:\2ndlife
├── app.py                 ← MAIN FILE (run this)
├── config.py              ← Settings
├── quickstart.py          ← Demo (no dashboard)
├── requirements.txt       ← Dependencies
├── src/
│   ├── battery_engine.py  ← Core logic
│   ├── certificate_generator.py
│   └── utils.py
└── data/sample_fleet.csv  ← Test data
```

---

## 🔧 Python API (Programmatic)

### Quick Assessment
```python
from src.battery_engine import BatteryEngine
import pandas as pd

engine = BatteryEngine()
df = pd.read_csv('data.csv')
results = engine.process_fleet(df)
summary = engine.get_fleet_summary(results)
```

### Generate Certificates
```python
from src.certificate_generator import CertificateGenerator

cert_gen = CertificateGenerator()
results = cert_gen.generate_batch_certificates(df)
```

---

## 🎨 Dashboard Pages

1. **📊 Dashboard** - View fleet analytics & metrics
2. **📤 Upload & Assess** - Import CSV & run assessment
3. **📜 Certificates** - Generate PDF/JSON passports
4. **ℹ️ About** - Learn the methodology

---

## 💾 Output Files

After assessment, you get:
- `assessment_results.csv` - Full data table
- `assessment_results.xlsx` - Excel spreadsheet
- `certificates/BATT_*.pdf` - PDF passports
- `certificates/BATT_*.json` - JSON data files

---

## 📊 Example Output

**Assessment Results for BATT_001:**
- Health Score: **83.3%** SoH
- Grade: **Grade B** ✓
- Thermal Factor: **0.71** (heat penalty)
- Residual Value: **₹127,500**
- Best For: Home UPS, Solar Microgrids

---

## 🐛 Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| "Python not found" | Add Python to PATH |
| "No module named streamlit" | Run `pip install -r requirements.txt` |
| "Port 8501 in use" | Run `streamlit run app.py --server.port 8502` |
| "Permission denied" | Use `python` not `python3` (Windows) |

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created & activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Dashboard launches (`streamlit run app.py`)
- [ ] Browser opens at localhost:8501
- [ ] Sample CSV loads successfully
- [ ] Assessment completes (should be instant)
- [ ] Certificates generate without errors

---

## 🚀 Key Commands

```bash
# Activate environment
.\venv\Scripts\activate               # Windows
source venv/bin/activate              # Mac/Linux

# Install packages
pip install -r requirements.txt

# Run dashboard
streamlit run app.py

# Run demo
python quickstart.py

# Check config
python config.py

# Deactivate environment
deactivate
```

---

## 📈 Assessment Example

**Input Fleet:** 30 batteries  
**Processing Time:** <100ms  
**Output:**
- 30 assessments
- Fleet summary (14 metrics)
- Grade breakdown: 12 A's, 14 B's, 4 C's
- Total value: ₹42,50,000
- 30 PDF + 30 JSON certificates

---

## 💡 Pro Tips

1. **Custom Pack Price:** Set on Upload page (default ₹2,50,000)
2. **Batch Processing:** Upload 1000+ batteries at once
3. **Offline Use:** Works completely offline (no cloud calls)
4. **Export Data:** Results auto-save to CSV/XLSX
5. **Rerun Assessment:** Just re-upload same CSV for latest calcs

---

## 🔗 Important Links

- **README.md** - Full documentation
- **SETUP.md** - Installation help
- **API_REFERENCE.md** - Programming guide
- **config.py** - Configuration settings
- **quickstart.py** - Demo without dashboard

---

## 🎯 Business Value

- ✅ **Fair Pricing** - Scientific Blue Book valuations
- ✅ **Market Trust** - Digital passports eliminate doubt
- ✅ **Second Life** - 3 optimization paths maximize value
- ✅ **Climate Aware** - India-specific thermal model
- ✅ **Fleet Planning** - Instant financial forecasting

---

## 📏 Configuration Limits

| Parameter | Min | Max |
|-----------|-----|-----|
| RUL (cycles) | 0 | 3,500 |
| Temperature (°C) | 0 | 60 |
| Pack Price (₹) | 100,000 | 5,000,000 |
| Fleet Size | 1 | 100,000+ |

---

## 🎓 Formula Reference Card

| Concept | Formula |
|---------|---------|
| Health Score | SoH = (RUL / 3000) × 100 |
| Thermal Factor | f(T) = 1 / 2^(ΔT/10) |
| Blue Book Value | V = P × S × M × f |
| Grade A | >85% SoH |
| Grade B | 70-85% SoH |
| Grade C | <70% SoH |

---

**Ready to Assess? Run:** `streamlit run app.py` 🚀

*Transform RUL into Value. Turn Second-Life into Sustainable Business.* 🇮🇳
