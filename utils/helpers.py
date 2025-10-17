from datetime import datetime, date
import pandas as pd
import re

def format_currency(amount, currency="ج.م"):
    """تنسيق المبلغ المالي"""
    try:
        return f"{float(amount):,.2f} {currency}"
    except Exception:
        return f"{amount} {currency}"

def format_date(date_str):
    """تنسيق التاريخ إلى yyyy-mm-dd"""
    if not date_str:
        return ""
    try:
        if isinstance(date_str, str):
            return pd.to_datetime(date_str).strftime("%Y-%m-%d")
        elif isinstance(date_str, (datetime, date)):
            return date_str.strftime("%Y-%m-%d")
        else:
            return str(date_str)
    except Exception:
        return str(date_str)

def calculate_age(birth_date):
    """حساب العمر من تاريخ الميلاد"""
    if not birth_date:
        return ""
    try:
        if isinstance(birth_date, str):
            birth_date = pd.to_datetime(birth_date).date()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except Exception:
        return ""

def validate_phone(phone):
    """التحقق من صحة رقم الهاتف المصري"""
    phone = ''.join(filter(str.isdigit, str(phone)))
    return len(phone) == 11 and phone.startswith('01')

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))

def export_to_excel(dataframe, filename):
    """تصدير بيانات إلى Excel"""
    try:
        dataframe.to_excel(filename, index=False, engine='openpyxl')
        return True
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False

def get_file_icon(filetype):
    """إرجاع أيقونة مناسبة لنوع الملف"""
    if not filetype:
        return "📄"
    filetype = filetype.lower()
    if "pdf" in filetype:
        return "📕"
    if "image" in filetype or filetype in ["jpg", "jpeg", "png"]:
        return "🖼️"
    if "word" in filetype or filetype in ["doc", "docx"]:
        return "📘"
    if "excel" in filetype or filetype in ["xls", "xlsx"]:
        return "📗"
    if "dicom" in filetype or filetype == "dcm":
        return "🩻"
    return "📄"

def arabic_number(n):
    """تحويل رقم إلى أرقام عربية"""
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    return ''.join(arabic_digits[int(d)] if d.isdigit() else d for d in str(n))
validate_phone_number = validate_phone
import streamlit as st

def show_success_message(msg):
    st.success(msg)