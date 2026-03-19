# 🚀 Endur-Cert Setup Guide

Complete step-by-step installation and first-run instructions.

## System Requirements

- **Python:** 3.8 or higher
- **OS:** Windows, macOS, or Linux
- **RAM:** 2GB minimum (4GB recommended)
- **Disk Space:** 500MB for dependencies

---

## ⚡ Quick Start (5 minutes)

### Windows

1. **Open PowerShell** and navigate to the project:
   ```powershell
   cd d:\2ndlife
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Launch dashboard:**
   ```powershell
   streamlit run app.py
   ```

5. **Browser automatically opens** at `http://localhost:8501`

---

### macOS / Linux

1. **Open Terminal** and navigate to the project:
   ```bash
   cd ~/2ndlife  # or wherever you cloned it
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch dashboard:**
   ```bash
   streamlit run app.py
   ```

5. **Open browser** to `http://localhost:8501`

---

## 📋 Detailed Installation

### Step 1: Install Python

#### Windows
- Download from https://www.python.org/downloads/
- Run installer and **check "Add Python to PATH"**
- Verify: Open PowerShell and run:
  ```powershell
  python --version
  ```

#### macOS
```bash
brew install python3
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

---

### Step 2: Clone/Navigate to Project

#### From GitHub
```bash
git clone https://github.com/yourusername/endur-cert.git
cd endur-cert
```

#### Or if you have it locally
```bash
cd d:\2ndlife  # Windows
cd ~/2ndlife   # macOS/Linux
```

---

### Step 3: Create Virtual Environment

**Why?** Isolates project dependencies from your system Python.

#### Windows
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

**Your terminal should show `(venv)` prefix after activation.**

---

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pandas` - Data processing
- `numpy` - Numerical computing
- `streamlit` - Web dashboard
- `plotly` - Interactive visualizations
- `reportlab` - PDF generation
- `openpyxl` - Excel export

---

### Step 5: Create Sample Data (Optional)

```bash
python src/utils.py
```

This creates `data/sample_fleet.csv` with 50 test batteries.

---

### Step 6: Launch the Application

#### Option A: Streamlit Dashboard (Recommended)
```bash
streamlit run app.py
```
- Opens interactive web interface
- Upload CSV, view analytics, generate certificates
- Perfect for demonstrations

#### Option B: Quick Start Script
```bash
python quickstart.py
```
- Non-interactive command-line demonstration
- Generates sample assessment and certificates
- Good for testing the pipeline

#### Option C: Programmatic Usage
```python
from src.battery_engine import BatteryEngine
import pandas as pd

engine = BatteryEngine(new_pack_price=250000)
df = pd.read_csv('data/sample_fleet.csv')
results = engine.process_fleet(df)
print(results)
```

---

## 🎯 First Run Checklist

- [ ] Python installed and added to PATH
- [ ] Navigated to `d:\2ndlife` directory
- [ ] Virtual environment created and activated
- [ ] Dependencies installed with `pip install -r requirements.txt`
- [ ] Dashboard launches with `streamlit run app.py`
- [ ] Browser opens to `http://localhost:8501`
- [ ] Can access all pages (Dashboard, Upload & Assess, Certificates, About)
- [ ] Can upload sample_fleet.csv
- [ ] Assessment completes successfully
- [ ] Certificates generate without errors

---

## 🔧 Troubleshooting

### "Python is not recognized"
- **Windows:** Python not in PATH
- **Solution:** Reinstall Python and check "Add Python to PATH" during installation

### "No module named 'streamlit'"
- **Cause:** Dependencies not installed or wrong virtual environment
- **Solution:** 
  ```bash
  pip install -r requirements.txt
  ```

### "Permission denied" (macOS/Linux)
- **Cause:** File permissions issue
- **Solution:**
  ```bash
  chmod +x quickstart.py
  python quickstart.py
  ```

### "Port 8501 already in use"
- **Cause:** Another Streamlit app is running
- **Solution:**
  ```bash
  streamlit run app.py --server.port 8502
  ```

### PDF generation fails
- **Cause:** Missing system fonts or invalid characters
- **Solution:** Update reportlab:
  ```bash
  pip install --upgrade reportlab
  ```

### Memory issues with large fleet
- **Solution:** Process in batches or increase system RAM

---

## 📦 Project Structure After Setup

```
d:\2ndlife/
├── venv/                    # Virtual environment
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── .gitignore
├── app.py                  # Main Streamlit app
├── quickstart.py           # Quick demo script
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md               # Full documentation
├── SETUP.md               # This file
├── src/
│   ├── __init__.py
│   ├── battery_engine.py   # Core assessment logic
│   ├── certificate_generator.py  # PDF/JSON generation
│   └── utils.py            # Helper functions
├── data/
│   └── sample_fleet.csv    # Example data
├── certificates/           # Generated certificates (created on first run)
└── assessment_results.*    # Export files (created after assessment)
```

---

## 🚀 Next Steps

1. **Run the dashboard:**
   ```bash
   streamlit run app.py
   ```

2. **Upload your battery data** (CSV with Battery_ID, Predicted_RUL, Avg_Temp)

3. **View analytics** on the Dashboard page

4. **Generate certificates** for your batteries

5. **Export results** as PDF, JSON, or CSV

---

## 💡 Tips

### Running in the Background (Windows)
```powershell
# Start Streamlit in background
Start-Process powershell -ArgumentList "cd d:\2ndlife; .\venv\Scripts\activate; streamlit run app.py"
```

### Running on Network
```bash
# Access from another computer
streamlit run app.py --server.address 0.0.0.0
# Then visit: http://<your-ip>:8501
```

### Disable Browser Auto-Open
```bash
streamlit run app.py --logger.level=error --client.showErrorDetails=false
```

### Performance Optimization
```bash
pip install --upgrade pandas numpy  # Get latest optimized versions
```

---

## 📚 Further Reading

- [Streamlit Documentation](https://docs.streamlit.io)
- [Pandas Guide](https://pandas.pydata.org/docs/)
- [Plotly Charts](https://plotly.com/python/)
- [ReportLab PDF](https://www.reportlab.com/)

---

## ✅ Verification Steps

After installation, verify everything works:

```bash
# Test 1: Import modules
python -c "import pandas, streamlit, plotly, reportlab; print('✓ All imports successful')"

# Test 2: Run quick assessment
python quickstart.py

# Test 3: Launch dashboard
streamlit run app.py
```

---

**Ready to transform RUL into value! 🚀**
