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
            treatment_id = st.number_input("رقم العلاج", min_value=1, step=1, key="edit_treatment_id")
            treatment = crud.get_treatment_by_id(treatment_id)

            if treatment:
                # ✅ الطريقة الصحيحة - استخدام value= بشكل صريح
                name = st.text_input("اسم العلاج", value=str(treatment[1]))
                description = st.text_area("الوصف", value=str(treatment[2]) if treatment[2] else "")
                
                # ✅ تصحيح: استخدام value= قبل float
                base_price = st.number_input(
                    "السعر الأساسي", 
                    value=float(treatment[3]), 
                    min_value=0.0,
                    step=50.0
                )
                
                duration = st.number_input(
                    "المدة بالدقائق", 
                    value=int(treatment[4]) if treatment[4] else 30, 
                    min_value=0,
                    step=5
                )
                
                category = st.text_input("الفئة", value=str(treatment[5]) if treatment[5] else "عام")
                
                doctor_pct = st.slider(
                    "نسبة الطبيب %", 
                    min_value=0, 
                    max_value=100, 
                    value=int(treatment[6]) if treatment[6] else 50
                )
                
                clinic_pct = 100 - doctor_pct
                st.info(f"✅ نسبة العيادة: {clinic_pct}%")

                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 تحديث العلاج", type="primary"):
                        try:
                            crud.update_treatment(
                                treatment_id, name, description, base_price,
                                duration, category, doctor_pct, clinic_pct
                            )
                            st.success("✅ تم التحديث بنجاح")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ خطأ: {str(e)}")

                with col2:
                    if st.button("🗑 حذف العلاج", type="secondary"):
                        try:
                            crud.delete_treatment(treatment_id)
                            st.success("✅ تم إلغاء تفعيل العلاج")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ خطأ: {str(e)}")
            else:
                st.warning("⚠️ لم يتم العثور على العلاج")

    else:
        st.info("لا توجد بيانات علاجات بعد.")

def render_add_treatment():
    """إضافة علاج جديد"""
    st.markdown("### ➕ إضافة علاج")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("اسم العلاج *")
        description = st.text_area("الوصف")
        
        # ✅ استخدام value= بشكل صريح
        base_price = st.number_input(
            "السعر *", 
            value=0.0,
            min_value=0.0, 
            step=50.0
        )
        
        duration = st.number_input(
            "المدة (دقائق)", 
            value=30,
            min_value=0,
            step=5
        )
        
        category = st.selectbox(
            "الفئة",
            ["عام", "وقائي", "علاجي", "تجميلي", "جراحي", "تشخيصي"]
        )

    with col2:
        doctor_pct = st.slider("نسبة الطبيب %", 0, 100, 50)
        clinic_pct = 100 - doctor_pct
        st.info(f"✅ نسبة العيادة: {clinic_pct}%")
        
        st.markdown("---")
        st.markdown("**💡 معاينة التقسيم:**")
        if base_price > 0:
            st.write(f"💰 السعر الكلي: **{base_price:.2f} ج.م**")
            st.write(f"👨‍⚕️ حصة الطبيب: **{(base_price * doctor_pct / 100):.2f} ج.م**")
            st.write(f"🏥 حصة العيادة: **{(base_price * clinic_pct / 100):.2f} ج.م**")
        else:
            st.caption("أدخل السعر لعرض التقسيم")
    
    if st.button("💾 حفظ العلاج", type="primary", use_container_width=True):
        if name and base_price > 0:
            try:
                crud.create_treatment(
                    name, description, base_price, duration, category,
                    doctor_pct, clinic_pct
                )
                st.success("✅ تم إضافة العلاج بنجاح!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
        else:
            st.warning("⚠️ يرجى إدخال اسم العلاج والسعر.")