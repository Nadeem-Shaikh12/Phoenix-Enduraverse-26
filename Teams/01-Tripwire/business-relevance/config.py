"""
Configuration File for Endur-Cert
Centralized settings for the battery assessment engine
"""

# =============================================================================
# BATTERY SPECIFICATIONS
# =============================================================================

# LFP Standard Life (cycles)
LFP_STANDARD_LIFE = 3000

# Temperature Degradation Rate
# LFP degrades ~2x for every 10°C increase above standard temp
TEMPERATURE_DEGRADATION_RATE = 2

# Standard Reference Temperature (°C)
STANDARD_TEMP = 25

# High-Heat Threshold for Indian conditions (°C)
HIGH_HEAT_THRESHOLD = 35


# =============================================================================
# BATTERY GRADING THRESHOLDS
# =============================================================================

# Health Score boundaries (% SoH)
GRADE_A_MIN = 85      # >85%  → Grade A
GRADE_B_MIN = 70      # 70-85% → Grade B
                      # <70%  → Grade C


# =============================================================================
# FINANCIAL CONFIGURATION
# =============================================================================

# New Battery Pack Reference Price (INR)
NEW_PACK_PRICE = 250000  # ₹2.5 Lakhs (default)

# Application Multipliers for Second-Life Careers
APPLICATION_MULTIPLIERS = {
    'Grade A': {
        'category': 'High-Power Mobility',
        'multiplier': 1.0,
        'applications': [
            'e-Rickshaws',
            'Last-Mile Delivery',
            'Two-Wheeler Charging Stations',
            'High-Power Applications'
        ]
    },
    'Grade B': {
        'category': 'Stationary Energy Storage',
        'multiplier': 0.85,
        'applications': [
            'Home UPS Systems',
            'Solar Microgrids',
            'Telecom Tower Backup',
            'Renewable Integration',
            'Grid Stabilization'
        ]
    },
    'Grade C': {
        'category': 'Resource Recovery',
        'multiplier': 0.2,
        'applications': [
            'Lithium Reclamation',
            'Phosphate Recovery',
            'Advanced Recycling',
            'Material Refurbishment'
        ]
    }
}

# Minimum Recycling Value (as % of new pack price)
MIN_RECYCLING_VALUE_PERCENTAGE = 15  # 15% minimum


# =============================================================================
# TEMPERATURE ASSESSMENT CATEGORIES
# =============================================================================

TEMPERATURE_CATEGORIES = {
    'excellent': {
        'range': (-10, 0),
        'multiplier': 1.2,
        'description': '⚡ Cooling Bonus: Operated in ideal conditions'
    },
    'good': {
        'range': (0, 10),
        'multiplier': 1.1,
        'description': '✓ Good: Operated below standard temperature'
    },
    'normal': {
        'range': (10, 20),
        'multiplier': 1.0,
        'description': '= Normal: Operated near standard temperature'
    },
    'hot': {
        'range': (20, 30),
        'multiplier': 'degradation',  # Calculated
        'description': '⚠ Heat Tax: Operated at elevated temperature'
    },
    'very_hot': {
        'range': (30, float('inf')),
        'multiplier': 'degradation',  # Calculated
        'description': '🔥 Severe Heat Tax: Operated at extreme temperature'
    }
}


# =============================================================================
# DATA VALIDATION RANGES
# =============================================================================

# RUL Range (cycles)
RUL_MIN = 0
RUL_MAX = 3500

# Temperature Range (Celsius)
TEMP_MIN = 0
TEMP_MAX = 60


# =============================================================================
# CERTIFICATE GENERATION
# =============================================================================

# Certificate Output Formats
CERTIFICATE_FORMATS = ['pdf', 'json', 'both']

# Certificate Output Directory
CERTIFICATES_DIR = 'certificates'

# PDF Page Size (can be 'letter' or 'A4')
PDF_PAGE_SIZE = 'A4'


# =============================================================================
# STREAMLIT DASHBOARD SETTINGS
# =============================================================================

# Page Configuration
STREAMLIT_PAGE_TITLE = "Endur-Cert: Battery Blue Book & Certification Engine"
STREAMLIT_PAGE_ICON = "🔋"
STREAMLIT_LAYOUT = "wide"

# Sample Data Configuration
SAMPLE_FLEET_SIZE = 50
SAMPLE_DATA_PATH = 'data/sample_fleet.csv'


# =============================================================================
# EXPORT & REPORTING
# =============================================================================

# Excel Sheet Names
EXCEL_SHEET_NAME = 'Assessment Results'

# Report File Names
REPORT_FILE_NAME = 'fleet_assessment_report.txt'
CSV_EXPORT_NAME = 'assessment_results.csv'
EXCEL_EXPORT_NAME = 'assessment_results.xlsx'


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_temperature_category(temp_diff: float) -> dict:
    """
    Get temperature assessment category based on difference from standard temp.
    
    Args:
        temp_diff: Temperature difference from standard (25°C)
        
    Returns:
        Dictionary with category info
    """
    for category_name, category_info in TEMPERATURE_CATEGORIES.items():
        min_val, max_val = category_info['range']
        if min_val <= temp_diff < max_val:
            return {
                'name': category_name,
                'description': category_info['description'],
                'multiplier': category_info['multiplier']
            }
    
    return {
        'name': 'extreme',
        'description': '🔥 Extreme conditions detected',
        'multiplier': TEMPERATURE_DEGRADATION_RATE ** (temp_diff / 10)
    }


if __name__ == "__main__":
    # Print configuration summary
    print("="*70)
    print("ENDUR-CERT CONFIGURATION")
    print("="*70)
    print(f"\nBattery Specifications:")
    print(f"  LFP Standard Life:           {LFP_STANDARD_LIFE} cycles")
    print(f"  Standard Reference Temp:     {STANDARD_TEMP}°C")
    print(f"  High-Heat Threshold:         {HIGH_HEAT_THRESHOLD}°C")
    print(f"  Thermal Degradation Rate:    {TEMPERATURE_DEGRADATION_RATE}x per 10°C")
    
    print(f"\nGrading Thresholds:")
    print(f"  Grade A (High-Power):        >{GRADE_A_MIN}% SoH")
    print(f"  Grade B (Stationary):        {GRADE_B_MIN}-{GRADE_A_MIN}% SoH")
    print(f"  Grade C (Recycling):         <{GRADE_B_MIN}% SoH")
    
    print(f"\nFinancial Configuration:")
    print(f"  New Pack Reference Price:    ₹{NEW_PACK_PRICE:,}")
    print(f"  Min Recycling Value:         {MIN_RECYCLING_VALUE_PERCENTAGE}% of new price")
    print(f"  Grade A Multiplier:          {APPLICATION_MULTIPLIERS['Grade A']['multiplier']:.2f}")
    print(f"  Grade B Multiplier:          {APPLICATION_MULTIPLIERS['Grade B']['multiplier']:.2f}")
    print(f"  Grade C Multiplier:          {APPLICATION_MULTIPLIERS['Grade C']['multiplier']:.2f}")
    
    print(f"\nData Validation Ranges:")
    print(f"  RUL:                         {RUL_MIN}-{RUL_MAX} cycles")
    print(f"  Temperature:                 {TEMP_MIN}-{TEMP_MAX}°C")
    
    print("\n" + "="*70)
