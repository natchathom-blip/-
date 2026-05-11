import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import io

# --- การตั้งค่าเบื้องต้น ---
st.set_page_config(page_title="CPRAM - Supplier Record", layout="wide")

# ส่วนหัวฟอร์ม CPRAM
st.markdown("<h1 style='text-align: center; color: #E31E24;'>CPRAM</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>แบบฟอร์มรายละเอียดข้อมูลวัตถุดิบ (Supplier Daily Record)</h3>", unsafe_allow_html=True)
st.write("---")

# --- การจัดการ State เพื่อให้แก้ไขข้อมูลได้ ---
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# --- ส่วนฟอร์มกรอกข้อมูล ---
with st.form("cpram_material_form"):
    st.subheader("1. ข้อมูลวัตถุดิบและแหล่งที่มา")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        mat_type = st.text_input("ชนิดวัตถุดิบที่ส่งให้ CPRAM")
        breed = st.text_input("สายพันธุ์")
    with col2:
        mat_code = st.text_input("Code วัตถุดิบ")
        plant_style = st.text_input("ลักษณะการปลูก")
    with col3:
        quantity = st.text_input("จำนวน (เช่น 500 กก.)")
        plant_system = st.text_input("ระบบการปลูก")

    st.write("---")
    st.subheader("2. ข้อมูลการเก็บเกี่ยวและผลิต")
    col4, col5 = st.columns(2)
    with col4:
        harvest_date = st.date_input("วันที่เก็บเกี่ยววัตถุดิบ")
        harvest_time = st.time_input("เวลาเก็บเกี่ยว")
    with col5:
        process_date = st.date_input("วันที่ล้าง/ตัดแต่ง")
        process_time = st.time_input("เวลาล้าง/ตัดแต่ง")

    st.write("---")
    st.subheader("3. ข้อมูลผู้ปลูกและสถานที่")
    grower_name = st.text_input("ชื่อผู้ปลูก")
    col6, col7 = st.columns(2)
    with col6:
        gap_no = st.text_input("เลขที่ GAP")
    with col7:
        farm_code = st.text_input("รหัสไร่")
    address = st.text_area("ที่อยู่/ที่ตั้งไร่")
    
    st.write("---")
    recipient_email = st.text_input("ระบุอีเมลสำหรับรับไฟล์ PDF (เช่น อีเมลของคุณ)", help="ไฟล์จะถูกส่งไปยังที่อยู่นี้")

    submit_btn = st.form_submit_button("บันทึกและตรวจสอบข้อมูล")

if submit_btn:
    # เก็บค่าลง session_state
    st.session_state.form_data = {
        "ชนิดวัตถุดิบ": mat_type, "Code": mat_code, "จำนวน": quantity,
        "สายพันธุ์": breed, "ลักษณะการปลูก": plant_style, "ระบบการปลูก": plant_system,
        "วันที่เก็บเกี่ยว": str(harvest_date), "เวลาเก็บเกี่ยว": str(harvest_time),
        "วันที่ล้าง": str(process_date), "เวลาล้าง": str(process_time),
        "ชื่อผู้ปลูก": grower_name, "เลขที่ GAP": gap_no, "รหัสไร่": farm_code,
        "ที่อยู่": address, "email": recipient_email
    }
    st.session_state.submitted = True

# --- ส่วนตรวจสอบ/แก้ไข และส่ง PDF ---
if st.session_state.submitted:
    st.info("💡 ข้อมูลถูกบันทึกชั่วคราวแล้ว คุณสามารถแก้ไขข้อมูลด้านบนแล้วกดบันทึกใหม่ หรือกดส่ง PDF หากข้อมูลถูกต้องแล้ว")
    
    # แสดงตารางสรุปข้อมูลที่จะส่ง
    df = pd.DataFrame([st.session_state.form_data]).T
    df.columns = ["รายละเอียด"]
    st.table(df)

    if st.button("ยืนยันส่งข้อมูลและส่งไฟล์ PDF"):
        data = st.session_state.form_data
        
        # 1. สร้าง PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        # หมายเหตุ: ในการใช้งานจริงต้องโหลด Font ภาษาไทยเพิ่มเพื่อให้แสดงผลภาษาไทยได้
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 800, "CPRAM - Material Record Report")
        p.setFont("Helvetica", 12)
        y = 770
        for key, value in data.items():
            p.drawString(50, y, f"{key}: {value}")
            y -= 20
        p.showPage()
        p.save()
        pdf_content = buffer.getvalue()

        # 2. ส่งอีเมล
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"CPRAM Record: {data['ชนิดวัตถุดิบ']} ({data['วันที่เก็บเกี่ยว']})"
            msg['From'] = "your-system@gmail.com" # ตั้งค่าอีเมลระบบ
            msg['To'] = data['email']
            
            msg.attach(MIMEText("เรียน ผู้เกี่ยวข้อง\n\nแนบไฟล์สรุปข้อมูลวัตถุดิบมาพร้อมกับอีเมลฉบับนี้", 'plain'))
            
            attachment = MIMEApplication(pdf_content, Name="CPRAM_Record.pdf")
            attachment['Content-Disposition'] = 'attachment; filename="CPRAM_Record.pdf"'
            msg.attach(attachment)

            # --- ส่วนเชื่อมต่อ Server (ต้องใส่ข้อมูล SMTP ของคุณ) ---
            # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            #     server.login("USER", "APP_PASSWORD")
            #     server.send_message(msg)
            
            st.success(f"ส่งไฟล์ PDF ไปยัง {data['email']} สำเร็จแล้ว!")
            st.balloons()
            
        except Exception as e:
            st.error(f"ไม่สามารถส่งอีเมลได้: {e}")
