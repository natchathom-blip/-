import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- 1. การตั้งค่าหน้าจอและดีไซน์ ---
st.set_page_config(page_title="CPRAM - Supplier Daily Record", layout="wide")

st.markdown("""
    <style>
    /* สไตล์หัวฟอร์ม CPRAM */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 3px solid #2e7d32;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .logo-section { display: flex; align-items: center; }
    .logo-box {
        background-color: #2e7d32;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 26px;
        margin-right: 15px;
        font-family: sans-serif;
    }
    .company-info { color: #2e7d32; line-height: 1.2; }
    .doc-info { text-align: right; font-size: 13px; color: #333; }
    .doc-id {
        border: 1.5px solid #000;
        padding: 4px 12px;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 4px;
    }
    .section-header { 
        color: #2e7d32; font-size: 20px; font-weight: bold; 
        border-bottom: 2px solid #2e7d32; margin-top: 25px; margin-bottom: 15px; 
    }
    .item-box { 
        background-color: #f1f8e9; padding: 25px; border-radius: 10px; 
        border: 1px solid #c8e6c9; margin-bottom: 20px; 
    }
    /* สไตล์ปุ่มลบ */
    div.stButton > button:first-child { background-color: #d32f2f; color: white; border: none; }
    /* สไตล์ปุ่มเพิ่มรายการ */
    .add-btn-container { border: 2px dashed #2e7d32; padding: 10px; text-align: center; border-radius: 10px; }
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

# --- 3. ส่วนหัวแบบฟอร์ม (Header) ---
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
    <div style="text-align: center; margin-top: 10px;">
        <h2 style="color: #2e7d32; margin-bottom: 5px;">แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h2>
        <p style="color: #666; font-size: 14px;">กรุณากรอกข้อมูลให้ครบถ้วน — เลือก จังหวัด/อำเภอ/ตำบล จาก dropdown ระบบจะกรอกรหัสไปรษณีย์ให้อัตโนมัติ</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    supplier_name = st.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
    supplier_email = st.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", key="s_email")

with col2:
    delivery_date = st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now(), key="d_date")
    recorded_by = st.text_input("ลงชื่อผู้กรอก", key="recorder")

with col3:
    delivery_time = st.time_input("เวลาส่ง *", value=time(14, 0), key="d_time")
    country_opt = st.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "ประเทศจีน", "อื่นๆ (โปรดระบุ)"], key="c_origin")
    if country_opt == "อื่นๆ (โปรดระบุ)":
        final_country = st.text_input("ระบุชื่อประเทศ *", key="c_custom")
    else:
        final_country = country_opt

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

for i, item in enumerate(st.session_state.items):
    with st.container():
        st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
        h_col1, h_col2 = st.columns([0.85, 0.15])
        h_col1.subheader(f"รายการที่ {i+1}")
        h_col2.button(f"✕ ลบรายการนี้", key=f"del_{i}", on_click=remove_item_callback, args=(i,))

        # แถวที่ 1
        r1c1, r1c2, r1c3 = st.columns(3)
        mat_type = r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        mat_code = r1c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
        qty = r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

        # แถวที่ 2
        r2c1, r2c2, r2c3 = st.columns(3)
        h_date = r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        h_time = r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
        c_date = r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

        # แถวที่ 3
        r3c1, r3c2, r3c3 = st.columns(3)
        c_time = r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00 หรือ 08:00-09:30", key=f"ct_{i}")
        grower = r3c2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        gap = r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

        # แถวที่ 4
        r4c1, r4c2, r4c3 = st.columns(3)
        farm_id = r4c1.text_input("รหัสไร่", key=f"farm_{i}")
        addr_no = r4c2.text_input("ที่อยู่เลขที่", key=f"addr_{i}")
        moo = r4c3.text_input("หมู่ที่", key=f"moo_{i}")

        # แถวที่ 5 (Cascading Dropdown Placeholder)
        st.markdown("📍 **ที่อยู่แหล่งปลูก (cascading dropdown)**")
        r5c1, r5c2, r5c3, r5c4 = st.columns(4)
        r5c1.selectbox("ประเทศ", ["ไทย"], key=f"loc_c_{i}")
        r5c2.selectbox("จังหวัด/มณฑล", ["- เลือก -", "กรุงเทพฯ", "นครปฐม"], key=f"loc_p_{i}")
        r5c3.selectbox("อำเภอ/เมือง", ["- เลือกจังหวัดก่อน -"], key=f"loc_a_{i}")
        r5c4.selectbox("ตำบล/เขต", ["- เลือกอำเภอก่อน -"], key=f"loc_t_{i}")

        # แถวที่ 6
        r6c1, r6c2, r6c3, r6c4 = st.columns(4)
        r6c1.text_input("รหัสไปรษณีย์", key=f"zip_{i}")
        r6c2.text_input("สายพันธุ์", key=f"breed_{i}")
        r6c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ดิน", "ไฮโดรโปนิกส์"], key=f"style_{i}")
        r6c4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_type_{i}")

        st.markdown('</div>', unsafe_allow_html=True)

# ส่วนปุ่มเพิ่มรายการ
st.markdown('<div class="add-btn-container">', unsafe_allow_html=True)
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item_callback)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. ปุ่มส่งข้อมูล ---
st.write("---")
if st.button("ยืนยันบันทึกข้อมูลและส่ง PDF", type="primary"):
    if not supplier_name or not supplier_email:
        st.error("กรุณากรอกข้อมูลผู้ส่งมอบและอีเมลให้ครบถ้วนก่อนส่ง")
    else:
        st.success(f"บันทึกข้อมูลสำเร็จ! ระบบกำลังสร้างไฟล์ PDF เพื่อส่งไปยัง {supplier_email}")
        # Logic สำหรับสร้าง PDF และส่ง Email จะอยู่ตรงนี้
