# app.py

import streamlit as st
from datetime import date
from database.crud import crud
from database.models import db
from styles import load_custom_css
from components.notifications import NotificationCenter
import time

# استيراد الصفحات (Pages Import)
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

# =========================
# تهيئة التطبيق (Application Setup)
# =========================
st.set_page_config(
    page_title="نظام إدارة العيادة - Cura Clinic",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تعيين حالة الصفحة الافتراضية
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'blue'

@st.cache_resource
def init_db():
    """تهيئة قاعدة البيانات مرة واحدة فقط."""
    db.initialize()
    return True

init_db()
load_custom_css(theme=st.session_state['theme'])

# =========================
# دالة عرض القائمة الجانبية (Sidebar)
# =========================
def render_sidebar():
    """تعرض شريط التنقل الجانبي مع الإخفاء التلقائي."""
    st.sidebar.image("https://placehold.co/150x50/3b82f6/ffffff?text=Cura+Clinic", use_column_width=True)
    st.sidebar.markdown("---")

    st.sidebar.markdown("## ⚙️ الإعدادات والمظهر")
    
    # اختيار الثيم
    themes = ['blue', 'green', 'orange', 'pink', 'purple', 'dark']
    current_theme = st.session_state['theme']
    new_theme = st.sidebar.selectbox("اختيار الثيم", themes, index=themes.index(current_theme))
    
    if new_theme != current_theme:
        st.session_state['theme'] = new_theme
        st.rerun() # Rerun to apply new theme via load_custom_css

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧭 التنقل")
    
    # تعريف الصفحات (Mapping page keys to titles)
    pages = {
        'dashboard': '🏠 لوحة التحكم',
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

    # حلقة التنقل مع ميزة الإخفاء التلقائي (Navigation loop with auto-hide)
    for key, title in pages.items():
        # استخدام st.button في الشريط الجانبي
        if st.sidebar.button(title, key=f"nav_{key}", use_container_width=True):
            st.session_state['page'] = key
            
            # START: JavaScript لتصغير وإخفاء القائمة الجانبية تلقائياً (Auto-hide JS Injection)
            st.markdown(
                """
                <script>
                    // البحث عن عنصر القائمة الجانبية في الصفحة الرئيسية (Find the sidebar element)
                    var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
                    
                    // استخدام مؤقت بسيط للتأكد من تسجيل تحديث حالة Streamlit
                    setTimeout(function() {
                        if (sidebar) {
                            // تعيين السمة التي تتحكم في حالة التصغير (Set collapse state)
                            sidebar.setAttribute('aria-expanded', 'false');
                        }
                    }, 10); // Small delay to ensure click registration
                </script>
                """,
                unsafe_allow_html=True
            )
            # END: JavaScript Injection
            
            # إعادة تشغيل التطبيق لعرض الصفحة الجديدة (Rerun to show new page content)
            st.rerun() 

# =========================
# دالة عرض شريط التنقل العلوي (Header Navigation)
# =========================
def render_header(page):
    """يعرض شريط التنقل العلوي وزر فتح القائمة الجانبية."""
    page_titles = {
        'dashboard': '🏠 لوحة التحكم',
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
        # زر فتح القائمة الجانبية
        if st.button("☰ القائمة", help="فتح القائمة الجانبية"):
            st.markdown(
                """
                <script>
                    // يفتح القائمة الجانبية بتعيين aria-expanded إلى true
                    var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
                    sidebar.setAttribute('aria-expanded', 'true');
                </script>
                """, 
                unsafe_allow_html=True
            )
    
    with col2:
        # عنوان الصفحة الحالي
        st.markdown(
            f"<h2 style='text-align: center; margin: 0;'>{page_titles.get(page, 'Cura Clinic')}</h2>",
            unsafe_allow_html=True
        )
    
    with col3:
        # زر الرجوع للرئيسية
        if page != 'dashboard':
            if st.button("🏠 الرئيسية", help="العودة إلى لوحة التحكم"):
                st.session_state['page'] = 'dashboard'
                st.rerun()

# =========================
# الدالة الرئيسية لتشغيل التطبيق (Main Run Function)
# =========================
def run():
    
    # عرض القائمة الجانبية
    render_sidebar()
    
    current_page = st.session_state['page']
    
    # عرض شريط التنقل العلوي
    render_header(current_page)

    st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    # عرض الإشعارات
    NotificationCenter.render(crud)

    # توجيه إلى الصفحة المختارة
    if current_page == 'dashboard':
        dashboard.render()
    elif current_page == 'appointments':
        appointments.render(crud)
    elif current_page == 'patients':
        patients.render(crud)
    elif current_page == 'doctors':
        doctors.render(crud)
    elif current_page == 'treatments':
        treatments.render(crud)
    elif current_page == 'payments':
        payments.render(crud)
    elif current_page == 'inventory':
        inventory.render(crud)
    elif current_page == 'suppliers':
        suppliers.render(crud)
    elif current_page == 'expenses':
        expenses.render(crud)
    elif current_page == 'reports':
        reports.render(crud)
    elif current_page == 'reports_advanced':
        reports_advanced.render(crud)
    elif current_page == 'settings':
        settings.render(crud)
    elif current_page == 'activity_log':
        activity_log.render(crud)

# تشغيل التطبيق
if __name__ == '__main__':
    run()

