import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email(pdf_content, receiver_email):
    # --- จุดที่ต้องแก้ไข ---
    sender_email = "your_email@gmail.com"  # อีเมลของคุณ
    password = "xxxx xxxx xxxx xxxx"       # ต้องเป็น App Password 16 หลัก (ไม่ใช่รหัสผ่านเมลปกติ)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบ"

    # แนบไฟล์ PDF
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_content)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="CPRAM_Record.pdf"')
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการส่ง: {e}")
        return False
