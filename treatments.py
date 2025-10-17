# treatments.py

import streamlit as st
import pandas as pd
from database.crud import crud

def render():
    """صفحة إدارة العلاجات"""
    st.markdown("## 💉 إدارة العلاجات")

    tab1, tab2 = st.tabs(["📋 قائمة العلاجات", "➕ علاج جديد"])

    with tab1:
        render_treatment_list()

    with tab2:
        render_add_treatment()

def render_treatment_list():
    """عرض جميع العلاجات"""
    treatments = crud.get_all_treatments()
    
    if not treatments.empty:
        st.dataframe(
            treatments[['id', 'name', 'category', 'base_price', 'duration_minutes', 'doctor_percentage', 'clinic_percentage']],
            use_container_width=True,
            hide_index=True
        )

        with st.expander("🛠 تعديل علاج"):
            treatment_id = st.number_input("رقم العلاج", min_value=1, step=1)
            treatment = crud.get_treatment_by_id(treatment_id)

            if treatment:
                name = st.text_input("اسم العلاج", treatment[1])
                description = st.text_area("الوصف", treatment[2])
                base_price = st.number_input("السعر الأساسي", float(treatment[3]), step=50.0, min_value=0.0)
                duration = st.number_input("المدة بالدقائق", treatment[4], min_value=0)
                category = st.text_input("الفئة", treatment[5])
                doctor_pct = st.slider("نسبة الطبيب", 0, 100, int(treatment[6]))
                clinic_pct = 100 - doctor_pct

                if st.button("تحديث العلاج"):
                    crud.update_treatment(
                        treatment_id, name, description, base_price,
                        duration, category, doctor_pct, clinic_pct
                    )
                    st.success("✅ تم التحديث بنجاح")
                    st.rerun()

                if st.button("🗑 حذف العلاج"):
                    crud.delete_treatment(treatment_id)
                    st.success("✅ تم إلغاء تفعيل العلاج")
                    st.rerun()
            else:
                st.warning("لم يتم العثور على العلاج")

    else:
        st.info("لا توجد بيانات علاجات بعد.")

def render_add_treatment():
    """إضافة علاج جديد"""
    st.markdown("### ➕ إضافة علاج")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("اسم العلاج *")
        description = st.text_area("الوصف")
        base_price = st.number_input("السعر", min_value=0.0, step=50.0)
        duration = st.number_input("المدة (دقائق)", min_value=0)
        category = st.text_input("الفئة", value="عام")

    with col2:
        doctor_pct = st.slider("نسبة الطبيب %", 0, 100, 50)
        clinic_pct = 100 - doctor_pct
        st.info(f"نسبة العيادة: {clinic_pct}%")
    
    if st.button("💾 حفظ العلاج", type="primary", use_container_width=True):
        if name and base_price > 0:
            try:
                crud.create_treatment(
                    name, description, base_price, duration, category,
                    doctor_pct, clinic_pct
                )
                st.success("✅ تم إضافة العلاج")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
        else:
            st.warning("يرجى إدخال اسم العلاج والسعر.")