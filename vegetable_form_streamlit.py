import streamlit as st
import pandas as pd
from datetime import datetime
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# --- 1. การตั้งค่าเบื้องต้นและ Style ---
st.set_page_config(page_title="CPRAM Supplier Record", layout="wide")

st.markdown("""
    <style>
    .section-header { 
        color: #2e7d32; font-size: 24px; font-weight: bold; 
        margin-top: 20px; border-bottom: 2px solid #2e7d32; padding-bottom: 5px; margin-bottom: 15px;
    }
    .item-box {
        background-color: #f1f8e9; padding: 25px; border-radius: 10px;
        border: 1px solid #c8e6c9; margin-bottom: 20px;
    }
    .cpram-logo {
        text-align: center; color: #d32f2f; font-size: 48px; font-weight: bold; margin-bottom: -10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. การจัดการ Session State (แก้ไขจุดที่ทำให้เกิด Error) ---
if 'items' not in st.session_state:
    st.session_state.items = [{"id": 0}]  # เริ่มต้นด้วย 1 รายการ
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# --- 3. ส่วนหัวข้อ (Header) ---
st.markdown('<div class="cpram-logo">CPRAM</div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center;">Supplier Daily Material Record Form</h3>', unsafe_allow_html=True)

# --- 4. ส่วนที่ 1: ข้อมูลผู้ส่งมอบ ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    supplier_name = st.text_input("ผู้ส่งมอบ (Supplier) *", key="supplier_name")
    supplier_email = st.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", key="supplier_email")
with col2:
    delivery_date = st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now(), key="delivery_date")
    recorded_by = st.text_input("ลงชื่อผู้กรอก", key="recorded_by")
with col3:
    delivery_time = st.text_input("เวลาส่ง", placeholder="เช่น 14:00 น.", key="delivery_time")
    origin_country = st.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "อื่นๆ"], key="origin_country")

# --- 5. ส่วนที่ 2: รายการวัตถุดิบ (Loop สร้างฟอร์ม) ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

# ฟังก์ชันสำหรับเพิ่ม/ลบ รายการ
def add_item():
    st.session_state.items.append({"id": len(st.session_state.items)})

def remove_item(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)
    else:
        st.warning("ต้องมีอย่างน้อย 1 รายการ")

# สร้างตัวแปรเก็บข้อมูลชั่วคราว
all_item_data = []

# ใช้ List ที่มีอยู่ใน Session State รัน Loop
for i, item in enumerate(st.session_state.items):
    with st.container():
        st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
        h_col1, h_col2 = st.columns([0.8, 0.2])
        h_col1.subheader(f"รายการที่ {i+1}")
        if h_col2.button(f"✕ ลบรายการที่ {i+1}", key=f"del_btn_{i}"):
            remove_item(i)
            st.rerun()

        # แถวที่ 1
        r1c1, r1c2, r1c3 = st.columns(3)
        mat_type = r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        mat_code = r1c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
        qty = r1c3.text_input("จำนวน (KG) *", key=f"qty_{i}")

        # แถวที่ 2
        r2c1, r2c2, r2c3 = st.columns(3)
        h_date = r2c1.date_input("วันที่เก็บเกี่ยว", key=f"h_date_{i}")
        h_time = r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"h_time_{i}")
        c_date = r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"c_date_{i}")

        # แถวที่ 3
        r3c1, r3c2, r3c3 = st.columns(3)
        c_time = r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00-09:30", key=f"c_time_{i}")
        grower = r3c2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        gap = r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

        # แถวที่ 4 (ที่อยู่)
        st.markdown("**📍 ที่อยู่แหล่งปลูก**")
        r4c1, r4c2, r4c3, r4c4 = st.columns(4)
        farm_id = r4c1.text_input("รหัสไร่", key=f"farm_{i}")
        addr = r4c2.text_input("ที่อยู่เลขที่", key=f"addr_{i}")
        moo = r4c3.text_input("หมู่ที่", key=f"moo_{i}")
        prov = r4c4.text_input("จังหวัด", key=f"prov_{i}")

        # แถวที่ 5
        r5c1, r5c2, r5c3, r5c4 = st.columns(4)
        zipc = r5c1.text_input("รหัสไปรษณีย์", key=f"zip_{i}")
        breed = r5c2.text_input("สายพันธุ์", key=f"breed_{i}")
        p_style = r5c3.selectbox("ลักษณะการปลูก", ["ดิน", "ไฮโดรโปนิกส์"], key=f"style_{i}")
        p_loc = r5c4.selectbox("ลักษณะสถานที่ปลูก", ["โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # รวบรวมข้อมูลแต่ละรายการใส่ List
        all_item_data.append({
            "ชนิดวัตถุดิบ": mat_type, "Code": mat_code, "จำนวน": qty,
            "วันที่เก็บเกี่ยว": h_date, "สายพันธุ์": breed, "ผู้ปลูก": grower
        })

# ปุ่มเพิ่มรายการ
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ระบบการส่งข้อมูลและแก้ไข ---
st.write("---")
if st.button("ตรวจสอบข้อมูลและยืนยันการส่ง (Confirm Submit)", type="primary"):
    if not supplier_name or not supplier_email:
        st.error("กรุณากรอกข้อมูล 'ผู้ส่งมอบ' และ 'อีเมล' ให้ครบถ้วน")
    else:
        st.session_state.final_summary = all_item_data
        st.session_state.form_submitted = True

# เมื่อกด Submit แล้วจะแสดงตารางให้ตรวจสอบ (แก้ไขได้โดยการเปลี่ยนค่าข้างบนแล้วกด Submit ใหม่)
if st.session_state.form_submitted:
    st.info("ตรวจสอบข้อมูลด้านล่าง หากถูกต้องแล้วกด 'ส่ง PDF ไปยังอีเมล'")
    st.table(pd.DataFrame(st.session_state.final_summary))
    
    if st.button("📧 ส่ง PDF ไปยังอีเมลทันที"):
        # ส่วนนี้คือ Logic การส่งอีเมล (คุณต้องใส่ SMTP ของคุณ)
        st.success(f"ระบบได้ส่งไฟล์ PDF ไปที่ {supplier_email} เรียบร้อยแล้ว! (จำลองระบบส่งอีเมล)")
        st.balloons()
