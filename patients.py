import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud
from report_generator import PatientReportGenerator

def render():
    """صفحة إدارة المرضى مع ميزة التقرير الشامل"""
    st.markdown("### 👥 إدارة المرضى")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 جميع المرضى", 
        "➕ مريض جديد", 
        "📝 سجل مريض",
        "📄 تقرير شامل"
    ])
    
    with tab1:
        render_all_patients()
    
    with tab2:
        render_add_patient()
    
    with tab3:
        render_patient_history()
    
    with tab4:
        render_patient_report()

def render_all_patients():
    """عرض جميع المرضى"""
    patients = crud.get_all_patients()
    if not patients.empty:
        # بحث
        search = st.text_input("🔍 بحث عن مريض", placeholder="اسم، هاتف، بريد إلكتروني...")
        
        if search:
            patients = crud.search_patients(search)
        
        st.dataframe(
            patients[['id', 'name', 'phone', 'email', 'gender', 'date_of_birth', 'blood_type']],
            use_container_width=True,
            hide_index=True
        )
        st.info(f"إجمالي المرضى: {len(patients)}")
    else:
        st.info("لا يوجد مرضى")

def render_add_patient():
    """نموذج إضافة مريض جديد"""
    st.markdown("#### إضافة مريض جديد")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("الاسم الكامل*")
        phone = st.text_input("رقم الهاتف*")
        email = st.text_input("البريد الإلكتروني")
        date_of_birth = st.date_input("تاريخ الميلاد", max_value=date.today())
        gender = st.selectbox("النوع*", ["ذكر", "أنثى"])
    
    with col2:
        address = st.text_area("العنوان")
        emergency_contact = st.text_input("جهة الاتصال للطوارئ")
        blood_type = st.selectbox("فصيلة الدم", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        allergies = st.text_input("الحساسية")
    
    medical_history = st.text_area("التاريخ الطبي")
    notes = st.text_area("ملاحظات إضافية")
    
    if st.button("إضافة المريض", type="primary", use_container_width=True):
        if name and phone:
            try:
                crud.create_patient(
                    name, phone, email, address,
                    date_of_birth.isoformat(), gender,
                    medical_history, emergency_contact,
                    blood_type, allergies, notes
                )
                st.success("✅ تم إضافة المريض بنجاح!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
        else:
            st.warning("الرجاء ملء الحقول المطلوبة")

def render_patient_history():
    """عرض سجل المريض الطبي"""
    st.markdown("#### سجل المريض الطبي")
    
    patients = crud.get_all_patients()
    if not patients.empty:
        patient_id = st.selectbox(
            "اختر المريض",
            patients['id'].tolist(),
            format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0]
        )
        
        if st.button("عرض السجل"):
            history = crud.get_patient_history(patient_id)
            if not history.empty:
                st.dataframe(history, use_container_width=True, hide_index=True)
                
                # إحصائيات
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("عدد الزيارات", len(history))
                with col2:
                    total_spent = history['total_cost'].sum()
                    st.metric("إجمالي الإنفاق", f"{total_spent:,.0f} ج.م")
                with col3:
                    last_visit = history['appointment_date'].iloc[0] if not history.empty else "لا يوجد"
                    st.metric("آخر زيارة", last_visit)
            else:
                st.info("لا توجد زيارات سابقة لهذا المريض")

def render_patient_report():
    """توليد تقرير شامل عن المريض"""
    st.markdown("#### 📄 تقرير شامل عن المريض")
    
    patients = crud.get_all_patients()
    
    if patients.empty:
        st.warning("لا يوجد مرضى في النظام")
        return
    
    # اختيار المريض
    col1, col2 = st.columns([3, 1])
    
    with col1:
        patient_id = st.selectbox(
            "اختر المريض",
            patients['id'].tolist(),
            format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0],
            key="report_patient_select"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_report = st.button("📊 توليد التقرير", type="primary", use_container_width=True)
    
    if generate_report:
        with st.spinner("جاري إنشاء التقرير..."):
            # جلب جميع بيانات المريض
            report_data = crud.get_patient_full_report(patient_id)
            
            if not report_data['patient']:
                st.error("لم يتم العثور على المريض")
                return
            
            # توليد التقرير HTML
            report_html = PatientReportGenerator.generate_html_report(
                report_data['patient'],
                report_data['appointments'],
                report_data['payments'],
                report_data['treatments']
            )
            
            # عرض التقرير
            st.markdown(report_html, unsafe_allow_html=True)
            
            # خيارات التصدير
            st.markdown("---")
            st.markdown("### 📥 تصدير التقرير")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🖨️ طباعة التقرير", use_container_width=True):
                    st.info("💡 استخدم Ctrl+P أو Cmd+P لطباعة التقرير")
            
            with col2:
                # تصدير Excel
                if st.button("📊 تصدير Excel", use_container_width=True):
                    try:
                        # دمج جميع البيانات في ملف Excel
                        patient_name = report_data['patient']['name']
                        filename = f"تقرير_{patient_name}_{date.today()}.xlsx"
                        
                        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                            # معلومات المريض
                            patient_df = pd.DataFrame([report_data['patient']])
                            patient_df.to_excel(writer, sheet_name='معلومات المريض', index=False)
                            
                            # المواعيد
                            if not report_data['appointments'].empty:
                                report_data['appointments'].to_excel(writer, sheet_name='المواعيد', index=False)
                            
                            # المدفوعات
                            if not report_data['payments'].empty:
                                report_data['payments'].to_excel(writer, sheet_name='المدفوعات', index=False)
                            
                            # العلاجات
                            if not report_data['treatments'].empty:
                                report_data['treatments'].to_excel(writer, sheet_name='العلاجات', index=False)
                        
                        st.success(f"✅ تم حفظ التقرير: {filename}")
                        
                        # تحميل الملف
                        with open(filename, 'rb') as f:
                            st.download_button(
                                label="⬇️ تحميل الملف",
                                data=f,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    except Exception as e:
                        st.error(f"حدث خطأ: {str(e)}")
            
            with col3:
                if st.button("📧 إرسال بالبريد", use_container_width=True):
                    st.info("🚧 ميزة الإرسال بالبريد قيد التطوير")
            
            # إحصائيات سريعة
            st.markdown("---")
            st.markdown("### 📊 ملخص سريع")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_visits = len(report_data['appointments'])
                st.metric("إجمالي الزيارات", f"{total_visits} زيارة")
            
            with col2:
                if not report_data['appointments'].empty:
                    completed = len(report_data['appointments'][report_data['appointments']['status'] == 'مكتمل'])
                    st.metric("الزيارات المكتملة", f"{completed} زيارة")
            
            with col3:
                if not report_data['payments'].empty:
                    total_paid = report_data['payments']['amount'].sum()
                    st.metric("إجمالي المدفوعات", f"{total_paid:,.0f} ج.م")
            
            with col4:
                if not report_data['appointments'].empty:
                    last_visit = report_data['appointments']['appointment_date'].max()
                    st.metric("آخر زيارة", last_visit)
