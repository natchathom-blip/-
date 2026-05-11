import streamlit as st
import pandas as pd
from datetime import datetime, time

# --- 1. การตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="CPRAM - Supplier Daily Record", layout="wide")

st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 15px; }
    .logo-box { background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px; font-family: sans-serif; }
    .company-info { color: #2e7d32; line-height: 1.2; margin-left: 15px; }
    .doc-id { border: 1.5px solid #000; padding: 4px 12px; font-weight: bold; font-size: 16px; text-align: center; }
    .section-header { color: #2e7d32; font-size: 20px; font-weight: bold; border-bottom: 2px solid #2e7d32; margin-top: 25px; margin-bottom: 15px; }
    .item-box { background-color: #f1f8e9; padding: 25px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชันโหลดข้อมูลจากไฟล์ thailand.xlsx ---
@st.cache_data
def load_address_data():
    try:
        # อ่านไฟล์ Excel (กรุณาตรวจสอบชื่อ Sheet หากข้อมูลไม่ได้อยู่ใน Sheet แรก)
        df = pd.read_excel('thailand.xlsx')
        # ปรับชื่อคอลัมน์ให้เป็นมาตรฐาน (แก้ตามชื่อหัวตารางจริงในไฟล์ของคุณ)
        # ตัวอย่างสมมติว่าคอลัมน์ชื่อ: province_th, district_th, subdistrict_th, postcode
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดไฟล์ thailand.xlsx ได้: {e}")
        return pd.DataFrame()

df_addr = load_address_data()

# --- 3. การจัดการ Session State เพื่อป้องกัน Error ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

def remove_item():
    if st.session_state.items_count > 1:
        st.session_state.items_count -= 1

# --- 4. ส่วนหัวแบบฟอร์ม (Header) ---
st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; align-items: center;">
            <div class="logo-box">cpram</div>
            <div class="company-info">
                <div style="font-weight: bold; font-size: 18px;">CPRAM Co., Ltd.</div>
                <div>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</div>
            </div>
        </div>
        <div style="text-align: right;">
            <div class="doc-id">FR-QAS-10-000</div>
            <div style="font-size: 13px; margin-top: 5px;">มีผลใช้งาน: 2026-05-11</div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 10px;">
        <h2 style="color: #2e7d32;">แบบบันทึกข้อมูลประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด</h2>
    </div>
    """, unsafe_allow_html=True)

# --- 5. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
    st.date_input("วันที่ส่งวัตถุดิบ *", datetime.now(), key="d_date")
with c2:
    st.time_input("เวลาส่ง *", value=time(14, 0), key="d_time")
    st.text_input("ลงชื่อผู้กรอก", key="recorder")
with c3:
    st.text_input("อีเมลของผู้ส่งมอบ *", key="s_email")
    st.selectbox("ประเทศแหล่งปลูก (default)", ["ประเทศไทย", "จีน", "อื่นๆ"], key="c_main")

# --- 6. ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด) ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f'<div class="item-box">', unsafe_allow_html=True)
        st.subheader(f"รายการที่ {i+1}")
        
        # ช่องกรอกข้อมูลทั่วไป
        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
        r1c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
        r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

        # [ส่วนวันเวลา/ชื่อผู้ปลูก/GAP/รหัสไร่ ฯลฯ]
        r2c1, r2c2, r2c3 = st.columns(3)
        r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
        r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

        # --- ส่วนที่อยู่แหล่งปลูก Cascading Dropdown ---
        st.markdown("📍 **ที่อยู่แหล่งปลูก (ระบบดึงข้อมูลอัตโนมัติ)**")
        r5c1, r5c2, r5c3 = st.columns(3)
        
        if not df_addr.empty:
            # ดึงรายชื่อจังหวัด (สมมติคอลัมน์ชื่อ 'province_th')
            province_list = sorted(df_addr['province_th'].unique())
            sel_prov = r5c1.selectbox("จังหวัด/มณฑล", ["- เลือก -"] + province_list, key=f"prov_{i}")
            
            # ดึงรายชื่ออำเภอตามจังหวัดที่เลือก (สมมติคอลัมน์ชื่อ 'district_th')
            amphoe_list = ["- เลือกจังหวัดก่อน -"]
            if sel_prov != "- เลือก -":
                amphoe_list = sorted(df_addr[df_addr['province_th'] == sel_prov]['district_th'].unique())
            sel_amp = r5c2.selectbox("อำเภอ/เมือง", ["- เลือก -"] + amphoe_list, key=f"amp_{i}")
            
            # ดึงรายชื่อตำบลตามอำเภอที่เลือก (สมมติคอลัมน์ชื่อ 'subdistrict_th')
            tumbon_list = ["- เลือกอำเภอก่อน -"]
            if sel_amp != "- เลือก -":
                tumbon_list = sorted(df_addr[(df_addr['province_th'] == sel_prov) & (df_addr['district_th'] == sel_amp)]['subdistrict_th'].unique())
            sel_tam = r5c3.selectbox("ตำบล/เขต", ["- เลือก -"] + tumbon_list, key=f"tam_{i}")
            
            # ดึงรหัสไปรษณีย์อัตโนมัติ (สมมติคอลัมน์ชื่อ 'postcode')
            zip_code = ""
            if sel_tam != "- เลือก -":
                zip_code = df_addr[(df_addr['province_th'] == sel_prov) & 
                                   (df_addr['district_th'] == sel_amp) & 
                                   (df_addr['subdistrict_th'] == sel_tam)]['postcode'].iloc[0]
        else:
            sel_prov = r5c1.text_input("จังหวัด", key=f"prov_manual_{i}")
            sel_amp = r5c2.text_input("อำเภอ", key=f"amp_manual_{i}")
            sel_tam = r5c3.text_input("ตำบล", key=f"tam_manual_{i}")
            zip_code = ""

        # ส่วนรหัสไปรษณีย์และข้อมูลการปลูก
        r6c1, r6c2, r6c3, r6c4 = st.columns(4)
        r6c1.text_input("รหัสไปรษณีย์", value=str(zip_code), key=f"zip_{i}")
        r6c2.text_input("สายพันธุ์", key=f"breed_{i}")
        r6c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        r6c4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_type_{i}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ปุ่มจัดการรายการ
col_btn1, col_btn2, _ = st.columns([0.15, 0.15, 0.7])
col_btn1.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)
col_btn2.button("- ลบรายการล่าสุด", on_click=remove_item)

st.write("---")
if st.button("ยืนยันบันทึกข้อมูลและส่ง PDF", type="primary"):
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
