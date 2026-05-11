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
# --- จัดการ Session State ให้ชัวร์ว่ามีตัวแปร items แน่นอน ---
if 'items' not in st.session_state:
    st.session_state.items = [{"id": 0}]

# --- ส่วนที่ 2: รายการวัตถุดิบ ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

# สร้างลิสต์ชั่วคราวเพื่อเก็บข้อมูลที่กรอก
item_results = []

# ใช้ copy ของลิสต์เพื่อป้องกันปัญหาเรื่อง Index ระหว่างการ Loop และ ลบรายการ
current_items = list(st.session_state.items)

for i, item in enumerate(current_items):
    with st.container():
        st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
        h_col1, h_col2 = st.columns([0.85, 0.15])
        h_col1.subheader(f"รายการที่ {i+1}")
        
        # ปรับการลบรายการให้ปลอดภัยขึ้น
        if h_col2.button(f"✕ ลบรายการที่ {i+1}", key=f"btn_del_{i}"):
            st.session_state.items.pop(i)
            st.rerun()

        # --- ส่วนของ Input (เหมือนเดิม) ---
        r1c1, r1c2, r1c3 = st.columns(3)
        mat_type = r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_type_{i}")
        mat_code = r1c2.text_input("Code", key=f"code_val_{i}")
        qty = r1c3.number_input("จำนวน (KG) *", min_value=0.0, key=f"qty_val_{i}")

        # ... (ส่วนอื่นๆ ของฟอร์มกรอกข้อมูลตามโค้ดเดิม) ...

        st.markdown('</div>', unsafe_allow_html=True)
        
        # เก็บข้อมูลเข้า List
        item_results.append({
            "รายการ": i+1,
            "ชนิดวัตถุดิบ": mat_type,
            "จำนวน": qty
        })

# ปุ่มเพิ่มรายการ (อยู่นอก Loop)
if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items.append({"id": len(st.session_state.items)})
    st.rerun()
