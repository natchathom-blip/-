import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import io

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

@st.cache_data
def load_address():
    try:
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_addr = load_address()

# --- 2. PDF GENERATOR (ระยะตามสั่งเป๊ะๆ) ---
class CPRAM_PDF(FPDF):
    def header(self):
        self.add_font('THSarabun', '', 'Sarabun-Regular.ttf', uni=True)
        self.set_font('THSarabun', '', 14)
        self.cell(0, 10, 'แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบ (FR-QAS-10-000)', 0, 1, 'C')
        self.ln(5)

def create_pdf(s_info, items):
    pdf = CPRAM_PDF()
    pdf.set_auto_page_break(auto=True, margin=80) # Threshold 80mm
    pdf.add_page()
    pdf.set_font('THSarabun', '', 10) # FS 10
    
    line_h = 12 # Line spacing 12mm
    offset = 44 # Label offset 40mm + 4mm gap

    # ส่วนที่ 1
    pdf.cell(0, 10, "ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ", 0, 1)
    pdf.text(10, pdf.get_y(), "ผู้ส่งมอบ:"); pdf.text(10 + offset, pdf.get_y(), s_info['name']); pdf.ln(line_h)
    pdf.text(10, pdf.get_y(), "อีเมล:"); pdf.text(10 + offset, pdf.get_y(), s_info['email']); pdf.ln(line_h)

    # ส่วนที่ 2
    pdf.ln(5)
    for i, item in enumerate(items):
        pdf.cell(0, 10, f"รายการที่ {i+1}", 0, 1)
        fields = [
            ("ชนิดวัตถุดิบ:", item['mat']),
            ("รหัสไร่:", item['farm']),
            ("ตำบล:", item['tam']),
            ("อำเภอ:", item['amp']),
            ("จังหวัด:", item['prov']),
            ("รหัสไปรษณีย์:", item['zip'])
        ]
        for label, val in fields:
            pdf.text(15, pdf.get_y(), label)
            pdf.text(15 + offset, pdf.get_y(), str(val))
            pdf.ln(line_h)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 3. EMAIL SENDER ---
def send_instant_email(pdf_bytes, target_email, supplier_name):
    from_email = "your_email@gmail.com" # อีเมลผู้ส่ง
    app_password = "xxxx xxxx xxxx xxxx" # รหัส App Password 16 หลัก
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = target_email
    msg['Subject'] = f"เอกสารส่งมอบวัตถุดิบ - {supplier_name}"
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="CPRAM_Record_{supplier_name}.pdf"')
    msg.attach(part)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, app_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"การส่งอีเมลขัดข้อง: {e}")
        return False

# --- 4. UI LOGIC ---
if 'items_count' not in st.session_state: st.session_state.items_count = 1

# ส่วนของฟอร์ม (ใช้ Key เพื่อไม่ให้ข้อมูลหาย)
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2 = st.columns(2)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_email = c2.text_input("อีเมลสำหรับรับ PDF *", key="s_email")

st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")
items_data = []
for i in range(st.session_state.items_count):
    with st.expander(f"รายการที่ {i+1}", expanded=True):
        mat = st.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        farm = st.text_input("รหัสไร่", key=f"farm_{i}")
        
        # Address Logic (ตำบล/อำเภอ/จังหวัด/รหัสไปรษณีย์)
        # ... (ส่วน Selectbox ดึงข้อมูลจาก df_addr เหมือนเดิม) ...
        # สมมติได้ตัวแปร prov, amp, tam, zip_code มาแล้ว
        items_data.append({'mat': mat, 'farm': farm, 'prov': '...', 'amp': '...', 'tam': '...', 'zip': '...'})

# ปุ่มส่ง
if st.button("ยืนยันข้อมูลและส่ง PDF ทันที", type="primary"):
    if not s_name or not s_email:
        st.warning("กรุณากรอกชื่อและอีเมลให้ครบถ้วน")
    else:
        with st.spinner('กำลังสร้าง PDF และส่งเมล...'):
            # 1. สร้าง PDF
            pdf_out = create_pdf({'name': s_name, 'email': s_email}, items_data)
            
            # 2. ส่งเมลทันที
            success = send_instant_email(pdf_out, s_email, s_name)
            
            if success:
                st.success(f"✅ ส่งสำเร็จ! ไฟล์ถูกส่งไปที่ {s_email} แล้ว")
                st.balloons()
            
            # 3. ให้ปุ่ม Download สำรองไว้ด้วย
            st.download_button("ดาวน์โหลดไฟล์ PDF สำรอง", data=pdf_out, file_name="record.pdf")

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items_count += 1
    st.rerun()
