# 🚀 GETTING STARTED - IMMEDIATE ACTION ITEMS

**Everything is working!** Here's exactly what you need to do:

---

## Step 1: Activate Virtual Environment

Open **PowerShell** and navigate to the project:

```powershell
cd d:\2ndlife
.\venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

---

## Step 2: Run Quickstart (Optional - To See It Work)

Test the system without opening a browser:

```powershell
python quickstart.py
```

This will:
- ✓ Load 30 sample batteries
- ✓ Run full assessment (~100ms)
- ✓ Generate 5 PDF + 5 JSON certificates
- ✓ Export CSV, Excel, and text reports

You'll see output like this:

```
✓ Loaded 30 batteries
✓ Assessed 30 batteries
✓ Generated 5 PDF certificates
✓ Generated 5 JSON certificates
✓ CSV export: assessment_results.csv
```

---

## Step 3: Launch Interactive Dashboard

```powershell
streamlit run app.py
```

**What happens:**
- Browser opens automatically to `http://localhost:8501`
- You see the Endur-Cert dashboard
- Four pages available: Dashboard, Upload & Assess, Certificates, About

---

## Step 4: Try It Yourself

### Option A: Use Sample Data
1. Go to **📤 Upload & Assess** page
2. The sample CSV is already in `data/sample_fleet.csv`
3. Click **📦 Choose CSV file**
4. Select `data/sample_fleet.csv`
5. Click **🚀 Run Assessment**
6. Go to **📊 Dashboard** to see results
7. Go to **📜 Certificates** to generate PDFs

### Option B: Upload Your Own Data

Create a CSV file with three columns:

```csv
Battery_ID,Predicted_RUL,Average_Operating_Temperature
BAT_001,2500,35.5
BAT_002,1800,40.0
BAT_003,500,38.0
```

Then upload it on the **📤 Upload & Assess** page.

---

## ⚡ Quick Commands

```powershell
# Start everything
cd d:\2ndlife
.\venv\Scripts\activate
streamlit run app.py

# Or for quick test (no browser)
python quickstart.py

# Check what was generated
dir certificates\
Get-Content assessment_results.csv
```

---

## 📊 What to Expect

### Dashboard Page
- Grade distribution pie chart
- Value distribution bar chart
- Health score histogram
- Temperature vs Health scatter plot
- Real-time metrics

### Sample Assessment Results
For a battery with:
- RUL: 2,500 cycles
- Temp: 38.5°C

You'll get:
- Health Score: 83.3% ✓
- Grade: B (Stationary Storage)
- Blue Book Value: ₹68,079
- Best For: Home UPS, Solar Microgrids

### Certificate Files Generated
Format: `BATT_001_certificate.pdf` and `.json`
- Professional PDF with grade badge
- Structured JSON data
- Ready for sharing/archiving

---

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `app.py` | **Run this for dashboard** |
| `quickstart.py` | Run this for quick test |
| `data/sample_fleet.csv` | Sample data |
| `certificates/` | Generated certificates |
| `README.md` | Full documentation |
| `API_REFERENCE.md` | Programming guide |

---

## ✅ Troubleshooting

### "streamlit: command not found"
→ Make sure venv is activated: `.\venv\Scripts\activate`

### "Port 8501 already in use"
→ Use different port: `streamlit run app.py --server.port 8502`

### "No module named pandas"
→ Install dependencies: `pip install -r requirements.txt`

### PDF certificates look blank
→ They're fine! ReportLab generates professional PDFs. Open with any PDF reader.

---

## 💡 Pro Tips

1. **Custom Pack Price:** Set on Upload & Assess page (default ₹2,50,000)
2. **Batch Process:** Upload 100+ batteries at once
3. **Export Results:** Download CSV, Excel, or PDF
4. **Filter Certificates:** Select by grade before generating
5. **View JSON:** Open the .json files in any text editor to see structured data

---

## 📚 Documentation

| Document | Read if... |
|----------|-----------|
| `SETUP.md` | You need installation help |
| `README.md` | You want full overview |
| `API_REFERENCE.md` | You're programming integration |
| `QUICK_REFERENCE.md` | You want one-page cheat sheet |
| `VERIFICATION_REPORT.md` | You want to see test results |

---

## 🎉 You're All Set!

Everything is working. Just:

1. Open PowerShell
2. Navigate to `d:\2ndlife`
3. Activate venv: `.\venv\Scripts\activate`
4. Run: `streamlit run app.py`
5. Browser opens automatically
6. Start assessing! 🚀

---

**Built for India's EV Revolution 🇮🇳**

Transform RUL into Value. Turn Second-Life into Sustainable Business.
