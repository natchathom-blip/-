import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time

# --- 1. SETUP & DATA LOADING ---
st.set_page_config(page_title="CPRAM - Supplier Form", layout="wide")

@st.cache_data
def load_thailand_data():
    try:
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        # ค้นหาคอลัมน์ จังหวัด/อำเภอ/ตำบล อัตโนมัติ (ป้องกัน KeyError)
        def find_col(keywords):
            for k in keywords:
                for col in df.columns:
                    if k in col.lower() or k in col: return col
            return None
        
        map_cols = {
            'prov': find_col(['province', 'จังหวัด']),
            'amp': find_col(['district_th', 'อำเภอ', 'district']),
            'tam': find_col(['subdistrict', 'ตำบล']),
            'zip': find_col(['postcode', 'รหัสไปรษณีย์', 'zip'])
        }
        return df, map_cols
    except:
        return pd.DataFrame(), {}

df_addr, col_map = load_thailand_data()

# --- 2. SESSION STATE MANAGEMENT ---
if 'items_count' not in st.session_state:
    st.session_state.items_count = 1

def add_item():
    st.session_state.items_count += 1

# --- 3. HEADER (ตาม FR-QAS-10-000) ---
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

# --- 4. INPUT FORM ---
# ส่วนที่ 1: ข้อมูลผู้ส่งมอบ (ล็อกด้วย key)
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบและการส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_date = c2.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")
s_time = c3.time_input("เวลาส่ง *", key="s_time")

c4, c5, c6 = st.columns(3)
s_email = c4.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
recorder = c5.text_input("ลงชื่อผู้กรอก", key="recorder")
origin = c6.selectbox("ประเทศแหล่งปลูก", ["ประเทศไทย", "ประเทศจีน", "อื่นๆ"], key="origin")

st.markdown("---")
st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ (รายละเอียดครบถ้วน)")

# วนลูปสร้างรายการวัตถุดิบ
for i in range(st.session_state.items_count):
    with st.expander(f"📦 รายการวัตถุดิบที่ {i+1}", expanded=True):
        # แถวที่ 1: ข้อมูลพื้นฐาน
        r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
        r1c1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r1c2.text_input("Code (เช่น 721003)", key=f"code_{i}")
        r1c3.number_input("จำนวน (KG)", key=f"qty_{i}")

        # แถวที่ 2: วันเวลาเก็บเกี่ยวและล้าง
        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        r2c1.date_input("วันที่เก็บเกี่ยว", key=f"h_date_{i}")
        r2c2.text_input("เวลาเก็บเกี่ยว", key=f"h_time_{i}", placeholder="เช่น 08:00")
        r2c3.date_input("วันที่ล้างทำความสะอาด", key=f"c_date_{i}")
        r2c4.text_input("เวลาที่ล้าง", key=f"c_time_{i}", placeholder="เช่น 10:30")

        # แถวที่ 3: ข้อมูลผู้ปลูกและไร่
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)
        r3c1.text_input("ชื่อผู้ปลูก", key=f"grower_{i}")
        r3c2.text_input("เลขที่ GAP", key=f"gap_{i}")
        r3c3.text_input("รหัสไร่", key=f"farm_{i}")
        r3c4.text_input("บ้านเลขที่/หมู่ที่", key=f"addr_no_{i}")

        # แถวที่ 4: ที่อยู่ (จังหวัด/อำเภอ/ตำบล)
        a1, a2, a3, a4 = st.columns(4)
        p_col, a_col, t_col, z_col = col_map.get('prov'), col_map.get('amp'), col_map.get('tam'), col_map.get('zip')

        if p_col and not df_addr.empty:
            sel_p = a1.selectbox("จังหวัด", ["- เลือก -"] + sorted(df_addr[p_col].unique().tolist()), key=f"p_{i}")
            
            amp_list = sorted(df_addr[df_addr[p_col] == sel_p][a_col].unique().tolist()) if sel_p != "- เลือก -" else []
            sel_a = a2.selectbox("อำเภอ/เมือง", ["- เลือก -"] + amp_list, key=f"a_{i}")
            
            tam_list = sorted(df_addr[(df_addr[p_col] == sel_p) & (df_addr[a_col] == sel_a)][t_col].unique().tolist()) if sel_a != "- เลือก -" else []
            sel_t = a3.selectbox("ตำบล/เขต", ["- เลือก -"] + tam_list, key=f"t_{i}")
            
            zip_val = ""
            if sel_t != "- เลือก -":
                zip_val = df_addr[(df_addr[p_col] == sel_p) & (df_addr[a_col] == sel_a) & (df_addr[t_col] == sel_t)][z_col].iloc[0]
            a4.text_input("รหัสไปรษณีย์", value=str(zip_val), key=f"z_{i}", disabled
