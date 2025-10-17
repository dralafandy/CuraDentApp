# reports_advanced.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from database.crud import crud
import plotly.express as px

def render():
    """صفحة التقارير المتقدمة"""
    st.markdown("## 📈 التقارير المتقدمة والتفصيلية")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 تقرير مريض", 
        "👨‍⚕️ تقرير طبيب", 
        "💉 تقرير علاج",
        "🏪 تقرير مورد",
        "💰 تقرير مالي شامل"
    ])
    
    with tab1:
        render_patient_report()
    
    with tab2:
        render_doctor_report()
    
    with tab3:
        render_treatment_report()
    
    with tab4:
        render_supplier_report()
    
    with tab5:
        render_comprehensive_financial_report()

def render_patient_report():
    """تقرير مريض مفصل"""
    st.markdown("### 👤 تقرير مريض مفصل")
    
    patients = crud.get_all_patients()
    
    if patients.empty:
        st.info("لا يوجد مرضى")
        return
    
    patient_id = st.selectbox(
        "اختر المريض",
        patients['id'].tolist(),
        format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0]
    )
    
    if st.button("📊 عرض التقرير"):
        report = crud.get_patient_detailed_report(patient_id)
        
        if report and report['patient']:
            patient = report['patient']
            
            # معلومات المريض
            st.markdown(f"### 👤 {patient['name']}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("الهاتف", patient['phone'])
            col2.metric("الجنس", patient['gender'])
            col3.metric("فصيلة الدم", patient.get('blood_type', 'غير محدد'))
            col4.metric("تاريخ الميلاد", patient['date_of_birth'])
            
            st.markdown("---")
            
            # إحصائيات الزيارات
            st.markdown("#### 📊 إحصائيات الزيارات")
            visits = report['visits_stats']
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("إجمالي الزيارات", visits['total_visits'])
            col2.metric("الزيارات المكتملة", visits['completed_visits'])
            col3.metric("الزيارات الملغية", visits['cancelled_visits'])
            col4.metric("أول زيارة", visits.get('first_visit', 'لا يوجد'))
            
            # الإحصائيات المالية
            st.markdown("#### 💰 الإحصائيات المالية")
            col1, col2, col3 = st.columns(3)
            col1.metric("التكلفة الإجمالية", f"{report['total_cost']:,.0f} ج.م")
            col2.metric("المدفوع", f"{report['total_paid']:,.0f} ج.م")
            col3.metric("المتبقي", f"{report['outstanding']:,.0f} ج.م")
            
            # المواعيد
            if not report['appointments'].empty:
                st.markdown("#### 📅 سجل المواعيد")
                st.dataframe(
                    report['appointments'][['appointment_date', 'doctor_name', 'treatment_name', 
                                          'status', 'total_cost']],
                    use_container_width=True,
                    hide_index=True
                )
            
            # العلاجات المستخدمة
            if not report['treatments'].empty:
                st.markdown("#### 💉 العلاجات المستخدمة")
                st.dataframe(
                    report['treatments'][['treatment_name', 'category', 'usage_count', 'total_cost']],
                    use_container_width=True,
                    hide_index=True
                )

def render_doctor_report():
    """تقرير طبيب مفصل"""
    st.markdown("### 👨‍⚕️ تقرير طبيب مفصل")
    
    doctors = crud.get_all_doctors()
    
    if doctors.empty:
        st.info("لا يوجد أطباء")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        doctor_id = st.selectbox(
            "اختر الطبيب",
            doctors['id'].tolist(),
            format_func=lambda x: doctors[doctors['id'] == x]['name'].iloc[0]
        )
    with col2:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=30), key="dr_start")
    with col3:
        end_date = st.date_input("حتى تاريخ", value=date.today(), key="dr_end")
    
    if st.button("📊 عرض التقرير"):
        report = crud.get_doctor_detailed_report(doctor_id, start_date.isoformat(), end_date.isoformat())
        
        if report and report['doctor']:
            doctor = report['doctor']
            
            st.markdown(f"### 👨‍⚕️ د. {doctor['name']}")
            st.markdown(f"**التخصص:** {doctor['specialization']}")
            
            st.markdown("---")
            
            # إحصائيات المواعيد
            stats = report['appointments_stats']
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("إجمالي المواعيد", stats['total_appointments'])
            col2.metric("المكتملة", stats['completed'])
            col3.metric("الملغية", stats['cancelled'])
            col4.metric("المجدولة", stats['scheduled'])
            
            # الإحصائيات المالية
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("إجمالي الإيرادات", f"{stats['total_revenue']:,.0f} ج.م")
            col2.metric("متوسط الإيراد", f"{stats['average_revenue']:,.0f} ج.م")
            col3.metric("معدل الإنجاز", f"{report['completion_rate']:.1f}%")
            col4.metric("معدل الإلغاء", f"{report['cancellation_rate']:.1f}%")
            
            # الأداء الشهري
            if not report['monthly_performance'].empty:
                st.markdown("#### 📊 الأداء الشهري")
                fig = px.line(report['monthly_performance'], x='month', y='revenue', 
                            title='الإيرادات الشهرية', markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            # العلاجات الأكثر تنفيذاً
            if not report['treatments'].empty:
                st.markdown("#### 💉 العلاجات الأكثر تنفيذاً")
                st.dataframe(
                    report['treatments'][['treatment_name', 'count', 'total_revenue']],
                    use_container_width=True,
                    hide_index=True
                )

def render_treatment_report():
    """تقرير علاج مفصل"""
    st.markdown("### 💉 تقرير علاج مفصل")
    
    treatments = crud.get_all_treatments()
    
    if treatments.empty:
        st.info("لا توجد علاجات")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        treatment_id = st.selectbox(
            "اختر العلاج",
            treatments['id'].tolist(),
            format_func=lambda x: treatments[treatments['id'] == x]['name'].iloc[0]
        )
    with col2:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=90), key="treat_start_adv")
    with col3:
        end_date = st.date_input("حتى تاريخ", value=date.today(), key="treat_end_adv")
    
    if st.button("📊 عرض التقرير"):
        report = crud.get_treatment_detailed_report(treatment_id, start_date.isoformat(), end_date.isoformat())
        
        if report and report['treatment']:
            treatment = report['treatment']
            
            st.markdown(f"### 💉 {treatment['name']}")
            st.markdown(f"**الفئة:** {treatment['category']}")
            st.markdown(f"**السعر الأساسي:** {treatment['base_price']:,.0f} ج.م")
            
            st.markdown("---")
            
            # إحصائيات الاستخدام
            stats = report['usage_stats']
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الحجوزات", stats['total_bookings'])
            col2.metric("المكتملة", stats['completed'])
            col3.metric("إجمالي الإيرادات", f"{stats['total_revenue']:,.0f} ج.م")
            
            # الأطباء المنفذين
            if not report['doctors'].empty:
                st.markdown("#### 👨‍⚕️ الأطباء المنفذين")
                st.dataframe(
                    report['doctors'][['doctor_name', 'specialization', 'booking_count', 'revenue']],
                    use_container_width=True,
                    hide_index=True
                )
            
            # الاتجاه الشهري
            if not report['monthly_trend'].empty:
                st.markdown("#### 📈 الاتجاه الشهري")
                fig = px.bar(report['monthly_trend'], x='month', y='booking_count', 
                           title='عدد الحجوزات الشهرية')
                st.plotly_chart(fig, use_container_width=True)

def render_supplier_report():
    """تقرير مورد مفصل"""
    st.markdown("### 🏪 تقرير مورد مفصل")
    
    suppliers = crud.get_all_suppliers()
    
    if suppliers.empty:
        st.info("لا يوجد موردين")
        return
    
    supplier_id = st.selectbox(
        "اختر المورد",
        suppliers['id'].tolist(),
        format_func=lambda x: suppliers[suppliers['id'] == x]['name'].iloc[0]
    )
    
    if st.button("📊 عرض التقرير"):
        report = crud.get_supplier_detailed_report(supplier_id)
        
        if report and report['supplier']:
            supplier = report['supplier']
            
            st.markdown(f"### 🏪 {supplier['name']}")
            col1, col2 = st.columns(2)
            col1.metric("الشخص المسؤول", supplier['contact_person'])
            col2.metric("الهاتف", supplier['phone'])
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("عدد الأصناف", report['total_items'])
            col2.metric("القيمة الإجمالية", f"{report['total_value']:,.0f} ج.م")
            col3.metric("أصناف منخفضة", report['low_stock_items'])
            
            if not report['items'].empty:
                st.markdown("#### 📦 الأصناف الموردة")
                st.dataframe(
                    report['items'][['item_name', 'category', 'quantity', 'unit_price', 'total_value']],
                    use_container_width=True,
                    hide_index=True
                )

def render_comprehensive_financial_report():
    """تقرير مالي شامل"""
    st.markdown("### 💰 التقرير المالي الشامل")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today().replace(day=1), key="fin_start")
    with col2:
        end_date = st.date_input("حتى تاريخ", value=date.today(), key="fin_end")
    
    if st.button("📊 إنشاء التقرير"):
        report = crud.get_comprehensive_financial_report(start_date.isoformat(), end_date.isoformat())
        
        if report:
            # أرباح العيادة
            clinic_earnings = report['clinic_earnings']
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الإيرادات", f"{clinic_earnings['total_revenue']:,.0f} ج.م")
            col2.metric("حصة العيادة", f"{clinic_earnings['total_clinic_earnings']:,.0f} ج.م")
            col3.metric("حصة الأطباء", f"{clinic_earnings['total_doctor_earnings']:,.0f} ج.م")
            
            st.markdown("---")
            
            # طرق الدفع
            if not report['payment_methods'].empty:
                st.markdown("#### 💳 الإيرادات حسب طريقة الدفع")
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(report['payment_methods'], use_container_width=True, hide_index=True)
                with col2:
                    fig = px.pie(report['payment_methods'], values='total', names='payment_method')
                    st.plotly_chart(fig, use_container_width=True)
            
            # فئات المصروفات
            if not report['expense_categories'].empty:
                st.markdown("#### 💸 المصروفات حسب الفئة")
                fig = px.bar(report['expense_categories'], x='category', y='total', 
                           title='توزيع المصروفات')
                st.plotly_chart(fig, use_container_width=True)
            
            # أرباح الأطباء
            if not report['doctor_earnings'].empty:
                st.markdown("#### 👨‍⚕️ أرباح الأطباء")
                st.dataframe(
                    report['doctor_earnings'][['doctor_name', 'total_earnings', 'payment_count']],
                    use_container_width=True,
                    hide_index=True
                )