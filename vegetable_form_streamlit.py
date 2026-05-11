import streamlit as st
import pandas as pd
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# --- CONFIG PDF CLASS ---
class CPRAM_PDF(FPDF):
    def header(self):
        self.add_font('THSarabun', '', 'Sarabun-Regular.ttf')
        self.set_font('THSarabun', '', 14)
        self.cell(0, 10, 'แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบ (FR-QAS-10-000)', 0, 1, 'C')
        self.ln(5)

# --- FUNCTION: GENERATE PDF (ปรับระยะตามสั่ง) ---
def create_pdf(supplier_info, items_list):
    # 1. Page Threshold 80mm ป้องกันตัวอักษรถูกตัดท้ายหน้า
    pdf = CPRAM_PDF()
    pdf.set_auto_page_break(auto=True, margin=80) 
    pdf.add_page()
    
    # 2. Font Size 10pt
    pdf.set_font('THSarabun', '', 10)
    
    # 3. Settings: ระยะบรรทัด 12mm และ Offset Value +4mm
    line_h = 12 
    label_w = 40
    val_offset = label_w + 4 

    # ข้อมูลส่วนที่ 1
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, "ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ", 0, 1)
    pdf.set_text_color(0, 0, 0)
    
    fields_s1 = [
        ("ผู้ส่งมอบ:", supplier_info['name']),
        ("อีเมล:", supplier_info['email']),
        ("วันที่ส่ง:", str(supplier_info['date']))
    ]
    
    for lbl, val in fields_s1:
        curr_y = pdf.get_y()
        pdf.text(10, curr_y, lbl)
        pdf.text(10 + val_offset, curr_y, str(val)) # เพิ่ม Offset 4mm
        pdf.ln(line_h) # ระยะบรรทัด 12mm

    # ข้อมูลส่วนที่ 2 (รายการวัตถุดิบ)
    pdf.ln(5)
    pdf.set_text_color(46, 125, 50)
    pdf.cell(0, 10, "ส่วนที่ 2 — รายการวัตถุดิบ", 0, 1)
    pdf.set_text_color(0, 0, 0)

    for i, item in enumerate(items_list):
        pdf.set_font('THSarabun', 'B', 10)
        pdf.cell(0, 10, f"รายการที่ {i+1}", 0, 1)
        pdf.set_font('THSarabun', '', 10)
        
        item_fields = [
            ("ชนิดวัตถุดิบ:", item.get('mat', '')),
            ("Code:", item.get('code', '')),
            ("จำนวน (KG):", str(item.get('qty', '0'))),
            ("แหล่งปลูก:", f"{item.get('tam', '')} {item.get('amp', '')} {item.get('prov', '')}"),
            ("รหัสไปรษณีย์:", item.get('zip', ''))
        ]
        
        for lbl, val in item_fields:
            curr_y = pdf.get_y()
            pdf.text(15, curr_y, lbl)
            pdf.text(15 + val_offset, curr_y, str(val))
            pdf.ln(line_h)
        pdf.ln(4) # เว้นระยะระหว่างกลุ่มรายการ

    return pdf.output()

# --- FUNCTION: SEND EMAIL ---
def send_email(pdf_content, to_email):
    # ตั้งค่า Email (แนะนำใช้ App Password ของ Gmail)
    from_email = "your_email@gmail.com" 
    password = "your_app_password" 

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = f"CPRAM Daily Record - {datetime.now().strftime('%Y-%m-%d')}"

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_content)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="CPRAM_Record.pdf"')
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# --- UI LOGIC (PREVIEW & EDIT) ---
# ... (ส่วนการกรอกข้อมูลและ Session State เหมือนเดิม) ...

if st.button("ยืนยันข้อมูลและส่ง PDF", type="primary"):
    # ดึงข้อมูลจาก Session State มาเตรียมทำ PDF
    s_info = {"name": st.session_state.s_name, "email": st.session_state.s_email, "date": st.session_state.d_date}
    
    # รวบรวมข้อมูลรายการวัตถุดิบ
    items_to_print = []
    for i in range(st.session_state.items_count):
        items_to_print.append({
            'mat': st.session_state.get(f"mat_{i}"),
            'code': st.session_state.get(f"code_{i}"),
            'qty': st.session_state.get(f"qty_{i}"),
            'prov': st.session_state.get(f"prov_{i}"),
            'amp': st.session_state.get(f"amp_{i}"),
            'tam': st.session_state.get(f"tam_{i}"),
            'zip': st.session_state.get(f"zip_{i}")
        })

    # สร้าง PDF
    pdf_out = create_pdf(s_info, items_to_print)
    
    # ส่งอีเมล
    success = send_email(pdf_out, s_info['email'])
    if success:
        st.success(f"ส่งไฟล์ PDF ไปยัง {s_info['email']} เรียบร้อยแล้ว!")
        st.download_button("ดาวน์โหลด PDF ไว้ในเครื่อง", data=pdf_out, file_name="CPRAM_Record.pdf")
