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

# --- 4. บันทึกลง Excel (ปรับปรุงรองรับการแก้ไข) ---
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
        if
