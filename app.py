from io import BytesIO
import numpy as np
import pandas as pd
import streamlit as st

# مكتبات توليد الـ PDF
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

# واجهة المدخلات مقسمة لعمودين
col1, col2 = st.columns(2)

with col1:
  st.markdown(
      "### 👤 بيانات الحالة الميدانية والملف الجيني (Case & Genetic Input)"
  )
  case_id = st.text_input("كود أو رقم الحالة (Case ID)", "CASE-2026-001")
  case_type = st.selectbox(
      "نوع الحالة الحية",
      [
          "استجابة غير طبيعية للمواد المخدرة / اشتباه تسمم",
          "تقييم إدمان وعلاج نفسي (مصحات)",
          "تحليل قرابة / إثبات نسب قانوني",
          "فحص روتيني للسموم والمستحضرات",
      ],
  )

  # خيار إدخال الملف الجيني أو الاختيار اليدوي
  input_method = st.radio(
      "طريقة إدخال البيانات الجينية",
      [
          "الاختيار اليدوي السريع للوحة الجينات (Interactive Panel)",
          "رفع ملف جيني حقيقي (VCF / CSV Uploader)",
      ],
  )

with col2:
  st.markdown("### 🧪 لوحة الجينات الحيوية المستهدفة (Key Pharmacogenetic Panel)")

  # تعريف المتغيرات الافتراضية
  cyp2d6_profile = "CYP2D6 *1/*1 (Extensive / Normal Metabolizer)"
  cyp2c19_profile = "CYP2C19 *1/*1 (Normal Metabolizer)"
  oprm1_profile = "A118G Wild Type (Normal Sensitivity)"
  abcb1_profile = "Normal Excretion / Barrier"

  if input_method == "الاختيار اليدوي السريع للوحة الجينات (Interactive Panel)":
    cyp2d6_profile = st.selectbox(
        "جين CYP2D6 (أيزومراز الأيض الرئيسي للمخدرات والمهدئات)",
        [
            "CYP2D6 *1/*1 (Extensive / Normal Metabolizer)",
            "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)",
            "CYP2D6 *1xN (Ultra-Rapid Metabolizer)",
        ],
    )

    cyp2c19_profile = st.selectbox(
        "جين CYP2C19 (مسؤول عن أيض مضادات الاكتئاب والمهدئات)",
        [
            "CYP2C19 *1/*1 (Normal Metabolizer)",
            "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)",
        ],
    )

    oprm1_profile = st.selectbox(
        "جين OPRM1 (مستقبلات الأفيون والمخدرات العصبية)",
        [
            "A118G Wild Type (Normal Sensitivity)",
            "A118G Variant / Mutated (High Sensitivity / Overdose Risk)",
        ],
    )

    abcb1_profile = st.selectbox(
        "جين ABCB1 / P-gp (نفاذية حاجز الدم في الدماغ)",
        [
            "Normal Excretion / Barrier",
            "Reduced Efflux (Enhanced Brain Concentration)",
        ],
    )
  else:
    uploaded_file = st.file_uploader(
        "ارفع ملف البيانات الجينية للحالة (CSV أو VCF أو TXT)", type=["csv", "vcf", "txt"]
    )
    
    if uploaded_file is not None:
      try:
        # قراءة الملف المحمل وتحليل محتواه بذكاء
        string_data = uploaded_file.getvalue().decode("utf-8")
        
        # محاولة قراءة كـ CSV أو نصوص بحثية
        if "," in string_data or "\t" in string_data:
            df_uploaded = pd.read_csv(BytesIO(uploaded_file.getvalue()), sep=None, engine='python')
            st.success("تم قراءة ملف البيانات الجينية المرفوع بنجاح وتحليل الأعمدة!")
            st.dataframe(df_uploaded.head(), use_container_width=True)
            
            # فحص محتوى الملف لتحديث النماذج إن وجدت تطابقات
            full_text_file = string_data.upper()
            if "CYP2D6" in full_text_file and "*4" in full_text_file:
                cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
            if "CYP2C19" in full_text_file and "*2" in full_text_file:
                cyp2c19_profile = "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)"
            if "OPRM1" in full_text_file and "VARIANT" in full_text_file:
                oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
            if "ABCB1" in full_text_file and "REDUCED" in full_text_file:
                abcb1_profile = "Reduced Efflux (Enhanced Brain Concentration)"
        else:
            st.success("تم استقبال الملف النصي الجيني بنجاح.")
            full_text_file = string_data.upper()
            if "POOR" in full_text_file or "*4" in full_text_file:
                cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
            if "VARIANT" in full_text_file or "A118G" in full_text_file:
                oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
      except Exception as e:
        st.warning(f"تعذر معالجة الملف المرفوع تلقائياً، جاري استخدام القيم الافتراضية. الخطأ: {e}")
    else:
      st.info("الرجاء رفع ملف لعرض البيانات المستخرجة أوتوماتيكياً.")
      cyp2d6_profile = "CYP2D6 *4/*4 (Poor Metabolizer - High Toxicity Risk)"
      cyp2c19_profile = "CYP2C19 *2/*2 (Poor Metabolizer - Drug Accumulation)"
      oprm1_profile = "A118G Variant / Mutated (High Sensitivity / Overdose Risk)"
      abcb1_profile = "Reduced Efflux (Enhanced Brain Concentration)"

# تحليل النتائج بناءً على الخيارات
st.markdown("---")
st.markdown("### 📊 تقرير التفسير الإكلينيكي والجنائي الآلي (Automated Forensic Report)")

is_poor_metabolizer = "Poor" in cyp2d6_profile or "Poor" in cyp2c19_profile
is_high_sensitivity = "Variant" in oprm1_profile

res_c1, res_c2, res_c3 = st.columns(3)

res_c1.metric(
    label="النمط الأيضي المتوقع (Metabolizer Phenotype)",
    value="حارق ضعيف (Poor Metabolizer)"
    if is_poor_metabolizer
    else "حارق طبيعي (Normal)",
)
res_c2.metric(
    label="خطورة التسمم أو تراكم الجرعات",
    value="عالية جداً (High Risk)" if is_poor_metabolizer else "منخفضة (Safe)",
)
res_c3.metric(
    label="حساسية المستقبلات العصبية للمخدرات",
    value="حساسية مفرطة (Vulnerable)" if is_high_sensitivity else "معيارية",
)

if is_poor_metabolizer and is_high_sensitivity:
  forensic_conclusion = (
      "⚠️ **استنتاج طب شرعي حرج:** الحالة تظهر نمطاً وراثياً من نوع (Poor Metabolizer) مع وجود طفرة في مستقبلات الأفيون (OPRM1). "
      "هذا التكوين الجيني يفسر بوضوح عدم قدرة الجسم على تكسير المواد المخدرة أو المهدئات، مما يؤدي إلى تراكمها السريع في الدم "
      "وعبورها بكثافة لعصارة الدماغ، مما يرفع احتمالية التعرض لـ (Toxicity / Overdose) حتى مع تعاطي جرعات معتادة أو ضعيفة."
  )
else:
  forensic_conclusion = (
      "✅ **استنتاج طب شرعي مستقر:** معدلات الأيض للمادة ضمن الحدود المعيارية، ولا توجد مؤشرات وراثية قوية تدل على خطورة تراكم السموم "
      "أو فرط الحساسية العصبية بناءً على اللوحة المدروسة."
  )

st.markdown(
    f"""
<div style="background-color:#1e293b; padding:18px; border-radius:8px; border-left: 5px solid #38bdf8;">
    <p style="color:#e2e8f0; font-size:16px; margin:0;">{forensic_conclusion}</p>
</div>
""",
    unsafe_allow_html=True,
)


def generate_pdf_report(
    case, c_type, c2d6, c2c19, oprm, ab, conclusion, status_risk
):
  buffer = BytesIO()
  p = canvas.Canvas(buffer, pagesize=letter)
  width, height = letter

  p.setFont("Helvetica-Bold", 18)
  p.drawString(50, height - 50, "Live Forensic PGx & Toxicology Report")

  p.setFont("Helvetica", 11)
  p.drawString(
      50, height - 80, f"Case ID: {case} | Date: 2026-10-01 (Giza, Egypt)"
  )
  p.drawString(50, height - 100, f"Case Type: {c_type}")

  p.line(50, height - 115, width - 50, height - 115)

  p.setFont("Helvetica-Bold", 13)
  p.drawString(50, height - 145, "Genetic Panel Profiling:")
  p.setFont("Helvetica", 10)
  p.drawString(70, height - 165, f"- CYP2D6 Profile: {c2d6}")
  p.drawString(70, height - 185, f"- CYP2C19 Profile: {c2c19}")
  p.drawString(70, height - 205, f"- OPRM1 Receptor: {oprm}")
  p.drawString(70, height - 225, f"- ABCB1 Transporter: {ab}")

  p.setFont("Helvetica-Bold", 13)
  p.drawString(50, height - 265, "Clinical & Forensic Conclusion:")

  text_obj = p.beginText(70, height - 285)
  text_obj.setFont("Helvetica", 10)
  plain_conclusion = conclusion.replace("⚠️", "").replace("✅", "")
  for line in [
      plain_conclusion[i : i + 85]
      for i in range(0, len(plain_conclusion), 85)
  ]:
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
