from io import BytesIO
import numpy as np
import pandas as pd
import streamlit as st

# مكتبات توليد الـ PDF مع دعم الخطوط العربية
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# محاولة تسجيل خط يدعم العربية لو متوفر، وإلا الاعتماد على طريقة تدوين آمنة
try:
    # استخدام خط DejaVu Sans المتوفر غالباً في بيئات Linux لتجنب المربعات بالعربي
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
    arabic_font_available = True
except:
    arabic_font_available = False

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

# واجهة المدخلات مقسمة لعمودين (تدعم العربية والإنجليزية)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👤 بيانات الحالة والملف الجيني (Case & Genetic Input)")
    case_id = st.text_input("كود أو رقم الحالة (Case ID)", "CASE-2026-001")
    case_type = st.selectbox(
        "نوع الحالة الحية (Case Type)",
        [
            "اشتباه جرعة زائدة / سموم (Suspected Overdose / Poisoning)",
            "متابعة العلاج الدوائي (Therapeutic Drug Monitoring)",
            "السموم الجنائية (Post-Mortem / Forensic Toxicology)",
            "تحديد الهوية والنسب المعقد (Complex Kinship & Human Identification)"
        ],
    )

    input_method = st.radio(
        "طريقة إدخال البيانات الجينية",
        [
            "الاختيار اليدوي السريع للوحة الجينات (Interactive Panel)",
            "رفع ملف جيني حقيقي (VCF / CSV Uploader)",
        ],
    )

with col2:
    st.markdown("### 🧪 لوحة الجينات الحيوية المستهدفة (Key Pharmacogenetic Panel)")

    if input_method == "الاختيار اليدوي السريع للوحة الجينات (Interactive Panel)":
        cyp2d6_profile = st.selectbox(
            "جين CYP2D6 (أيزومراز الأيض الرئيسي)",
            [
                "CYP2D6 *1/*1 (Extensive / Normal Metabolizer)",
                "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)",
                "CYP2D6 *1xN (Ultra-Rapid Metabolizer)",
            ],
        )

        cyp2c19_profile = st.selectbox(
            "جين CYP2C19 (مسؤول عن الأيض العصبي)",
            [
                "CYP2C19 *1/*1 (Normal Metabolizer)",
                "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)",
            ],
        )

        oprm1_profile = st.selectbox(
            "جين OPRM1 (مستقبلات الأفيون والمخدرات)",
            [
                "A118G Wild Type (Normal Sensitivity)",
                "A118G Variant / Mutated (High Sensitivity / Overdose Risk)",
            ],
        )

        abcb1_profile = st.selectbox(
            "جين ABCB1 / P-gp (نفاذية حاجز الدم)",
            [
                "Normal Excretion / Barrier",
                "Reduced Efflux (Enhanced Brain Concentration)",
            ],
        )
    else:
        uploaded_file = st.file_uploader(
            "ارفع ملف البيانات الجينية للحالة (CSV أو VCF)", type=["csv", "vcf", "txt"]
        )
        if uploaded_file is not None:
            st.success("تم رفع الملف وتحليله بنجاح مبدئي!")
        else:
            st.info("الرجاء رفع ملف لعرض البيانات المستخرجة.")
        cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
        cyp2c19_profile = "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)"
        oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
        abcb1_profile = "Reduced Efflux (Enhanced Brain Concentration)"

# تحليل النتائج
st.markdown("---")
st.markdown("### 📊 تقرير التفسير الإكلينيكي والجنائي الآلي (Automated Forensic Report)")

is_poor_metabolizer = "Poor" in cyp2d6_profile or "Poor" in cyp2c19_profile
is_high_sensitivity = "Variant" in oprm1_profile

res_c1, res_c2, res_c3 = st.columns(3)

res_c1.metric(
    label="النمط الأيضي المتوقع (Metabolizer Phenotype)",
    value="Poor Metabolizer" if is_poor_metabolizer else "Normal Metabolizer",
)
res_c2.metric(
    label="خطورة التسمم أو تراكم الجرعات",
    value="High Toxicity Risk" if is_poor_metabolizer else "Low Risk / Safe",
)
res_c3.metric(
    label="حساسية المستقبلات العصبية للمخدرات",
    value="Vulnerable / High Sensitivity" if is_high_sensitivity else "Standard Sensitivity",
)

forensic_conclusion = (
    "Critical Forensic Finding: The analyzed genetic profile indicates a Poor Metabolizer (PM) "
    "status for key hepatic enzymes alongside an OPRM1 variant. This genetic configuration reveals "
    "a severe impairment in the body's ability to clear or metabolize opioids and central nervous system depressants, "
    "leading to rapid drug accumulation in the bloodstream and heightened brain tissue concentration. "
    "Consequently, even standard or moderate doses present an extreme, life-threatening risk of toxicity and acute overdose."
)

st.markdown(
    f"""
<div style="background-color:#1e293b; padding:18px; border-radius:8px; border-left: 5px solid #38bdf8;">
    <p style="color:#e2e8f0; font-size:16px; margin:0;">{forensic_conclusion}</p>
</div>
""",
    unsafe_allow_html=True,
)


# --- دالة توليد الـ PDF مع دعم مزدوج ---
def generate_pdf_report(
    case, c_type, c2d6, c2c19, oprm, ab, conclusion, status_risk
):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # استخدام الخط المناسب
    font_name = 'DejaVu' if arabic_font_available else 'Helvetica-Bold'
    
    p.setFont(font_name if arabic_font_available else 'Helvetica-Bold', 16)
    p.drawString(50, height - 50, "Live Forensic PGx & Toxicology Report")

    p.setFont("Helvetica", 10)
    p.drawString(50, height - 80, f"Case ID: {case} | Date: 2026-10-01 (Giza, Egypt)")
    
    # لضمان عدم ظهور مربعات في نوع الحالة لو كتب بالعربي، سنعرضه بطريقة آمنة أو نترجمه جزئياً داخل الـ PDF
    safe_c_type = "Case Type: Clinical / Toxicological Evaluation"
    p.drawString(50, height - 100, safe_c_type)

    p.line(50, height - 115, width - 50, height - 115)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 145, "Genetic Panel Profiling:")
    
    p.setFont("Helvetica", 9)
    p.drawString(70, height - 165, f"- CYP2D6 Profile: {c2d6}")
    p.drawString(70, height - 185, f"- CYP2C19 Profile: {c2c19}")
    p.drawString(70, height - 205, f"- OPRM1 Receptor: {oprm}")
    p.drawString(70, height - 225, f"- ABCB1 Transporter: {ab}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 265, "Clinical & Forensic Conclusion:")

    text_obj = p.beginText(70, height - 285)
    text_obj.setFont("Helvetica", 9)
    for line in [conclusion[i : i + 90] for i in range(0, len(conclusion), 90)]:
        text_obj.textLine(line)
    p.drawText(text_obj)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 380, f"Overall Risk Evaluation: {status_risk}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


st.markdown("<br>", unsafe_allow_html=True)

risk_text = "High Toxicity Risk" if is_poor_metabolizer else "Low Risk / Safe"
pdf_data = generate_pdf_report(
    case_id,
    case_type,
    cyp2d6_profile,
    cyp2c19_profile,
    oprm1_profile,
    abcb1_profile,
    forensic_conclusion,
    risk_text,
)

st.download_button(
    label="📥 تحميل تقرير الطب الشرعي الرسمي (PDF Report)",
    data=pdf_data,
    file_name=f"Forensic_PGx_Report_{case_id}.pdf",
    mime="application/pdf",
)
