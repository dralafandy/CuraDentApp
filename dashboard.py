import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud
from components.quick_actions import QuickActions

def render():
    """صفحة لوحة التحكم المحسنة"""
    st.markdown("""<div class='main-header'><h1>🏥 لوحة معلومات العيادة</h1><p>مرحباً بك في نظام إدارة العيادة المتكامل</p></div>""", unsafe_allow_html=True)
    
    # قسم المهام السريعة
    QuickActions.render()
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # مقارنة الأداء الشهري
    st.markdown("### 📈 مقارنة الأداء الشهري")
    monthly_comparison = crud.get_monthly_comparison()
    
    def render_metric(label, current, previous):
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        st.metric(label, f"{current:,.0f} ج.م", f"{change:.1f}%")

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric("الإيرادات", monthly_comparison['current_revenue'], monthly_comparison['last_revenue'])
    with col2:
        render_metric("المصروفات", monthly_comparison['current_expenses'], monthly_comparison['last_expenses'])
    with col3:
        st.metric("📅 المواعيد", f"{monthly_comparison['current_appointments']}", f"{monthly_comparison['appointments_change']:.1f}%")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # الإحصائيات الرئيسية
    stats = crud.get_dashboard_stats()
    financial_summary = crud.get_financial_summary()
    
    st.markdown("### 📊 الملخص العام")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 عدد المرضى", stats['total_patients'])
    with col2:
        st.metric("👨‍⚕️ عدد الأطباء", stats['total_doctors'])
    with col3:
        st.metric("📅 مواعيد اليوم", stats['today_appointments'])
    with col4:
        st.metric("💰 صافي الربح", f"{financial_summary['net_profit']:,.0f} ج.م")

    # مواعيد اليوم والتنبيهات
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 مواعيد اليوم")
        today_appointments = crud.get_appointments_by_date(date.today().isoformat())
        if not today_appointments.empty:
            st.dataframe(
                today_appointments[[
                    'patient_name', 'doctor_name', 'appointment_time', 'status'
                ]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("لا توجد مواعيد اليوم")
    
    with col2:
        st.markdown("### ⚠️ التنبيهات المهمة")
        low_stock = crud.get_low_stock_items()
        if not low_stock.empty:
            st.warning(f"يوجد {len(low_stock)} عنصر بمخزون منخفض")
        else:
            st.success("✅ المخزون في المستوى الآمن")
        
        expiring = crud.get_expiring_inventory(days=30)
        if not expiring.empty:
            st.error(f"يوجد {len(expiring)} صنف ينتهي خلال 30 يوم")
        else:
            st.success("✅ لا توجد أصناف قريبة من الانتهاء")