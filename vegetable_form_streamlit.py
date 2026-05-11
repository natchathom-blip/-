import streamlit as st  # บรรทัดนี้สำคัญที่สุด ห้ามลบ!
import pandas as pd
from datetime import datetime, time

# --- 1. การตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="CPRAM - Supplier Form", layout="wide")

st.markdown("""
    <style>
    .header-container { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; margin-bottom: 15px; }
    .logo-box { background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 26px; }
    .doc-id { border: 1.5px solid #000; padding: 4px 12px; font-weight: bold; text-align: center; }
    .section-header { color: #2e7d32; font-size: 20px; font-weight: bold; border-bottom: 2px solid #2e7d32; margin-top: 25px; margin-bottom: 15px; }
    .item-box { background-color: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9; margin-bottom: 20px; }
    .stButton>button { width: 100%; }
    .delete-btn button { background-color: #c62828 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. โหลดข้อมูลที่อยู่ ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_addr = load_data()

# --- 3. จัดการ Session State ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item(): st.session_state.items_count += 1
def remove_item(): 
    if st.session_state.items_count > 1: st.session_state.items_count -= 1

# --- 4. ส่วนหัว (Header) ---
st.markdown("""
    <div class="header-container">
        <div style="display: flex; align-items: center;">
            <div class="logo-box">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;"><b>CPRAM Co., Ltd.</b><br>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</div>
        </div>
        <div>
            <div class="doc-id">FR-QAS-10-000</div>
            <div style="font-size: 12px; text-align: right;">มีผลใช้งาน: 2026-05-11</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. ส่วนที่ 1 ---
st.markdown('<div class="section-header">ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
with c2: st.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
with c3: st.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")

# --- 6. ส่วนที่ 2 (UI ตามรูป image_a46037.png) ---
st.markdown('<div class="section-header">ส่วนที่ 2 — รายการวัตถุดิบ (เพิ่มได้ไม่จำกัด)</div>', unsafe_allow_html=True)

for i in range(st.session_state.items_count):
    st.markdown('<div class="item-box">', unsafe_allow_html=True)
    
    # ส่วนหัวรายการและปุ่มลบ
    h_col, b_col = st.columns([0.85, 0.15])
    h_col.subheader(f"รายการที่ {i+1}")
    if st.session_state.items_count > 1 and i == st.session_state.items_count - 1:
        b_col.button("✕ ลบรายการนี้", key=f"del_{i}", on_click=remove_item)

    # แถวที่ 1
    r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
    r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM *", key=f"mat_{i}")
    r1c2.text_input("Code", placeholder="เช่น 71000277", key=f"code_{i}")
    r1c3.number_input("จำนวน (KG) *", min_value=0.0, step=0.1, key=f"qty_{i}")

    # แถวที่ 2
    r2c1, r2c2, r2c3 = st.columns(3)
    r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
    r2c2.text_input("เวลาเก็บเกี่ยว", placeholder="เช่น 08:00", key=f"ht_{i}")
    r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")

    # แถวที่ 3
    r3c1, r3c2, r3c3 = st.columns(3)
    r3c1.text_input("เวลาที่ล้างทำความสะอาด", placeholder="เช่น 08:00 หรือ 08:00-09:30", key=f"ct_{i}")
    r3c1_2, r3c2_2, r3c3_2 = st.columns(3) # แตกแถวเพิ่มตามรูป
    r3c1_2.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
    r3c2_2.text_input("เลขที่ GAP", key=f"gap_{i}")
    r3c3_2.text_input("รหัสไร่", key=f"farm_{i}")

    # แถวที่ 4
    r4c1, r4c2 = st.columns(2)
    r4c1.text_input("ที่อยู่เลขที่", key=f"addr_no_{i}")
    r4c2.text_input("หมู่ที่", key=f"moo_{i}")

    # แถวที่ 5: ที่อยู่ Cascading
    st.markdown("📍 **ที่อยู่แหล่งปลูก (cascading dropdown)**")
    a1, a2, a3, a4 = st.columns(4)
    a1.selectbox("ประเทศ", ["ไทย", "จีน", "อื่นๆ"], key=f"country_{i}")
    
    zip_code = ""
    if not df_addr.empty:
        prov_list = sorted(df_addr['province_th'].unique())
        sel_prov = a2.selectbox("จังหวัด/มณฑล", ["- เลือก -"] + prov_list, key=f"prov_{i}")
        
        amp_opts = sorted(df_addr[df_addr['province_th'] == sel_prov]['district_th'].unique()) if sel_prov != "- เลือก -" else []
        sel_amp = a3.selectbox("อำเภอ/เมือง", ["- เลือก -"] + amp_opts, key=f"amp_{i}")
        
        tam_opts = sorted(df_addr[(df_addr['province_th'] == sel_prov) & (df_addr['district_th'] == sel_amp)]['subdistrict_th'].unique()) if sel_amp != "- เลือก -" else []
        sel_tam = a4.selectbox("ตำบล/เขต", ["- เลือก -"] + tam_opts, key=f"tam_{i}")
        
        if sel_tam != "- เลือก -":
            zip_code = df_addr[(df_addr['province_th'] == sel_prov) & (df_addr['district_th'] == sel_amp) & (df_addr['subdistrict_th'] == sel_tam)]['postcode'].iloc[0]
    
    # แถวสุดท้ายของรายการ
    r5c1, r5c2, r5c3, r5c4 = st.columns(4)
    r5c1.text_input("รหัสไปรษณีย์", value=str(zip_code), key=f"zip_{i}", disabled=True)
    r5c2.text_input("สายพันธุ์", key=f"breed_{i}")
    r5c3.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
    r5c4.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")

    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. ปุ่มดำเนินการ ---
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)
if st.button("ยืนยันข้อมูลและส่ง PDF", type="primary"):
    st.success("บันทึกข้อมูลเรียบร้อย! ระบบกำลังเตรียมส่ง PDF...")
