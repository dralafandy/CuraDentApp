# components/quick_actions.py

import streamlit as st
from datetime import date
from database.crud import crud

class QuickActions:
    """مكون الإجراءات السريعة"""
    
    @staticmethod
    def render():
        """عرض أزرار الإجراءات السريعة"""
        st.markdown("### ⚡ إجراءات سريعة")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ موعد جديد", use_container_width=True):
                st.session_state.current_page = 'appointments'
                st.rerun()
        
        with col2:
            if st.button("👤 مريض جديد", use_container_width=True):
                st.session_state.current_page = 'patients'
                st.rerun()
        
        with col3:
            if st.button("💰 تسجيل دفعة", use_container_width=True):
                st.session_state.current_page = 'payments'
                st.rerun()
        
        with col4:
            if st.button("📦 إضافة مخزون", use_container_width=True):
                st.session_state.current_page = 'inventory'
                st.rerun()
        
        # إحصائيات سريعة
        stats = crud.get_dashboard_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 مرضى", stats['total_patients'], delta=None)
        
        with col2:
            st.metric("📅 مواعيد اليوم", stats['today_appointments'])
        
        with col3:
            low_stock = stats.get('low_stock_items', 0)
            if low_stock > 0:
                st.metric("⚠️ مخزون منخفض", low_stock, delta=f"-{low_stock}")
            else:
                st.metric("✅ المخزون", "آمن")
        
        with col4:
            expiring = stats.get('expiring_items', 0)
            if expiring > 0:
                st.metric("⏳ قريب الانتهاء", expiring, delta=f"-{expiring}")
            else:
                st.metric("✅ الصلاحية", "جيدة")