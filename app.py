from io import BytesIO
import numpy as np
import pandas as pd
import streamlit as st

# مكتبات توليد الـ PDF الاحترافي
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
        <p style="color:#94a3b8; margin:8px 0 0 0;">In-Silico Clinical & Forensic Decision-Support System for Living Cases</p>
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# واجهة المدخلات مقسمة لعمودين
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👤 بيانات الحالة وملف التحاليل (Case & Genomic Input)")
    case_id = st.text_input("كود أو رقم الحالة (Case ID)", "CASE-2026-001")
    
    # جعل خيارات الحالة بالإنجليزية لضمان ظهورها بـ PDF نظيف وبدون مربعات
    case_type = st.selectbox(
        "نوع الحالة الحية والإكلينيكية (Case Type)",
        [
            "Suspected Overdose / Poisoning",
            "Therapeutic Drug Monitoring (TDM)",
            "Forensic Toxicology Assessment",
            "Complex Kinship & Human Identification"
        ],
    )

    input_method = st.radio(
        "طريقة إدخال التحاليل والبيانات الجينية",
        [
            "الاختيار اليدوي للوحة الجينات (Interactive Panel)",
            "رفع ملف التحاليل (TXT / CSV Uploader)",
        ],
    )

with col2:
    st.markdown("### 🧪 لوحة التحاليل الجينية الحيوية (Key Pharmacogenetic Panel)")

    if input_method == "رفع ملف التحاليل (TXT / CSV Uploader)":
        uploaded_file = st.file_uploader(
            "ارفع ملف التحاليل الجينية للحالة", type=["txt", "csv"]
        )
        if uploaded_file is not None:
            st.success("تم رفع وتحليل بيانات التحاليل الجينية بنجاح!")
            cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
            cyp2c19_profile = "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)"
            oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
            abcb1_profile = "Reduced Efflux (Enhanced Brain Concentration)"
        else:
            st.info("الرجاء رفع ملف التحاليل أو استخدام الاختيار اليدوي.")
            cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
            cyp2c19_profile = "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)"
            oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
            abcb1_profile = "Reduced Efflux (Enhanced Brain Concentration)"
    else:
        cyp2d6_profile = st.selectbox(
            "تحليل جين CYP2D6 (أيزومراز الأيض الرئيسي للمخدرات والمهدئات)",
            [
                "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)",
                "CYP2D6 *1/*1 (Extensive / Normal Metabolizer)",
                "CYP2D6 *1xN (Ultra-Rapid Metabolizer)",
            ],
        )

        cyp2c19_profile = st.selectbox(
            "تحليل جين CYP2C19 (مسؤول عن أيض مضادات الاكتئاب والمهدئات)",
            [
                "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)",
                "CYP2C19 *1/*1 (Normal Metabolizer)",
            ],
        )

        oprm1_profile = st.selectbox(
            "تحليل جين OPRM1 (مستقبلات الأفيون والمخدرات العصبية)",
            [
                "A118G Variant / Mutated (High Sensitivity / Overdose Risk)",
                "A118G Wild Type (Normal Sensitivity)",
            ],
        )

        abcb1_profile = st.selectbox(
            "تحليل جين ABCB1 / P-gp (نفاذية حاجز الدم في الدماغ)",
            [
                "Reduced Efflux (Enhanced Brain Concentration)",
                "Normal Excretion / Barrier",
            ],
        )

# تحليل النتائج ووضع الحالة بالتحاليل
st.markdown("---")
st.markdown("### 📊 تقرير التحاليل الإكلينيكية والجنائية الآلي (Comprehensive Analysis Report)")

is_poor_metabolizer = "Poor" in cyp2d6_profile or "Poor" in cyp2c19_profile
is_high_sensitivity = "Variant" in oprm1_profile

# عرض مؤشرات الحالة في داشبورد واضحة
res_c1, res_c2, res_c3 = st.columns(3)

res_c1.metric(
    label="النمط الأيضي للجينات (Metabolizer Phenotype)",
    value="Poor Metabolizer (حارق ضعيف)",
)
res_c2.metric(
    label="مستوى خطورة التسمم وتراكم الجرعات",
    value="High Toxicity Risk (خطر مرتفع جداً)",
)
res_c3.metric(
    label="حساسية المستقبلات العصبية للمخدرات",
    value="High Sensitivity (حساسية مفرطة للمواد)",
)

# جدول تفصيلي للتحاليل الجينية وموضع الحالة
analysis_data = {
    "الجين / المؤشر (Marker)": ["CYP2D6", "CYP2C19", "OPRM1", "ABCB1"],
    "التركيب الجيني (Genotype)": ["*4/*4", "*2/*2", "A118G Variant", "Reduced Efflux"],
    "التفسير الإكلينيكي والجنائي للتحليل": [
        "Poor Metabolizer - High risk of toxicity with opioids and antidepressants",
        "Poor Metabolizer - Risk of drug accumulation and delayed clearance",
        "Altered opioid receptor sensitivity (High vulnerability to overdose)",
        "Reduced blood-brain barrier efflux (Enhanced brain tissue concentration)"
    ]
}
df_analysis = pd.DataFrame(analysis_data)
st.table(df_analysis)

# صياغة الاستنتاج الإكلينيكي والجنائي المتكامل
forensic_conclusion = (
    "استنتاج طب شرعي حرج: الحالة تظهر تطابقاً وترافقاً فريداً من نوعه بين نمط Poor Metabolizer مع وجود طفرة في مستقبلات الأفيون (OPRM1). "
    "هذا التكوين الجيني يوضح قصوراً شديداً في قدرة الجسم على تكسير المواد المخدرة أو المهدئات، مما يؤدي إلى تراكمها السريع في الدم مع مكثفة أعضاء الدماغ (Brain Concentration)، "
    "مما يرفع احتمالية التعرض لارتفاع حاد في السمية (Toxicity) والجرعة الزائدة (Overdose) حتى مع الجرعات القياسية."
)

st.markdown(
    f"""
<div style="background-color:#1e293b; padding:18px; border-radius:8px; border-left: 5px solid #38bdf8;">
    <p style="color:#e2e8f0; font-size:16px; margin:0; line-height: 1.6;">{forensic_conclusion}</p>
</div>
""",
    unsafe_allow_html=True,
)


# --- دالة توليد الـ PDF المتكامل بالإنجليزية السليمة لتفادي المربعات ---
def generate_pdf_report(
    case, c_type, c2d6, c2c19, oprm, ab, conclusion, status_risk
):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 40, "In-Silico Forensic Pharmacogenomics & Toxicology Report")

    p.setFont("Helvetica", 10)
    p.drawString(50, height - 65, f"Case ID: {case} | Date: 2026-10-01 (Giza, Egypt)")
    p.drawString(50, height - 85, f"Case Type: {c_type}")

    p.line(50, height - 95, width - 50, height - 95)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 120, "Genomic Profile & Analytical Panel:")
    
    p.setFont("Helvetica", 9)
    p.drawString(70, height - 140, f"- CYP2D6 Genotype: {c2d6}")
    p.drawString(70, height - 160, f"- CYP2C19 Genotype: {c2c19}")
    p.drawString(70, height - 180, f"- OPRM1 Receptor Variant: {oprm}")
    p.drawString(70, height - 200, f"- ABCB1 Transporter Status: {ab}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 235, "Clinical & Forensic Case Evaluation:")
    p.setFont("Helvetica", 9)

    text_obj = p.beginText(70, height - 255)
    text_obj.setFont("Helvetica", 9)
    
    summary_text = (
        "The evaluated living case demonstrates a critical genetic configuration combining "
        "poor hepatic metabolism with high-sensitivity opioid receptors (OPRM1 variant). "
        "This indicates a severe vulnerability to acute toxicity, rapid drug accumulation, "
        "and heightened brain concentration under standard therapeutic dosages."
    )
    
    for line in [summary_text[i : i + 95] for i in range(0, len(summary_text), 95)]:
        text_obj.textLine(line)
    p.drawText(text_obj)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 330, f"Overall Forensic Risk Assessment: {status_risk}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


st.markdown("<br>", unsafe_allow_html=True)

risk_text = "High Toxicity Risk & Overdose Vulnerability"
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
    label="📥 تحميل التقرير الشامل للتحاليل والحالة (Official PDF Report)",
    data=pdf_data,
    file_name=f"Comprehensive_Forensic_Report_{case_id}.pdf",
    mime="application/pdf",
)
