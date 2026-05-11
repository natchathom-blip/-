import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- 1. การตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

st.markdown("""
    <style>
    .section-header { color: #2e7d32; font-size: 22px; font-weight: bold; border-bottom: 2px solid #2e7d32; margin-bottom: 20px; }
    .item-box { background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    .cpram-logo { text-align: center; color: #d32f2f; font-size: 40px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. แก้ปัญหา Error บรรทัด 69: ตรวจสอบและสร้าง Session State ก่อนเริ่มทำงาน ---
if 'items' not in st.session_state:
    st.session_state.items = [{"id": 0}]  # สร้างรายการเริ่มต้น

# --- 3. ฟังก์ชันสำหรับเพิ่ม/ลบรายการ (ป้องกันการ Refresh แล้ว Error) ---
def add_item_callback():
    st.session_state.items.append({"id": len(st.session_state.items)})

def remove_item_callback(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)
    else:
        st.warning("ต้องมีอย่างน้อย 1 รายการ")

# --- 4. หัวฟอร์ม CPRAM ---
st.markdown('<div class="cpram-logo">CPRAM</div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center;">Supplier Daily Material Record Form</h3>', unsafe_allow_html=True)

# --- 5. ส่วนที่ 1: ข้อมูลผู้ส่งมอบ ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    supplier_name = st.text_input("ผู้ส่งมอบ (Supplier) *", key="main_supplier")
    supplier_email = st.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", key="main_email")
with col2:
    delivery_date = st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now(), key="main_date")
    recorded_by = st.text_input("ลงชื่อผู้กรอก", key="main_recorder")
with col3:
    delivery_time = st.text_input("เวลาส่ง", placeholder="เช่น 14:00 น.", key="main_time")
    origin_country = st.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "อื่นๆ"], key="main_country")

# --- 6. ส่วนที่ 2: รายการวัตถุดิบ (จุดที่เคย Error) ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

current_material_data = []

# ใช้ List ที่มีอยู่ใน session_state รัน Loop สร้าง Form
# เพิ่มความปลอดภัยโดยการเช็คเงื่อนไขก่อนรัน enumerate
if "items" in st.session_state:
    for i, item in enumerate(st.session_state.items):
        with st.container():
            st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
            h_col1, h_col2 = st.columns([0.85, 0.15])
            h_col1.subheader(f"รายการที่ {i+1}")
            
            # ปุ่มลบรายการ (ใช้ Callback เพื่อความเสถียร)
            h_col2.button(f"✕ ลบรายการที่ {i+1}", key=f"del_{i}", on_click=remove_item_callback, args=(i,))

            # แถวข้อมูลหลัก
            r1c1, r1c2, r1c3 = st.columns(3)
            m_type = r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_t_{i}")
            m_code = r1c2.text_input("Code", key=f"mat_c_{i}")
            m_qty = r1c3.text_input("จำนวน (KG) *", key=f"mat_q_{i}")

            # แถววันเวลา
            r2c1, r2c2, r2c3 = st.columns(3)
            h_d = r2c1.date_input("วันที่เก็บเกี่ยว", key=f"mat_hd_{i}")
            h_t = r2c2.text_input("เวลาเก็บเกี่ยว", key=f"mat_ht_{i}")
            c_d = r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"mat_cd_{i}")

            # ข้อมูลผู้ปลูก
            r3c1, r3c2, r3c3 = st.columns(3)
            c_t = r3c1.text_input("เวลาที่ล้างทำความสะอาด", key=f"mat_ct_{i}")
            grower = r3c2.text_input("ชื่อผู้ปลูก", key=f"mat_grow_{i}")
            gap = r3c3.text_input("เลขที่ GAP", key=f"mat_gap_{i}")

            # ที่อยู่และสายพันธุ์
            st.markdown("📍 **รายละเอียดเพิ่มเติม**")
            r4c1, r4c2, r4c3, r4c4 = st.columns(4)
            farm = r4c1.text_input("รหัสไร่", key=f"mat_farm_{i}")
            breed = r4c2.text_input("สายพันธุ์", key=f"mat_breed_{i}")
            style = r4c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ดิน", "ไฮโดรโปนิกส์"], key=f"mat_style_{i}")
            loc = r4c4.selectbox("สถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"mat_loc_{i}")

            st.markdown('</div>', unsafe_allow_html=True)
            
            # เก็บข้อมูลเข้าลิสต์ชั่วคราว
            current_material_data.append({
                "รายการ": i+1, "ชนิดวัตถุดิบ": m_type, "จำนวน": m_qty, "วันที่เก็บเกี่ยว": h_d
            })

# ปุ่มเพิ่มรายการ (ใช้ on_click)
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item_callback)

# --- 7. การตรวจสอบและส่งข้อมูล ---
st.write("---")
if st.button("บันทึกข้อมูลและแสดงผลตรวจสอบ", type="primary"):
    if not supplier_name or not supplier_email:
        st.error("กรุณากรอกข้อมูลส่วนที่ 1 ให้ครบถ้วน")
    else:
        st.success("บันทึกสำเร็จ! คุณสามารถแก้ไขข้อมูลด้านบนได้จนกว่าจะพอใจ")
        st.write("### สรุปรายการที่จะส่ง PDF")
        st.table(pd.DataFrame(current_material_data))
        
        # ปุ่มจำลองการส่ง PDF
        if st.button("ยืนยันส่ง PDF ไปยังอีเมล"):
            st.info(f"ระบบกำลังส่งไฟล์ไปยัง {supplier_email}...")
