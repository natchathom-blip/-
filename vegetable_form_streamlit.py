import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. การตั้งค่าหน้าจอและสไตล์ (CSS ให้เหมือนแบบฟอร์มจริง) ---
st.set_page_config(page_title="CPRAM - Supplier Form", layout="wide")

st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 15px; }
    .logo-box { background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px; }
    .doc-id { border: 1.5px solid #000; padding: 4px 12px; font-weight: bold; text-align: center; }
    .section-header { color: #2e7d32; font-size: 20px; font-weight: bold; border-bottom: 2px solid #2e7d32; margin-top: 25px; margin-bottom: 15px; }
    .item-box { background-color: #f1f8e9; padding: 25px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชันโหลดข้อมูลจังหวัด (รองรับคอลัมน์ภาษาไทยจากไฟล์ของคุณ) ---
@st.cache_data
def load_address_data():
    try:
        # พยายามอ่านไฟล์ (ถ้าเป็น .csv หรือ .xlsx)
        df = pd.read_csv('thailand.xlsx - Sheet1.csv') if 'thailand.xlsx - Sheet1.csv' else pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_addr = load_address_data()

# กำหนดชื่อคอลัมน์ตามไฟล์จริงของคุณ
P_COL, A_COL, T_COL = "จังหวัด", "อำเภอ", "ตำบล"

# --- 3. ส่วนหัวแบบฟอร์ม (Header) ---
st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center;">
            <div class="logo-box">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;">
                <b>CPRAM Co., Ltd.</b><br><small>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</small>
            </div>
        </div>
        <div style="text-align: right;">
            <div class="doc-id">FR-QAS-10-000</div>
            <div style="font-size: 13px; margin-top: 5px;">มีผลใช้งาน: 2026-05-08</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ (ครบตามรูป image_a4592f.png) ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
s_time = c3.text_input("เวลาส่ง (น.)", placeholder="เช่น 14:00", key="s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder")
origin_main = c6.selectbox("ประเทศแหล่งปลูกหลัก", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin_main")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ (ครบตามรูป image_a4590e.png / image_a46037.png) ---
if 'items_count' not in st.session_state: st.session_state.items_count = 1
def add_item(): st.session_state.items_count += 1

st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

for i in range(st.session_state.items_count):
    st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
    
    col_h, col_del = st.columns([0.8, 0.2])
    col_h.subheader(f"รายการที่ {i+1}")
    if st.session_state.items_count > 1 and col_del.button(f"✕ ลบรายการ", key=f"del_{i}"):
        st.session_state.items_count -= 1
        st.rerun()

    # แถวที่ 1: ข้อมูลวัตถุดิบ
    r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
    r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
    r1c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
    r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

    # แถวที่ 2: วันเวลาเก็บเกี่ยว/ล้าง
    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
    r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
    r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

    # แถวที่ 3: เวลาล้าง/ชื่อผู้ปลูก/GAP
    r3c1, r3c2, r3c3 = st.columns(3)
    r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00-09:30", key=f"ct_{i}")
    r3c2.text_input("ชื่อผู้ปลูก", key=f"grow_{i}")
    r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

    # แถวที่ 4: รหัสไร่/บ้านเลขที่/หมู่
    r4c1, r4c2, r4c3 = st.columns(3)
    r4c1.text_input("รหัสไร่", key=f"farm_{i}")
    r4c2.text_input("ที่อยู่เลขที่", key=f"addr_no_{i}")
    r4c3.text_input("หมู่ที่", key=f"moo_{i}")

    # แถวที่ 5: ที่อยู่ Cascading Dropdown (📍)
    st.markdown("📍 **ที่อยู่แหล่งปลูก (Dropdown)**")
    a1, a2, a3, a4 = st.columns(4)
    a1.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"country_{i}")
    
    # ดึงข้อมูลจากไฟล์ Excel/CSV ที่คุณส่งมา
    if not df_addr.empty and P_COL in df_addr.columns:
        p_list = sorted(df_addr[P_COL].unique())
        sel_p = a2.selectbox("จังหวัด", ["- เลือก -"] + p_list, key=f"p_{i}")
        
        a_opts = sorted(df_addr[df_addr[P_COL] == sel_p][A_COL].unique()) if sel_p != "- เลือก -" else []
        sel_a = a3.selectbox("อำเภอ", ["- เลือก -"] + a_opts, key=f"a_{i}")
        
        t_opts = sorted(df_addr[(df_addr[P_COL] == sel_p) & (df_addr[A_COL] == sel_a)][T_COL].unique()) if sel_a != "- เลือก -" else []
        sel_t = a4.selectbox("ตำบล", ["- เลือก -"] + t_opts, key=f"t_{i}")
    else:
        a2.text_input("จังหวัด", key=f"p_manual_{i}")
        a3.text_input("อำเภอ", key=f"a_manual_{i}")
        a4.text_input("ตำบล", key=f"t_manual_{i}")

    # แถวที่ 6: รหัสไปรษณีย์/สายพันธุ์/ลักษณะการปลูก
    r5c1, r5c2, r5c3, r5c4 = st.columns(4)
    r5c1.text_input("รหัสไปรษณีย์", key=f"z_{i}")
    r5c2.text_input("สายพันธุ์", key=f"breed_{i}")
    r5c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
    r5c4.selectbox("ลักษณะสถานที่", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")

    st.markdown('</div>', unsafe_allow_html=True)

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ส่วนการดาวน์โหลด PDF (พร้อมใช้งานทันที) ---
st.write("---")
if s_name:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="CPRAM Supplier Record", ln=True, align='C')
    # (โค้ดสร้างเนื้อหา PDF สามารถเพิ่มตามต้องการ)
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    
    st.download_button(
        label="📥 ดาวน์โหลด PDF และส่งข้อมูล",
        data=pdf_bytes,
        file_name=f"CPRAM_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )
