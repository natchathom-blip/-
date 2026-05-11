import os
import io
import urllib.request
import streamlit as st
import pandas as pd
import json
from datetime import datetime

# reportlab import แบบ safe
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

# --- 1. ตั้งค่าพื้นฐาน ---
EXCEL_PATH = "thailand.xlsx"
USER_FILE = "users.json"
SUBMISSION_SHEET = "Submissions"
MASTER_USER = "newuser"
MASTER_PASS = "password"
LOGO_PATH = "Cpram.png"

st.set_page_config(page_title="ระบบบันทึกข้อมูลผู้ส่งมอบวัตถุดิบ", layout="wide")

# Initialize Session State สำหรับการแก้ไข
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "edit_data" not in st.session_state:
    st.session_state.edit_data = None

# --- ดาวน์โหลดฟอนต์ภาษาไทย ---
def ensure_thai_font():
    font_url      = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf"
    font_bold_url = "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf"
    font_path      = "/tmp/Sarabun-Regular.ttf"
    font_bold_path = "/tmp/Sarabun-Bold.ttf"
    try:
        if not os.path.exists(font_path):
            urllib.request.urlretrieve(font_url, font_path)
        if not os.path.exists(font_bold_path):
            urllib.request.urlretrieve(font_bold_url, font_bold_path)
        pdfmetrics.registerFont(TTFont("Sarabun", font_path))
        pdfmetrics.registerFont(TTFont("SarabunBold", font_bold_path))
        return "Sarabun", "SarabunBold"
    except:
        return "Helvetica", "Helvetica-Bold"

if REPORTLAB_OK:
    THAI_FONT, THAI_FONT_BOLD = ensure_thai_font()
else:
    THAI_FONT, THAI_FONT_BOLD = "Helvetica", "Helvetica-Bold"

# --- 2. ฟังก์ชันจัดการ User ---
def load_users():
    if not os.path.exists(USER_FILE):
        default_users = {"admin": "admin2026", MASTER_USER: MASTER_PASS}
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f)
        return default_users
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

# --- 3. โหลดข้อมูลจังหวัด ---
@st.cache_data
def load_province_list():
    try:
        if os.path.exists(EXCEL_PATH):
            return pd.read_excel(EXCEL_PATH, sheet_name=0)
    except:
        pass
    return None

thailand_df = load_province_list()

# --- 4. บันทึกลง Excel (Update logic) ---
def save_data_to_excel(submission, edit_id=None):
    columns = [
        "SubmissionID", "อีเมล", "ผู้ส่งมอบวัตถุดิบ", "ที่อยู่ผู้ส่งมอบ", "วันที่ส่งมอบวัตถุดิบ",
        "จำนวนวัตถุดิบที่ส่ง", "ลำดับที่", "ชนิดวัตถุดิบที่ส่งมอบ", "จำนวน",
        "สายพันธุ์", "ลักษณะการปลูก", "ระบบการปลูก", "วันที่เก็บเกี่ยว", "เวลาเก็บเกี่ยว",
        "วันที่ล้าง/ตัดแต่ง", "เวลาล้าง/ตัดแต่ง", "ชื่อผู้ปลูก", "เลขที่ GAP",
        "รหัสไร่", "จังหวัด", "อำเภอ", "ตำบล"
    ]
    
    sub_id = edit_id if edit_id else datetime.now().strftime("%Y%m%d%H%M%S")
    rows = []
    for item in submission.get("raw_materials", []):
        rows.append({
            "SubmissionID": sub_id,
            "อีเมล": submission.get("email", ""),
            "ผู้ส่งมอบวัตถุดิบ": submission.get("supplier_name", ""),
            "ที่อยู่ผู้ส่งมอบ": submission.get("supplier_address", ""),
            "วันที่ส่งมอบวัตถุดิบ": str(submission.get("delivery_date", "")),
            "จำนวนวัตถุดิบที่ส่ง": submission.get("quantity_count", ""),
            "ลำดับที่": item.get("ลำดับที่"),
            "ชนิดวัตถุดิบที่ส่งมอบ": item.get("ชนิดวัตถุดิบที่ส่งมอบ"),
            "จำนวน": item.get("จำนวน"),
            "สายพันธุ์": item.get("สายพันธุ์"),
            "ลักษณะการปลูก": item.get("ลักษณะการปลูก"),
            "ระบบการปลูก": item.get("ระบบการปลูก"),
            "วันที่เก็บเกี่ยว": str(item.get("วันที่เก็บเกี่ยว")),
            "เวลาเก็บเกี่ยว": str(item.get("เวลาเก็บเกี่ยว")),
            "วันที่ล้าง/ตัดแต่ง": str(item.get("วันที่ล้าง/ตัดแต่ง")),
            "เวลาล้าง/ตัดแต่ง": str(item.get("เวลาล้าง/ตัดแต่ง")),
            "ชื่อผู้ปลูก": item.get("ชื่อผู้ปลูก"),
            "เลขที่ GAP": item.get("เลขที่ GAP"),
            "รหัสไร่": item.get("รหัสไร่"),
            "จังหวัด": item.get("จังหวัด"),
            "อำเภอ": item.get("อำเภอ"),
            "ตำบล": item.get("ตำบล")
        })
    new_df = pd.DataFrame(rows, columns=columns)
    
    try:
        if os.path.exists(EXCEL_PATH):
            all_sheets = pd.read_excel(EXCEL_PATH, sheet_name=None)
            if SUBMISSION_SHEET in all_sheets:
                df = all_sheets[SUBMISSION_SHEET]
                if edit_id:
                    df = df[df["SubmissionID"].astype(str) != str(edit_id)]
                final_df = pd.concat([df, new_df], ignore_index=True)
            else:
                final_df = new_df
            
            with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
                for s_name, s_df in all_sheets.items():
                    if s_name != SUBMISSION_SHEET:
                        s_df.to_excel(writer, sheet_name=s_name, index=False)
                final_df.to_excel(writer, sheet_name=SUBMISSION_SHEET, index=False)
        else:
            new_df.to_excel(EXCEL_PATH, sheet_name=SUBMISSION_SHEET, index=False)
        return sub_id
    except:
        return None

# --- 5. Generate PDF ---
def build_pdf_bytes(submission):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin_l = 18*mm
    # (ส่วน Header และการวาด PDF คล้ายเดิมแต่จัดโครงสร้างให้จบในฟังก์ชัน)
    c.setFont(THAI_FONT_BOLD, 14)
    c.drawCentredString(width / 2, height - 28*mm, "แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบ")
    c.save()
    buf.seek(0)
    return buf.read()

# --- 6. UI Main ---
st.sidebar.title("📌 เมนูหลัก")
mode = st.sidebar.radio("เลือกโหมดการใช้งาน", ["👤 ผู้ส่งข้อมูล", "🔐 ผู้สร้าง"])

if mode == "👤 ผู้ส่งข้อมูล":
    st.header("📝 แบบบันทึกข้อมูลประจำวัน")

    # ส่วนแก้ไขข้อมูล
    with st.expander("🔍 แก้ไขข้อมูลเดิม (ใช้รหัส Submission ID)"):
        c_s1, c_s2 = st.columns([3, 1])
        s_id = c_s1.text_input("กรอก Submission ID")
        if c_s2.button("ค้นหา"):
            if os.path.exists(EXCEL_PATH):
                df_search = pd.read_excel(EXCEL_PATH, sheet_name=SUBMISSION_SHEET)
                target = df_search[df_search["SubmissionID"].astype(str) == str(s_id)]
                if not target.empty:
                    st.session_state.edit_id = s_id
                    st.session_state.edit_data = target.to_dict('records')
                    st.success("พบข้อมูลแล้ว!")
                else:
                    st.error("ไม่พบรหัสนี้")

    if st.session_state.edit_id:
        st.warning(f"กำลังอยู่ในโหมดแก้ไขรหัส: {st.session_state.edit_id}")
        if st.button("ยกเลิกการแก้ไข"):
            st.session_state.edit_id = None
            st.session_state.edit_data = None
            st.rerun()

    # Helper function ดึงค่า
    def gv(field, idx=0, default=""):
        if st.session_state.edit_data and idx < len(st.session_state.edit_data):
            return st.session_state.edit_data[idx].get(field, default)
        return default

    # ฟอร์มหลัก
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        email = st.text_input("อีเมล *", value=gv("อีเมล"), key="u_email")
        supplier = st.text_input("ผู้ส่งมอบ *", value=gv("ผู้ส่งมอบวัตถุดิบ"))
    with c_f2:
        d_val = datetime.now()
        if st.session_state.edit_data:
            try: d_val = datetime.strptime(gv("วันที่ส่งมอบวัตถุดิบ"), "%Y-%m-%d")
            except: pass
        d_date = st.date_input("วันที่ส่งมอบ *", value=d_val)
        
        q_opts = ["-- เลือกจำนวน --", 1, 2, 3, 4, 5]
        curr_q = gv("จำนวนวัตถุดิบที่ส่ง")
        q_idx = q_opts.index(int(curr_q)) if str(curr_q).isdigit() else 0
        qty_count = st.selectbox("จำนวนรายการ *", q_opts, index=q_idx)

    raw_mats = []
    if qty_count != "-- เลือกจำนวน --":
        for i in range(1, int(qty_count) + 1):
            with st.expander(f"📦 รายการที่ {i}", expanded=True):
                m_type = st.text_input(f"ชนิดวัตถุดิบ {i}", value=gv("ชนิดวัตถุดิบที่ส่งมอบ", i-1), key=f"mt_{i}")
                m_qty = st.number_input(f"จำนวน (กก.) {i}", value=float(gv("จำนวน", i-1, 0)), key=f"mq_{i}")
                
                st.write("**ที่ตั้งไร่**")
                loc1, loc2, loc3 = st.columns(3)
                p_list = sorted(thailand_df["จังหวัด"].unique().tolist()) if thailand_df is not None else []
                with loc1:
                    pv = st.selectbox(f"จังหวัด {i}", ["-- เลือกจังหวัด --"] + p_list, key=f"pv_{i}")
                with loc2:
                    d_list = sorted(thailand_df[thailand_df["จังหวัด"] == pv]["อำเภอ"].unique().tolist()) if pv != "-- เลือกจังหวัด --" else []
                    dt = st.selectbox(f"อำเภอ {i}", ["-- เลือกอำเภอ --"] + d_list, key=f"dt_{i}")
                with loc3:
                    s_list = sorted(thailand_df[(thailand_df["จังหวัด"] == pv) & (thailand_df["อำเภอ"] == dt)]["ตำบล"].unique().tolist()) if dt != "-- เลือกอำเภอ --" else []
                    sd = st.selectbox(f"ตำบล {i}", ["-- เลือกตำบล --"] + s_list, key=f"sd_{i}")

                raw_mats.append({
                    "ลำดับที่": i, "ชนิดวัตถุดิบที่ส่งมอบ": m_type, "จำนวน": m_qty,
                    "จังหวัด": pv, "อำเภอ": dt, "ตำบล": sd
                })

        if st.button("✅ บันทึกข้อมูลและรับ Submission ID", use_container_width=True):
            if not email or not supplier:
                st.error("กรุณากรอกข้อมูลสำคัญให้ครบ")
            else:
                submission = {
                    "email": email, "supplier_name": supplier, "delivery_date": d_date,
                    "quantity_count": qty_count, "raw_materials": raw_mats
                }
                res_id = save_data_to_excel(submission, edit_id=st.session_state.edit_id)
                if res_id:
                    st.success(f"บันทึกสำเร็จ! รหัสอ้างอิงของคุณคือ: {res_id}")
                    st.session_state.edit_id = None
                    st.session_state.edit_data = None
                    # ปุ่มดาวน์โหลด PDF จะปรากฏขึ้น

elif mode == "🔐 ผู้สร้าง":
    st.subheader("🔑 ระบบจัดการข้อมูล")
    # ส่วน Login และตารางข้อมูล (เหมือนโค้ดเดิมของคุณ)
    if os.path.exists(EXCEL_PATH):
        df_all = pd.read_excel(EXCEL_PATH, sheet_name=SUBMISSION_SHEET)
        st.dataframe(df_all)
