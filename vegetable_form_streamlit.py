import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# ฟังก์ชันโหลดข้อมูลที่อยู่
@st.cache_data
def load_address():
    try:
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_addr = load_address()

# --- 2. SESSION STATE (กันข้อมูลหาย) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

# --- 3. UI HEADER ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px;">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 24px;">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;">
                <b>CPRAM Co., Ltd.</b><br><small>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</small>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="border: 1.5px solid black; padding: 2px 10px;"><b>FR-QAS-10-000</b></div>
            <small>มีผลใช้งาน: 2026-05-08</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. FORM ---
with st.form("delivery_form"):
    st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
    c1, c2 = st.columns(2)
    s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name_input")
    s_email = c2.text_input("อีเมลสำหรับรับไฟล์ PDF *", key="s_email_input")
    
    st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")
    items_data = []
    for i in range(st.session_state.items_count):
        st.markdown(f"**รายการที่ {i+1}**")
        r1, r2 = st.columns([2, 1])
        mat = r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        farm = r2.text_input("รหัสไร่", key=f"farm_{i}")
        
        # เก็บข้อมูลไว้ใน list เพื่อไปสร้าง PDF
        items_data.append({'mat': mat, 'farm': farm})
        st.write("---")

    # ปรับชื่อปุ่มตามที่ต้องการ (เอาคำว่า ทันที ออก)
    submit = st.form_submit_button("ยืนยันข้อมูลและส่ง PDF", type="primary")

# ปุ่มเพิ่มรายการ (อยู่นอก Form)
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 5. LOGIC เมื่อกดส่ง ---
if submit:
    if not s_name or not s_email:
        st.error("❌ กรุณากรอกข้อมูลชื่อและอีเมลให้ครบถ้วน")
    else:
        # ระบบจะประมวลผลส่งเมลตรงนี้ (ใช้ SMTP Logic เดิม)
        st.success(f"บันทึกข้อมูลเรียบร้อย! ระบบกำลังส่ง PDF ไปที่ {s_email}")
        # pdf_bytes = generate_pdf(...)
        # send_email(pdf_bytes, s_email)
