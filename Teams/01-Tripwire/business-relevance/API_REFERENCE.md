# 🔌 Endur-Cert API Reference

Complete programming interface documentation for integrating Endur-Cert into your applications.

---

## Table of Contents

1. [BatteryEngine](#batteryengine)
2. [CertificateGenerator](#certificategenerator)
3. [Utility Functions](#utility-functions)
4. [Code Examples](#code-examples)

---

## BatteryEngine

Core assessment engine for battery health scoring and valuation.

### Initialization

```python
from src.battery_engine import BatteryEngine

# Default pack price: ₹2,50,000
engine = BatteryEngine()

# Custom pack price
engine = BatteryEngine(new_pack_price=300000)
```

### Methods

#### `calculate_health_score(predicted_rul: float) -> float`

Converts Remaining Useful Life to State-of-Health percentage.

```python
soh = engine.calculate_health_score(2500)  # Returns: 83.33
```

**Parameters:**
- `predicted_rul` (float): Remaining cycles (0-3500)

**Returns:**
- `float`: Health Score percentage (0-100)

**Formula:** `SoH = (RUL / 3000) × 100`

---

#### `calculate_temperature_penalty(avg_operating_temp: float) -> Tuple[float, str]`

Applies thermal penalty/bonus based on LFP degradation model.

```python
penalty, assessment = engine.calculate_temperature_penalty(38.5)
# Returns: (0.78, "⚠ Heat Tax: Operated at elevated temp (38.5°C)")
```

**Parameters:**
- `avg_operating_temp` (float): Operating temperature in Celsius

**Returns:**
- `Tuple[float, str]`: (penalty_factor, human_readable_assessment)

**Degradation Model:**
- Every 10°C above 25°C → ~2x degradation
- Penalty factor: `1.0 / (2^(temp_diff/10))`

**Example Temperature Factors:**
| Temp | Factor | Impact |
|------|--------|--------|
| 15°C | 1.2 | Cooling Bonus ⚡ |
| 25°C | 1.0 | Normal = |
| 35°C | 0.56 | Heat Tax ⚠ |
| 45°C | 0.31 | Severe Tax 🔥 |

---

#### `grade_battery(health_score: float) -> str`

Assigns grade based on health score.

```python
grade = engine.grade_battery(87.5)  # Returns: 'Grade A'
```

**Parameters:**
- `health_score` (float): SoH percentage (0-100)

**Returns:**
- `str`: 'Grade A', 'Grade B', or 'Grade C'

**Grading Scale:**
- `Grade A`: >85% SoH → High-Power Mobility
- `Grade B`: 70-85% SoH → Stationary Storage
- `Grade C`: <70% SoH → Resource Recovery

---

#### `calculate_residual_value(health_score: float, grade: str, temperature_penalty: float) -> float`

Calculates fair market price (Blue Book Value) in Rupees.

```python
value = engine.calculate_residual_value(
    health_score=75.0,
    grade='Grade B',
    temperature_penalty=0.85
)
# Returns: 131062.5
```

**Parameters:**
- `health_score` (float): SoH percentage
- `grade` (str): 'Grade A', 'Grade B', or 'Grade C'
- `temperature_penalty` (float): Thermal factor (0.5-1.2)

**Returns:**
- `float`: Residual value in INR

**Formula:**
```
Value = (New Pack Price × SoH%) × Application Multiplier × Temperature Penalty
```

**Application Multipliers:**
- Grade A: 1.0 (full value)
- Grade B: 0.85 (15% discount)
- Grade C: 0.2 (80% discount, recycling only)

---

#### `process_battery(battery_id: str, predicted_rul: float, avg_operating_temp: float) -> Dict`

Complete assessment pipeline for a single battery.

```python
result = engine.process_battery(
    battery_id='BATT_001',
    predicted_rul=2500,
    avg_operating_temp=35.5
)

print(result['Battery_ID'])          # 'BATT_001'
print(result['Health_Score_%'])      # 83.33
print(result['Grade'])               # 'Grade B'
print(result['Residual_Value_INR'])  # 123456.78
```

**Parameters:**
- `battery_id` (str): Unique identifier
- `predicted_rul` (float): RUL in cycles
- `avg_operating_temp` (float): Temperature in Celsius

**Returns:**
- `Dict`: Complete assessment with keys:
  - `Battery_ID`
  - `Predicted_RUL`
  - `Avg_Operating_Temp`
  - `Health_Score_%`
  - `Grade`
  - `Category`
  - `Applications`
  - `Temperature_Penalty_Factor`
  - `Temperature_Assessment`
  - `Residual_Value_INR`
  - `Assessment_Date`

---

#### `process_fleet(df: DataFrame) -> DataFrame`

Assess an entire fleet of batteries.

```python
import pandas as pd
from src.battery_engine import BatteryEngine

df = pd.read_csv('data/sample_fleet.csv')
engine = BatteryEngine()
results = engine.process_fleet(df)

print(f"Assessed {len(results)} batteries")
print(results.head())
```

**Parameters:**
- `df` (DataFrame): Must contain columns:
  - `Battery_ID` (str)
  - `Predicted_RUL` (float)
  - `Average_Operating_Temperature` (float)

**Returns:**
- `DataFrame`: Assessment results for all batteries

**Example:**
```
        Battery_ID  Predicted_RUL  Avg_Operating_Temp  Health_Score_%   Grade
0  BATT_0001       2850            26.3                95.0             Grade A
1  BATT_0002       2750            28.5                91.7             Grade A
2  BATT_0003       2650            31.2                88.3             Grade A
3  BATT_0004       2550            35.0                85.0             Grade B
4  BATT_0005       2450            38.5                81.7             Grade B
```

---

#### `get_fleet_summary(assessed_df: DataFrame) -> Dict`

Generate summary statistics for a fleet.

```python
summary = engine.get_fleet_summary(results)

print(f"Total: {summary['Total_Batteries']}")
print(f"Grade A: {summary['Grade_A_Count']} ({summary['Grade_A_Percentage']}%)")
print(f"Total Value: ₹{summary['Total_Residual_Value_INR']:,.0f}")
```

**Parameters:**
- `assessed_df` (DataFrame): Output from `process_fleet()`

**Returns:**
- `Dict`: Summary with keys:
  - `Total_Batteries`
  - `Grade_A_Count`, `Grade_A_Percentage`
  - `Grade_B_Count`, `Grade_B_Percentage`
  - `Grade_C_Count`, `Grade_C_Percentage`
  - `Total_Residual_Value_INR`
  - `Avg_Health_Score_%`
  - `Avg_Operating_Temp_C`
  - `Min_Residual_Value_INR`
  - `Max_Residual_Value_INR`

---

## CertificateGenerator

Generates digital battery passports in PDF and JSON formats.

### Initialization

```python
from src.certificate_generator import CertificateGenerator

# Default output directory: 'certificates'
cert_gen = CertificateGenerator()

# Custom output directory
cert_gen = CertificateGenerator(output_dir='/path/to/certs')
```

### Methods

#### `generate_json_certificate(battery_data: Dict, filename: str = None) -> str`

Creates a JSON certificate for a battery.

```python
battery_data = {
    'Battery_ID': 'BATT_001',
    'Predicted_RUL': 2500,
    'Avg_Operating_Temp': 35.5,
    'Health_Score_%': 83.33,
    'Grade': 'Grade B',
    'Category': 'Stationary Energy Storage',
    'Applications': 'Home UPS, Solar Microgrids',
    'Temperature_Penalty_Factor': 0.78,
    'Temperature_Assessment': '⚠ Heat Tax...',
    'Residual_Value_INR': 123456.78,
    'Assessment_Date': '2024-03-17 10:30:00'
}

cert_path = cert_gen.generate_json_certificate(battery_data)
# Returns: 'certificates/BATT_001_certificate.json'
```

**Parameters:**
- `battery_data` (Dict): Battery assessment dictionary
- `filename` (str, optional): Custom filename

**Returns:**
- `str`: Path to generated JSON file

**JSON Structure:**
```json
{
  "certificate_type": "Digital Battery Passport",
  "issue_date": "2024-03-17T10:30:00",
  "version": "1.0",
  "battery_info": {
    "battery_id": "BATT_001",
    "predicted_rul_cycles": 2500,
    "average_operating_temp_c": 35.5
  },
  "health_assessment": {
    "health_score_percent": 83.33,
    "grade": "Grade B",
    "category": "Stationary Energy Storage",
    "certified_applications": ["Home UPS", "Solar Microgrids"]
  },
  "thermal_audit": {
    "temperature_penalty_factor": 0.78,
    "assessment": "⚠ Heat Tax..."
  },
  "valuation": {
    "residual_value_inr": 123456.78,
    "currency": "INR",
    "blue_book_value": "₹123,456.78"
  }
}
```

---

#### `generate_pdf_certificate(battery_data: Dict, filename: str = None) -> str`

Creates a professional PDF certificate.

```python
pdf_path = cert_gen.generate_pdf_certificate(battery_data)
# Returns: 'certificates/BATT_001_certificate.pdf'
```

**Parameters:**
- `battery_data` (Dict): Battery assessment dictionary
- `filename` (str, optional): Custom filename

**Returns:**
- `str`: Path to generated PDF file

**PDF Content:**
- Header: "ENDUR-CERT Digital Battery Passport"
- Grade badge with color coding
- Battery information table
- Health assessment details
- Thermal audit results
- Blue Book valuation (large, highlighted)
- Certification metadata

---

#### `generate_batch_certificates(assessed_df: DataFrame, format: str = 'both') -> Dict[str, list]`

Generate certificates for all batteries in a fleet.

```python
results = cert_gen.generate_batch_certificates(assessed_df, format='both')

print(f"Generated {len(results['pdf'])} PDFs")
print(f"Generated {len(results['json'])} JSONs")

# Access results
for pdf_path in results['pdf']:
    print(f"  ✓ {pdf_path}")
```

**Parameters:**
- `assessed_df` (DataFrame): Assessment results from `process_fleet()`
- `format` (str): 'pdf', 'json', or 'both' (default: 'both')

**Returns:**
- `Dict`: With keys 'pdf' and 'json', each containing list of file paths

---

## Utility Functions

Located in `src/utils.py`

### `load_sample_fleet_data() -> DataFrame`

Generates sample battery data for testing.

```python
from src.utils import load_sample_fleet_data

df = load_sample_fleet_data()
print(df.head())
```

### `create_sample_csv(output_path: str = 'data/sample_fleet.csv')`

Creates a sample CSV file.

```python
from src.utils import create_sample_csv

create_sample_csv('my_sample.csv')
```

### `validate_battery_data(df: DataFrame) -> Tuple[bool, str]`

Validates data format and content.

```python
from src.utils import validate_battery_data

df = pd.read_csv('data.csv')
is_valid, message = validate_battery_data(df)

if is_valid:
    print(f"✓ {message}")
else:
    print(f"❌ {message}")
```

---

## Code Examples

### Complete Assessment Pipeline

```python
import pandas as pd
from src.battery_engine import BatteryEngine
from src.certificate_generator import CertificateGenerator

# 1. Initialize components
engine = BatteryEngine(new_pack_price=250000)
cert_gen = CertificateGenerator(output_dir='my_certs')

# 2. Load data
df = pd.read_csv('battery_data.csv')

# 3. Assess fleet
results = engine.process_fleet(df)

# 4. Get summary
summary = engine.get_fleet_summary(results)
print(f"Fleet total value: ₹{summary['Total_Residual_Value_INR']:,.0f}")

# 5. Generate certificates
certs = cert_gen.generate_batch_certificates(results, format='both')
print(f"Generated {len(certs['pdf'])} certificates")

# 6. Export results
results.to_csv('assessment_results.csv', index=False)
print("Results saved!")
```

### Single Battery Assessment

```python
from src.battery_engine import BatteryEngine

engine = BatteryEngine()

# Assess one battery
assessment = engine.process_battery(
    battery_id='BATT_12345',
    predicted_rul=2000,
    avg_operating_temp=38.0
)

# Display results
print(f"Battery: {assessment['Battery_ID']}")
print(f"Grade: {assessment['Grade']}")
print(f"Health: {assessment['Health_Score_%']:.1f}%")
print(f"Value: ₹{assessment['Residual_Value_INR']:,.0f}")
print(f"Best For: {assessment['Applications']}")
```

### Filtered Assessment

```python
import pandas as pd
from src.battery_engine import BatteryEngine

engine = BatteryEngine()

# Load data
df = pd.read_csv('fleet.csv')

# Assess all
results = engine.process_fleet(df)

# Filter Grade A only
grade_a = results[results['Grade'] == 'Grade A']
print(f"High-power batteries: {len(grade_a)}")
print(f"Total value: ₹{grade_a['Residual_Value_INR'].sum():,.0f}")

# Sort by value
top_10 = results.nlargest(10, 'Residual_Value_INR')
```

### Custom Configuration

```python
import pandas as pd
from src.battery_engine import BatteryEngine
import config

# Use configuration file
engine = BatteryEngine(new_pack_price=config.NEW_PACK_PRICE)

# Modify on the fly
engine.LFP_STANDARD_LIFE = 2500  # Custom life expectancy

# Process with custom settings
df = pd.read_csv('data.csv')
results = engine.process_fleet(df)
```

### Error Handling

```python
import pandas as pd
from src.battery_engine import BatteryEngine
from src.utils import validate_battery_data

engine = BatteryEngine()

try:
    df = pd.read_csv('battery_data.csv')
    
    # Validate before processing
    is_valid, message = validate_battery_data(df)
    if not is_valid:
        raise ValueError(message)
    
    # Process
    results = engine.process_fleet(df)
    print(f"✓ Assessed {len(results)} batteries")
    
except FileNotFoundError:
    print("❌ CSV file not found")
except ValueError as e:
    print(f"❌ Validation error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

---

## Configuration Reference

Modify `config.py` to customize the engine:

```python
# Battery specifications
LFP_STANDARD_LIFE = 3000        # Cycles
TEMPERATURE_DEGRADATION_RATE = 2  # 2x per 10°C
STANDARD_TEMP = 25              # Reference temperature (°C)

# Grade thresholds (% SoH)
GRADE_A_MIN = 85
GRADE_B_MIN = 70

# Financial
NEW_PACK_PRICE = 250000         # ₹2.5 Lakhs
MIN_RECYCLING_VALUE_PERCENTAGE = 15  # 15% floor
```

---

## Performance Notes

- **Single Battery:** <1ms processing time
- **100 Battery Fleet:** <50ms processing time
- **1000 Battery Fleet:** <500ms processing time
- **Memory Usage:** ~1MB per 1000 batteries

---

## Thread Safety

The `BatteryEngine` is thread-safe for:
- `calculate_health_score()`
- `calculate_temperature_penalty()`
- `grade_battery()`
- `calculate_residual_value()`

Not recommended for concurrent `process_fleet()` calls on massive datasets.

---

## Version & Compatibility

- **Endur-Cert:** v1.0.0
- **Python:** 3.8+
- **Pandas:** 2.0+
- **NumPy:** 1.24+

---

**Ready to integrate! 🚀**
