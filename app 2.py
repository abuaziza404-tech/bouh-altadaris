import streamlit as st
import os
import time
import pandas as pd

# --- حل مشكلة قواعد البيانات للسيرفر (إلزامي لـ ChromaDB) ---
try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

# --- استدعاء محركات الذكاء والتحليل ---
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# --- إعدادات الواجهة السيادية (ذهبي وأسود احترافي) ---
st.set_page_config(
    page_title="BOUH ALTADARIS V100", 
    page_icon="🛰️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# الربط مع المفتاح السري (Secrets)
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- التنسيق البصري المؤسسي (Sovereign CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0b0d11; color: #e0e0e0; }
    .stButton>button { 
        background-color: #b8860b; color: white; border-radius: 5px; 
        font-weight: bold; border: 1px solid #ffd700; width: 100%; height: 3em;
    }
    .stTextInput>div>div>input { background-color: #1a1c23; color: gold; border: 1px solid #b8860b; }
    .sidebar .sidebar-content { background-color: #11141a; border-right: 1px solid #b8860b; }
    h1, h2, h3 { color: #ffd700; font-family: 'Times New Roman', serif; border-bottom: 1px solid #333; padding-bottom: 10px; }
    .poetry { font-style: italic; color: #8b8b8b; text-align: center; font-size: 1.1em; margin-top: 20px; }
    .signature { color: gold; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- الهوية الرسمية في رأس الصفحة ---
col_logo, col_title = st.columns([1, 4])
with col_title:
    st.title("🛰️ منظومة بوح التضاريس | BOUH ALTADARIS")
    st.markdown("<p style='font-size: 1.2em; color: #b8860b;'>Enterprise Geological Intelligence Operating System</p>", unsafe_allow_html=True)

# --- محرك القرار الجيولوجي (GPI Calculation Engine) ---
def calculate_gpi(structure, pattern, alteration, quartz, cluster, terrain, context):
    # تطبيق أوزان دستور بوح التضاريس V100
    score = (structure * 0.30) + (pattern * 0.20) + (alteration * 0.15) + \
            (quartz * 0.10) + (cluster * 0.10) + (terrain * 0.10) + (context * 0.05)
    return round(score, 3)

# --- لوحة التحكم الجانبية ---
with st.sidebar:
    st.markdown("<div class='signature'>أحمد أبو عزيزة الرشيدي</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:right; font-size:0.8em;'>Abuaziza404@gmail.com</p>", unsafe_allow_html=True)
    st.divider()
    
    st.header("🔐 الوصول السيادي")
    pwd = st.text_input("التوقيع الرقمي (Signature)", type="password")
    
    if pwd == "abuaziza2000":
        st.success("✅ تم التحقق من الهوية")
        mode = st.selectbox("وحدة العمليات", [
            "🧠 المساعد الجيولوجي (Oracle)", 
            "📡 المسح الطيفي الشامل (Spectra)", 
            "📍 مركز الأهداف الميدانية (Field)"
        ])
        st.divider()
        st.info("نطاق العمل: تلال البحر الأحمر - أربعات")
    else:
        st.warning("بانتظار التوقيع الرقمي...")

# --- واجهة التشغيل عند الدخول ---
if pwd == "abuaziza2000":
    
    if mode == "🧠 المساعد الجيولوجي (Oracle)":
        st.header("🧠 المساعد الجيولوجي الذكي (AI Oracle)")
        st.markdown("> **مهمة المساعد:** تحليل الإحداثيات، شرح معادلات التحوير، وتقديم توصيات ميدانية.")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("اسأل المساعد عن عروق المرو أو معادلات ASTER..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)
                    full_prompt = f"أنت خبير جيولوجي استراتيجي في نظام 'بوح التضاريس' للمهندس أحمد أبو عزيزة الرشيدي. التزم بالعقيدة الجيولوجية للنظام (Structure -> Pattern -> Alteration). سؤال المهندس: {prompt}"
                    response = llm.invoke([HumanMessage(content=full_prompt)])
                    st.markdown(response.content)
                    st.session_state.messages.append({"role": "assistant", "content": response.content})
                except Exception as e:
                    st.error("خطأ: يرجى التحقق من مفتاح API في الإعدادات.")

    elif mode == "📡 المسح الطيفي الشامل (Spectra)":
        st.header("📡 مركز الاستقبال ومعالجة المشاهد")
        
        # مركز الرفع العالمي (تعديل بناءً على طلبك لاستقبال كل شيء)
        uploaded_files = st.file_uploader(
            "ارفع صور الأقمار الصناعية (TIF)، ملفات ZIP، فيديوهات الدرون، أو لقطات الشاشة الميدانية", 
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'tif', 'zip', 'mp4', 'kml', 'kmz']
        )
        
        if uploaded_files:
            st.success(f"تم استقبال {len(uploaded_files)} ملفات بنجاح في قاعدة بيانات بوح التضاريس.")
            
        col_ctrl, col_gpi = st.columns([1, 1])
        with col_ctrl:
            st.subheader("⚙️ معايير الهدف")
            s = st.slider("كثافة البنية (Structure)", 0.0, 1.0, 0.7)
            p = st.slider("النمط الهندسي (Pattern)", 0.0, 1.0, 0.6)
            a = st.slider("مؤشر التحوير (Alteration)", 0.0, 1.0, 0.8)
            q = st.slider("مؤشر الكوارتز (Quartz)", 0.0, 1.0, 0.5)
            
        with col_gpi:
            st.subheader("🔢 تقييم الاحتمالية (GPI)")
            score = calculate_gpi(s, p, a, q, 0.7, 0.6, 0.8)
            st.metric("مؤشر احتمالية الذهب", f"{score * 100}%")
            
            if score >= 0.88:
                st.error("🚀 الحالة: هدف حفر مؤكد (DRILL TARGET)")
                st.balloons()
            elif score >= 0.75:
                st.warning("⚒️ الحالة: هدف تخندق (TRENCH TARGET)")
            else:
                st.info("🔍 الحالة: مراقبة وبحث (MONITOR)")

    elif mode == "📍 مركز الأهداف الميدانية (Field)":
        st.header("📍 إدارة الأهداف والخرائط")
        st.write("جدول الأهداف الاستراتيجية المكتشفة في منطقة أربعات")
        # بيانات افتراضية بناءً على المخطط
        target_data = {
            "ID": ["Target-B", "GV-1", "GM-2"],
            "Coordinates": ["35.85, 19.35", "35.45, 18.45", "36.35, 20.15"],
            "GPI Score": [0.92, 0.89, 0.78],
            "Action": ["DRILL", "DRILL", "TRENCH"]
        }
        st.table(pd.DataFrame(target_data))
        st.button("تصدير الأهداف إلى ملف KML (Google Earth)")

    # --- التذييل الرسمي (Poetry & Signature) ---
    st.divider()
    st.markdown("<p class='poetry'>لمعة ذهب بين الصخر والتضاريس .. مضمونها سيرة عظيم النزاهه</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.8em; color: #555;'>إصدار مؤسسي V100 - جميع الحقوق محفوظة للمهندس أحمد أبو عزيزة الرشيدي © 2026</p>", unsafe_allow_html=True)

else:
    st.info("🔐 المنصة في وضع 'التأمين السيادي'. يرجى إدخال التوقيع الرقمي في القائمة الجانبية لفتح محركات الاستكشاف.")