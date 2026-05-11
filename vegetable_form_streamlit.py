import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import io

# --- 1. หัวฟอร์ม CPRAM ---
st.set_page_config(page_title="CPRAM - Supplier Daily Record", layout="centered")
st.title("🏭 CPRAM - แบบฟอร์มบันทึกวัตถุดิบรายวัน")
st.subheader("Supplier Daily Raw Material Record")

# --- การจัดการ State สำหรับการแก้ไขข้อมูล ---
if 'submitted_data' not in st.session_state:
    st.session_state.submitted_data = None

# --- 2. แบบฟอร์มกรอกข้อมูล ---
with st.form("raw_material_form"):
    supplier_email = st.text_input("อีเมลผู้ส่ง (สำหรับรับไฟล์ PDF)", placeholder="example@cpram.co.th")
    material_name = st.text_input("ชื่อวัตถุดิบ")
    quantity = st.number_input("จำนวน", min_value=0)
    unit = st.selectbox("หน่วย", ["กก.", "กล่อง", "ชิ้น"])
    
    submit_button = st.form_submit_button("บันทึกข้อมูล")

if submit_button:
    # เก็บข้อมูลลง Session State เพื่อให้สามารถ "เห็น" และ "แก้ไข" ได้
    st.session_state.submitted_data = {
        "email": supplier_email,
        "material": material_name,
        "quantity": quantity,
        "unit": unit
    }
    st.success("บันทึกข้อมูลเบื้องต้นสำเร็จ!")

# --- 3. ส่วนการแก้ไขและส่ง PDF ---
if st.session_state.submitted_data:
    st.write("---")
    st.info("ตรวจสอบข้อมูล: หากต้องการแก้ไข สามารถแก้ไขที่ฟอร์มด้านบนแล้วกดบันทึกใหม่")
    st.write(pd.DataFrame([st.session_state.submitted_data]))

    if st.button("ยืนยันและส่ง PDF ไปยังอีเมล"):
        data = st.session_state.submitted_data
        
        # --- สร้างไฟล์ PDF (In-memory) ---
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, f"CPRAM - Daily Record")
        p.drawString(100, 780, f"Material: {data['material']}")
        p.drawString(100, 760, f"Quantity: {data['quantity']} {data['unit']}")
        p.showPage()
        p.save()
        
        pdf_data = buffer.getvalue()

        # --- ฟังก์ชันส่งอีเมล (ตัวอย่างการตั้งค่า) ---
        try:
            # หมายเหตุ: คุณต้องมี SMTP Server (เช่น Gmail หรือ Outlook)
            msg = MIMEMultipart()
            msg['Subject'] = f"CPRAM Raw Material Record: {data['material']}"
            msg['From'] = "your-system-email@gmail.com"
            msg['To'] = data['email']
            
            body = "แจ้งข้อมูลการส่งวัตถุดิบ รายละเอียดตามเอกสารแนบ"
            msg.attach(MIMEText(body, 'plain'))
            
            part = MIMEApplication(pdf_data, Name="Record.pdf")
            part['Content-Disposition'] = 'attachment; filename="Record.pdf"'
            msg.attach(part)

            # โค้ดส่วนเชื่อมต่อ Server (ต้องระบุรหัสผ่านและ Server ที่ใช้งานจริง)
            # server = smtplib.SMTP('smtp.gmail.com', 587)
            # server.starttls()
            # server.login("user", "pass")
            # server.send_message(msg)
            # server.quit()
            
            st.success(f"ส่งไฟล์ PDF ไปที่ {data['email']} เรียบร้อยแล้ว!")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการส่งอีเมล: {e}")
