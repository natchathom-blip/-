from fpdf import FPDF
import streamlit as st

class CPRAM_PDF(FPDF):
    def header(self):
        # ตั้งค่า Font สำหรับ Header (ต้องมีไฟล์ font ในเครื่อง)
        try:
            self.add_font('THSarabun', 'B', 'Sarabun-Bold.ttf', uni=True)
            self.set_font('THSarabun', 'B', 14)
        except:
            self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบ (CPRAM)', 0, 1, 'C')
        self.ln(5)

def create_pdf(items_data, supplier_info):
    # ปรับ Page Break Threshold เป็น 80mm ตามสั่ง (ป้องกันถูกตัด)
    pdf = CPRAM_PDF()
    pdf.set_auto_page_break(auto=True, margin=80) 
    pdf.add_page()
    
    # เพิ่ม Font ภาษาไทย (Sarabun-Regular.ttf)
    try:
        pdf.add_font('THSarabun', '', 'Sarabun-Regular.ttf', uni=True)
        pdf.set_font('THSarabun', '', 10) # ขนาดตัวอักษร 10pt ตามสั่ง
    except:
        pdf.set_font('Arial', '', 10)

    # ระยะบรรทัดห่างขึ้น (Line Spacing = 12mm)
    line_height = 12 
    # Offset ของ Value (Label ห่างจาก Value เพิ่ม 4mm)
    label_width = 40 
    value_offset = label_width + 4 

    # --- ส่วนที่ 1: ข้อมูลผู้ส่งมอบ ---
    pdf.set_font('', 'B', 11)
    pdf.cell(0, 10, 'ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ', 0, 1)
    pdf.set_font('', '', 10)
    
    pdf.text(10, pdf.get_y(), "ผู้ส่งมอบ:")
    pdf.text(10 + value_offset, pdf.get_y(), f"{supplier_info['name']}")
    pdf.ln(line_height)

    # --- ส่วนที่ 2: รายการวัตถุดิบ ---
    pdf.set_font('', 'B', 11)
    pdf.cell(0, 10, 'ส่วนที่ 2 — รายการวัตถุดิบ', 0, 1)
    pdf.set_font('', '', 10)

    for i, item in enumerate(items_data):
        # แสดงรายการที่ i
        pdf.cell(0, 10, f"รายการที่ {i+1}", 0, 1)
        
        # ฟิลด์ข้อมูล พร้อมระยะห่าง Value Offset 4mm
        fields = [
            ("ชนิดวัตถุดิบ:", item['mat']),
            ("Code:", item['code']),
            ("จำนวน (KG):", str(item['qty'])),
            ("วันที่เก็บเกี่ยว:", str(item['hd'])),
            ("สถานที่ปลูก:", f"{item['tam']} {item['amp']} {item['prov']}")
        ]

        for label, val in fields:
            curr_y = pdf.get_y()
            pdf.text(15, curr_y, label)
            pdf.text(15 + value_offset, curr_y, val) # ขยับ Value ไม่ให้ทับ Label
            pdf.ln(line_height) # บรรทัดห่างขึ้น อ่านง่าย
            
        pdf.ln(5) # เว้นระยะระหว่างรายการ
        
    return pdf.output(dest='S').encode('latin-1')

# --- ส่วนส่งอีเมล (Concept) ---
def send_email_with_pdf(pdf_content, target_email):
    # ใช้ st.info หรือระบบ SMTP ส่งออกไปยัง target_email
    st.info(f"ระบบกำลังเตรียมส่ง PDF ไปที่: {target_email}")
    # (ใส่โค้ด smtplib ตรงนี้)
