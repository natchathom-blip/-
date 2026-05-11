import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- 1. การตั้งค่าหน้าจอและสไตล์ (CSS) ---
st.set_page_config(page_title="CPRAM - Supplier Form", layout="wide")

st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 15px; }
    .logo-box { background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px; }
    .doc-id { border: 1.5px solid #000; padding: 4px 12px; font-weight: bold; text-align: center; }
    .section-header { color: #2e7d32; font-size: 20px; font-weight: bold; margin-top: 25px; margin-bottom: 10px; }
    .item-box { background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    .stButton>button { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชันโหลดข้อมูลที่อยู่ (พร้อมป้องกัน KeyError) ---
@st.cache_data
def load_address_data():
    try:
        df = pd.read_excel('thailand.xlsx')
        # ล้างช่องว่างในชื่อคอลัมน์เพื่อป้องกัน KeyError
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดไฟล์ thailand.xlsx ได้: {e}")
        return pd.DataFrame()

df_addr = load_address_data()

# ตรวจสอบชื่อคอลัมน์จริงในไฟล์ (ปรับให้ตรงกับไฟล์ของคุณ)
P_COL = 'province_th'
A_COL = 'district_th'
T_COL = 'subdistrict_th'
Z_COL = 'postcode'

# --- 3. การจัดการ Session State ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item(): st.session_state.items_count += 1

# --- 4. ส่วนหัวแบบฟอร์ม (Header) ---
st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; align-items: center;">
            <div class="logo-box">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;">
                <b style="font-size: 18px;">CPRAM Co., Ltd.</b><br>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ
            </div>
        </div>
        <div>
            <div class="doc-id">FR-QAS-10-000</div>
            <div style="font-size: 12px; text-align: right; margin-top: 5px;">มีผลใช้งาน: 2026-05-08</div>
        </div>
    </div>
    <div style="text-align: center; margin: 20px 0;">
        <h2 style="color: #2e7d32;">แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h2>
        <p style="color: #666;">กรุณากรอกข้อมูลให้ครบถ้วน — ระบบจะกรอกรหัสไปรษณีย์ให้อัตโนมัติจาก Dropdown</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
s_time = c3.text_input("เวลาส่ง", placeholder="เช่น 14:00 น.", key="s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลของผู้ส่งมอบ (สำหรับรับ PDF) *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder")
origin = c6.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "จีน", "อื่นๆ"], key="origin")

# --- 6. ส่วนที่ 2 — รายการวัตถุดิบ ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

for i in range(st.session_state.items_count):
    st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
    
    h_col, b_col = st.columns([0.8, 0.2])
    h_col.subheader(f"รายการที่ {i+1}")
    if st.session_state.items_count > 1 and b_col.button(f"✕ ลบรายการนี้", key=f"del_{i}"):
        st.session_state.items_count -= 1
        st.rerun()

    # แถวที่ 1-3 ตามรูป
    r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
    r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
    r1c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
    r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
    r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
    r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

    r3c1, r3c2, r3c3 = st.columns(3)
    r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00 หรือ 08:00-09:30", key=f"ct_{i}")
    r3c2.text_input("ชื่อผู้ปลูก", key=f"grow_{i}")
    r3c3.text_input("เลขที่ GAP", key=f"gap_{i}")

    r4c1, r4c2, r4c3 = st.columns(3)
    r4c1.text_input("รหัสไร่", key=f"farm_{i}")
    r4c2.text_input("ที่อยู่เลขที่", key=f"addr_no_{i}")
    r4c3.text_input("หมู่ที่", key=f"moo_{i}")

    # แถวที่ 5: ที่อยู่ Cascading Dropdown
    st.markdown("📍 **ที่อยู่แหล่งปลูก (cascading dropdown)**")
    a1, a2, a3, a4 = st.columns(4)
    a1.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"country_{i}")
    
    zip_val = ""
    if not df_addr.empty:
        # ป้องกัน KeyError ด้วยการเช็คชื่อคอลัมน์
        p_list = sorted(df_addr[P_COL].unique()) if P_COL in df_addr else []
        sel_p = a2.selectbox("จังหวัด/มณฑล", ["- เลือก -"] + p_list, key=f"p_{i}")
        
        a_opts = sorted(df_addr[df_addr[P_COL] == sel_p][A_COL].unique()) if sel_p != "- เลือก -" else []
        sel_a = a3.selectbox("อำเภอ/เมือง", ["- เลือก -"] + a_opts, key=f"a_{i}")
        
        t_opts = sorted(df_addr[(df_addr[P_COL] == sel_p) & (df_addr[A_COL] == sel_a)][T_COL].unique()) if sel_a != "- เลือก -" else []
        sel_t = a4.selectbox("ตำบล/เขต", ["- เลือก -"] + t_opts, key=f"t_{i}")
        
        if sel_t != "- เลือก -":
            res = df_addr[(df_addr[P_COL] == sel_p) & (df_addr[A_COL] == sel_a) & (df_addr[T_COL] == sel_t)]
            if not res.empty: zip_val = res[Z_COL].iloc[0]

    r5c1, r5c2, r5c3, r5c4 = st.columns(4)
    r5c1.text_input("รหัสไปรษณีย์", value=str(zip_val), key=f"z_{i}", disabled=True)
    r5c2.text_input("สายพันธุ์", key=f"breed_{i}")
    r5c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
    r5c4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")

    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. ปุ่มดำเนินการและดาวน์โหลด PDF ---
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

st.write("---")
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="CPRAM - Supplier Daily Record", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Supplier: {st.session_state.s_name}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

c_send, c_down = st.columns(2)
with c_send:
    if st.button("📧 ยืนยันข้อมูลและส่ง PDF", type="primary", use_container_width=True):
        if not s_name or not s_email:
            st.error("กรุณากรอกข้อมูลส่วนที่ 1 ให้ครบถ้วน")
        else:
            st.success(f"บันทึกและเตรียมส่ง PDF ไปที่ {s_email} เรียบร้อย!")

with c_down:
    if s_name:
        st.download_button(
            label="📥 ดาวน์โหลด PDF ทันที",
            data=generate_pdf(),
            file_name=f"CPRAM_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
