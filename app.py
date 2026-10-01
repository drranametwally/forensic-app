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

    # متغيرات لتخزين الملف المرفوع أو الاختيارات
    uploaded_data_loaded = False
    file_cyp2d6, file_cyp2c19, file_oprm1, file_abcb1 = "", "", "", ""

    if input_method == "رفع ملف التحاليل (TXT / CSV Uploader)":
        uploaded_file = st.file_uploader(
            "ارفع ملف التحاليل الجينية للحالة", type=["txt", "csv"]
        )
        if uploaded_file is not None:
            try:
                content = uploaded_file.getvalue().decode("utf-8")
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                if len(lines) > 1:
                    parts = lines[1].split(",")
                    if len(parts) >= 4:
                        file_cyp2d6 = parts[0]
                        file_cyp2c19 = parts[1]
                        file_oprm1 = parts[2]
                        file_abcb1 = parts[3]
                        uploaded_data_loaded = True
                st.success("تم قراءة ملف التحاليل المرفوع وتحديث بيانات الحالة بنجاح!")
            except:
                st.warning("تعذر قراءة تنسيق الملف، يرجى التأكد من تطابق الأعمدة.")

        if not uploaded_data_loaded:
            st.info("الرجاء رفع ملف صالح أو سيتم استخدام الاختيار الافتراضي.")
            file_cyp2d6 = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
            file_cyp2c19 = "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)"
            file_oprm1 = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
            file_abcb1 = "Reduced Efflux (Enhanced Brain Concentration)"

        cyp2d6_profile = file_cyp2d6
        cyp2c19_profile = file_cyp2c19
        oprm1_profile = file_oprm1
        abcb1_profile = file_abcb1
    else:
        # لو اختيار يدوي، البرنامج يتغير حسب نوع الحالة أو الختيارات
        if "Overdose" in case_type or "Poisoning" in case_type:
            default_2d6 = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
            default_oprm = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
        elif "Therapeutic" in case_type:
            default_2d6 = "CYP2D6 *1/*1 (Extensive / Normal Metabolizer)"
            default_oprm = "A118G Wild Type (Normal Sensitivity)"
        else:
            default_2d6 = "CYP2D6 *1xN (Ultra-Rapid Metabolizer)"
            default_oprm = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"

        cyp2d6_profile = st.selectbox(
            "تحليل جين CYP2D6",
            [
                default_2d6,
                "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)",
                "CYP2D6 *1/*1 (Extensive / Normal Metabolizer)",
                "CYP2D6 *1xN (Ultra-Rapid Metabolizer)",
            ],
        )

        cyp2c19_profile = st.selectbox(
            "تحليل جين CYP2C19",
            [
                "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)",
                "CYP2C19 *1/*1 (Normal Metabolizer)",
            ],
        )

        oprm1_profile = st.selectbox(
            "تحليل جين OPRM1",
            [
                default_oprm,
                "A118G Variant / Mutated (High Sensitivity / Overdose Risk)",
                "A118G Wild Type (Normal Sensitivity)",
            ],
        )

        abcb1_profile = st.selectbox(
            "تحليل جين ABCB1 / P-gp",
            [
                "Reduced Efflux (Enhanced Brain Concentration)",
                "Normal Excretion / Barrier",
            ],
        )

# تحليل النتائج بناءً على المدخلات المتغيرة للحالة
st.markdown("---")
st.markdown("### 📊 تقرير التحاليل الإكلينيكية والجنائية الآلي (Dynamic Analysis Report)")

is_poor_metabolizer = "Poor" in cyp2d6_profile or "Poor" in cyp2c19_profile
is_high_sensitivity = "Variant" in oprm1_profile

# تحديث الـ Metrics ديناميكياً
res_c1, res_c2, res_c3 = st.columns(3)

if is_poor_metabolizer:
    phenotype_text = "Poor Metabolizer (حارق ضعيف)"
    risk_text_ui = "High Toxicity Risk (خطر مرتفع جداً)"
else:
    phenotype_text = "Normal / Rapid Metabolizer (أعماد طبيعي)"
    risk_text_ui = "Low Risk / Standard Profile (آمن / طبيعي)"

if is_high_sensitivity:
    sens_text = "High Sensitivity (حساسية مفرطة للمواد)"
else:
    sens_text = "Standard Sensitivity (حساسية معيارية)"

res_c1.metric(label="النمط الأيضي للجينات (Metabolizer Phenotype)", value=phenotype_text)
res_c2.metric(label="مستوى خطورة التسمم وتراكم الجرعات", value=risk_text_ui)
res_c3.metric(label="حساسية المستقبلات العصبية للمخدرات", value=sens_text)

# استخراج الجينوتيب والترتيب للجدول الديناميكي
g2d6_val = cyp2d6_profile.split(" ")[1] if "*" in cyp2d6_profile else "Normal"
g2c19_val = cyp2c19_profile.split(" ")[1] if "*" in cyp2c19_profile else "Normal"
g_oprm = "A118G Variant" if "Variant" in oprm1_profile else "Wild Type"
g_abcb1 = "Reduced Efflux" if "Reduced" in abcb1_profile else "Normal"

# جدول تفصيلي ديناميكي يتغير حسب الحالة
analysis_data = {
    "الجين / المؤشر (Marker)": ["CYP2D6", "CYP2C19", "OPRM1", "ABCB1"],
    "التركيب الجيني (Genotype)": [g2d6_val, g2c19_val, g_oprm, g_abcb1],
    "التفسير الإكلينيكي والجنائي للتحليل": [
        f"Metabolism status: {cyp2d6_profile}",
        f"Metabolism status: {cyp2c19_profile}",
        f"Receptor status: {oprm1_profile}",
        f"Transporter status: {abcb1_profile}"
    ]
}
df_analysis = pd.DataFrame(analysis_data)
st.table(df_analysis)

# صياغة الاستنتاج الإكلينيكي والجنائي ديناميكياً حسب حالة المريض
if is_poor_metabolizer and is_high_sensitivity:
    forensic_conclusion = (
        f"استنتاج طب شرعي للحالة ({case_id}): تظهر الحالة تطابقاً حرجاً بين نمط الأيض الضعيف (Poor Metabolizer) "
        f"وطفرة مستقبلات الأفيون ({g_oprm}). هذا التكوين يشير إلى قصور بالغ في التخلص من السموم والمخدرات وتراكمها السريع، "
        f"مما يرفع احتمالية التسمم الحاد والجرعة الزائدة بشكل خطير."
    )
    pdf_risk_summary = "High Toxicity Risk & Overdose Vulnerability"
else:
    forensic_conclusion = (
        f"استنتاج طب شرعي للحالة ({case_id}): تظهر التحاليل الجينية للحالة استقراراً نسبياً في معدلات الأيض المعياري، "
        f"مع عدم وجود مؤشرات قوية تدل على خطورة سمية عالية أو تراكم دوائي حرج تحت الجرعات القياسية."
    )
    pdf_risk_summary = "Stable / Standard Toxicity Risk"

st.markdown(
    f"""
<div style="background-color:#1e293b; padding:18px; border-radius:8px; border-left: 5px solid #38bdf8;">
    <p style="color:#e2e8f0; font-size:16px; margin:0; line-height: 1.6;">{forensic_conclusion}</p>
</div>
""",
    unsafe_allow_html=True,
)


# --- دالة توليد الـ PDF الديناميكي المتكامل ---
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
    p.drawString(50, height - 120, "Dynamic Genomic Profile & Analytical Panel:")
    
    p.setFont("Helvetica", 9)
    p.drawString(70, height - 140, f"- CYP2D6 Profile: {c2d6}")
    p.drawString(70, height - 160, f"- CYP2C19 Profile: {c2c19}")
    p.drawString(70, height - 180, f"- OPRM1 Receptor: {oprm}")
    p.drawString(70, height - 200, f"- ABCB1 Transporter: {ab}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 235, "Clinical & Forensic Case Evaluation:")
    p.setFont("Helvetica", 9)

    text_obj = p.beginText(70, height - 255)
    text_obj.setFont("Helvetica", 9)
    
    for line in [conclusion[i : i + 95] for i in range(0, len(conclusion), 95)]:
        text_obj.textLine(line)
    p.drawText(text_obj)

    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, height - 340, f"Overall Forensic Risk Assessment: {status_risk}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


st.markdown("<br>", unsafe_allow_html=True)

pdf_data = generate_pdf_report(
    case_id,
    case_type,
    cyp2d6_profile,
    cyp2c19_profile,
    oprm1_profile,
    abcb1_profile,
    forensic_conclusion,
    pdf_risk_summary,
)

st.download_button(
    label="📥 تحميل التقرير الديناميكي المحدث (Official PDF Report)",
    data=pdf_data,
    file_name=f"Dynamic_Forensic_Report_{case_id}.pdf",
    mime="application/pdf",
)

