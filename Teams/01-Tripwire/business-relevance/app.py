"""
Endur-Cert Streamlit Dashboard
Interactive web interface for battery fleet assessment and certification
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from pathlib import Path

# Import our modules
from src.battery_engine import BatteryEngine
from src.certificate_generator import CertificateGenerator


# Page configuration
st.set_page_config(
    page_title="Endur-Cert: Battery Blue Book & Certification Engine",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2C3E50;
        margin-bottom: 30px;
    }
    .grade-a { color: #27AE60; font-weight: bold; }
    .grade-b { color: #F39C12; font-weight: bold; }
    .grade-c { color: #E74C3C; font-weight: bold; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'assessed_df' not in st.session_state:
    st.session_state.assessed_df = None
if 'fleet_summary' not in st.session_state:
    st.session_state.fleet_summary = None
if 'engine' not in st.session_state:
    st.session_state.engine = BatteryEngine()
if 'cert_gen' not in st.session_state:
    st.session_state.cert_gen = CertificateGenerator(output_dir='certificates')


# ============================================================================
# MAIN TITLE & INTRODUCTION
# ============================================================================

st.markdown("""
<h1 style='text-align: center; color: #2C3E50;'>
    🔋 ENDUR-CERT
</h1>
<h3 style='text-align: center; color: #34495E;'>
    The Battery "Blue Book" & Certification Engine
</h3>
<p style='text-align: center; color: #7F8C8D; font-size: 14px;'>
    Transform RUL into Financial Value. Turn Second-Life into Sustainable Business.
</p>
""", unsafe_allow_html=True)

st.divider()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    st.header("🚀 Navigation")
    page = st.radio(
        "Select a page:",
        ["📊 Dashboard", "📤 Upload & Assess", "📜 Certificates", "ℹ️ About"]
    )


# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================

if page == "📊 Dashboard":
    st.header("Fleet Assessment Dashboard")
    
    if st.session_state.assessed_df is None or st.session_state.assessed_df.empty:
        st.info(
            "📌 No fleet data loaded yet. Please upload a CSV file on the **Upload & Assess** page "
            "containing Battery_ID, Predicted_RUL, and Average_Operating_Temperature columns."
        )
    else:
        df = st.session_state.assessed_df
        summary = st.session_state.fleet_summary
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Batteries",
                f"{summary['Total_Batteries']}",
                delta=None
            )
        
        with col2:
            st.metric(
                "Total Residual Value",
                f"₹{summary['Total_Residual_Value_INR']:,.0f}",
                delta="Fleet valuation"
            )
        
        with col3:
            st.metric(
                "Avg Health Score",
                f"{summary['Avg_Health_Score_%']:.1f}%",
                delta="SoH"
            )
        
        with col4:
            st.metric(
                "Avg Operating Temp",
                f"{summary['Avg_Operating_Temp_C']:.1f}°C",
                delta="Thermal profile"
            )
        
        st.divider()
        
        # Grade Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of grades
            grade_counts = df['Grade'].value_counts()
            grade_counts = grade_counts.reindex(['Grade A', 'Grade B', 'Grade C'], fill_value=0)
            color_discrete_map = {'Grade A': '#27AE60', 'Grade B': '#FFD700', 'Grade C': '#E74C3C'}
            
            fig_pie = px.pie(
                values=grade_counts.values,
                names=grade_counts.index,
                color=grade_counts.index,
                color_discrete_map=color_discrete_map,
                title="Battery Grade Distribution",
                hole=0.4
            )
            fig_pie.update_traces(textposition='inside', textinfo='label+percent')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart of value by grade
            grade_value = df.groupby('Grade')['Residual_Value_INR'].sum()
            grade_value = grade_value.reindex(['Grade A', 'Grade B', 'Grade C'], fill_value=0)
            color_discrete_map = {'Grade A': '#27AE60', 'Grade B': '#FFD700', 'Grade C': '#E74C3C'}
            
            fig_bar = px.bar(
                x=grade_value.index,
                y=grade_value.values,
                color=grade_value.index,
                color_discrete_map=color_discrete_map,
                title="Total Residual Value by Grade",
                labels={'x': 'Grade', 'y': 'Value (₹)'}
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.divider()
        
        # Health Score Distribution
        fig_health = px.histogram(
            df,
            x='Health_Score_%',
            nbins=20,
            title="Health Score Distribution Across Fleet",
            labels={'Health_Score_%': 'Health Score (%)'},
            color_discrete_sequence=['#3498DB']
        )
        fig_health.add_vline(x=summary['Avg_Health_Score_%'], 
                            line_dash="dash", line_color="red",
                            annotation_text=f"Mean: {summary['Avg_Health_Score_%']:.1f}%")
        st.plotly_chart(fig_health, use_container_width=True)
        
        st.divider()
        
        # Grade Breakdown Stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🟢 Grade A - High-Power Mobility")
            st.write(f"**Count:** {summary['Grade_A_Count']} ({summary['Grade_A_Percentage']}%)")
            st.write(f"**Applications:** e-Rickshaws, Last-Mile Delivery, Two-Wheelers")
            grade_a_value = df[df['Grade'] == 'Grade A']['Residual_Value_INR'].sum()
            st.write(f"**Total Value:** ₹{grade_a_value:,.0f}")
        
        with col2:
            st.subheader("🟡 Grade B - Stationary Storage")
            st.write(f"**Count:** {summary['Grade_B_Count']} ({summary['Grade_B_Percentage']}%)")
            st.write(f"**Applications:** Home UPS, Solar Microgrids, Telecom Backup")
            grade_b_value = df[df['Grade'] == 'Grade B']['Residual_Value_INR'].sum()
            st.write(f"**Total Value:** ₹{grade_b_value:,.0f}")
        
        with col3:
            st.subheader("🔴 Grade C - Resource Recovery")
            st.write(f"**Count:** {summary['Grade_C_Count']} ({summary['Grade_C_Percentage']}%)")
            st.write(f"**Applications:** Lithium Reclamation, Recycling, Refurbishment")
            grade_c_value = df[df['Grade'] == 'Grade C']['Residual_Value_INR'].sum()
            st.write(f"**Total Value:** ₹{grade_c_value:,.0f}")
        
        st.divider()
        
        # Temperature vs Health scatter
        fig_scatter = px.scatter(
            df,
            x='Avg_Operating_Temp',
            y='Health_Score_%',
            color='Grade',
            size='Residual_Value_INR',
            hover_data=['Battery_ID'],
            title="Health Score vs Operating Temperature (bubble size = residual value)",
            color_discrete_map={
                'Grade A': '#27AE60',
                'Grade B': '#FFD700',
                'Grade C': '#E74C3C'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)


# ============================================================================
# PAGE 2: UPLOAD & ASSESS
# ============================================================================

elif page == "📤 Upload & Assess":
    st.header("Battery Fleet Assessment Engine")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Step 1: Upload Your Battery Data")
        st.write("""
        Upload a CSV file with the following columns:
        - **Battery_ID**: Unique identifier (e.g., "BATT_001")
        - **Predicted_RUL**: Remaining Useful Life in cycles (e.g., 2500)
        - **Average_Operating_Temperature**: Avg temp in Celsius (e.g., 38.5)
        """)
    
    with col2:
        st.subheader("📋 Sample Format")
        sample_df = pd.DataFrame({
            'Battery_ID': ['BATT_001', 'BATT_002', 'BATT_003'],
            'Predicted_RUL': [2800, 1950, 500],
            'Average_Operating_Temperature': [28.5, 42.0, 35.0]
        })
        st.dataframe(sample_df, use_container_width=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    
    with col2:
        new_pack_price = st.number_input(
            "New Battery Pack Price (₹)",
            value=250000,
            min_value=100000,
            step=10000,
            help="Reference price for a brand-new battery pack"
        )
    
    if uploaded_file is not None:
        try:
            # Read CSV
            input_df = pd.read_csv(uploaded_file)
            
            # Validate columns
            required_cols = ['Battery_ID', 'Predicted_RUL', 'Average_Operating_Temperature']
            missing_cols = [col for col in required_cols if col not in input_df.columns]
            
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            else:
                st.success(f"✅ Loaded {len(input_df)} batteries")
                
                st.divider()
                st.subheader("Input Data Preview")
                st.dataframe(input_df, use_container_width=True)
                
                # Assess button
                if st.button("🚀 Run Assessment", key="assess_button", type="primary"):
                    with st.spinner("🔄 Assessing fleet..."):
                        # Re-initialize engine with new price
                        st.session_state.engine = BatteryEngine(new_pack_price=new_pack_price)
                        
                        # Process fleet
                        st.session_state.assessed_df = st.session_state.engine.process_fleet(input_df)
                        st.session_state.fleet_summary = st.session_state.engine.get_fleet_summary(
                            st.session_state.assessed_df
                        )
                    
                    st.success("✅ Assessment complete!")
                    st.info("📊 Check the Dashboard page to view results and analytics.")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    st.divider()
    st.subheader("Assessment Logic")
    
    with st.expander("📖 How the Engine Works", expanded=False):
        st.markdown("""
        ### The Endur-Cert Pipeline
        
        **1️⃣ Health Score Calculation**
        - Converts Remaining Useful Life (RUL) to State-of-Health (SoH) percentage
        - Formula: `SoH = (RUL / 3000) × 100`
        - LFP batteries have a standard life of 3,000 cycles
        
        **2️⃣ Thermal Audit**
        - Applies "Heat Tax" or "Cooling Bonus" based on operating temperature
        - LFP degradation roughly doubles for every 10°C above standard (25°C)
        - High-heat conditions (>35°C, typical in India) reduce battery lifespan estimates
        
        **3️⃣ Grade Classification**
        - **Grade A (>85% SoH)**: High-Power Mobility (e-Rickshaws, delivery)
        - **Grade B (70-85% SoH)**: Stationary Storage (UPS, solar microgrids)
        - **Grade C (<70% SoH)**: Resource Recovery (recycling, refurbishment)
        
        **4️⃣ Blue Book Valuation**
        - Calculates fair market price in Rupees for second-life deployment
        - Formula: `Value = (New Price × SoH%) × Multiplier × Temperature Factor`
        - Provides instant buyback quotes for fleet operators
        
        **5️⃣ Digital Passport**
        - Creates a "Passport" with health grade, best-fit jobs, and valuation
        - Solves trust problem in used battery market
        """)


# ============================================================================
# PAGE 3: CERTIFICATES
# ============================================================================

elif page == "📜 Certificates":
    st.header("Digital Battery Passports")
    
    if st.session_state.assessed_df is None or st.session_state.assessed_df.empty:
        st.info(
            "📌 No assessment data available. Please complete an assessment on the "
            "**Upload & Assess** page first."
        )
    else:
        df = st.session_state.assessed_df
        
        st.subheader("Step 1: Select Batteries for Certification")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Select by grade
            grade_filter = st.multiselect(
                "Filter by Grade:",
                options=['Grade A', 'Grade B', 'Grade C'],
                default=['Grade A', 'Grade B', 'Grade C'],
                key="grade_filter"
            )
            filtered_df = df[df['Grade'].isin(grade_filter)]
        
        with col2:
            # Select specific batteries
            battery_options = {
                f"{row['Battery_ID']} ({row['Grade']} - {row['Health_Score_%']:.1f}% SoH)": row['Battery_ID']
                for _, row in filtered_df.iterrows()
            }
            
            selected_batteries = st.multiselect(
                "Or select specific batteries:",
                options=list(battery_options.keys()),
                key="battery_filter"
            )
        
        # Filter to selected batteries if any
        if selected_batteries:
            selected_ids = [battery_options[b] for b in selected_batteries]
            df_to_certify = df[df['Battery_ID'].isin(selected_ids)]
        else:
            df_to_certify = filtered_df
        
        st.write(f"**Selected {len(df_to_certify)} batteries for certification**")
        
        st.divider()
        
        # Certificate format selection
        st.subheader("Step 2: Choose Certificate Format")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            generate_pdf = st.checkbox("📄 PDF Certificates", value=True)
        with col2:
            generate_json = st.checkbox("📋 JSON Certificates", value=True)
        with col3:
            st.write("")  # Spacing
        
        if generate_pdf or generate_json:
            if st.button("🏆 Generate Certificates", type="primary"):
                with st.spinner("⏳ Generating certificates..."):
                    format_choice = 'both' if (generate_pdf and generate_json) else (
                        'pdf' if generate_pdf else 'json'
                    )
                    
                    results = st.session_state.cert_gen.generate_batch_certificates(
                        df_to_certify,
                        format=format_choice
                    )
                
                st.success("✅ All certificates generated!")
                
                # Display results
                if results['pdf']:
                    st.subheader("📄 PDF Certificates Generated")
                    for pdf_path in results['pdf']:
                        st.write(f"✓ {Path(pdf_path).name}")
                
                if results['json']:
                    st.subheader("📋 JSON Certificates Generated")
                    for json_path in results['json']:
                        st.write(f"✓ {Path(json_path).name}")
                
                st.info("🗂️ All files saved to the `certificates/` directory")
        
        st.divider()
        
        # Sample certificate display
        if len(df_to_certify) > 0 and st.checkbox("👁️ Preview Sample Certificate"):
            sample_battery = df_to_certify.iloc[0].to_dict()
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader(f"Battery ID: {sample_battery['Battery_ID']}")
                
                grade = sample_battery['Grade']
                grade_colors = {'Grade A': '🟢', 'Grade B': '🟠', 'Grade C': '🔴'}
                
                st.markdown(f"### {grade_colors[grade]} {grade}")
                st.write(f"**{sample_battery['Category']}**")
                
                st.metric("Health Score", f"{sample_battery['Health_Score_%']:.1f}%")
                st.metric("Predicted RUL", f"{sample_battery['Predicted_RUL']:.0f} cycles")
                st.metric("Operating Temp", f"{sample_battery['Avg_Operating_Temp']:.1f}°C")
            
            with col2:
                st.subheader("Valuation & Applications")
                
                st.markdown(f"### ₹ {sample_battery['Residual_Value_INR']:,.0f}")
                st.write("**Residual Blue Book Value**")
                
                st.divider()
                
                st.write("**Certified Applications:**")
                for app in sample_battery['Applications'].split(', '):
                    st.write(f"• {app}")
                
                st.divider()
                
                st.write("**Thermal Assessment:**")
                st.info(sample_battery['Temperature_Assessment'])


# ============================================================================
# PAGE 4: ABOUT
# ============================================================================

elif page == "ℹ️ About":
    st.header("About Endur-Cert")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## The Problem We Solve
        
        India's EV revolution is creating millions of second-life batteries—but the used battery 
        market lacks **trust and transparency**. How do fleet operators know what battery is truly 
        worth? How can recyclers identify high-value refurbishment candidates?
        
        **Endur-Cert** transforms battery prediction data into a **business-ready valuation tool**.
        
        ---
        
        ## Core Philosophy
        
        A battery's life is **elastic**:
        - 80% health ≠ **end of life**
        - 80% health = **beginning of second career**
        
        By creating a **"Digital Battery Passport,"** we solve the trust problem in the used battery market.
        """)
    
    with col2:
        st.metric("Standard LFP Life", "3,000 cycles")
        st.metric("Thermal Impact", "2x per 10°C")
        st.metric("Grade Categories", "3 paths")
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🟢 Grade A: High-Power Mobility")
        st.write("""
        **Health Score:** >85% SoH
        
        **Best For:**
        • e-Rickshaws
        • Last-Mile Delivery
        • Two-Wheeler Charging Stations
        
        **Why:** Still have the "punch" for vehicle acceleration
        """)
    
    with col2:
        st.subheader("🟠 Grade B: Stationary Storage")
        st.write("""
        **Health Score:** 70-85% SoH
        
        **Best For:**
        • Home UPS Systems
        • Solar Microgrids
        • Telecom Backup
        • Renewable Integration
        
        **Why:** Perfect for stable, low-stress backup roles
        """)
    
    with col3:
        st.subheader("🔴 Grade C: Resource Recovery")
        st.write("""
        **Health Score:** <70% SoH
        
        **Best For:**
        • Lithium Reclamation
        • Phosphate Recovery
        • Advanced Recycling
        
        **Why:** Recover raw materials for new battery production
        """)
    
    st.divider()
    
    st.markdown("""
    ## The "Blue Book" Valuation Formula
    
    $$Value = (\\text{New Pack Price} \\times \\text{SoH\\%}) \\times \\text{Application Multiplier} \\times \\text{Thermal Factor}$$
    
    This gives fleet owners an immediate **buyback quote**, allowing them to:
    1. Trade in old LCV batteries
    2. Offset the cost of new ones
    3. Achieve circular economy benefits
    
    ---
    
    ## Technical Stack
    
    | Component | Technology |
    |-----------|-----------|
    | **Backend** | Python + Pandas |
    | **Diagnostics** | Rule-based scoring engine |
    | **Frontend** | Streamlit Dashboard |
    | **Certificates** | PDF + JSON |
    | **Deployment** | Cloud-ready Python app |
    
    ---
    
    ## Key Features
    
    ✅ **Fast Assessment:** Process entire fleets in seconds
    
    ✅ **Temperature-Aware:** Accounts for Indian climate conditions
    
    ✅ **Business-Ready:** Immediate market valuations
    
    ✅ **Transparent:** Digital passports for every battery
    
    ✅ **Scalable:** Handles fleets of any size
    """)
    
    st.divider()
    
    st.subheader("🚀 Why Endur-Cert Wins")
    
    st.write("""
    While other teams provide a **"math result,"** we provide a **"market solution."**
    
    1. **Indian Climate Context:** By incorporating average_temperature, we demonstrate 
       deep understanding of EV degradation in India's high-heat conditions.
    
    2. **Business Relevance:** By providing "Blue Book" valuations, we prove immediate 
       commercial applicability and scalability.
    
    3. **Trust & Transparency:** Digital passports solve the structural problem of 
       information asymmetry in the used battery market.
    
    4. **Second-Life Optimization:** We don't just predict degradation—we match batteries 
       to their ideal second careers.
    """)


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #95A5A6; font-size: 12px;'>
    <p>Endur-Cert v1.0 | Battery Blue Book & Certification Engine</p>
    <p>Built for India's EV Revolution | 🇮🇳</p>
</div>
""", unsafe_allow_html=True)
