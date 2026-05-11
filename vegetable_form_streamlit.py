import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- ตั้งค่าหน้ากระดาษและดีไซน์ ---
st.set_page_config(page_title="CPRAM Supplier Daily Record", layout="wide")

st.markdown("""
    <style>
    .section-header { 
        color: #2e7d32; font-size: 24px; font-weight: bold; 
        margin-top: 20px; border-bottom: 2px solid #2e7d32; padding-bottom: 5px;
    }
    .item-box {
        background-color: #f1f8e9; padding: 20px; border-radius: 10px;
        border: 1px solid #c8e6c9; margin-bottom: 20px;
    }
    .cpram-logo {
        text-align: center; color: #d32f2f; font-size: 45px; font-weight: bold; margin-bottom: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- หัวข้อฟอร์ม ---
st.markdown('<div class="cpram-logo">CPRAM</div>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center;">Supplier Daily Material Record Form</h3>', unsafe_allow_html=True)

# --- จัดการ Session State เพื่อให้เพิ่ม/ลบรายการและแก้ไขได้ ---
if 'items' not in st.session_state:
    st.session_state.items = [{"id": 0}]

# --- ส่วนที่ 1: ข้อมูลผู้ส่งมอบ ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    supplier_name = st.text_input("ผู้ส่งมอบ (Supplier) *")
    supplier_email = st.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *")
with col2:
    delivery_date = st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now())
    recorded_by = st.text_input("ลงชื่อผู้กรอก")
with col3:
    delivery_time = st.text_input("เวลาส่ง", placeholder="เช่น 14:00 น.")
    origin_country = st.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "อื่นๆ"])

# --- ส่วนที่ 2: รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด) ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

def remove_item(idx):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(idx)

item_results = []
for i, item in enumerate(st.session_state.items):
    with st.container():
        st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
        h_col1, h_col2 = st.columns([0.85, 0.15])
        h_col1.subheader(f"รายการที่ {i+1}")
        if h_col2.button(f"✕ ลบรายการที่ {i+1}", key=f"del_{i}"):
            remove_item(i)
            st.rerun()

        # แถวที่ 1
        r1c1, r1c2, r1c3 = st.columns(3)
        mat_type = r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        mat_code = r1c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
        qty = r1c3.number_input("จำนวน (KG) *", min_value=0.0, key=f"qty_{i}")

        # แถวที่ 2
        r2c1, r2c2, r2c3 = st.columns(3)
        h_date = r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        h_time = r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
        c_date = r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

        # แถวที่ 3
        r3c1, r3c2, r3c3 = st.columns(3)
        c_time = r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00-09:30", key=f"ct_{i}")
        grower = r3c2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        gap = r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

        # แถวที่ 4 (ที่อยู่แหล่งปลูก)
        st.markdown("**📍 ที่อยู่แหล่งปลูก (cascading dropdown)**")
        r4c1, r4c2, r4c3, r4c4 = st.columns(4)
        farm_id = r4c1.text_input("รหัสไร่", key=f"farm_{i}")
        addr = r4c2.text_input("ที่อยู่เลขที่", key=f"addr_{i}")
        moo = r4c3.text_input("หมู่ที่", key=f"moo_{i}")
        prov = r4c4.selectbox("จังหวัด", ["- เลือก -", "กรุงเทพฯ", "นครปฐม", "ปทุมธานี"], key=f"prov_{i}")

        # แถวที่ 5
        r5c1, r5c2, r5c3, r5c4 = st.columns(4)
        zipc = r5c1.text_input("รหัสไปรษณีย์", key=f"zip_{i}")
        breed = r5c2.text_input("สายพันธุ์", key=f"breed_{i}")
        p_style = r5c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ดิน", "ไฮโดรโปนิกส์"], key=f"style_{i}")
        p_loc = r5c4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        item_results.append({"Item": i+1, "Material": mat_type, "Qty": qty})

if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items.append({"id": len(st.session_state.items)})
    st.rerun()

# --- ปุ่มส่งข้อมูล ---
st.write("---")
if st.button("บันทึกข้อมูลและเตรียมส่ง PDF", type="primary"):
    if not supplier_name or not supplier_email:
        st.error("กรุณากรอกชื่อผู้ส่งมอบและอีเมลให้ครบถ้วน")
    else:
        st.success("บันทึกข้อมูลสำเร็จ! ตรวจสอบความถูกต้องด้านล่างก่อนยืนยันส่งอีเมล")
        st.table(pd.DataFrame(item_results))
        # ส่วนนี้คือจุดที่คุณจะเรียกฟังก์ชันส่ง Email และ PDF ต่อไป
