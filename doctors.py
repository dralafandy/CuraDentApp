# doctors.py

import streamlit as st
import pandas as pd
from database.crud import crud
from datetime import date

def render():
    """صفحة إدارة الأطباء"""
    st.markdown("## 👨‍⚕️ إدارة الأطباء")
    
    tab1, tab2 = st.tabs(["📋 قائمة الأطباء", "➕ إضافة طبيب جديد"])

    with tab1:
        render_doctor_list()

    with tab2:
        render_add_doctor()

def render_doctor_list():
    """عرض جميع الأطباء"""
    doctors = crud.get_all_doctors()
    if not doctors.empty:
        st.dataframe(
            doctors[['id', 'name', 'specialization', 'phone', 'email', 'salary', 'commission_rate']],
            use_container_width=True,
            hide_index=True
        )
        with st.expander("🛠 تحديث بيانات طبيب"):
            selected_id = st.number_input("رقم الطبيب", min_value=1, step=1)
            doctor = crud.get_doctor_by_id(selected_id)
            if doctor:
                name = st.text_input("الاسم", doctor[1])
                spec = st.text_input("التخصص", doctor[2])
                phone = st.text_input("الهاتف", doctor[3])
                email = st.text_input("البريد الإلكتروني", doctor[4])
                address = st.text_input("العنوان", doctor[5])
                salary = st.number_input("الراتب", float(doctor[7]))
                commission = st.number_input("نسبة العمولة", float(doctor[8]))

                if st.button("💾 تحديث"):
                    try:
                        crud.update_doctor(selected_id, name, spec, phone, email, address, salary, commission)
                        st.success("✅ تم تحديث بيانات الطبيب")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")
                
                if st.button("🗑 حذف الطبيب"):
                    crud.delete_doctor(selected_id)
                    st.success("🚫 تم إلغاء تفعيل الطبيب")
                    st.rerun()
            else:
                st.warning("لم يتم العثور على الطبيب")

    else:
        st.info("لا يوجد أطباء في النظام حالياً.")

def render_add_doctor():
    """إضافة طبيب جديد"""
    st.markdown("### ➕ إضافة طبيب جديد")
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("اسم الطبيب *")
        specialization = st.text_input("التخصص *")
        phone = st.text_input("رقم الهاتف")
        salary = st.number_input("الراتب الأساسي", min_value=0.0, step=100.0)
    
    with col2:
        email = st.text_input("البريد الإلكتروني")
        address = st.text_input("العنوان")
        hire_date = st.date_input("تاريخ التعيين", value=date.today())
        commission_rate = st.number_input("نسبة العمولة %", min_value=0.0, max_value=100.0, step=1.0)

    if st.button("💾 حفظ الطبيب", type="primary", use_container_width=True):
        if name and specialization:
            crud.create_doctor(
                name, specialization, phone, email, address,
                hire_date.isoformat(), salary, commission_rate
            )
            st.success("✅ تم إضافة الطبيب بنجاح")
            st.balloons()
            st.rerun()
        else:
            st.warning("⚠️ يرجى إدخال الاسم والتخصص كحد أدنى.")