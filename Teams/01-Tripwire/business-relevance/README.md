# 🔋 ENDUR-CERT: Battery "Blue Book" & Certification Engine

Transform Remaining Useful Life (RUL) data into a **business-ready valuation tool** for India's EV revolution.

## 📋 Table of Contents

- [Overview](#overview)
- [Core Philosophy](#core-philosophy)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [The Engine Explained](#the-engine-explained)
- [Technical Architecture](#technical-architecture)

---

## 📖 Overview

India's EV revolution is creating millions of second-life batteries—but the used battery market lacks **trust and transparency**. 

**Endur-Cert** solves this by:
1. Converting RUL into **State-of-Health (SoH) percentages**
2. Applying **thermal audits** for India's high-heat conditions
3. Assigning batteries to **"Career Paths"** (mobility, storage, recycling)
4. Providing **Blue Book valuations** for immediate business impact

A battery at 80% health is not the **end of its life**—it's the **beginning of its second career**.

---

## 🧠 Core Philosophy

### The Data-to-Value Pipeline

The engine follows a **three-step logic flow**:

```
INPUT → HEALTH SCORE → THERMAL AUDIT → GRADING → VALUATION → OUTPUT
```

1. **Input:** Battery_ID, Predicted_RUL (cycles), Average_Operating_Temperature
2. **Health Score:** Converts RUL to SoH% using LFP standard of 3,000 cycles
3. **Temperature Audit:** Applies "Heat Tax" or "Cooling Bonus" (degradation doubles every 10°C)
4. **Grading:** Categorizes into Grade A/B/C based on SoH
5. **Valuation:** Calculates fair market price (Residual Value) in Rupees
6. **Output:** Digital Battery Passport (PDF + JSON certificate)

### Functional Grading System

| Grade | SoH | Application | Examples |
|-------|-----|-------------|----------|
| **A** | >85% | High-Power Mobility | e-Rickshaws, Last-mile Delivery |
| **B** | 70-85% | Stationary Storage | Home UPS, Solar Microgrids |
| **C** | <70% | Resource Recovery | Lithium Reclamation, Recycling |

---

## ✨ Features

- ✅ **Fast Assessment:** Process entire fleets in seconds
- ✅ **Temperature-Aware:** Accounts for India's hot climate (>35°C)
- ✅ **Business-Ready:** Instant "Blue Book" valuations
- ✅ **Digital Passports:** Transparent certificates for every battery
- ✅ **Scalable:** Handles fleets of any size
- ✅ **Interactive Dashboard:** Real-time analytics and insights
- ✅ **Multiple Exports:** PDF certificates, JSON data, Excel reports

---

## 📁 Project Structure

```
d:\2ndlife/
├── app.py                      # Streamlit dashboard (main entry point)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── src/
│   ├── battery_engine.py       # Core valuation logic
│   ├── certificate_generator.py # PDF/JSON certificate creation
│   └── utils.py                # Utility functions
├── data/
│   └── sample_fleet.csv        # Example battery dataset
└── certificates/               # Output directory (auto-created)
    ├── BATT_001_certificate.pdf
    ├── BATT_001_certificate.json
    └── ...
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Navigate to Project

```bash
cd d:\2ndlife
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Launch the Dashboard

```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501` in your browser.

---

## 📚 Usage Guide

### 1. **Prepare Your Data**

Create a CSV file with three columns:

```csv
Battery_ID,Predicted_RUL,Average_Operating_Temperature
BATT_001,2800,28.5
BATT_002,1950,42.0
BATT_003,500,35.0
```

**Column Definitions:**
- `Battery_ID`: Unique identifier (string)
- `Predicted_RUL`: Remaining cycles (integer, 0-3500)
- `Average_Operating_Temperature`: Celsius (float, 0-60)

### 2. **Upload & Assess**

1. Open the dashboard (run `streamlit run app.py`)
2. Navigate to **📤 Upload & Assess**
3. Upload your CSV file
4. (Optional) Set custom "New Pack Price" 
5. Click **🚀 Run Assessment**

### 3. **View Results**

- **📊 Dashboard:** See fleet analytics, grade distribution, valuations
- **📜 Certificates:** Generate PDF and JSON passports for each battery
- **📋 Export:** Download results as Excel, JSON, or PDF

### 4. **Generate Certificates**

1. Navigate to **📜 Certificates**
2. Filter batteries by grade or select specific ones
3. Choose PDF and/or JSON format
4. Click **🏆 Generate Certificates**
5. Certificates are saved in the `certificates/` folder

---

## 🔧 The Engine Explained

### Health Score Calculation

```
Health Score (%) = (Predicted_RUL / 3000) × 100
```

Where 3,000 cycles is the LFP battery standard life.

**Example:**
- RUL = 2,500 cycles → Health Score = 83.3%

### Thermal Penalty Factor

LFP batteries degrade **2x faster** for every 10°C above standard (25°C).

| Temperature | Penalty Factor | Interpretation |
|-------------|----------------|-----------------|
| 15°C | 1.2 | ⚡ Cooling Bonus |
| 25°C | 1.0 | = Normal |
| 35°C | 0.56 | ⚠ Heat Tax |
| 45°C | 0.31 | 🔥 Severe Heat Tax |

### Blue Book Valuation Formula

```
Value (₹) = (New Pack Price × SoH%) × Application Multiplier × Temperature Factor
```

**Example:**
- New Pack Price: ₹2,50,000
- SoH: 75%
- Grade B Multiplier: 0.85
- Temperature Factor: 0.8 (hot conditions)
- **Residual Value = 250,000 × 0.75 × 0.85 × 0.8 = ₹1,27,500**

---

## 📊 Python API Usage

### Programmatic Assessment (Without Dashboard)

```python
from src.battery_engine import BatteryEngine
import pandas as pd

# Initialize engine
engine = BatteryEngine(new_pack_price=250000)

# Load data
df = pd.read_csv('data/sample_fleet.csv')

# Process fleet
results = engine.process_fleet(df)

# Get summary
summary = engine.get_fleet_summary(results)
print(f"Total Batteries: {summary['Total_Batteries']}")
print(f"Avg Health Score: {summary['Avg_Health_Score_%']:.1f}%")
print(f"Total Residual Value: ₹{summary['Total_Residual_Value_INR']:,.0f}")
```

### Generate Certificates Programmatically

```python
from src.certificate_generator import CertificateGenerator

cert_gen = CertificateGenerator(output_dir='certificates')

# Generate batch certificates
results = cert_gen.generate_batch_certificates(results, format='both')

print(f"Generated {len(results['pdf'])} PDFs")
print(f"Generated {len(results['json'])} JSONs")
```

---

## 🏗️ Technical Architecture

### Backend
- **Language:** Python 3.8+
- **Data Processing:** Pandas, NumPy
- **Logic:** Rule-based scoring engine (if-else diagnostics)

### Frontend
- **Framework:** Streamlit
- **Visualization:** Plotly (interactive charts)
- **UI/UX:** Custom HTML/CSS styling

### Certificate Generation
- **PDF:** ReportLab (professional, styled documents)
- **JSON:** Native Python JSON with structured metadata

### Deployment Ready
- Cloud-friendly (no database required)
- Stateless design (independent assessments)
- Scalable to millions of batteries

---

## 📈 Example Output

### Dashboard Insights
- **Grade Distribution Pie Chart:** Visual breakdown of fleet composition
- **Residual Value by Grade:** Bar chart showing financial distribution
- **Health Score Histogram:** Distribution curve with mean line
- **Temperature vs Health Scatter:** Correlation analysis

### Certificate Example

**Grade A - High-Power Mobility Battery**
```
Battery ID: BATT_001
Health Score: 87.5% SoH
Grade: Grade A ✓ CERTIFIED
Certified Applications: e-Rickshaws, Last-Mile Delivery
Blue Book Value: ₹2,18,750
Temperature Assessment: ✓ Good (Operated below standard)
Thermal Penalty Factor: 1.1 (Cooling Bonus)
```

---

## 🎯 Why Endur-Cert Wins

1. **Indian Context:** Accounts for >35°C heat degradation common in India
2. **Market Solution:** Provides immediate "Blue Book" valuations, not just math
3. **Trust Building:** Digital passports solve information asymmetry in used battery market
4. **Business Impact:** Enables fleet operators to execute trade-in programs
5. **Sustainability:** Facilitates circular economy through second-life optimization

---

## 🔗 Future Enhancements

- [ ] Integration with EV fleet management systems
- [ ] Real-time degradation tracking via IoT sensors
- [ ] Blockchain certificates for immutable records
- [ ] Price prediction based on market demand
- [ ] Multi-chemistry support (NCA, NCM, LMO)
- [ ] Warranty estimation engine

---

## 📞 Support & Contribution

For issues, questions, or feature requests, please create an issue in the repository.

---

## 📄 License

Built for India's EV Revolution 🇮🇳

---

**Happy Assessing! 🚀**
