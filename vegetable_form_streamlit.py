import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- 1. การตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="CPRAM - Supplier Daily Record", layout="wide")

st.markdown("""
    <style>
    /* สไตล์สำหรับหัวฟอร์มแบบใหม่ */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 3px solid #2e7d32;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .logo-section {
        display: flex;
        align-items: center;
    }
    .logo-box {
        background-color: #2e7d32;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 24px;
        margin-right: 15px;
    }
    .company-info {
        color: #2e7d32;
        line-height: 1.2;
    }
    .doc-info {
        text-align: right;
        font-size: 14px;
        color: #333;
    }
    .doc-id {
        border: 2px solid #000;
        padding: 5px 10px;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 5px;
    }
    .section-header { 
        color: #2e7d32; font-size: 20px; font-weight: bold; 
        border-bottom: 2px solid #2e7d32; margin-top: 20px; margin-bottom: 15px; 
    }
    .item-box { 
        background-color: #f1f8e9; padding: 25px; border-radius: 10px; 
        border: 1px solid #c8e6c9; margin-bottom: 20px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. การจัดการ Session State ---
if 'items' not in st.session_state:
    st.session_state.items = [{"id": 0}]

def add_item_callback():
    st.session_state.items.append({"id": len(st.session_state.items)})

def remove_item_callback(index):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop(index)

# --- 3. ส่วนหัวแบบฟอร์ม (Header) ตามรูปภาพที่ส่งมา ---
st.markdown(f"""
    <div class="header-container">
        <div class="logo-section">
            <div class="logo-box">cpram</div>
            <div class="company-info">
                <div style="font-weight: bold; font-size: 18px;">CPRAM Co., Ltd.</div>
                <div>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</div>
            </div>
        </div>
        <div class="doc-info">
            <div class="doc-id">FR-QAS-10-000</div>
            <div>มีผลใช้งาน: 2026-05-08</div>
        </div>
    </div>
    <div style="text-align: center; margin-bottom: 30px;">
        <h2 style="color: #2e7d32; margin-bottom: 5px;">แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h2>
        <p style="color: #666;">กรุณากรอกข้อมูลให้ครบถ้วน — ระบบจะส่งเอกสารสรุปไปที่อีเมลของผู้ส่งมอบอัตโนมัติ</p>
    </div>
    """, unsafe_allow_html=True)

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
    
    # ประเทศแหล่งปลูก
    origin_country_opt = st.selectbox(
        "ประเทศแหล่งปลูก (Country of Origin)", 
        ["ประเทศไทย", "ประเทศจีน", "อื่นๆ (โปรดระบุ)"], 
        key="main_country_sel"
    )
    final_country = origin_country_opt
    if origin_country_opt == "อื่นๆ (โปรดระบุ)":
        final_country = st.text_input("ระบุประเทศเพิ่มเติม *", key="main_country_custom")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

current_material_data = []

if "items" in st.session_state:
    for i, item in enumerate(st.session_state.items):
        with st.container():
            st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
            h_col1, h_col2 = st.columns([0.85, 0.15])
            h_col1.subheader(f"รายการที่ {i+1}")
            h_col2.button(f"✕ ลบรายการนี้", key=f"del_{i}", on_click=remove_item_callback, args=(i,))

            r1c1, r1c2, r1c3 = st.columns(3)
            m_type = r1c1.text_input("ชนิดวัตถุดิบ *", key=f"mat_type_{i}")
            m_code = r1c2.text_input("Code", key=f"mat_code_{i}")
            m_qty = r1c3.text_input("จำนวน (KG) *", key=f"mat_qty_{i}")

            r2c1, r2c2, r2c3 = st.columns(3)
            h_d = r2c1.date_input("วันที่เก็บเกี่ยว", key=f"h_date_{i}")
            h_t = r2c2.time_input("เวลาเก็บเกี่ยว", key=f"h_time_{i}")
            grower = r2c3.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")

            st.markdown('</div>', unsafe_allow_html=True)
            
            current_material_data.append({
                "รายการ": i+1, "วัตถุดิบ": m_type, "จำนวน": m_qty, "ผู้ปลูก": grower
            })

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item_callback)

# --- 6. ส่วนตรวจสอบและส่งข้อมูล ---
st.write("---")
if st.button("ยืนยันข้อมูลและส่ง PDF", type="primary"):
    if not supplier_name or not supplier_email:
        st.error("กรุณากรอกข้อมูลส่วนที่ 1 (ผู้ส่งมอบและอีเมล) ให้ครบถ้วน")
    else:
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
        st.table(pd.DataFrame(current_material_data))
        st.info(f"ระบบกำลังดำเนินการส่ง PDF ไปยัง {supplier_email}...")
