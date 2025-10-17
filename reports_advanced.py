# reports_advanced.py (Full Corrected Code)

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
        st.info("لا يوجد مرضى لعرض تقاريرهم.")
        return
    
    patient_id = st.selectbox(
        "اختر المريض",
        patients['id'].tolist(),
        format_func=lambda x: f"{patients[patients['id'] == x]['name'].iloc[0]} (ID: {x})",
        key="adv_report_patient_select"
    )
    
    if st.button("📊 عرض تقرير المريض", key="show_patient_report_adv"):
        with st.spinner("جاري تحميل التقرير..."):
            report = crud.get_patient_detailed_report(patient_id)
            
            if not report or not report.get('patient'):
                st.warning("لا توجد بيانات كافية لعرض تقرير هذا المريض.")
                return

            patient_info = report['patient']
            st.markdown(f"#### 👤 {patient_info.get('name', 'بيانات المريض')}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("الهاتف", patient_info.get('phone', '-'))
            col2.metric("الجنس", patient_info.get('gender', '-'))
            col3.metric("فصيلة الدم", patient_info.get('blood_type', '-'))
            col4.metric("تاريخ الميلاد", patient_info.get('date_of_birth', '-'))
            
            st.markdown("---")
            
            visits_stats = report.get('visits_stats', {})
            st.markdown("#### 📅 إحصائيات الزيارات")
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الزيارات", visits_stats.get('total_visits', 0))
            col2.metric("الزيارات المكتملة", visits_stats.get('completed_visits', 0))
            col3.metric("الزيارات الملغية", visits_stats.get('cancelled_visits', 0))
            
            st.markdown("#### 💰 الملخص المالي")
            col1, col2, col3 = st.columns(3)
            col1.metric("التكلفة الإجمالية", f"{report.get('total_cost', 0):,.2f} ج.م")
            col2.metric("إجمالي المدفوعات", f"{report.get('total_paid', 0):,.2f} ج.م")
            col3.metric("المبلغ المتبقي", f"{report.get('outstanding', 0):,.2f} ج.م")
            
            if not report['appointments'].empty:
                with st.expander("📅 عرض سجل المواعيد التفصيلي"):
                    st.dataframe(report['appointments'], use_container_width=True, hide_index=True)
            
            if not report['payments'].empty:
                with st.expander("💳 عرض سجل المدفوعات"):
                    st.dataframe(report['payments'], use_container_width=True, hide_index=True)

def render_doctor_report():
    """تقرير طبيب مفصل"""
    st.markdown("### 👨‍⚕️ تقرير طبيب مفصل")
    
    doctors = crud.get_all_doctors()
    if doctors.empty:
        st.info("لا يوجد أطباء.")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        doctor_id = st.selectbox(
            "اختر الطبيب",
            doctors['id'].tolist(),
            format_func=lambda x: f"{doctors[doctors['id'] == x]['name'].iloc[0]} (ID: {x})",
            key="adv_report_doctor_select"
        )
    with col2:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=30), key="dr_start_adv")
    with col3:
        end_date = st.date_input("حتى تاريخ", value=date.today(), key="dr_end_adv")
    
    if st.button("📊 عرض تقرير الطبيب", key="show_doctor_report_adv"):
        with st.spinner("جاري تحميل التقرير..."):
            report = crud.get_doctor_detailed_report(doctor_id, start_date.isoformat(), end_date.isoformat())

            if not report or not report.get('doctor'):
                st.warning("لا توجد بيانات كافية لعرض تقرير هذا الطبيب.")
                return
            
            doctor_info = report['doctor']
            st.markdown(f"#### 👨‍⚕️ د. {doctor_info.get('name', 'بيانات الطبيب')}")
            
            stats = report['appointments_stats']
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي المواعيد", stats.get('total_appointments', 0))
            col2.metric("الإيرادات", f"{stats.get('total_revenue', 0):,.2f} ج.م")
            col3.metric("العمولة", f"{report.get('total_commission', 0):,.2f} ج.م")
            
            if not report['monthly_performance'].empty:
                st.markdown("##### الأداء الشهري")
                fig = px.bar(report['monthly_performance'], x='month', y='revenue', title="الإيرادات الشهرية")
                st.plotly_chart(fig, use_container_width=True)

def render_treatment_report():
    """تقرير علاج مفصل"""
    st.markdown("### 💉 تقرير علاج مفصل")
    
    treatments = crud.get_all_treatments()
    if treatments.empty:
        st.info("لا توجد علاجات.")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        treatment_id = st.selectbox(
            "اختر العلاج",
            treatments['id'].tolist(),
            format_func=lambda x: treatments[treatments['id'] == x]['name'].iloc[0],
            key="adv_report_treatment_select"
        )
    with col2:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=90), key="treat_start_adv")
    with col3:
        end_date = st.date_input("حتى تاريخ", value=date.today(), key="treat_end_adv")
    
    if st.button("📊 عرض تقرير العلاج", key="show_treatment_report_adv"):
        with st.spinner("جاري تحميل التقرير..."):
            report = crud.get_treatment_detailed_report(treatment_id, start_date.isoformat(), end_date.isoformat())
            
            if not report or not report.get('treatment'):
                st.warning("لا توجد بيانات كافية لهذا العلاج.")
                return
            
            treatment_info = report['treatment']
            st.markdown(f"#### 💉 {treatment_info.get('name', 'بيانات العلاج')}")
            
            stats = report['usage_stats']
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الحجوزات", stats.get('total_bookings', 0))
            col2.metric("إجمالي الإيرادات", f"{stats.get('total_revenue', 0):,.2f} ج.م")
            col3.metric("متوسط السعر", f"{stats.get('average_price', 0):,.2f} ج.م")

def render_supplier_report():
    """تقرير مورد مفصل"""
    st.markdown("### 🏪 تقرير مورد مفصل")
    
    suppliers = crud.get_all_suppliers()
    if suppliers.empty:
        st.info("لا يوجد موردين.")
        return
    
    supplier_id = st.selectbox(
        "اختر المورد",
        suppliers['id'].tolist(),
        format_func=lambda x: suppliers[suppliers['id'] == x]['name'].iloc[0],
        key="adv_report_supplier_select"
    )
    
    if st.button("📊 عرض تقرير المورد", key="show_supplier_report_adv"):
        with st.spinner("جاري تحميل التقرير..."):
            report = crud.get_supplier_detailed_report(supplier_id)
            
            if not report or not report.get('supplier'):
                st.warning("لا توجد بيانات كافية لهذا المورد.")
                return
                
            supplier_info = report['supplier']
            st.markdown(f"#### 🏪 {supplier_info.get('name', 'بيانات المورد')}")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("عدد الأصناف الموردة", report.get('total_items', 0))
            col2.metric("القيمة الإجمالية للمخزون", f"{report.get('total_value', 0):,.2f} ج.م")
            col3.metric("أصناف منخفضة", report.get('low_stock_items', 0))
            
            if not report['items'].empty:
                st.markdown("##### الأصناف الموردة")
                st.dataframe(report['items'], use_container_width=True)

def render_comprehensive_financial_report():
    """تقرير مالي شامل"""
    st.markdown("### 💰 التقرير المالي الشامل")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today().replace(day=1), key="fin_start_adv")
    with col2:
        end_date = st.date_input("حتى تاريخ", value=date.today(), key="fin_end_adv")
    
    if st.button("📊 إنشاء التقرير المالي", key="create_financial_report_adv"):
        with st.spinner("جاري تحميل التقرير..."):
            report = crud.get_comprehensive_financial_report(start_date.isoformat(), end_date.isoformat())
            
            if not report:
                st.warning("لا توجد بيانات مالية في هذه الفترة.")
                return
            
            earnings = report['clinic_earnings']
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الإيرادات", f"{earnings.get('total_revenue', 0):,.2f} ج.م")
            col2.metric("حصة العيادة", f"{earnings.get('total_clinic_earnings', 0):,.2f} ج.م")
            col3.metric("حصة الأطباء", f"{earnings.get('total_doctor_earnings', 0):,.2f} ج.م")
            
            if not report['cash_flow'].empty:
                st.markdown("##### التدفق النقدي")
                fig = px.line(report['cash_flow'], x='date', y='cumulative', title="التدفق النقدي التراكمي")
                st.plotly_chart(fig, use_container_width=True)