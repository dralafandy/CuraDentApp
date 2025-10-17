# components/notifications.py

import streamlit as st
from database.crud import crud

class NotificationCenter:
    """مركز الإشعارات المتقدم"""
    
    @staticmethod
    def render():
        """عرض الإشعارات في الشريط الجانبي"""
        st.markdown("### 🔔 الإشعارات")
        
        notifications = crud.get_unread_notifications(limit=5)
        
        if not notifications.empty:
            unread_count = len(notifications)
            st.warning(f"⚠️ لديك {unread_count} إشعار جديد")
            
            for _, notif in notifications.iterrows():
                priority_icons = {
                    'urgent': '🔴',
                    'high': '🟠',
                    'normal': '🟢',
                    'low': '⚪'
                }
                icon = priority_icons.get(notif['priority'], '🟢')
                
                with st.expander(f"{icon} {notif['title']}", expanded=False):
                    st.write(notif['message'])
                    st.caption(f"📅 {notif['created_at']}")
                    
                    if st.button("✅ تحديد كمقروء", key=f"notif_{notif['id']}"):
                        crud.mark_notification_as_read(notif['id'])
                        st.rerun()
        else:
            st.success("✅ لا توجد إشعارات جديدة")
    
    @staticmethod
    def show_urgent_toast_notifications():
        """عرض إشعارات فورية للحالات العاجلة"""
        urgent_notifications = crud.get_unread_notifications(limit=10)
        
        if not urgent_notifications.empty:
            urgent = urgent_notifications[urgent_notifications['priority'] == 'urgent']
            
            for _, notif in urgent.iterrows():
                st.toast(f"🚨 {notif['title']}: {notif['message']}", icon="🚨")