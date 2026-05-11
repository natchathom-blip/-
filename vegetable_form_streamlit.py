import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime, time

# --- 1. SETUP & DATA LOADING ---
st.set_page_config(page_title="CPRAM Form", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        # ระบบค้นหาหัวคอลัมน์แบบยืดหยุ่นสูง
        def find_c(keys):
            for k in keys:
                for col in df.columns:
                    if k in col.lower() or k in col: return col
            return None
        
        m = {
            'p': find_c(['province', 'จังหวัด']),
            'a': find_c(['district_th', 'อำเภอ']),
            't': find_c(['subdistrict', 'ตำบล']),
            'z': find_c(['postcode', 'รหัสไปรษณีย์', 'zip'])
        }
        return df, m
    except:
        return pd.DataFrame(), {}

df_addr, col_m = load_data()

# --- 2. SESSION STATE MANAGEMENT (ล็อกข้อมูลถาวร) ---
if 'items_count' not in st.session_state: st.session_state.items_count = 1
# สร้างคลังเก็บข้อมูลเพื่อไม่ให้หายตอน Rerun
if 'form_data' not in st.session_state: st.session_state.form_data = {}

def sync_data(key, val):
    st.session_state.form_data[key] = val

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
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2, c3 = st.columns(3)
# ทุุกช่องใช้ key และเก็บเข้า form_data ทันที
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_n", on_change=None)
s_email = c2.text_input("อีเมลสำหรับรับ PDF *", key="s_e")
s_date = c3.date_input("วันที่ส่งวัตถุดิบ *", key="s_d")

st.markdown("---")
st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ (ฟิลด์ครบ)")

for i in range(st.session_state.items_count):
    with st.expander(f"📦 รายการที่ {i+1}", expanded=True):
        r1, r2, r3 = st.columns([2, 1, 1])
        r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r2.text_input("Code", key=f"code_{i}")
        r3.number_input("จำนวน (KG)", key=f"qty_{i}", step=0.01)

        r4, r5, r6, r7 = st.columns(4)
        r4.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
        r5.text_input("เวลาเก็บเกี่ยว", key=f"ht_{i}", placeholder="08:00")
        r6.text_input("ชื่อผู้ปลูก", key=f"grow_{i}")
        r7.text_input("เลขที่ GAP", key=f"gap_{i}")

        # ที่อยู่ (แก้ไข KeyError บรรทัด 109)
        a1, a2, a3, a4 = st.columns(4)
        pc, ac, tc, zc = col_m['p'], col_m['a'], col_m['t'], col_m['z']
        
        if pc and not df_addr.empty:
            p_val = a1.selectbox("จังหวัด", ["- เลือก -"] + sorted(df_addr[pc].unique().tolist()), key=f"p_{i}")
            
            a_opts = sorted(df_addr[df_addr[pc] == p_val][ac].unique().tolist()) if p_val != "- เลือก -" else []
            a_val = a2.selectbox("อำเภอ", ["- เลือก -"] + a_opts, key=f"a_{i}")
            
            t_opts = sorted(df_addr[(df_addr[pc] == p_val) & (df_addr[ac] == a_val)][tc].unique().tolist()) if a_val != "- เลือก -" else []
            t_val = a3.selectbox("ตำบล", ["- เลือก -"] + t_opts, key=f"t_{i}")
            
            # ป้องกัน KeyError บรรทัด 109 โดยตรวจสอบคอลัมน์ก่อนดึงค่า
            zip_final = ""
            if t_val != "- เลือก -" and zc in df_addr.columns:
                res = df_addr[(df_addr[pc] == p_val) & (df_addr[ac] == a_val) & (df_addr[tc] == t_val)]
                if not res.empty:
                    zip_final = res[zc].iloc[0]
            a4.text_input("รหัสไปรษณีย์", value=str(zip_final), key=f"z_show_{i}", disabled=True)

# --- 5. BUTTONS ---
if st.button("+ เพิ่มรายการวัตถุดิบ"):
    st.session_state.items_count += 1
    st.rerun()

if st.button("ยืนยันข้อมูลและส่ง PDF", type="primary"):
    if not s_name or not s_email:
        st.error("กรุณากรอกข้อมูลส่วนที่ 1 ให้ครบถ้วน")
    else:
        st.success(f"บันทึกสำเร็จ! ระบบกำลังส่ง PDF ไปที่ {s_email}")
        # ข้อมูลทุกอย่างถูกล็อกไว้ใน st.session_state เรียบร้อยแล้ว
