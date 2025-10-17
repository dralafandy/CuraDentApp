# settings.py

import streamlit as st
import pandas as pd
from database.crud import crud
from database.models import db
from datetime import datetime

def render():
    """صفحة الإعدادات"""
    st.markdown("## ⚙️ الإعدادات")
    
    tab1, tab2, tab3 = st.tabs(["🏥 إعدادات العيادة", "💾 النسخ الاحتياطي", "🔔 الإشعارات"])
    
    with tab1:
        render_clinic_settings()
    
    with tab2:
        render_backup_settings()
    
    with tab3:
        render_notification_settings()

def render_clinic_settings():
    """إعدادات العيادة"""
    st.markdown("### 🏥 إعدادات العيادة الأساسية")
    
    settings = crud.get_all_settings()
    
    if not settings.empty:
        settings_dict = dict(zip(settings['key'], settings['value']))
    else:
        settings_dict = {}
    
    with st.form("clinic_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            clinic_name = st.text_input(
                "اسم العيادة",
                value=settings_dict.get('clinic_name', 'عيادة Cura الطبية')
            )
            clinic_phone = st.text_input(
                "هاتف العيادة",
                value=settings_dict.get('clinic_phone', '01234567890')
            )
            clinic_email = st.text_input(
                "بريد العيادة",
                value=settings_dict.get('clinic_email', 'info@curaclinic.com')
            )
        
        with col2:
            clinic_address = st.text_area(
                "عنوان العيادة",
                value=settings_dict.get('clinic_address', 'القاهرة، مصر')
            )
            working_hours = st.text_input(
                "ساعات العمل",
                value=settings_dict.get('working_hours', 'السبت - الخميس: 9 صباحاً - 9 مساءً')
            )
            currency = st.text_input(
                "العملة",
                value=settings_dict.get('currency', 'ج.م')
            )
        
        submitted = st.form_submit_button("💾 حفظ الإعدادات", type="primary", use_container_width=True)
        
        if submitted:
            try:
                crud.update_setting('clinic_name', clinic_name)
                crud.update_setting('clinic_phone', clinic_phone)
                crud.update_setting('clinic_email', clinic_email)
                crud.update_setting('clinic_address', clinic_address)
                crud.update_setting('working_hours', working_hours)
                crud.update_setting('currency', currency)
                
                st.success("✅ تم حفظ الإعدادات بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ في حفظ الإعدادات: {str(e)}")
    
    st.markdown("---")
    
    # إعدادات متقدمة
    st.markdown("### 🎨 الإعدادات المتقدمة")
    
    col1, col2 = st.columns(2)
    
    with col1:
        notifications_enabled = st.checkbox(
            "تفعيل الإشعارات",
            value=settings_dict.get('notifications_enabled', '1') == '1'
        )
        
        if st.button("حفظ الإشعارات"):
            crud.update_setting('notifications_enabled', '1' if notifications_enabled else '0')
            st.success("✅ تم التحديث")
    
    with col2:
        auto_backup = st.checkbox(
            "النسخ الاحتياطي التلقائي",
            value=settings_dict.get('auto_backup', '1') == '1'
        )
        
        if st.button("حفظ النسخ الاحتياطي"):
            crud.update_setting('auto_backup', '1' if auto_backup else '0')
            st.success("✅ تم التحديث")

def render_backup_settings():
    """إعدادات النسخ الاحتياطي"""
    st.markdown("### 💾 النسخ الاحتياطي")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📤 إنشاء نسخة احتياطية")
        st.info("سيتم حفظ نسخة من قاعدة البيانات في مجلد backups")
        
        if st.button("🔄 إنشاء نسخة احتياطية الآن", type="primary", use_container_width=True):
            with st.spinner("جاري إنشاء النسخة الاحتياطية..."):
                backup_path = db.backup_database()
                if backup_path:
                    st.success(f"✅ تم إنشاء النسخة الاحتياطية بنجاح!\n\n📁 المسار: `{backup_path}`")
                else:
                    st.error("❌ فشل إنشاء النسخة الاحتياطية")
    
    with col2:
        st.markdown("#### 📜 سجل النسخ الاحتياطي")
        
        conn = db.get_connection()
        backup_log = pd.read_sql_query(
            "SELECT * FROM backup_log ORDER BY created_at DESC LIMIT 10",
            conn
        )
        conn.close()
        
        if not backup_log.empty:
            st.dataframe(
                backup_log[['backup_type', 'backup_path', 'status', 'created_at']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("لا يوجد سجل نسخ احتياطي")
    
    st.markdown("---")
    
    # معلومات قاعدة البيانات
    st.markdown("### 📊 معلومات قاعدة البيانات")
    
    import os
    if os.path.exists(db.db_path):
        file_size = os.path.getsize(db.db_path) / (1024 * 1024)  # MB
        col1, col2, col3 = st.columns(3)
        col1.metric("📁 حجم قاعدة البيانات", f"{file_size:.2f} MB")
        col2.metric("📍 المسار", db.db_path)
        col3.metric("🕐 آخر تعديل", datetime.fromtimestamp(os.path.getmtime(db.db_path)).strftime("%Y-%m-%d %H:%M"))

def render_notification_settings():
    """إعدادات الإشعارات"""
    st.markdown("### 🔔 إدارة الإشعارات")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📨 الإشعارات الحالية")
        notifications = crud.get_all_notifications(limit=20)
        
        if not notifications.empty:
            for _, notif in notifications.iterrows():
                status_icon = "✅" if notif['is_read'] else "🔴"
                priority_color = {
                    'urgent': '🔴',
                    'high': '🟠',
                    'normal': '🟢',
                    'low': '⚪'
                }.get(notif['priority'], '🟢')
                
                with st.expander(f"{status_icon} {priority_color} {notif['title']}"):
                    st.write(f"**الرسالة:** {notif['message']}")
                    st.write(f"**التاريخ:** {notif['created_at']}")
                    st.write(f"**الأولوية:** {notif['priority']}")
                    
                    if not notif['is_read']:
                        if st.button("تحديد كمقروء", key=f"read_{notif['id']}"):
                            crud.mark_notification_as_read(notif['id'])
                            st.rerun()
        else:
            st.info("لا توجد إشعارات")
    
    with col2:
        st.markdown("#### ⚙️ إجراءات")
        
        if st.button("✅ تحديد الكل كمقروء", use_container_width=True):
            crud.mark_all_notifications_as_read()
            st.success("تم تحديد جميع الإشعارات كمقروءة")
            st.rerun()
        
        if st.button("🔄 توليد إشعارات يومية", use_container_width=True):
            crud.generate_daily_notifications()
            st.success("✅ تم توليد الإشعارات اليومية")
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("#### ➕ إضافة إشعار يدوي")
        
        with st.form("add_notification"):
            notif_type = st.selectbox("النوع", ["appointment", "inventory", "payment", "general"])
            title = st.text_input("العنوان")
            message = st.text_area("الرسالة")
            priority = st.selectbox("الأولوية", ["normal", "high", "urgent", "low"])
            
            if st.form_submit_button("إضافة إشعار"):
                if title and message:
                    crud.create_notification(notif_type, title, message, priority)
                    st.success("✅ تم إضافة الإشعار")
                    st.rerun()
                else:
                    st.warning("⚠️ يرجى ملء العنوان والرسالة")