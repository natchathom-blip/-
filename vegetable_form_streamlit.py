import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel('thailand.xlsx')
    df.columns = [str(c).strip() for c in df.columns]
    return df

df_addr = load_data()

# --- 2. PDF CONFIG (ปรับระยะตามสั่ง) ---
class CPRAM_PDF(FPDF):
    def header(self):
        # ใช้ไฟล์ Sarabun-Regular.ttf ที่คุณมีใน GitHub
        self.add_font('THSarabun', '', 'Sarabun-Regular.ttf', uni=True)
        self.set_font('THSarabun', '', 14)
        self.cell(0, 10, 'แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบ (FR-QAS-10-000)', 0, 1, 'C')
        self.ln(5)

def generate_pdf(s_info, items):
    pdf = CPRAM_PDF()
    # 1. Page Threshold 80mm ป้องกันตัวอักษรถูกตัด
    pdf.set_auto_page_break(auto=True, margin=80) 
    pdf.add_page()
    
    # 2. Font Size 10pt
    pdf.set_font('THSarabun', '', 10)
    
    # 3. ระยะบรรทัด 12mm และ Offset Value +4mm
    line_h = 12 
    val_offset = 44 # (Label 40mm + 4mm)

    pdf.cell(0, 10, "ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ", 0, 1)
    # แสดงข้อมูลพร้อม Offset
    pdf.text(10, pdf.get_y(), "ผู้ส่งมอบ:"); pdf.text(10 + val_offset, pdf.get_y(), s_info['name']); pdf.ln(line_h)
    pdf.text(10, pdf.get_y(), "อีเมล:"); pdf.text(10 + val_offset, pdf.get_y(), s_info['email']); pdf.ln(line_h)

    pdf.ln(5)
    pdf.cell(0, 10, "ส่วนที่ 2 — รายการวัตถุดิบ", 0, 1)
    for i, item in enumerate(items):
        pdf.cell(0, 10, f"รายการที่ {i+1}", 0, 1)
        pdf.text(15, pdf.get_y(), "ชนิดวัตถุดิบ:"); pdf.text(15 + val_offset, pdf.get_y(), item['mat']); pdf.ln(line_h)
        pdf.text(15, pdf.get_y(), "รหัสไร่:"); pdf.text(15 + val_offset, pdf.get_y(), item['farm']); pdf.ln(line_h)
        pdf.ln(4)
        
    return pdf.output()

# --- 3. UI DISPLAY ---
# แสดง Header ตามภาพ image_a5b629.png
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

# ส่วนการกรอกข้อมูล (ใช้ Session State เพื่อไม่ให้ข้อมูลหาย)
if 'items_count' not in st.session_state: st.session_state.items_count = 1

with st.form("supplier_form"):
    s_name = st.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
    s_email = st.text_input("อีเมลรับไฟล์ PDF *", key="s_email")
    
    items_data = []
    for i in range(st.session_state.items_count):
        st.write(f"รายการที่ {i+1}")
        mat = st.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        farm = st.text_input("รหัสไร่", key=f"farm_{i}")
        items_data.append({'mat': mat, 'farm': farm})
        
    submit = st.form_submit_button("ยืนยันข้อมูลและส่ง PDF", type="primary")

if submit:
    if s_name and s_email:
        pdf_file = generate_pdf({'name': s_name, 'email': s_email}, items_data)
        st.success(f"บันทึกข้อมูลสำเร็จ! ระบบเตรียมส่ง PDF ไปที่ {s_email}")
        st.download_button("ดาวน์โหลด PDF เพื่อตรวจสอบ", data=pdf_file, file_name="record.pdf")
