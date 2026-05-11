import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- 1. ตั้งค่าหน้าจอและดีไซน์ ---
st.set_page_config(page_title="CPRAM Supplier Form", layout="wide")

st.markdown("""
    <style>
    .section-header { color: #2e7d32; font-size: 22px; font-weight: bold; border-bottom: 2px solid #2e7d32; margin-bottom: 20px; }
    .item-box { background-color: #f1f8e9; padding: 25px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    .cpram-logo { text-align: center; color: #d32f2f; font-size: 40px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. การจัดการ Session State (ป้องกัน Error บรรทัด 69) ---
if 'items' not in st.session_state:
    st.session_state.items = [{"id": 0}]

def add_item_callback():
    st.session_state.items.append({"id": len(st.session_state.items)})

def remove_item_callback(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)

# --- 3. หัวฟอร์ม CPRAM ---
st.markdown('<div class="cpram-logo">CPRAM</div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center;">Supplier Daily Material Record Form</h3>', unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    supplier_name = st.text_input("ผู้ส่งมอบ (Supplier) *", key="main_supplier")
    delivery_date = st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now(), key="main_date")

with col2:
    delivery_time = st.time_input("เวลาส่ง *", value=time(14, 0), key="main_time")
    recorded_by = st.text_input("ลงชื่อผู้กรอก", key="main_recorder")

with col3:
    supplier_email = st.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", key="main_email")
    
    # --- ปรับปรุงส่วนประเทศแหล่งปลูกตามสั่ง ---
    origin_country = st.selectbox(
        "ประเทศแหล่งปลูก (Country of Origin)", 
        ["ประเทศไทย", "ประเทศจีน", "อื่นๆ (โปรดระบุ)"], 
        index=0, 
        key="main_country"
    )
    
    # ถ้าเลือก "อื่นๆ (โปรดระบุ)" จะแสดงช่องให้กรอกเอง
    final_country = origin_country
    if origin_country == "อื่นๆ (โปรดระบุ)":
        final_country = st.text_input("ระบุชื่อประเทศ *", placeholder="กรุณากรอกชื่อประเทศ", key="custom_country")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด) ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

current_material_data = []

if "items" in st.session_state:
    for i, item in enumerate(st.session_state.items):
        with st.container():
            st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
            h_col1, h_col2 = st.columns([0.85, 0.15])
            h_col1.subheader(f"รายการที่ {i+1}")
            
            # ปุ่มลบรายการ
            h_col2.button(f"✕ ลบรายการที่ {i+1}", key=f"del_{i}", on_click=remove_item_callback, args=(i,))

            # ฟิลด์ข้อมูลวัตถุดิบ
            r1c1, r1c2, r1c3 = st.columns(3)
            m_type = r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_type_{i}")
            m_code = r1c2.text_input("Code", key=f"mat_code_{i}")
            m_qty = r1c3.text_input("จำนวน (KG) *", key=f"mat_qty_{i}")

            r2c1, r2c2, r2c3 = st.columns(3)
            h_d = r2c1.date_input("วันที่เก็บเกี่ยว", key=f"h_date_{i}")
            h_t = r2c2.time_input("เวลาเก็บเกี่ยว", key=f"h_time_{i}")
            c_d = r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"c_date_{i}")

            r3c1, r3c2, r3c3 = st.columns(3)
            c_t = r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00-09:30", key=f"c_time_{i}")
            grower = r3c2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
            gap = r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

            st.markdown("📍 **ข้อมูลแหล่งปลูกและสายพันธุ์**")
            r4c1, r4c2, r4c3, r4c4 = st.columns(4)
            farm = r4c1.text_input("รหัสไร่", key=f"farm_{i}")
            breed = r4c2.text_input("สายพันธุ์", key=f"breed_{i}")
            style = r4c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ดิน", "ไฮโดรโปนิกส์"], key=f"style_{i}")
            loc = r4c4.selectbox("สถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")

            st.markdown('</div>', unsafe_allow_html=True)
            
            current_material_data.append({
                "รายการ": i+1,
                "ชนิดวัตถุดิบ": m_type,
                "จำนวน": m_qty,
                "ประเทศ": final_country # ดึงค่าประเทศจากส่วนที่ 1 มาใช้
            })

# ปุ่มเพิ่มรายการ
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item_callback)

# --- 6. สรุปและส่งข้อมูล ---
st.write("---")
if st.button("บันทึกและตรวจสอบข้อมูลเพื่อส่ง PDF", type="primary"):
    if not supplier_name or not supplier_email or (origin_country == "อื่นๆ (โปรดระบุ)" and not final_country):
        st.error("กรุณากรอกข้อมูลสำคัญ (ที่มี *) ให้ครบถ้วน")
    else:
        st.success(f"บันทึกข้อมูลเรียบร้อย! ประเทศแหล่งปลูกคือ: {final_country}")
        st.write("### ตารางสรุปรายการ")
        st.table(pd.DataFrame(current_material_data))
        
        # ส่วนเตรียมส่ง PDF
        st.info(f"ระบบพร้อมส่งไฟล์สรุปไปยังอีเมล: {supplier_email}")
