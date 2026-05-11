import streamlit as st
import pandas as pd
import os
import base64
from fpdf import FPDF
from datetime import datetime

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# ฟังก์ชันดึงรูปภาพโลโก้
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

# --- 2. ส่วนหัวแบบฟอร์ม (Header) ตามภาพ image_940297.png และ image_9489c3.png ---
logo_base64 = get_image_base64("image_9482bc.png") #

header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; margin-bottom: 10px;">
        <div style="display: flex; align-items: center;">
            {f'<img src="data:image/png;base64,{logo_base64}" width="140">' if logo_base64 else ''}
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
st.markdown(header_html, unsafe_allow_html=True) #

st.markdown("<h3 style='text-align: center; color: #2e7d32;'>แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>กรุณากรอกข้อมูลให้ครบถ้วน — เลือก จังหวัด/อำเภอ/ตำบล จาก dropdown ระบบจะกรอกรหัสไปรษณีย์ให้อัตโนมัติ</p>", unsafe_allow_html=True) #

# --- 3. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ (ตามภาพ image_89a8b7.png) ---
st.markdown("#### <span style='color: #2e7d32;'>ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</span>", unsafe_allow_html=True)

# แถวที่ 1
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", placeholder="ระบุชื่อบริษัท/ฟาร์ม")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", value=datetime.now())
s_time = c3.text_input("เวลาส่ง", placeholder="เช่น 14:00 น.")

# แถวที่ 2
c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", placeholder="example@mail.com")
s_recorder = c5.text_input("ลงชื่อผู้กรอก", placeholder="ชื่อ-นามสกุล")
origin_main = c6.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "จีน", "อื่นๆ"]) #

# --- 4. ส่วนที่ 2 — รายการวัตถุดิบ (คงข้อมูลครบถ้วนตามเดิม) ---
st.markdown("---")
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

for i in range(st.session_state.items_count):
    with st.expander(f"รายการที่ {i+1}", expanded=True):
        # ข้อมูลสินค้าหลัก
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        r1c2.text_input("Code", key=f"code_{i}")
        r1c3.number_input("จำนวน (KG) *", min_value=0.0, key=f"qty_{i}")

        # ข้อมูลการปลูกและ GAP
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.text_input("สายพันธุ์", key=f"breed_{i}")
        r2c2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        r2c3.text_input("เลขที่ GAP", key=f"gap_{i}")

        # ที่อยู่แหล่งปลูก
        st.write("📍 **ที่อยู่แหล่งปลูก**")
        if origin_main == "ประเทศไทย" and not df_addr.empty:
            a1, a2, a3 = st.columns(3)
            p_list = sorted(df_addr["จังหวัด"].unique().tolist())
            p_val = a1.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
            d_list = sorted(df_addr[df_addr["จังหวัด"] == p_val]["อำเภอ"].unique().tolist()) if p_val != "- เลือก -" else []
            a_val = a2.selectbox("อำเภอ", ["- เลือก -"] + d_list, key=f"a_{i}")
            t_list = sorted(df_addr[(df_addr["จังหวัด"] == p_val) & (df_addr["อำเภอ"] == a_val)]["ตำบล"].unique().tolist()) if a_val != "- เลือก -" else []
            t_val = a3.selectbox("ตำบล", ["- เลือก -"] + t_list, key=f"t_{i}")

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items_count += 1
    st.rerun()

# --- 5. ปุ่มดำเนินการ ---
if st.button("✅ ยืนยันและสร้าง PDF", type="primary", use_container_width=True):
    if not s_name or not s_email:
        st.error("กรุณากรอกข้อมูลในส่วนที่ 1 ให้ครบถ้วน")
    else:
        st.success("บันทึกข้อมูลเรียบร้อย กำลังเตรียมไฟล์ PDF...")
    
