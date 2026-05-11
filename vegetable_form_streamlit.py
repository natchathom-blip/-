import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CPRAM Form", layout="wide")

# --- 2. โหลดข้อมูล (ดึงตามชื่อคอลัมน์ภาษาไทย) ---
@st.cache_data
def load_address_data():
    try:
        # อ่านไฟล์และล้างช่องว่างที่หัวคอลัมน์
        df = pd.read_excel('thailand.xlsx')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดไฟล์ได้: {e}")
        return pd.DataFrame()

df_addr = load_address_data()

# กำหนดชื่อคอลัมน์ให้ตรงกับไฟล์ของคุณเป๊ะๆ
P_COL = "จังหวัด"
A_COL = "อำเภอ"
T_COL = "ตำบล"

# --- 3. ส่วนหัว (Header) ---
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2e7d32; padding-bottom: 10px;">
        <div style="background-color: #2e7d32; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; font-size: 24px;">cpram</div>
        <div style="text-align: right;"><b>FR-QAS-10-000</b><br><small>มีผลใช้งาน: 2026-05-08</small></div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ ---
st.subheader("ส่วนที่ 1 — ข้อมูลผู้ส่งมอบ")
c1, c2, c3 = st.columns(3)
s_name = c1.text_input("ผู้ส่งมอบ (Supplier) *", key="s_name")
s_email = c2.text_input("อีเมลสำหรับรับ PDF *", key="s_email")
s_date = c3.date_input("วันที่ส่งวัตถุดิบ *", key="s_date")

# --- 5. ส่วนที่ 2 — รายการวัตถุดิบ ---
if 'items_count' not in st.session_state: st.session_state.items_count = 1
def add_item(): st.session_state.items_count += 1

st.markdown("---")
st.subheader("ส่วนที่ 2 — รายการวัตถุดิบ")

for i in range(st.session_state.items_count):
    with st.container():
        st.markdown(f"**📦 รายการที่ {i+1}**")
        
        # ข้อมูลวัตถุดิบ
        r1, r2, r3 = st.columns([2, 1, 1])
        r1.text_input("ชนิดวัตถุดิบ *", key=f"mat_{i}")
        r2.text_input("Code", key=f"code_{i}")
        r3.number_input("จำนวน (KG)", key=f"qty_{i}", step=0.1)

        # ส่วนที่อยู่ (Cascading Dropdown จากไฟล์ภาษาไทย)
        st.write("📍 ที่อยู่แหล่งปลูก")
        a1, a2, a3, a4 = st.columns(4)
        
        # 1. เลือกจังหวัด
        prov_list = sorted(df_addr[P_COL].unique()) if P_COL in df_addr.columns else []
        sel_p = a1.selectbox("จังหวัด", ["- เลือก -"] + prov_list, key=f"p_{i}")
        
        # 2. เลือกอำเภอ
        amp_opts = sorted(df_addr[df_addr[P_COL] == sel_p][A_COL].unique()) if sel_p != "- เลือก -" else []
        sel_a = a2.selectbox("อำเภอ", ["- เลือก -"] + amp_opts, key=f"a_{i}")
        
        # 3. เลือกตำบล
        tam_opts = sorted(df_addr[(df_addr[P_COL] == sel_p) & (df_addr[A_COL] == sel_a)][T_COL].unique()) if sel_a != "- เลือก -" else []
        sel_t = a3.selectbox("ตำบล", ["- เลือก -"] + tam_opts, key=f"t_{i}")
        
        # 4. รหัสไปรษณีย์ (เนื่องจากไฟล์ไม่มีข้อมูล จึงให้กรอกเอง)
        a4.text_input("รหัสไปรษณีย์", key=f"z_{i}")

        st.markdown("---")

st.button("+ เพิ่มรายการวัตถุดิบ", on_click=add_item)

# --- 6. ปุ่มส่งข้อมูล ---
if st.button("ยืนยันข้อมูลและดาวน์โหลด PDF", type="primary"):
    if not s_name or not s_email:
        st.error("กรุณากรอกข้อมูลส่วนที่ 1 ให้ครบถ้วน")
    else:
        st.success("บันทึกสำเร็จ!")
