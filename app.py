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
        <p style="color:#94a3b8; margin:8px 0 0 0;">In-Silico Clinical & Forensic Decision-Support Tool for Living Cases</p>
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
    st.markdown("### 🧪 Pharmacogenetic Target Panel")

    cyp2d6_profile = "CYP2D6 *1/*1 (Extensive / Normal Metabolizer)"
    cyp2c19_profile = "CYP2C19 *1/*1 (Normal Metabolizer)"
    oprm1_profile = "A118G Wild Type (Normal Sensitivity)"
    abcb1_profile = "Normal Excretion / Barrier"

    if input_method == "Interactive Panel Selection":
        cyp2d6_profile = st.selectbox(
            "CYP2D6 Gene",
            [
                "CYP2D6 *1/*1 (Extensive / Normal Metabolizer)",
                "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)",
                "CYP2D6 *1xN (Ultra-Rapid Metabolizer)",
            ],
        )

        cyp2c19_profile = st.selectbox(
            "CYP2C19 Gene",
            [
                "CYP2C19 *1/*1 (Normal Metabolizer)",
                "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)",
            ],
        )

        oprm1_profile = st.selectbox(
            "OPRM1 Receptor Gene",
            [
                "A118G Wild Type (Normal Sensitivity)",
                "A118G Variant / Mutated (High Sensitivity / Overdose Risk)",
            ],
        )

        abcb1_profile = st.selectbox(
            "ABCB1 / P-gp Transporter Gene",
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
                if "OPRM1" in full_text_file and "VARIANT" in full_text_file:
                    oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
            except Exception as e:
                st.warning(f"Using default parameters. Error: {e}")
        else:
            st.info("Please upload a file or default test profile will apply.")
            cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
            cyp2c19_profile = "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)"
            oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
            abcb1_profile = "Reduced Efflux (Enhanced Brain Concentration)"

st.markdown("---")
st.markdown("### 📊 Automated Forensic Evaluation Report")

is_poor_metabolizer = "Poor" in cyp2d6_profile or "Poor" in cyp2c19_profile
is_high_sensitivity = "Variant" in oprm1_profile

res_c1, res_c2, res_c3 = st.columns(3)
res_c1.metric("Metabolizer Phenotype", "Poor Metabolizer" if is_poor_metabolizer else "Normal Metabolizer")
res_c2.metric("Toxicity & Overdose Risk", "High Risk" if is_poor_metabolizer else "Low Risk / Safe")
res_c3.metric("Receptor Sensitivity", "High Sensitivity" if is_high_sensitivity else "Standard Sensitivity")

if is_poor_metabolizer and is_high_sensitivity:
    forensic_conclusion = (
        f"Forensic Conclusion for Case ({case_id}): The evaluated case demonstrates a critical genomic "
        f"concordance between poor hepatic metabolism and the opioid receptor variant. "
        f"This profile indicates severe impairment in drug clearance, rapid accumulation, "
        f"and heightened vulnerability to acute toxicity and overdose."
    )
    pdf_risk_summary = "High Toxicity Risk & Overdose Vulnerability"
else:
    forensic_conclusion = (
        f"Forensic Conclusion for Case ({case_id}): The genomic analysis shows a stable metabolic profile "
        f"with standard clearance rates and no strong indicators of high toxicity risk under standard dosages."
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

def generate_pdf_report(case, c_type, c2d6, c2c19, oprm, ab, conclusion_text, status_risk):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 15)
    p.drawString(40, height - 40, "In-Silico Forensic Pharmacogenomics & Toxicology Report")

    p.setFont("Helvetica", 10)
    p.drawString(40, height - 65, f"Case ID: {case} | Date: 2026-10-01")
    p.drawString(40, height - 85, f"Case Type: {c_type}")

    p.setLineWidth(1)
    p.line(40, height - 95, width - 40, height - 95)

    # Panel Section
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 120, "Dynamic Genomic Profile & Analytical Panel:")
    
    p.setFont("Helvetica", 9)
    y_pos = 145
    for item in [f"CYP2D6: {c2d6}", f"CYP2C19: {c2c19}", f"OPRM1: {oprm}", f"ABCB1: {ab}"]:
        p.drawString(55, height - y_pos, f"- {item}")
        y_pos += 20

    # Evaluation Section
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 245, "Clinical & Forensic Case Evaluation:")
    
    p.setFont("Helvetica", 9)
    text_obj = p.beginText(55, height - 270)
    text_obj.setLeading(14)
    for line in [conclusion_text[i:i+90] for i in range(0, len(conclusion_text), 90)]:
        text_obj.textLine(line)
    p.drawText(text_obj)

    # Risk Assessment
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, height - 370, f"Overall Forensic Risk Assessment: {status_risk}")

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
    oprm1_profile,
    abcb1_profile,
    forensic_conclusion,
    pdf_risk_summary,
)

st.download_button(
    label="📥 Download Clean Official PDF Report",
    data=pdf_data,
    file_name=f"Forensic_Report_{case_id}.pdf",
    mime="application/pdf",
)

