# reports.py

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from database.crud import crud
import plotly.express as px
import plotly.graph_objects as go

def render():
    """صفحة التقارير العامة"""
    st.markdown("## 📊 التقارير العامة")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "💰 التقارير المالية", 
        "👨‍⚕️ أداء الأطباء", 
        "💉 العلاجات", 
        "📈 الاتجاهات"
    ])
    
    with tab1:
        render_financial_reports()
    
    with tab2:
        render_doctor_performance()
    
    with tab3:
        render_treatment_reports()
    
    with tab4:
        render_trends()

def render_financial_reports():
    """التقارير المالية"""
    st.markdown("### 💰 التقارير المالية")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("حتى تاريخ", value=date.today())
    
    if start_date > end_date:
        st.warning("⚠️ التاريخ غير صحيح")
        return
    
    financial_summary = crud.get_financial_summary(start_date.isoformat(), end_date.isoformat())
    
    # الملخص
    col1, col2, col3 = st.columns(3)
    col1.metric("📥 إجمالي الإيرادات", f"{financial_summary['total_revenue']:,.0f} ج.م")
    col2.metric("📤 إجمالي المصروفات", f"{financial_summary['total_expenses']:,.0f} ج.م")
    col3.metric("💰 صافي الربح", f"{financial_summary['net_profit']:,.0f} ج.م")
    
    st.markdown("---")
    
    # طرق الدفع
    st.markdown("#### 💳 الإيرادات حسب طريقة الدفع")
    payment_methods = crud.get_payment_methods_stats(start_date.isoformat(), end_date.isoformat())
    
    if not payment_methods.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(payment_methods, use_container_width=True, hide_index=True)
        with col2:
            fig = px.pie(payment_methods, values='total', names='payment_method', title='توزيع طرق الدفع')
            st.plotly_chart(fig, use_container_width=True)
    
    # المصروفات حسب الفئة
    st.markdown("#### 💸 المصروفات حسب الفئة")
    expenses_by_cat = crud.get_expenses_by_category(start_date.isoformat(), end_date.isoformat())
    
    if not expenses_by_cat.empty:
        fig = px.bar(expenses_by_cat, x='category', y='total', title='المصروفات حسب الفئة')
        st.plotly_chart(fig, use_container_width=True)

def render_doctor_performance():
    """تقرير أداء الأطباء"""
    st.markdown("### 👨‍⚕️ تقرير أداء الأطباء")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=30), key="doc_start")
    with col2:
        end_date = st.date_input("حتى تاريخ", value=date.today(), key="doc_end")
    
    if start_date > end_date:
        st.warning("⚠️ التاريخ غير صحيح")
        return
    
    doctor_performance = crud.get_doctor_performance(start_date.isoformat(), end_date.isoformat())
    
    if not doctor_performance.empty:
        st.dataframe(
            doctor_performance[['doctor_name', 'specialization', 'total_appointments', 
                               'completed_appointments', 'total_revenue', 'total_commission']],
            use_container_width=True,
            hide_index=True
        )
        
        # رسم بياني للإيرادات
        fig = px.bar(
            doctor_performance, 
            x='doctor_name', 
            y='total_revenue',
            title='الإيرادات حسب الطبيب',
            color='total_revenue'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات أداء للأطباء في هذه الفترة")

def render_treatment_reports():
    """تقرير العلاجات"""
    st.markdown("### 💉 تقرير العلاجات الأكثر طلباً")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=30), key="treat_start")
    with col2:
        end_date = st.date_input("حتى تاريخ", value=date.today(), key="treat_end")
    
    if start_date > end_date:
        st.warning("⚠️ التاريخ غير صحيح")
        return
    
    treatment_popularity = crud.get_treatment_popularity(start_date.isoformat(), end_date.isoformat())
    
    if not treatment_popularity.empty:
        st.dataframe(
            treatment_popularity[['treatment_name', 'category', 'booking_count', 
                                 'total_revenue', 'avg_price']],
            use_container_width=True,
            hide_index=True
        )
        
        # رسم بياني
        fig = px.bar(
            treatment_popularity.head(10), 
            x='treatment_name', 
            y='booking_count',
            title='أكثر 10 علاجات طلباً',
            color='booking_count'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات علاجات في هذه الفترة")

def render_trends():
    """الاتجاهات والتحليلات"""
    st.markdown("### 📈 الاتجاهات")
    
    # مقارنة شهرية - استخدام دالة بديلة
    st.markdown("#### 📊 المقارنة الشهرية")
    
    try:
        # استخدام دالة get_revenue_by_period بدلاً من get_monthly_comparison
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=180)  # آخر 6 أشهر
        
        monthly_data = crud.get_revenue_by_period(
            start_date.isoformat(), 
            end_date.isoformat(), 
            group_by='month'
        )
        
        if not monthly_data.empty:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly_data['period'], 
                y=monthly_data['total_revenue'], 
                name='الإيرادات'
            ))
            
            fig.update_layout(
                title='الإيرادات الشهرية',
                xaxis_title='الشهر',
                yaxis_title='الإيرادات (ج.م)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # إضافة جدول البيانات
            st.dataframe(monthly_data, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد بيانات كافية للمقارنة الشهرية")
    except Exception as e:
        st.warning(f"⚠️ لا توجد بيانات مقارنة شهرية: {str(e)}")
    
    st.markdown("---")
    
    # الإيرادات اليومية
    st.markdown("#### 💵 الإيرادات اليومية (آخر 30 يوم)")
    daily_revenue = crud.get_daily_revenue_comparison(days=30)
    
    if not daily_revenue.empty:
        import plotly.express as px
        fig = px.line(
            daily_revenue, 
            x='payment_date', 
            y='daily_revenue', 
            title='الإيرادات اليومية', 
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات إيرادات يومية")
    
    st.markdown("---")
    
    # إحصائيات المواعيد
    st.markdown("#### 📅 حالة المواعيد")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من", value=date.today() - timedelta(days=30), key="appt_start")
    with col2:
        end_date = st.date_input("حتى", value=date.today(), key="appt_end")
    
    if start_date <= end_date:
        appointment_stats = crud.get_appointment_status_stats(
            start_date.isoformat(), 
            end_date.isoformat()
        )
        
        if not appointment_stats.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(appointment_stats, use_container_width=True, hide_index=True)
            with col2:
                import plotly.express as px
                fig = px.pie(
                    appointment_stats, 
                    values='count', 
                    names='status', 
                    title='توزيع حالات المواعيد'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد مواعيد في هذه الفترة")
    else:
        st.warning("⚠️ تاريخ البداية يجب أن يكون قبل تاريخ النهاية")