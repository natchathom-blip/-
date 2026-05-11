import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Digital Form", layout="wide")

# --- 2. ฟังก์ชันช่วยจัดการรูปภาพ ---
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
        df = pd.read_excel(file_path)
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    return pd.DataFrame()

df_addr = load_address_data()

# จัดการ State ของรายการวัตถุดิบ
if 'item_ids' not in st.session_state:
    st.session_state.item_ids = [0]
if 'next_id' not in st.session_state:
    st.session_state.next_id = 1

# --- 3. ส่วนหัว (Header) แบบไม่มีวันที่และมีกรอบ ---
logo_base64 = get_image_base64("image_9482bc.png") 

header_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center;">
            {f'<img src="data:image/png;base64,{logo_base64}" width="120">' if logo_base64 else ''}
            <div style="margin-left: 15px;">
                <b style="font-size: 20px; color: #2e7d32; line-height: 1.2;">CPRAM Co., Ltd.</b><br>
                <span style="font-size: 14px; color: #444;">ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</span>
            </div>
        </div>
        <div style="text-align: right;">
            <div style="border: 1.5px solid #333; padding: 5px 15px; display: inline-block; font-weight: bold; font-size: 18px; letter-spacing: 1px;">
                FR-QAS-10-000
            </div>
        </div>
    </div>
"""

st.markdown(header_html, unsafe_allow_html=True)

# ส่วนหัวชื่อแบบฟอร์ม
st.markdown("<h3 style='text-align: center; color: #2e7d32;'>แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>กรุณากรอกข้อมูลให้ครบถ้วน — เลือก จังหวัด/อำเภอ/ตำบล จาก dropdown ระบบจะกรอกรหัสไปรษณีย์ให้อัตโนมัติ</p>", unsafe_allow_html=True)
