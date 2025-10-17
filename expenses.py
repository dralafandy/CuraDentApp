# expenses.py

import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud

def render():
    """صفحة إدارة المصروفات"""
    st.markdown("## 💸 إدارة المصروفات")
    
    tab1, tab2, tab3 = st.tabs(["📋 جميع المصروفات", "➕ تسجيل مصروف", "📊 تحليل المصروفات"])
    
    with tab1:
        render_all_expenses()
    
    with tab2:
        render_add_expense()
    
    with tab3:
        render_expense_analysis()

def render_all_expenses():
    """عرض جميع المصروفات"""
    expenses = crud.get_all_expenses()
    
    if not expenses.empty:
        # فلترة
        col1, col2 = st.columns(2)
        with col1:
            categories = ["الكل"] + expenses['category'].unique().tolist()
            category_filter = st.selectbox("فلترة حسب الفئة", categories)
        
        with col2:
            date_filter = st.date_input("التاريخ (اختياري)", value=None, key="expense_date_filter")
        
        filtered_expenses = expenses.copy()
        
        if category_filter != "الكل":
            filtered_expenses = filtered_expenses[filtered_expenses['category'] == category_filter]
        
        if date_filter:
            filtered_expenses = filtered_expenses[filtered_expenses['expense_date'] == date_filter.isoformat()]
        
        st.dataframe(
            filtered_expenses[['id', 'category', 'description', 'amount', 'expense_date', 
                              'payment_method', 'receipt_number', 'approved_by']],
            use_container_width=True,
            hide_index=True
        )
        
        # حذف مصروف
        with st.expander("🗑 حذف مصروف"):
            expense_id = st.number_input("رقم المصروف", min_value=1, step=1)
            if st.button("حذف", type="secondary"):
                crud.delete_expense(expense_id)
                st.success("✅ تم حذف المصروف")
                st.rerun()
    else:
        st.info("لا توجد مصروفات مسجلة")

def render_add_expense():
    """تسجيل مصروف جديد"""
    st.markdown("### ➕ تسجيل مصروف جديد")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "الفئة *",
            ["رواتب", "إيجار", "كهرباء ومياه", "صيانة", "مستلزمات", 
             "تسويق", "اتصالات", "نظافة", "ضرائب", "أخرى"]
        )
        
        if category == "أخرى":
            category = st.text_input("حدد الفئة")
        
        description = st.text_area("الوصف *")
        amount = st.number_input("المبلغ *", min_value=0.0, step=10.0)
        expense_date = st.date_input("تاريخ المصروف", value=date.today())
    
    with col2:
        payment_method = st.selectbox(
            "طريقة الدفع",
            ["نقدي", "شيك", "تحويل بنكي", "بطاقة ائتمان"]
        )
        receipt_number = st.text_input("رقم الإيصال / الفاتورة")
        approved_by = st.text_input("تمت الموافقة بواسطة", value="الإدارة")
        is_recurring = st.checkbox("مصروف متكرر (شهري)")
    
    notes = st.text_area("ملاحظات إضافية")
    
    if st.button("💾 حفظ المصروف", type="primary", use_container_width=True):
        if description and amount > 0:
            try:
                crud.create_expense(
                    category, description, amount, expense_date.isoformat(),
                    payment_method, receipt_number, notes, approved_by, is_recurring
                )
                st.success("✅ تم تسجيل المصروف بنجاح")
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
        else:
            st.warning("⚠️ يرجى ملء الحقول المطلوبة")

def render_expense_analysis():
    """تحليل المصروفات"""
    st.markdown("### 📊 تحليل المصروفات")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("حتى تاريخ", value=date.today())
    
    if start_date > end_date:
        st.warning("⚠️ التاريخ غير صحيح")
        return
    
    expenses_by_category = crud.get_expenses_by_category(
        start_date.isoformat(), 
        end_date.isoformat()
    )
    
    if not expenses_by_category.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### المصروفات حسب الفئة")
            st.dataframe(
                expenses_by_category,
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.markdown("#### التوزيع البياني")
            import plotly.express as px
            fig = px.pie(
                expenses_by_category, 
                values='total', 
                names='category',
                title='توزيع المصروفات'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # الإجمالي
        total_expenses = expenses_by_category['total'].sum()
        st.metric("💰 إجمالي المصروفات", f"{total_expenses:,.0f} ج.م")
    else:
        st.info("لا توجد مصروفات في هذه الفترة")