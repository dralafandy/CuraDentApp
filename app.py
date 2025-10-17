# app.py

import streamlit as st
from datetime import date
from database.crud import crud
from database.models import db
from styles import load_custom_css
from components.notifications import NotificationCenter
import time

# استيراد الصفحات
import dashboard
import appointments
import patients
import doctors
import treatments
import payments
import inventory
import suppliers
import expenses
import reports
import reports_advanced
import settings
import activity_log

# ========================
# تهيئة التطبيق
# ========================
st.set_page_config(
    page_title="نظام إدارة العيادة - Cura Clinic",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_db():
    db.initialize()
    return True

init_db()

# ========================
# دالة إخفاء القائمة الجانبية
# ========================
def auto_hide_sidebar():
    """إخفاء القائمة الجانبية تلقائياً بعد الاختيار"""
    hide_sidebar_style = """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
    </style>
    """
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)
    
    # إخفاء القائمة بعد ثانية واحدة
    time.sleep(0.1)
    st.markdown(
        """
        <script>
            var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
            setTimeout(function() {
                sidebar.setAttribute('aria-expanded', 'false');
            }, 100);
        </script>
        """, 
        unsafe_allow_html=True
    )

# ========================
# الشريط الجانبي المحسّن
# ========================
def render_sidebar():
    with st.sidebar:
        # شعار العيادة
        st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px;'>
                <h1 style='color: white; margin: 0; font-size: 2rem;'>🏥 Cura Clinic</h1>
                <p style='color: #e0e0e0; margin: 5px 0; font-size: 0.9rem;'>نظام إدارة العيادة المتكامل</p>
                <p style='color: #ffeb3b; margin: 5px 0; font-size: 0.8rem;'>⭐ الإصدار المحسّن 2.0</p>
            </div>
        """, unsafe_allow_html=True)

        # اختيار الثيم مع معاينة
        st.markdown("### 🎨 تخصيص الواجهة")
        theme_map = {
            "🔵 أزرق احترافي": "blue",
            "🟣 بنفسجي أنيق": "purple", 
            "🟢 أخضر مريح": "green",
            "🟠 برتقالي دافئ": "orange",
            "⚫ داكن حديث": "dark",
            "🩷 وردي ناعم": "pink"
        }
        
        theme_choice = st.selectbox(
            "اختر الثيم المفضل",
            list(theme_map.keys()),
            key="theme_select",
            help="غيّر شكل التطبيق حسب ذوقك"
        )
        load_custom_css(theme=theme_map[theme_choice])

        st.markdown("---")

        # القائمة الرئيسية المحسّنة
        st.markdown("### 📱 القائمة الرئيسية")
        
        menu_items = {
            "🏠 الرئيسية": "dashboard",
            "📅 المواعيد": "appointments",
            "👥 المرضى": "patients",
            "👨‍⚕️ الأطباء": "doctors",
            "💉 العلاجات": "treatments",
            "💰 المدفوعات": "payments",
            "📦 المخزون": "inventory",
            "🏪 الموردين": "suppliers",
            "💸 المصروفات": "expenses",
            "📊 التقارير": "reports",
            "📈 تقارير متقدمة": "reports_advanced",
            "⚙️ الإعدادات": "settings",
            "📝 سجل الأنشطة": "activity_log"
        }
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        
        # إضافة أيقونة للصفحة الحالية
        for label, page_id in menu_items.items():
            button_label = f"✅ {label}" if st.session_state.current_page == page_id else label
            
            if st.button(
                button_label, 
                key=f"nav_{page_id}",
                use_container_width=True,
                help=f"انتقل إلى {label.split()[1]}"
            ):
                st.session_state.current_page = page_id
                st.session_state.sidebar_action = True  # علامة لإخفاء القائمة
                st.rerun()

        st.markdown("---")
        
        # معلومات سريعة محسّنة
        st.markdown("### 📊 نظرة سريعة")
        stats = crud.get_dashboard_stats()
        
        # التاريخ والوقت
        from datetime import datetime
        now = datetime.now()
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📅 {now.strftime('%Y-%m-%d')}")
        with col2:
            st.info(f"⏰ {now.strftime('%H:%M')}")
        
        # إحصائيات اليوم
        st.success(f"📌 مواعيد اليوم: {stats['today_appointments']}")
        
        # التنبيهات
        if stats['low_stock_items'] > 0:
            st.warning(f"⚠️ مخزون منخفض: {stats['low_stock_items']} عنصر")
        else:
            st.success("✅ المخزون آمن")
            
        if stats['expiring_items'] > 0:
            st.error(f"🚨 أصناف تنتهي قريباً: {stats['expiring_items']}")
        else:
            st.success("✅ لا توجد أصناف منتهية")
        
        st.markdown("---")
        
        # مركز الإشعارات المحسّن
        NotificationCenter.render()
        
        # زر إظهار/إخفاء القائمة
        st.markdown("---")
        if st.button("🔄 إخفاء القائمة", use_container_width=True, type="secondary"):
            st.session_state.sidebar_action = True
            st.rerun()

# ========================
# التوجيه إلى الصفحات
# ========================
def main():
    render_sidebar()
    
    # إخفاء القائمة الجانبية إذا تم اختيار صفحة
    if 'sidebar_action' in st.session_state and st.session_state.sidebar_action:
        auto_hide_sidebar()
        st.session_state.sidebar_action = False
    
    # عرض الإشعارات العاجلة
    NotificationCenter.show_urgent_toast_notifications()

    # تعيين الصفحات
    page_mapping = {
        'dashboard': dashboard.render,
        'appointments': appointments.render,
        'patients': patients.render,
        'doctors': doctors.render,
        'treatments': treatments.render,
        'payments': payments.render,
        'inventory': inventory.render,
        'suppliers': suppliers.render,
        'expenses': expenses.render,
        'reports': reports.render,
        'reports_advanced': reports_advanced.render,
        'settings': settings.render,
        'activity_log': activity_log.render
    }
    
    # عرض الصفحة المختارة
    page = st.session_state.get('current_page', 'dashboard')
    render_func = page_mapping.get(page, dashboard.render)
    
    # إضافة عنوان الصفحة الحالية
    page_titles = {
        'dashboard': '🏠 لوحة التحكم الرئيسية',
        'appointments': '📅 إدارة المواعيد',
        'patients': '👥 إدارة المرضى',
        'doctors': '👨‍⚕️ إدارة الأطباء',
        'treatments': '💉 إدارة العلاجات',
        'payments': '💰 إدارة المدفوعات',
        'inventory': '📦 إدارة المخزون',
        'suppliers': '🏪 إدارة الموردين',
        'expenses': '💸 إدارة المصروفات',
        'reports': '📊 التقارير العامة',
        'reports_advanced': '📈 التقارير المتقدمة',
        'settings': '⚙️ الإعدادات',
        'activity_log': '📝 سجل الأنشطة'
    }
    
    # عرض شريط التنقل العلوي
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("☰ القائمة", help="فتح القائمة الجانبية"):
            st.markdown(
                """
                <script>
                    var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
                    sidebar.setAttribute('aria-expanded', 'true');
                </script>
                """, 
                unsafe_allow_html=True
            )
    
    with col2:
        st.markdown(
            f"<h2 style='text-align: center; margin: 0;'>{page_titles.get(page, 'Cura Clinic')}</h2>",
            unsafe_allow_html=True
        )
    
    with col3:
        # زر الرجوع للرئيسية
        if page != 'dashboard':
            if st.button("🏠 الرئيسية", help="العودة للوحة التحكم"):
                st.session_state.current_page = 'dashboard'
                st.rerun()
    
    st.markdown("---")
    
    # عرض الصفحة
    render_func()

if __name__ == "__main__":
    main()
