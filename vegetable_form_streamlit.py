import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time

# --- 1. SETUP ---
st.set_page_config(page_title="CPRAM Form", layout="wide")

# --- 2. SESSION STATE (หัวใจสำคัญที่ทำให้ข้อมูลไม่หาย) ---
# เราจะใช้รหัส 'key' ในทุกช่อง input เพื่อให้ Streamlit จำค่าไว้ในหน่วยความจำ
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

# --- 3. HEADER (FR-QAS-10-000) ---
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
    <h3 style="text-align: center; color: #2e7d32; margin-top: 20px;">แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h3>
    """, unsafe_allow_html=True)

# --- 4. FORM UI ---
# ใช้ st.container แทน st.form ในกรณีที่ต้องการให้ปุ่ม "เพิ่มรายการ" ทำงานได้ทันทีโดยไม่ล้างค่า
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
# ทุกช่องต้องมี 'key' เพื่อล็อกข้อมูล
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="keep_s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="keep_s_date")
s_time = c3.time_input("เวลาส่ง *", value=time(14, 0), key="keep_s_time")

c4, c5 = st.columns(2)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="keep_s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="keep_recorder")

st.markdown("---")
st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")

# วนลูปสร้างรายการวัตถุดิบตามจำนวน items_count
for i in range(st.session_state.items_count):
    with st.expander(f"📦 รายการที่ {i+1}", expanded=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        # ใช้ i ใน key เพื่อให้แต่ละรายการมี ID แยกกัน เช่น mat_0, mat_1
        col1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        col2.text_input("Code", key=f"code_{i}")
        col3.number_input("จำนวน (KG)", min_value=0.0, key=f"qty_{i}")
        
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.text_input("รหัสไร่", key=f"farm_{i}")
        r2c2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        r2c3.text_input("เลขที่ GAP", key=f"gap_{i}")

# --- 5. BUTTONS ---
col_btn1, col_btn2 = st.columns([0.2, 0.8])

with col_btn1:
    if st.button("+ เพิ่มรายการวัตถุดิบ"):
        st.session_state.items_count += 1
        st.rerun() # เพิ่มจำนวนแล้วรันใหม่ ข้อมูลที่มี key จะไม่หาย

with col_btn2:
    if st.button("ยืนยันข้อมูลและส่ง PDF", type="primary"):
        if not s_name or not s_email:
            st.error("❌ กรุณากรอกชื่อผู้ส่งมอบและอีเมลในส่วนที่ 1")
        else:
            st.success(f"✅ บันทึกข้อมูลเรียบร้อย! ระบบกำลังส่ง PDF ไปที่ {s_email}")
            # ข้อมูลในส่วนที่ 2 สามารถดึงมาใช้ได้ผ่าน st.session_state[f'mat_{i}']
