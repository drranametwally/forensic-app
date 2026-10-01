from io import BytesIO
import pandas as pd
import streamlit as st

# مكتبات توليد الـ PDF الآمنة
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# إعدادات الصفحة
st.set_page_config(
    page_title="Live Forensic PGx & Toxicology Suite", page_icon="🧬", layout="wide"
)

# عنوان التطبيق وتصميمه
st.markdown(
    """
    <div style="background-color:#0f172a; padding:25px; border-radius:12px; text-align:center;">
        <h1 style="color:#38bdf8; margin:0;">🧬 Live Forensic Pharmacogenetics & Toxicology Suite</h1>
        <p style="color:#94a3b8; margin:8px 0 0 0;">In-Silico Clinical & Forensic Decision-Support Tool (Enhanced with CYP3A4 & Antidepressant Pathways)</p>
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👤 بيانات الحالة وملف الجينوم (Case & Genetic Input)")
    case_id = st.text_input("Case ID", "CASE-2026-001")
    
    case_type_display = st.selectbox(
        "Case Type",
        [
            "Suspected Overdose / Poisoning",
            "Addiction & Psychiatric TDM Evaluation",
            "Forensic Kinship & Identification",
            "Routine Toxicology Screening"
        ],
    )

    input_method = st.radio(
        "Genetic Input Method",
        [
            "Interactive Panel Selection",
            "Upload Genomic File (VCF / CSV / TXT)",
        ],
    )

with col2:
    st.markdown("### 🧪 Expanded Pharmacogenetic & Toxicological Panel")

    cyp2d6_profile = "CYP2D6 *1/*1 (Extensive / Normal)"
    cyp2c19_profile = "CYP2C19 *1/*1 (Normal)"
    cyp3a4_profile = "CYP3A4 *1/*1 (Normal Hepatic Clearance)"
    antidepressant_profile = "CYP2C9 / Antidepressant Pathway: Normal Metabolizer"
    oprm1_profile = "A118G Wild Type (Normal Sensitivity)"
    abcb1_profile = "Normal Excretion / Barrier"

    if input_method == "Interactive Panel Selection":
        cyp2d6_profile = st.selectbox(
            "CYP2D6 Gene (Opioids & Psychiatric Drugs)",
            [
                "CYP2D6 *1/*1 (Extensive / Normal)",
                "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)",
                "CYP2D6 *1xN (Ultra-Rapid Metabolizer)",
            ],
        )

        cyp2c19_profile = st.selectbox(
            "CYP2C19 Gene (Sedatives & SSRIs)",
            [
                "CYP2C19 *1/*1 (Normal)",
                "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)",
            ],
        )

        cyp3a4_profile = st.selectbox(
            "CYP3A4 Gene (Major Drug & Toxin Metabolism - Over 50% drugs)",
            [
                "CYP3A4 *1/*1 (Normal Hepatic Clearance)",
                "CYP3A4 *22 / Reduced Function (Slow Clearance & Toxicity Risk)",
            ],
        )

        antidepressant_profile = st.selectbox(
            "Antidepressant & Psychiatric Pathway (CYP2C9 / CYP2C19 interaction)",
            [
                "CYP2C9/2C19 Normal Pathway (Standard Elimination)",
                "Compromised Antidepressant Clearance (High Accumulation Risk)",
            ],
        )

        oprm1_profile = st.selectbox(
            "OPRM1 Receptor Gene (Opioid & Narcotic Sensitivity)",
            [
                "A118G Wild Type (Normal Sensitivity)",
                "A118G Variant / Mutated (High Sensitivity / Overdose Risk)",
            ],
        )

        abcb1_profile = st.selectbox(
            "ABCB1 / P-gp Transporter Gene (Blood-Brain Barrier)",
            [
                "Normal Excretion / Barrier",
                "Reduced Efflux (Enhanced Brain Concentration)",
            ],
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload Genomic File", type=["csv", "vcf", "txt"]
        )
        if uploaded_file is not None:
            try:
                string_data = uploaded_file.getvalue().decode("utf-8")
                st.success("Genomic file successfully loaded and parsed!")
                full_text_file = string_data.upper()
                if "CYP2D6" in full_text_file and "*4" in full_text_file:
                    cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
                if "CYP3A4" in full_text_file and "REDUCED" in full_text_file:
                    cyp3a4_profile = "CYP3A4 *22 / Reduced Function (Slow Clearance & Toxicity Risk)"
                if "OPRM1" in full_text_file and "VARIANT" in full_text_file:
                    oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
            except Exception as e:
                st.warning(f"Using default parameters. Error: {e}")
        else:
            st.info("Please upload a file or default test profile will apply.")
            cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
            cyp2c19_profile = "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)"
            cyp3a4_profile = "CYP3A4 *22 / Reduced Function (Slow Clearance & Toxicity Risk)"
            antidepressant_profile = "Compromised Antidepressant Clearance (High Accumulation Risk)"
            oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
            abcb1_profile = "Reduced Efflux (Enhanced Brain Concentration)"

st.markdown("---")
st.markdown("### 📊 Automated Forensic Evaluation Report")

is_poor_metabolizer = (
    "Poor" in cyp2d6_profile or 
    "Poor" in cyp2c19_profile or 
    "Reduced" in cyp3a4_profile or
    "Compromised" in antidepressant_profile
)
is_high_sensitivity = "Variant" in oprm1_profile

res_c1, res_c2, res_c3 = st.columns(3)
res_c1.metric("Metabolic Status", "Compromised / Slow" if is_poor_metabolizer else "Normal Metabolizer")
res_c2.metric("Toxicity & Overdose Risk", "High Risk" if is_poor_metabolizer else "Low Risk / Safe")
res_c3.metric("Receptor Sensitivity", "High Sensitivity" if is_high_sensitivity else "Standard Sensitivity")

if is_poor_metabolizer and is_high_sensitivity:
    forensic_conclusion = (
        f"Forensic Conclusion for Case ({case_id}): The expanded genomic panel indicates critical impairments across "
        f"major hepatic pathways (including CYP3A4 and psychiatric drug metabolism) combined with OPRM1 receptor variant. "
        f"This multigene risk profile strongly points toward profound drug/toxin clearance failure, severe psychiatric or narcotic accumulation, "
        f"and extreme vulnerability to acute toxicity and overdose."
    )
    pdf_risk_summary = "High Toxicity Risk & Overdose Vulnerability"
else:
    forensic_conclusion = (
        f"Forensic Conclusion for Case ({case_id}): The genomic analysis across extended metabolic pathways shows a stable profile "
        f"with standard clearance rates and no strong indicators of high systemic toxicity risk."
    )
    pdf_risk_summary = "Stable / Standard Toxicity Risk"

st.markdown(
    f"""
<div style="background-color:#1e293b; padding:18px; border-radius:8px; border-left: 5px solid #38bdf8;">
    <p style="color:#e2e8f0; font-size:16px; margin:0;">{forensic_conclusion}</p>
</div>
""",
    unsafe_allow_html=True,
)

def generate_pdf_report(case, c_type, c2d6, c2c19, c3a4, antidep, oprm, ab, conclusion_text, status_risk):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, height - 35, "In-Silico Forensic Pharmacogenomics & Toxicology Report")

    p.setFont("Helvetica", 9)
    p.drawString(40, height - 55, f"Case ID: {case} | Date: 2026-10-01")
    p.drawString(40, height - 72, f"Case Type: {c_type}")

    p.setLineWidth(1)
    p.line(40, height - 80, width - 40, height - 80)

    # Panel Section
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, height - 100, "Expanded Genomic Profile & Analytical Panel:")
    
    p.setFont("Helvetica", 8.5)
    y_pos = 120
    for item in [f"CYP2D6: {c2d6}", f"CYP2C19: {c2c19}", f"CYP3A4: {c3a4}", f"Antidepressant Pathway: {antidep}", f"OPRM1: {oprm}", f"ABCB1: {ab}"]:
        p.drawString(55, height - y_pos, f"- {item}")
        y_pos += 16

    # Evaluation Section
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, height - 225, "Clinical & Forensic Case Evaluation:")
    
    p.setFont("Helvetica", 8.5)
    text_obj = p.beginText(55, height - 245)
    text_obj.setLeading(13)
    for line in [conclusion_text[i:i+95] for i in range(0, len(conclusion_text), 95)]:
        text_obj.textLine(line)
    p.drawText(text_obj)

    # Risk Assessment
    p.setFont("Helvetica-Bold", 10.5)
    p.drawString(40, height - 335, f"Overall Forensic Risk Assessment: {status_risk}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

st.markdown("<br>", unsafe_allow_html=True)

pdf_data = generate_pdf_report(
    case_id,
    case_type_display,
    cyp2d6_profile,
    cyp2c19_profile,
    cyp3a4_profile,
    antidepressant_profile,
    oprm1_profile,
    abcb1_profile,
    forensic_conclusion,
    pdf_risk_summary,
)

st.download_button(
    label="📥 Download Expanded Official PDF Report",
    data=pdf_data,
    file_name=f"Expanded_Forensic_Report_{case_id}.pdf",
    mime="application/pdf",
)
