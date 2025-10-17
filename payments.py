# payments.py

import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud

def render():
    """صفحة إدارة المدفوعات"""
    st.markdown("## 💰 إدارة المدفوعات")
    
    tab1, tab2, tab3 = st.tabs(["📋 جميع المدفوعات", "➕ تسجيل دفعة", "📊 تقارير مالية قصيرة"])
    
    with tab1:
        render_all_payments()
    
    with tab2:
        render_add_payment()
    
    with tab3:
        render_payment_summary()

def render_all_payments():
    """عرض المدفوعات"""
    payments = crud.get_all_payments()
    if not payments.empty:
        st.dataframe(
            payments[['id', 'patient_name', 'amount', 'doctor_share', 'clinic_share', 
                      'payment_method', 'payment_date', 'status']],
            use_container_width=True,
            hide_index=True
        )
        with st.expander("🔄 تحديث حالة دفعة"):
            payment_id = st.number_input("رقم الدفعة", min_value=1, step=1)
            new_status = st.selectbox("الحالة الجديدة", ["مكتمل", "ملغي", "معلق"])
            if st.button("تحديث الحالة"):
                try:
                    crud.update_payment_status(payment_id, new_status)
                    st.success("✅ تم التحديث")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {str(e)}")
    else:
        st.info("لا توجد مدفوعات حتى الآن.")

def render_add_payment():
    """إضافة دفعة"""
    st.markdown("### ➕ تسجيل دفعة يدويًا")
    
    patients = crud.get_all_patients()
    appointments = crud.get_all_appointments()
    
    if patients.empty:
        st.warning("⚠️ لا يوجد مرضى")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        patient_id = st.selectbox(
            "اختيار المريض",
            patients['id'].tolist(),
            format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0]
        )
        appointment_id = st.selectbox(
            "موعد (اختياري)",
            [None] + appointments['id'].dropna().tolist()
        )

    with col2:
        payment_method = st.selectbox("طريقة الدفع", ["نقدي", "بطاقة ائتمان", "تحويل بنكي", "شيك"])
        payment_date = st.date_input("تاريخ الدفع", value=date.today())
        amount = st.number_input("قيمة الدفعة", min_value=0.0, step=10.0)
    
    notes = st.text_area("ملاحظات")
    
    if st.button("💾 حفظ الدفعة", type="primary"):
        if amount > 0:
            crud.create_payment(
                appointment_id,
                patient_id,
                amount,
                payment_method,
                payment_date.isoformat(),
                notes
            )
            st.success("✅ تم حفظ الدفعة!")
            st.rerun()
        else:
            st.warning("⚠️ تأكد من قيمة الدفعة.")

def render_payment_summary():
    """عرض ملخص مالي سريع"""
    st.markdown("### 📊 ملخص إيرادات ومصروفات سريعة")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("حتى تاريخ", value=date.today())
    
    if start_date > end_date:
        st.warning("⚠️ التاريخ غير منطقي")
        return
    
    summary = crud.get_financial_summary(start_date.isoformat(), end_date.isoformat())
    col1, col2, col3 = st.columns(3)
    
    col1.metric("📥 الإيرادات", f"{summary['total_revenue']:,.0f} ج.م")
    col2.metric("📤 المصروفات", f"{summary['total_expenses']:,.0f} ج.م")
    col3.metric("💰 صافي الربح", f"{summary['net_profit']:,.0f} ج.م")