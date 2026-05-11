import streamlit as st
import pandas as pd
import os
import base64
from fpdf import FPDF
from datetime import datetime

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# ฟังก์ชันแปลงรูปภาพเป็น Base64 เพื่อให้ภาพแสดงผลเสถียร
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# โหลดข้อมูลที่อยู่
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx' 
    if os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_addr = load_address_data()

# --- 2. ส่วนหัวแบบฟอร์ม (Header) ---
logo_path = "image_9482bc.png" # หรือชื่อไฟล์โลโก้ที่คุณอัปโหลดไว้
logo_base64 = get_image_base64(logo_path)

header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center;">
            {f'<img src="data:image/png;base64,{logo_base64}" width="140">' if logo_base64 else '<div style="background-color:#2e7d32; color:white; padding:10px;">CPRAM</div>'}
            <div style="margin-left: 15px;">
                <b style="font-size: 22px; color: #2e7d32; line-height: 1;">CPRAM Co., Ltd.</b><br>
                <span style="font-size: 16px; color: #444;">ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</span>
            </div>
        </div>
        <div style="text-align: right; line-height: 1.2;">
            <b style="font-size: 18px; color: #333;">FR-QAS-10-000</b><br>
            <span style="font-size: 14px; color: #666;">มีผลใช้งาน: 2026-05-08</span>
        </div>
    </div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# หัวข้อหลักและคำแนะนำ
st.markdown("<h3 style='text-align: center; color: #2e7d32;'>แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>กรุณากรอกข้อมูลให้ครบถ้วน — เลือก จังหวัด/อำเภอ/ตำบล จาก dropdown ระบบจะกรอกรหัสไปรษณีย์ให้อัตโนมัติ</p>", unsafe_allow_html=True)

# --- 3. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ (Layout ตาม image_89a8b7.png) ---
st.markdown("#### <span style='color: #2e7d32;'>ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</span>", unsafe_allow_html=True)

# แถวที่ 1: ผู้ส่งมอบ, วันที่, เวลา
c1, c2, c3 = st.columns(3)
supplier = c1.text_input("ผู้ส่งมอบ (Supplier) *", placeholder="ชื่อบริษัท/ฟาร์ม")
delivery_date = c2.date_input("วันที่ส่งวัตถุดิบ *", value=datetime.now())
delivery_time = c3.text_input("เวลาส่ง", placeholder="เช่น 14:00 น.")

# แถวที่ 2: อีเมล, ลงชื่อผู้กรอก, ประเทศ
c4, c5, c6 = st.columns(3)
email = c4.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", placeholder="example@mail.com")
recorder_name = c5.text_input("ลงชื่อผู้กรอก", placeholder="ระบุชื่อผู้บันทึกข้อมูล")
origin_country = c6.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "จีน", "อื่นๆ"])

st.markdown("---")

# --- 4. ส่วนที่ 2 — รายการวัตถุดิบ (ยังคงไว้เพื่อให้โปรแกรมทำงานสมบูรณ์) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

for i in range(st.session_state.items_count):
    with st.container():
        st.write(f"**รายการที่ {i+1}**")
        col_a, col_b, col_c = st.columns([2, 1, 1])
        col_a.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        col_b.text_input("Code", key=f"code_{i}")
        col_c.number_input("จำนวน (KG)", key=f"qty_{i}")
        
        # ที่อยู่ดึงจาก thailand.xlsx
        if origin_country == "ประเทศไทย" and not df_addr.empty:
            addr_col1, addr_col2, addr_col3 = st.columns(3)
            p_val = addr_col1.selectbox("จังหวัด", sorted(df_addr["จังหวัด"].unique()), key=f"p_{i}")
            d_list = sorted(df_addr[df_addr["จังหวัด"] == p_val]["อำเภอ"].unique())
            a_val = addr_col2.selectbox("อำเภอ", d_list, key=f"a_{i}")
            t_list = sorted(df_addr[(df_addr["จังหวัด"] == p_val) & (df_addr["อำเภอ"] == a_val)]["ตำบล"].unique())
            t_val = addr_col3.selectbox("ตำบล", t_list, key=f"t_{i}")

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items_count += 1
    st.rerun()

# --- 5. ปุ่มบันทึก ---
if st.button("✅ ยืนยันข้อมูล", type="primary", use_container_width=True):
    if not supplier or not email:
        st.warning("กรุณากรอกข้อมูลสำคัญ (เครื่องหมาย *) ให้ครบถ้วน")
    else:
        st.success("ข้อมูลส่วนที่ 1 ได้รับการบันทึกเรียบร้อยแล้ว")
