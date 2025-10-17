# suppliers.py

import streamlit as st
import pandas as pd
from database.crud import crud

def render():
    """صفحة إدارة الموردين"""
    st.markdown("## 🏪 إدارة الموردين")
    
    tab1, tab2 = st.tabs(["📋 قائمة الموردين", "➕ إضافة مورد"])
    
    with tab1:
        render_supplier_list()
    
    with tab2:
        render_add_supplier()

def render_supplier_list():
    """عرض جميع الموردين"""
    suppliers = crud.get_all_suppliers()
    
    if not suppliers.empty:
        st.dataframe(
            suppliers[['id', 'name', 'contact_person', 'phone', 'email', 'payment_terms']],
            use_container_width=True,
            hide_index=True
        )
        
        with st.expander("🔧 تعديل بيانات مورد"):
            supplier_id = st.number_input("رقم المورد", min_value=1, step=1)
            supplier = crud.get_supplier_by_id(supplier_id)
            
            if supplier:
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("اسم المورد", value=supplier[1])
                    contact_person = st.text_input("الشخص المسؤول", value=supplier[2])
                    phone = st.text_input("رقم الهاتف", value=supplier[3])
                
                with col2:
                    email = st.text_input("البريد الإلكتروني", value=supplier[4])
                    address = st.text_input("العنوان", value=supplier[5])
                    payment_terms = st.text_input("شروط الدفع", value=supplier[6])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 حفظ التعديلات", type="primary"):
                        try:
                            crud.update_supplier(
                                supplier_id, name, contact_person, 
                                phone, email, address, payment_terms
                            )
                            st.success("✅ تم تحديث بيانات المورد")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ خطأ: {str(e)}")
                
                with col2:
                    if st.button("🗑 حذف المورد", type="secondary"):
                        crud.delete_supplier(supplier_id)
                        st.success("✅ تم إلغاء تفعيل المورد")
                        st.rerun()
            else:
                st.warning("⚠️ لم يتم العثور على المورد")
        
        # عرض تقرير مورد
        with st.expander("📊 تقرير مورد"):
            report_supplier_id = st.number_input("رقم المورد للتقرير", min_value=1, step=1, key="report_supplier")
            
            if st.button("عرض التقرير"):
                report = crud.get_supplier_detailed_report(report_supplier_id)
                
                if report and report['supplier']:
                    st.markdown(f"### تقرير المورد: {report['supplier']['name']}")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("عدد الأصناف", report['total_items'])
                    col2.metric("القيمة الإجمالية", f"{report['total_value']:,.0f} ج.م")
                    col3.metric("أصناف منخفضة", report['low_stock_items'])
                    
                    if not report['items'].empty:
                        st.markdown("#### الأصناف الموردة")
                        st.dataframe(
                            report['items'][['item_name', 'category', 'quantity', 'unit_price', 'total_value']],
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    if not report['categories'].empty:
                        st.markdown("#### توزيع الفئات")
                        st.dataframe(
                            report['categories'],
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.info("لا توجد بيانات لهذا المورد")
    else:
        st.info("لا يوجد موردين في النظام حالياً")

def render_add_supplier():
    """إضافة مورد جديد"""
    st.markdown("### ➕ إضافة مورد جديد")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("اسم المورد *")
        contact_person = st.text_input("الشخص المسؤول")
        phone = st.text_input("رقم الهاتف *")
    
    with col2:
        email = st.text_input("البريد الإلكتروني")
        address = st.text_area("العنوان")
        payment_terms = st.selectbox(
            "شروط الدفع",
            ["نقدي", "آجل 30 يوم", "آجل 60 يوم", "آجل 90 يوم", "أخرى"]
        )
        
        if payment_terms == "أخرى":
            payment_terms = st.text_input("حدد شروط الدفع")
    
    if st.button("💾 حفظ المورد", type="primary", use_container_width=True):
        if name and phone:
            try:
                crud.create_supplier(
                    name, contact_person, phone, 
                    email, address, payment_terms
                )
                st.success("✅ تم إضافة المورد بنجاح")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
        else:
            st.warning("⚠️ يرجى ملء الحقول المطلوبة")