#!/usr/bin/env python
"""
Quick Start Script for Endur-Cert
Demonstrates the full pipeline without the Streamlit dashboard
"""

import pandas as pd
from src.battery_engine import BatteryEngine
from src.certificate_generator import CertificateGenerator
from src.utils import validate_battery_data, create_industry_report
import os


def main():
    print("\n" + "="*70)
    print("🔋 ENDUR-CERT: Battery Blue Book & Certification Engine")
    print("="*70 + "\n")
    
    # Step 1: Load sample data
    print("📂 Step 1: Loading sample battery fleet data...")
    data_path = 'data/sample_fleet.csv'
    
    if not os.path.exists(data_path):
        print(f"   Creating sample data at {data_path}...")
        from src.utils import create_sample_csv
        create_sample_csv(data_path)
    
    df = pd.read_csv(data_path)
    print(f"   ✓ Loaded {len(df)} batteries\n")
    
    # Step 2: Validate data
    print("✓ Step 2: Validating battery data...")
    is_valid, message = validate_battery_data(df)
    if is_valid:
        print(f"   {message}\n")
    else:
        print(f"   ❌ {message}")
        return
    
    # Step 3: Initialize engine
    print("⚙️  Step 3: Initializing assessment engine...")
    engine = BatteryEngine(new_pack_price=250000)
    print("   ✓ Engine ready (Pack Price: ₹2,50,000)\n")
    
    # Step 4: Process fleet
    print("🔄 Step 4: Processing fleet assessment...")
    assessed_df = engine.process_fleet(df)
    print(f"   ✓ Assessed {len(assessed_df)} batteries\n")
    
    # Step 5: Generate summary
    print("📊 Step 5: Generating fleet summary...")
    summary = engine.get_fleet_summary(assessed_df)
    
    print("\n" + "─"*70)
    print("FLEET ASSESSMENT SUMMARY")
    print("─"*70)
    print(f"Total Batteries:              {summary['Total_Batteries']}")
    print(f"Total Residual Value:         ₹{summary['Total_Residual_Value_INR']:,.0f}")
    print(f"\nGrade Distribution:")
    print(f"  🟢 Grade A (High-Power):    {summary['Grade_A_Count']:3d} ({summary['Grade_A_Percentage']:5.1f}%)")
    print(f"  🟠 Grade B (Stationary):    {summary['Grade_B_Count']:3d} ({summary['Grade_B_Percentage']:5.1f}%)")
    print(f"  🔴 Grade C (Recycling):     {summary['Grade_C_Count']:3d} ({summary['Grade_C_Percentage']:5.1f}%)")
    print(f"\nHealth Metrics:")
    print(f"  Avg Health Score:           {summary['Avg_Health_Score_%']:.1f}%")
    print(f"  Avg Operating Temp:         {summary['Avg_Operating_Temp_C']:.1f}°C")
    print(f"  Value Range:                ₹{summary['Min_Residual_Value_INR']:,.0f} - ₹{summary['Max_Residual_Value_INR']:,.0f}")
    print("─"*70 + "\n")
    
    # Step 6: Show sample assessments
    print("📋 Step 6: Sample battery assessments:")
    print("─"*70)
    
    for grade in ['Grade A', 'Grade B', 'Grade C']:
        grade_df = assessed_df[assessed_df['Grade'] == grade]
        if len(grade_df) > 0:
            sample = grade_df.iloc[0]
            print(f"\n{grade} Example: {sample['Battery_ID']}")
            print(f"  Health Score:     {sample['Health_Score_%']:.1f}%")
            print(f"  RUL:              {sample['Predicted_RUL']:.0f} cycles")
            print(f"  Temp:             {sample['Avg_Operating_Temp']:.1f}°C")
            print(f"  Category:         {sample['Category']}")
            print(f"  Blue Book Value:  ₹{sample['Residual_Value_INR']:,.0f}")
            print(f"  Thermal Factor:   {sample['Temperature_Penalty_Factor']:.3f}")
    
    print("\n" + "─"*70 + "\n")
    
    # Step 7: Generate certificates
    print("📜 Step 7: Generating digital certificates...")
    cert_gen = CertificateGenerator(output_dir='certificates')
    
    # Generate for first 5 batteries as demo
    sample_for_cert = assessed_df.head(5)
    results = cert_gen.generate_batch_certificates(sample_for_cert, format='both')
    
    print(f"   ✓ Generated {len(results['pdf'])} PDF certificates")
    print(f"   ✓ Generated {len(results['json'])} JSON certificates")
    print(f"   Location: ./certificates/\n")
    
    # Step 8: Export full results
    print("💾 Step 8: Exporting results...")
    
    # Save CSV
    assessed_df.to_csv('assessment_results.csv', index=False)
    print("   ✓ CSV export: assessment_results.csv")
    
    # Save Excel
    try:
        assessed_df.to_excel('assessment_results.xlsx', index=False, sheet_name='Results')
        print("   ✓ Excel export: assessment_results.xlsx")
    except:
        print("   ⚠ Excel export skipped (openpyxl not installed)")
    
    # Generate text report
    report = create_industry_report(assessed_df, summary, 'fleet_assessment_report.txt')
    print("   ✓ Text report: fleet_assessment_report.txt\n")
    
    # Step 9: Ready for dashboard
    print("="*70)
    print("✨ Assessment Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review results in assessment_results.csv or .xlsx")
    print("2. Check digital passports in ./certificates/ folder")
    print("3. Launch interactive dashboard:")
    print("   $ streamlit run app.py")
    print("\n🚀 Happy Assessing!\n")


if __name__ == "__main__":
    main()
