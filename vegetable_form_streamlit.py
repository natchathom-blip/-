import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM - Supplier Form", layout="wide")

# --- 2. ฟังก์ชันโหลดข้อมูล (ปรับให้ตรงกับไฟล์ CSV ของคุณ) ---
@st.cache_data
def load_address_data():
    try:
        # อ่านไฟล์ CSV ที่คุณอัปโหลดมาล่าสุด
        df = pd.read_csv('thailand.xlsx - Sheet1.csv')
        # ล้างช่องว่างที่อาจติดมาในชื่อคอลัมน์หรือข้อมูล
        df.columns = [str(c).strip() for c in df.columns]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดไฟล์ที่อยู่ได้: {e}")
        return pd.DataFrame()

df_addr = load_address_data()

# กำหนดชื่อคอลัมน์ตามไฟล์จริงของคุณเป๊ะๆ
P_COL, A_COL, T_COL = "จังหวัด", "อำเภอ", "ตำบล"

# --- 3. ส่วนหัว (Header) ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px;">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;"><b>CPRAM Co., Ltd.</b><br><small>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</small></div>
        </div>
        <div style="text-align: right;">
            <div style="border: 1.5px solid #000; padding: 4px 12px; font-weight: bold;">FR-QAS-10-000</div>
            <div style="font-size: 12px; margin-top: 5px;">มีผลใช้งาน: 2026-05-08</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ (ครบตามรูป image_a4592f.png) ---
st.markdown('<p style="color: #2e7d32; font-size: 20px; font-weight: bold; border-bottom: 2px solid #2e7d32;">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</p>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: s_name = st.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
with c2: s_date = st.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
with c3: s_time = st.text_input("เวลาส่ง (น.)", placeholder="เช่น 14:00", key="s_time")

c4, c5, c6 = st.columns(3)
with c4: s_email = st.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
with c5: recorder = st.text_input("ลงชื่อผู้กรอก", key="recorder")
with c6: origin_main = st.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ครบตามรูป image_a4590e.png / image_a46037.png) ---
if 'items_count' not in st.session_state: st.session_state.items_count = 1
def add_item(): st.session_state.items_count += 1

st.markdown('<p style="color: #2e7d32; font-size: 20px; font-weight: bold; border-bottom: 2px solid #2e7d32;">ส่วนที่ 2 — รายการวัตถุดิบ</p>', unsafe_allow_html=True)

for i in range(st.session_state.items_count):
    st.markdown(f'<div style="background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px;">', unsafe_allow_html=True)
    
    col_h, col_del = st.columns([0.8, 0.2])
    col_h.subheader(f"รายการที่ {i+1}")
    if st.session_state.items_count > 1 and col_del.button(f"✕ ลบรายการนี้", key=f"del_{i}"):
        st.session_state.items_count -= 1
        st.rerun()

    # แถวที่ 1
    r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
    r1c1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
    r1c2.text_input("Code", key=f"code_{i}")
    r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

    # แถวที่ 2
    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
    r2c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
    r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

    # แถวที่ 3
    r3c1, r3c2, r3c3 = st.columns(3)
    r3c1.text_input("เวลาที่ล้างทำความสะอาด", key=f"ct_{i}")
    r3c2.text_input("ชื่อผู้ปลูก", key=f"grow_{i}")
    r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

    # แถวที่ 4
    r4c1, r4c2, r4c3 = st.columns(3)
    r4c1.text_input("รหัสไร่", key=f"farm_{i}")
    r4c2.text_input("ที่อยู่เลขที่", key=f"addr_no_{i}")
    r4c3.text_input("หมู่ที่", key=f"moo_{i}")

    # แถวที่ 5: 📍 Cascading Dropdown (จุดที่แก้ไข)
    st.markdown("📍 **ที่อยู่แหล่งปลูก**")
    a1, a2, a3, a4 = st.columns(4)
    a1.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"country_{i}")
    
    if not df_addr.empty:
        # จังหวัด
        p_list = sorted(df_addr[P_COL].unique())
        sel_p = a2.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
        
        # อำเภอ (กรองตามจังหวัด)
        amp_opts = sorted(df_addr[df_addr[P_COL] == sel_p][A_COL].unique()) if sel_p != "- เลือก -" else []
        sel_a = a3.selectbox("อำเภอ", ["- เลือก -"] + amp_opts, key=f"a_{i}")
        
        # ตำบล (กรองตามจังหวัดและอำเภอ)
        tam_opts = sorted(df_addr[(df_addr[P_COL] == sel_p) & (df_addr[A_COL] == sel_a)][T_COL].unique()) if sel_a != "- เลือก -" else []
        sel_t = a4.selectbox("ตำบล", ["- เลือก -"] + tam_opts, key=f"t_{i}")
    else:
        a2.warning("ไม่พบข้อมูลจังหวัด")

    # แถวที่ 6
    r5c1, r5c2, r5c3, r5c4 = st.columns(4)
    r5c1.text_input("รหัสไปรษณีย์", key=f"z_{i}") # กรอกมือตามแบบฟอร์ม
    r5c2.text_input("สายพันธุ์", key=f"breed_{i}")
    r5c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกดินยกพื้น", "ไฮโดรโปนิกส์"], key=f"style_{i}")
    r5c4.selectbox("ลักษณะสถานที่", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")

    st.markdown('</div>', unsafe_allow_html=True)

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ปุ่มส่งข้อมูล ---
st.write("---")
if st.button("✅ ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary", use_container_width=True):
    if not s_name or not s_email:
        st.error("กรุณากรอกชื่อผู้ส่งมอบและอีเมลให้ครบถ้วน")
    else:
        st.success("บันทึกข้อมูลเรียบร้อย!")
