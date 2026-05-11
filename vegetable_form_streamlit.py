import streamlit as st
import pandas as pd
import os
import base64
from fpdf import FPDF

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

# ฟังก์ชันดึงรูปภาพ (แก้ไขให้เสถียรขึ้น)
def get_image_as_base64(file_name):
    # พยายามหาไฟล์ในโฟลเดอร์ปัจจุบัน
    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# โหลดข้อมูลที่อยู่
@st.cache_data
def load_address_data():
    file_path = 'thailand.xlsx'
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return pd.DataFrame()

df_addr = load_address_data()

# --- 2. ส่วนหัวแบบฟอร์ม (Header) ปรับปรุงใหม่ ---
# ตรวจสอบชื่อไฟล์ให้ตรงกับใน GitHub (image_9482bc.png)
logo_base64 = get_image_as_base64("image_9482bc.png")

if logo_base64:
    # แสดงผลแบบมีรูปภาพตามโครงสร้าง image_9747d4.png
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{logo_base64}" width="180">
            <div style="text-align: right; line-height: 1.2;">
                <b style="font-size: 20px; color: #333;">FR-QAS-10-000</b><br>
                <span style="font-size: 14px; color: #666;">มีผลใช้งาน: 2026-05-08</span>
            </div>
        </div>
    """, unsafe_allow_html=True) #
else:
    # หากยังไม่ขึ้น ให้ใช้โลโก้ตัวอักษรแทนเพื่อไม่ให้ขึ้น [Logo Missing]
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
            <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 24px;">cpram</div>
            <div style="text-align: right; line-height: 1.2;">
                <b style="font-size: 20px; color: #333;">FR-QAS-10-000</b><br>
                <span style="font-size: 14px; color: #666;">มีผลใช้งาน: 2026-05-08</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.subheader("แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด")

# --- 3. ส่วนข้อมูล (ดึงฟิลด์กลับมาครบถ้วน) ---
st.markdown("#### ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
col1, col2, col3 = st.columns(3)
s_name = col1.text_input("ผู้ส่งมอบ (Supplier) *") # [cite: 2]
s_date = col2.date_input("วันที่ส่งวัตถุดิบ *") # [cite: 5]
origin = col3.selectbox("แหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"])

# ส่วนที่ 2: รายการวัตถุดิบ [cite: 6-25]
if 'rows' not in st.session_state: st.session_state.rows = 1

for i in range(st.session_state.rows):
    with st.expander(f"รายการวัตถุดิบที่ {i+1}", expanded=True):
        r1, r2, r3 = st.columns([2, 1, 1])
        r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}") # [cite: 7]
        r2.text_input("Code", key=f"code_{i}") # [cite: 8]
        r3.number_input("จำนวน (KG)", key=f"qty_{i}") # [cite: 9]
        
        r4, r5, r6 = st.columns(3)
        r4.text_input("สายพันธุ์", key=f"breed_{i}") # [cite: 10]
        r5.selectbox("ลักษณะการปลูก", ["ปลูกดินยกพื้น", "ปลูกไฮโดรโปนิกส์", "อื่นๆ"], key=f"type_{i}") # [cite: 11]
        r6.text_input("เลขที่ GAP", key=f"gap_{i}") # [cite: 23]

# --- 4. ปุ่มดาวน์โหลด PDF (แก้ Error Character "บ") ---
if st.button("✅ ยืนยันและดาวน์โหลด PDF", type="primary"):
    pdf = FPDF()
    pdf.add_page()
    # ตรวจสอบชื่อไฟล์ฟอนต์ Sarabun-Regular.ttf ใน GitHub
    if os.path.exists("Sarabun-Regular.ttf"):
        pdf.add_font('Sarabun', '', 'Sarabun-Regular.ttf', uni=True)
        pdf.set_font('Sarabun', '', 14)
        pdf.cell(0, 10, f"ผู้ส่งมอบ: {s_name}", ln=True)
        # แก้ปัญหา Character "บ" ด้วยการ encode แบบปลอดภัย
        pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 โหลดไฟล์ PDF", pdf_out, "CPRAM_Form.pdf")
    else:
        st.error("ไม่พบไฟล์ฟอนต์ Sarabun-Regular.ttf")
