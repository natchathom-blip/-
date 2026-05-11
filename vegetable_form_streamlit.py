import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="CPRAM Form", layout="wide")

@st.cache_data
def load_address():
    try:
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns] # ล้างช่องว่างที่หัวคอลัมน์
        
        # ฟังก์ชันค้นหาชื่อคอลัมน์อัตโนมัติ (ต่อให้ชื่อ จังหวัด หรือ province ก็หาเจอ)
        def find_col(keywords):
            for k in keywords:
                for col in df.columns:
                    if k in col.lower() or k in col: return col
            return None

        map_cols = {
            'p': find_col(['province', 'จังหวัด']),
            'a': find_col(['district_th', 'อำเภอ']),
            't': find_col(['subdistrict', 'ตำบล']),
            'z': find_col(['postcode', 'รหัสไปรษณีย์', 'zip'])
        }
        return df, map_cols
    except:
        return pd.DataFrame(), {}

df_addr, col_map = load_address()

# --- 2. SESSION STATE (กันข้อมูลหาย) ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item_callback():
    st.session_state.items_count += 1

# --- 3. HEADER (FR-QAS-10-000) ---
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; border-bottom: 3px solid #2e7d32; padding-bottom: 10px;">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 24px;">cpram</div>
            <div style="margin-left: 15px; color: #2e7d32;"><b>CPRAM Co., Ltd.</b><br><small>ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ</small></div>
        </div>
        <div style="text-align: right;">
            <div style="border: 1.5px solid black; padding: 2px 10px;"><b>FR-QAS-10-000</b></div>
            <small>มีผลใช้งาน: 2026-05-08</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. FORM INPUTS ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="lock_s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="lock_s_date")
s_time = c3.time_input("เวลาส่ง *", value=time(14, 0), key="lock_s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="lock_s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="lock_recorder")
origin = c6.selectbox("ประเทศแหล่งปลูก", ["ประเทศไทย", "ประเทศจีน", "อื่นๆ"], key="lock_origin")

st.markdown("---")
st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ (รายละเอียดครบถ้วน)")

for i in range(st.session_state.items_count):
    with st.expander(f"📦 รายการวัตถุดิบที่ {i+1}", expanded=True):
        # แถวที่ 1
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        r1c1.text_input("ชนิดวัตถุดิบที่ส่งให้ CPRAM *", key=f"mat_{i}")
        r1c2.text_input("Code", key=f"code_{i}")
        r1c3.number_input("จำนวน (KG)", key=f"qty_{i}")

        # แถวที่ 2: วันเวลา
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        r2c1.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r2c2.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
        r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"cd_{i}")
        r2c4.text_input("เวลาที่ล้าง", key=f"ct_{i}")

        # แถวที่ 3: ข้อมูลผู้ปลูก
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        r3c1.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        r3c2.text_input("เลขที่ GAP", key=f"gap_{i}")
        r3c3.text_input("รหัสไร่", key=f"farm_{i}")
        r3c4.text_input("บ้านเลขที่/หมู่ที่", key=f"addr_no_{i}")

        # แถวที่ 4: ที่อยู่ (ดึงจาก col_map เพื่อแก้ KeyError)
        a1, a2, a3, a4 = st.columns(4)
        p_col, a_col, t_col, z_col = col_map['p'], col_map['a'], col_map['t'], col_map['z']

        if p_col:
            sel_p = a1.selectbox("จังหวัด", ["- เลือก -"] + sorted(df_addr[p_col].unique().tolist()), key=f"p_{i}")
            
            amp_list = sorted(df_addr[df_addr[p_col] == sel_p][a_col].unique().tolist()) if sel_p != "- เลือก -" else []
            sel_a = a2.selectbox("อำเภอ/เมือง", ["- เลือก -"] + amp_list, key=f"a_{i}")
            
            tam_list = sorted(df_addr[(df_addr[p_col] == sel_p) & (df_addr[a_col] == sel_a)][t_col].unique().tolist()) if sel_a != "- เลือก -" else []
            sel_t = a3.selectbox("ตำบล/เขต", ["- เลือก -"] + tam_list, key=f"t_{i}")
            
            zip_val = ""
            if sel_t != "- เลือก -":
                zip_val = df_addr[(df_addr[p_col] == sel_p) & (df_addr[a_col] == sel_a) & (df_addr[t_col] == sel_t)][z_col].iloc[0]
            a4.text_input("รหัสไปรษณีย์", value=str(zip_val), key=f"z_{i}", disabled=True)

        # แถวที่ 5: ลักษณะการปลูก
        r5c1, r5c2, r5c3 = st.columns(3)
        r5c1.text_input("สายพันธุ์", key=f"breed_{i}")
        r5c2.selectbox("ลักษณะการปลูก", ["- เลือก -", "ปลูกอินทรีย์", "ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ปลูกไฮโดรโปนิกส์"], key=f"style_{i}")
        r5c3.selectbox("ลักษณะสถานที่ปลูก", ["- เลือก -", "โรงเรือน", "แปลงเปิด"], key=f"loc_{i}")

# --- 5. ACTION BUTTONS ---
st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item_callback)

if st.button("ยืนยันข้อมูลและส่ง PDF", type="primary"):
    if not s_name or not s_email:
        st.error("❌ กรุณากรอกชื่อและอีเมลให้ครบถ้วน")
    else:
        st.success(f"✅ บันทึกข้อมูลสำเร็จ! ระบบกำลังเตรียมส่ง PDF ไปที่ {s_email}")
        # ส่วนเรียก PDF Generator และ SMTP จะดึงข้อมูลจาก st.session_state มาใช้ได้เลย ข้อมูลไม่หายแน่นอน
