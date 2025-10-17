# activity_log.py

import streamlit as st
import pandas as pd
from database.crud import crud
from datetime import date, timedelta

def render():
    """صفحة سجل الأنشطة"""
    st.markdown("## 📝 سجل الأنشطة")
    
    st.info("📌 هنا يمكنك متابعة جميع العمليات التي تمت على النظام")
    
    tab1, tab2 = st.tabs(["📋 جميع الأنشطة", "🔍 بحث وفلترة"])
    
    with tab1:
        render_all_activities()
    
    with tab2:
        render_search_activities()

def render_all_activities():
    """عرض جميع الأنشطة"""
    st.markdown("### 📋 سجل الأنشطة الأخير")
    
    # اختيار عدد السجلات
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("#### آخر الأنشطة")
    with col2:
        limit = st.selectbox("عدد السجلات", [50, 100, 200, 500], index=0)
    
    activities = crud.get_activity_log(limit=limit)
    
    if not activities.empty:
        # تلوين حسب نوع النشاط
        def color_action(action):
            colors = {
                'إضافة': '🟢',
                'تحديث': '🟡',
                'حذف': '🔴',
                'استخدام': '🔵'
            }
            for key, icon in colors.items():
                if key in action:
                    return f"{icon} {action}"
            return action
        
        # عرض الجدول
        display_df = activities.copy()
        display_df['action'] = display_df['action'].apply(color_action)
        
        st.dataframe(
            display_df[['id', 'action', 'table_name', 'record_id', 'details', 'user_name', 'created_at']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": "رقم",
                "action": "النشاط",
                "table_name": "الجدول",
                "record_id": "رقم السجل",
                "details": "التفاصيل",
                "user_name": "المستخدم",
                "created_at": "التاريخ والوقت"
            }
        )
        
        # إحصائيات سريعة
        st.markdown("---")
        st.markdown("### 📊 إحصائيات الأنشطة")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_activities = len(activities)
            st.metric("📝 إجمالي الأنشطة", total_activities)
        
        with col2:
            add_count = len(activities[activities['action'].str.contains('إضافة', na=False)])
            st.metric("🟢 عمليات الإضافة", add_count)
        
        with col3:
            update_count = len(activities[activities['action'].str.contains('تحديث', na=False)])
            st.metric("🟡 عمليات التحديث", update_count)
        
        with col4:
            delete_count = len(activities[activities['action'].str.contains('حذف', na=False)])
            st.metric("🔴 عمليات الحذف", delete_count)
        
        # توزيع الأنشطة حسب الجدول
        st.markdown("#### 📊 توزيع الأنشطة حسب الجدول")
        
        table_counts = activities['table_name'].value_counts()
        
        if not table_counts.empty:
            import plotly.express as px
            fig = px.bar(
                x=table_counts.index,
                y=table_counts.values,
                labels={'x': 'الجدول', 'y': 'عدد الأنشطة'},
                title='الأنشطة حسب الجدول'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد أنشطة مسجلة حتى الآن")

def render_search_activities():
    """البحث والفلترة في الأنشطة"""
    st.markdown("### 🔍 بحث وفلترة متقدمة")
    
    activities = crud.get_activity_log(limit=1000)
    
    if activities.empty:
        st.info("لا توجد أنشطة للبحث فيها")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # فلترة حسب نوع النشاط
        action_types = ["الكل"] + activities['action'].unique().tolist()
        selected_action = st.selectbox("نوع النشاط", action_types)
    
    with col2:
        # فلترة حسب الجدول
        tables = ["الكل"] + activities['table_name'].unique().tolist()
        selected_table = st.selectbox("الجدول", tables)
    
    with col3:
        # فلترة حسب المستخدم
        users = ["الكل"] + activities['user_name'].unique().tolist()
        selected_user = st.selectbox("المستخدم", users)
    
    # فلترة حسب التاريخ
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=7))
    with col2:
        end_date = st.date_input("إلى تاريخ", value=date.today())
    
    # بحث نصي
    search_text = st.text_input("🔍 بحث في التفاصيل")
    
    # تطبيق الفلاتر
    filtered_activities = activities.copy()
    
    if selected_action != "الكل":
        filtered_activities = filtered_activities[filtered_activities['action'] == selected_action]
    
    if selected_table != "الكل":
        filtered_activities = filtered_activities[filtered_activities['table_name'] == selected_table]
    
    if selected_user != "الكل":
        filtered_activities = filtered_activities[filtered_activities['user_name'] == selected_user]
    
    # فلترة التاريخ
    filtered_activities['created_date'] = pd.to_datetime(filtered_activities['created_at']).dt.date
    filtered_activities = filtered_activities[
        (filtered_activities['created_date'] >= start_date) & 
        (filtered_activities['created_date'] <= end_date)
    ]
    
    if search_text:
        filtered_activities = filtered_activities[
            filtered_activities['details'].str.contains(search_text, case=False, na=False)
        ]
    
    # عرض النتائج
    st.markdown(f"### 📊 النتائج ({len(filtered_activities)} سجل)")
    
    if not filtered_activities.empty:
        st.dataframe(
            filtered_activities[['id', 'action', 'table_name', 'record_id', 'details', 'user_name', 'created_at']],
            use_container_width=True,
            hide_index=True
        )
        
        # تصدير النتائج
        st.markdown("---")
        st.markdown("#### 📥 تصدير النتائج")
        
        csv = filtered_activities.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 تحميل كملف CSV",
            data=csv,
            file_name=f"activity_log_{date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("لا توجد نتائج مطابقة للبحث")