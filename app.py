import streamlit as st
from datetime import date
from database.crud import crud
from database.models import db
from styles import load_custom_css
from components.notifications import NotificationCenter

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
# الشريط الجانبي - التنقل
# ========================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: white; margin: 0;'>🏥 Cura Clinic</h1>
                <p style='color: #bdc3c7; margin: 5px 0;'>نظام إدارة العيادة المتكامل</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # اختيار الثيم
        theme_map = {
            "بنفسجي": "purple", "أزرق": "blue", "أخضر": "green",
            "برتقالي": "orange", "داكن": "dark", "وردي": "pink"
        }
        theme_choice = st.selectbox("🎨 اختر الثيم", list(theme_map.keys()), key="theme_select")
        load_custom_css(theme=theme_map[theme_choice])

        st.markdown("---")

        # القائمة الرئيسية
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
            "⚙️ الإعدادات": "settings",
            "📝 سجل الأنشطة": "activity_log"
        }
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        for label, page_id in menu_items.items():
            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()

        st.markdown("---")
        # معلومات سريعة
        stats = crud.get_dashboard_stats()
        st.info(f"📅 {date.today().strftime('%Y-%m-%d')}")
        st.success(f"📌 مواعيد اليوم: {stats['today_appointments']}")
        if stats['low_stock_items'] > 0:
            st.warning(f"⚠️ مخزون منخفض: {stats['low_stock_items']} عنصر")
        if stats['expiring_items'] > 0:
            st.error(f"🚨 أصناف تنتهي قريباً: {stats['expiring_items']}")
        st.markdown("---")
        # إشعارات
        NotificationCenter.render()

# ========================
# التوجيه إلى الصفحات
# ========================
def main():
    render_sidebar()
    NotificationCenter.show_urgent_toast_notifications()

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
        'settings': settings.render,
        'activity_log': activity_log.render
    }
    page = st.session_state.get('current_page', 'dashboard')
    render_func = page_mapping.get(page, dashboard.render)
    render_func()

if __name__ == "__main__":
    main()