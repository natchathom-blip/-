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
    except: pass
    return None

thailand_df = load_province_list()

# --- 4. บันทึกลง Excel ---
def save_data_to_excel(submission):
    columns = [
        "อีเมล", "ผู้ส่งมอบวัตถุดิบ", "ที่อยู่ผู้ส่งมอบ", "วันที่ส่งมอบวัตถุดิบ",
        "จำนวนวัตถุดิบที่ส่ง", "ลำดับที่", "ชนิดวัตถุดิบที่ส่งมอบ", "จำนวน",
        "สายพันธุ์", "ลักษณะการปลูก", "ระบบการปลูก", "วันที่เก็บเกี่ยว", "เวลาเก็บเกี่ยว",
        "วันที่ล้าง/ตัดแต่ง", "เวลาล้าง/ตัดแต่ง", "ชื่อผู้ปลูก", "เลขที่ GAP",
        "รหัสไร่", "จังหวัด", "อำเภอ", "ตำบล"
    ]
    rows = []
    for item in submission.get("raw_materials", []):
        rows.append({
            "อีเมล": submission.get("email", ""),
            "ผู้ส่งมอบวัตถุดิบ": submission.get("supplier_name", ""),
            "ที่อยู่ผู้ส่งมอบ": submission.get("supplier_address", ""),
            "วันที่ส่งมอบวัตถุดิบ": submission.get("delivery_date", ""),
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
            with pd.ExcelWriter(EXCEL_PATH, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                try:
                    existing_df = pd.read_excel(EXCEL_PATH, sheet_name=SUBMISSION_SHEET)
                    final_df = pd.concat([existing_df, new_df], ignore_index=True)
                except: final_df = new_df
                final_df.to_excel(writer, sheet_name=SUBMISSION_SHEET, index=False)
        else:
            new_df.to_excel(EXCEL_PATH, sheet_name=SUBMISSION_SHEET, index=False)
    except: pass

# --- 5. Generate PDF ---
def draw_header(c, width, height):
    if os.path.exists(LOGO_PATH):
        logo_w, logo_h = 35*mm, 20*mm
        c.drawImage(LOGO_PATH, width - logo_w - 15*mm, height - logo_h - 8*mm,
                    width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")
    c.setFillColor(colors.black)
    c.setFont(THAI_FONT_BOLD, 16)
    c.drawCentredString(width / 2, height - 30*mm,
                        "แบบสอบถามประจำวันผู้ส่งมอบวัตถุดิบกลุ่มผักสลัด")

def build_pdf_bytes(submission):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin_l = 20*mm
    margin_r = width - 20*mm
    fs = 13

    items           = submission.get("raw_materials", [])
    delivery_date   = submission.get("delivery_date", "")
    supplier_name   = submission.get("supplier_name", "")
    supplier_address= submission.get("supplier_address", "")

    def draw_line_only(x1, y, x2):
        c.setLineWidth(0.5)
        c.setStrokeColor(colors.black)
        c.line(x1, y - 1.5*mm, x2, y - 1.5*mm)

    def put_label(label, x, y):
        c.setFont(THAI_FONT, fs)
        c.setFillColor(colors.black)
        c.drawString(x, y, label)

    def put_value(value, x, y, line_end):
        c.setFont(THAI_FONT, fs)
        c.setFillColor(colors.black)
        c.drawString(x, y, str(value) if value else "")
        draw_line_only(x, y, line_end)

    def new_page():
        c.showPage()
        draw_header(c, width, height)
        return height - 38*mm

    def row_supplier(y):
        put_label("ผู้ส่งมอบ (Supplier)", margin_l, y)
        put_value(supplier_name, margin_l + 48*mm, y, width/2 + 10*mm)
        put_label("วันที่ส่งวัตถุดิบ", width/2 + 12*mm, y)
        put_value(delivery_date, width/2 + 40*mm, y, margin_r)
        return y - 12*mm

    def row_material(mat, seq, y):
        if y < 70*mm:
            y = new_page()

        m_type = mat.get("ชนิดวัตถุดิบที่ส่งมอบ", "")
        m_code = mat.get("รหัสไร่", "")
        m_qty  = mat.get("จำนวน", "")
        m_var  = mat.get("สายพันธุ์", "")
        m_meth = mat.get("ลักษณะการปลูก", "")
        m_sys  = mat.get("ระบบการปลูก", "")
        h_date = str(mat.get("วันที่เก็บเกี่ยว", ""))
        h_time = str(mat.get("เวลาเก็บเกี่ยว", ""))
        p_date = str(mat.get("วันที่ล้าง/ตัดแต่ง", ""))
        p_time = str(mat.get("เวลาล้าง/ตัดแต่ง", ""))
        grower = mat.get("ชื่อผู้ปลูก", "")
        gap    = mat.get("เลขที่ GAP", "")
        addr   = f"จ.{mat.get('จังหวัด','')}  อ.{mat.get('อำเภอ','')}  ต.{mat.get('ตำบล','')}  {supplier_address}"

        # แถว: ลำดับ / ชนิดวัตถุดิบ / Code / จำนวน
        put_label(f"{seq}. ชนิดวัตถุดิบที่ส่งให้ทาง CPRAM", margin_l, y)
        put_value(m_type, margin_l + 68*mm, y, width/2 + 5*mm)
        put_label("Code", width/2 + 7*mm, y)
        put_value(m_code, width/2 + 19*mm, y, width/2 + 42*mm)
        put_label("จำนวน", width/2 + 44*mm, y)
        put_value(m_qty, width/2 + 57*mm, y, margin_r)
        y -= 10*mm

        # สายพันธุ์ / ลักษณะการปลูก / ระบบการปลูก
        put_label("สายพันธุ์", margin_l, y)
        put_value(m_var, margin_l + 20*mm, y, margin_l + 58*mm)
        put_label("ลักษณะการปลูก", margin_l + 60*mm, y)
        put_value(m_meth, margin_l + 88*mm, y, width/2 + 30*mm)
        put_label("ระบบการปลูก", width/2 + 32*mm, y)
        put_value(m_sys, width/2 + 56*mm, y, margin_r)
        y -= 10*mm

        # วันที่เก็บเกี่ยว / เวลาเก็บเกี่ยว
        put_label("วันที่เก็บเกี่ยววัตถุดิบ", margin_l, y)
        put_value(h_date, margin_l + 48*mm, y, width/2 - 5*mm)
        put_label("เวลาเก็บเกี่ยว", width/2 + 2*mm, y)
        put_value(h_time, width/2 + 30*mm, y, margin_r)
        y -= 10*mm

        # วันที่ล้าง / เวลาล้าง
        put_label("วันที่ล้าง/ตัดแต่ง", margin_l, y)
        put_value(p_date, margin_l + 40*mm, y, width/2 - 5*mm)
        put_label("เวลาล้าง/ตัดแต่ง", width/2 + 2*mm, y)
        put_value(p_time, width/2 + 32*mm, y, margin_r)
        y -= 10*mm

        # ชื่อผู้ปลูก
        put_label("ชื่อผู้ปลูก", margin_l, y)
        put_value(grower, margin_l + 24*mm, y, width/2 - 5*mm)
        y -= 10*mm

        # เลขที่ GAP / รหัสไร่
        put_label("เลขที่ GAP", margin_l, y)
        put_value(gap, margin_l + 24*mm, y, width/2 - 5*mm)
        put_label("รหัสไร่", width/2 + 2*mm, y)
        put_value(mat.get("รหัสไร่", ""), width/2 + 18*mm, y, width/2 + 50*mm)
        y -= 10*mm

        # ที่อยู่
        put_label("ที่อยู่", margin_l, y)
        put_value(addr, margin_l + 14*mm, y, margin_r)
        y -= 14*mm

        return y

    def draw_signature(y):
        sig_x = width/2 + 15*mm
        put_label("ลงชื่อ", sig_x, y)
        draw_line_only(sig_x + 16*mm, y, margin_r)
        put_label("วันที่", sig_x, y - 8*mm)
        draw_line_only(sig_x + 14*mm, y - 8*mm, margin_r)

    # วาดหน้าแรก
    draw_header(c, width, height)
    y = height - 38*mm
    y = row_supplier(y)
    y -= 4*mm

    for idx, mat in enumerate(items, start=1):
        y = row_material(mat, idx, y)

    draw_signature(min(y - 10*mm, 55*mm))
    c.save()
    buf.seek(0)
    return buf.read()

# --- 6. Sidebar ---
st.sidebar.title("📌 เมนูหลัก")
mode = st.sidebar.radio("เลือกโหมดการใช้งาน", ["👤 ผู้ส่งข้อมูล", "🔐 ผู้สร้าง"])

# --- 7. โหมดผู้ส่งข้อมูล ---
if mode == "👤 ผู้ส่งข้อมูล":
    st.header("📝 แบบบันทึกข้อมูลประจำวัน")

    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("อีเมลของคุณ *", key="u_email")
    with col2:
        supplier_name = st.text_input("ผู้ส่งมอบวัตถุดิบ *")

    address = st.text_area("ที่อยู่ผู้ส่งมอบ *")

    c3, c4 = st.columns(2)
    with c3:
        d_date = st.date_input("วันที่ส่งมอบวัตถุดิบ *")
    with c4:
        qty_count = st.selectbox("จำนวนวัตถุดิบที่ส่ง *", ["-- เลือกจำนวน --", 1, 2, 3, 4, 5])

    raw_mats = []
    if qty_count != "-- เลือกจำนวน --":
        st.markdown("---")
        st.subheader("📦 รายละเอียดวัตถุดิบที่ส่งมอบ")
        for i in range(1, int(qty_count) + 1):
            with st.expander(f"📦 วัตถุดิบที่ {i}", expanded=True):
                l1, l2 = st.columns(2)
                with l1:
                    m_type = st.text_input(f"ชนิดวัตถุดิบที่ส่งมอบ * (รายการที่ {i})", key=f"mt_{i}")
                    m_qty  = st.number_input("จำนวน (กก.)", key=f"mq_{i}", min_value=0.0)
                    m_var  = st.text_input("สายพันธุ์ *", key=f"mv_{i}")
                    m_method = st.radio("ลักษณะการปลูก *",
                                        ["ปลูกดินยกพื้น", "ปลูกดินไม่ยกพื้น", "ไฮโดรโปนิกส์"],
                                        key=f"meth_{i}")
                with l2:
                    m_sys  = st.radio("ระบบการปลูก *", ["ระบบเปิด", "ระบบปิด"], key=f"sys_{i}")
                    h_date = st.date_input("วันที่เก็บเกี่ยว", key=f"hd_{i}")
                    h_time = st.time_input("เวลาเก็บเกี่ยว", key=f"ht_{i}")
                    p_date = st.date_input("วันที่ล้าง/ตัดแต่ง", key=f"pd_{i}")
                    p_time = st.time_input("เวลาล้าง/ตัดแต่ง", key=f"pt_{i}")

                st.markdown("---")
                l3, l4 = st.columns(2)
                with l3:
                    m_grower = st.text_input("ชื่อผู้ปลูก *", key=f"mg_{i}")
                    m_gap    = st.text_input("เลขที่ GAP", key=f"gap_{i}")
                with l4:
                    m_code = st.text_input("รหัสไร่", key=f"code_{i}")

                st.write("**ที่ตั้งไร่ (จังหวัด/อำเภอ/ตำบล) ***")
                loc1, loc2, loc3 = st.columns(3)
                p_list = sorted(thailand_df["จังหวัด"].unique().tolist()) if thailand_df is not None else []
                with loc1:
                    pv = st.selectbox("จังหวัด", ["-- เลือกจังหวัด --"] + p_list, key=f"pv_{i}")
                with loc2:
                    d_list = sorted(thailand_df[thailand_df["จังหวัด"] == pv]["อำเภอ"].unique().tolist()) if pv != "-- เลือกจังหวัด --" else []
                    dt = st.selectbox("อำเภอ", ["-- เลือกอำเภอ --"] + d_list, key=f"dt_{i}")
                with loc3:
                    s_list = sorted(thailand_df[(thailand_df["จังหวัด"] == pv) & (thailand_df["อำเภอ"] == dt)]["ตำบล"].unique().tolist()) if dt != "-- เลือกอำเภอ --" else []
                    sd = st.selectbox("ตำบล", ["-- เลือกตำบล --"] + s_list, key=f"sd_{i}")

                raw_mats.append({
                    "ลำดับที่": i, "ชนิดวัตถุดิบที่ส่งมอบ": m_type, "จำนวน": m_qty,
                    "สายพันธุ์": m_var, "ลักษณะการปลูก": m_method, "ระบบการปลูก": m_sys,
                    "วันที่เก็บเกี่ยว": h_date, "เวลาเก็บเกี่ยว": h_time,
                    "วันที่ล้าง/ตัดแต่ง": p_date, "เวลาล้าง/ตัดแต่ง": p_time,
                    "ชื่อผู้ปลูก": m_grower, "เลขที่ GAP": m_gap, "รหัสไร่": m_code,
                    "จังหวัด": pv, "อำเภอ": dt, "ตำบล": sd
                })

        # ปุ่มบันทึก
        if st.button("✅ ส่งข้อมูลและดาวน์โหลด PDF", use_container_width=True):
            if not email or qty_count == "-- เลือกจำนวน --":
                st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
            else:
                submission = {
                    "email": email, "supplier_name": supplier_name,
                    "supplier_address": address, "delivery_date": str(d_date),
                    "quantity_count": qty_count, "raw_materials": raw_mats
                }
                save_data_to_excel(submission)
                if REPORTLAB_OK:
                    pdf_bytes = build_pdf_bytes(submission)
                    st.session_state["last_pdf"]      = pdf_bytes
                    st.session_state["last_pdf_name"] = f"vegetable_delivery_{str(d_date)}.pdf"
                st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

        # ปุ่มโหลด PDF
        if st.session_state.get("last_pdf"):
            st.download_button(
                label="📄 ดาวน์โหลด PDF แบบฟอร์ม",
                data=st.session_state["last_pdf"],
                file_name=st.session_state.get("last_pdf_name", "form.pdf"),
                mime="application/pdf",
                use_container_width=True
            )

    # ประวัติเฉพาะอีเมลตัวเอง
    if email and os.path.exists(EXCEL_PATH):
        try:
            st.markdown("---")
            st.subheader("🗂️ ข้อมูลที่บันทึก")
            all_df = pd.read_excel(EXCEL_PATH, sheet_name=SUBMISSION_SHEET)
            my_df  = all_df[all_df["อีเมล"] == email]   # ← กรองเฉพาะอีเมลตัวเอง
            if not my_df.empty:
                st.dataframe(my_df, use_container_width=True)
            else:
                st.info("ยังไม่มีข้อมูลที่บันทึก")
        except:
            pass

# --- 8. โหมดผู้สร้าง ---
elif mode == "🔐 ผู้สร้าง":
    users_db = load_users()
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    if "must_reset" not in st.session_state:
        st.session_state.must_reset = False

    # ── หน้า Login ──
    if not st.session_state.logged_in_user:
        st.subheader("🔑 เข้าสู่ระบบผู้สร้าง")
        u_in = st.text_input("ชื่อผู้ใช้", key="lin_u")
        p_in = st.text_input("รหัสผ่าน", type="password", key="lin_p")
        if st.button("ตกลง", use_container_width=True):
            if u_in in users_db and users_db[u_in] == p_in:
                st.session_state.logged_in_user = u_in
                # ถ้าเข้าด้วยรหัสกลาง → บังคับตั้งรหัสใหม่
                if u_in == MASTER_USER and p_in == MASTER_PASS:
                    st.session_state.must_reset = True
                else:
                    st.session_state.must_reset = False
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    # ── บังคับตั้งรหัสใหม่ (เฉพาะคนที่เข้าด้วยรหัสกลาง) ──
    elif st.session_state.must_reset:
        st.subheader("🔒 ตั้งรหัสผ่านส่วนตัวก่อนใช้งาน")
        st.info("คุณเข้าสู่ระบบด้วยรหัสกลาง กรุณาตั้งชื่อผู้ใช้และรหัสผ่านของตัวเองก่อน")

        new_u     = st.text_input("ชื่อผู้ใช้ใหม่ (ห้ามซ้ำกับ 'newuser')")
        new_p     = st.text_input("รหัสผ่านใหม่", type="password")
        confirm_p = st.text_input("ยืนยันรหัสผ่านใหม่", type="password")

        if st.button("บันทึกและเข้าใช้งาน", use_container_width=True):
            if not new_u or not new_p:
                st.error("กรุณากรอกข้อมูลให้ครบ")
            elif new_u == MASTER_USER:
                st.error("❌ ไม่สามารถใช้ชื่อ 'newuser' ได้ กรุณาเลือกชื่ออื่น")
            elif new_p != confirm_p:
                st.error("❌ รหัสผ่านไม่ตรงกัน")
            else:
                save_user(new_u, new_p)
                st.session_state.logged_in_user = new_u
                st.session_state.must_reset = False
                st.success(f"✅ บันทึกสำเร็จ! ยินดีต้อนรับ {new_u}")
                st.rerun()

    # ── หน้าหลักหลัง login ──
    else:
        st.sidebar.button("ออกจากระบบ",
                          on_click=lambda: st.session_state.update({
                              "logged_in_user": None,
                              "must_reset": False
                          }))

        tab_data, tab_pass = st.tabs(["📊 ข้อมูลสรุปทั้งหมด", "⚙️ เปลี่ยนรหัสผ่าน"])

        with tab_data:
            st.subheader("📂 ข้อมูลทั้งหมดในระบบ")
            if os.path.exists(EXCEL_PATH):
                try:
                    df = pd.read_excel(EXCEL_PATH, sheet_name=SUBMISSION_SHEET)
                    st.dataframe(df, use_container_width=True)
                except:
                    st.info("ยังไม่มีข้อมูลการบันทึก")

        with tab_pass:
            st.subheader("🛠 เปลี่ยนรหัสผ่านของตัวเอง")
            st.info(f"ผู้ใช้ปัจจุบัน: **{st.session_state.logged_in_user}**")
            new_p2     = st.text_input("รหัสผ่านใหม่", type="password", key="np2")
            confirm_p2 = st.text_input("ยืนยันรหัสผ่านใหม่", type="password", key="cp2")
            if st.button("บันทึกรหัสผ่านใหม่"):
                if new_p2 and new_p2 == confirm_p2:
                    save_user(st.session_state.logged_in_user, new_p2)
                    st.success("✅ เปลี่ยนรหัสผ่านเรียบร้อย!")
                else:
                    st.error("❌ รหัสผ่านไม่ตรงกันหรือกรอกไม่ครบ")
