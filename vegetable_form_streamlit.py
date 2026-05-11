from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class CPRAM_PDF(FPDF):
    def header(self):
        self.set_font('THSarabun', 'B', 16)
        self.cell(0, 10, 'แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด', 0, 1, 'C')
        self.ln(5)

def generate_and_send_email(data_summary, target_email):
    pdf = CPRAM_PDF()
    pdf.add_page()
    # เพิ่ม Font ภาษาไทย (ต้องมีไฟล์ .ttf ในโฟลเดอร์)
    pdf.add_font('THSarabun', '', 'Sarabun-Regular.ttf', uni=True)
    pdf.set_font('THSarabun', '', 10) # ปรับขนาดตัวอักษรเป็น 10
    
    # ตั้งค่า Page Threshold เป็น 80mm
    pdf.set_auto_page_break(auto=True, margin=80) 
    
    y = 30
    for item in data_summary:
        if y > 220: # ตรวจสอบระยะก่อนขึ้นหน้าใหม่
            pdf.add_page()
            y = 30
            
        pdf.set_xy(10, y)
        # ปรับระยะห่างบรรทัด และ Offset ของ Value (เพิ่ม 4mm)
        pdf.text(10, y, f"ชนิดวัตถุดิบ:")
        pdf.text(10 + 35 + 4, y, f"{item['mat_type']}") # Offset เพิ่ม 4mm
        
        y += 12 # เพิ่มระยะห่างระหว่างบรรทัด (เดิม 10 เป็น 12)

    # บันทึกไฟล์
    file_path = "summary_report.pdf"
    pdf.output(file_path)

    # --- ส่วนส่งอีเมล ---
    msg = MIMEMultipart()
    msg['From'] = "your_system@email.com"
    msg['To'] = target_email
    msg['Subject'] = "แบบบันทึกข้อมูล CPRAM ประจำวัน"

    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {file_path}")
        msg.attach(part)

    # เชื่อมต่อ Server (ตัวอย่าง Gmail)
    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login("user", "pass")
    # server.send_message(msg)
    # server.quit()
