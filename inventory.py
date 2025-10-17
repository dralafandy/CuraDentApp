# inventory.py

import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud

def render():
    """صفحة إدارة المخزون"""
    st.markdown("## 📦 إدارة المخزون")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 المخزون الحالي", "➕ إضافة صنف", "📉 المخزون المنخفض", "⏳ الأصناف المنتهية"])
    
    with tab1:
        render_current_inventory()
    
    with tab2:
        render_add_item()
    
    with tab3:
        render_low_stock()
    
    with tab4:
        render_expiring_items()

def render_current_inventory():
    """عرض المخزون الحالي"""
    inventory = crud.get_all_inventory()
    
    if not inventory.empty:
        st.dataframe(
            inventory[['id', 'item_name', 'category', 'quantity', 'unit_price', 
                      'min_stock_level', 'supplier_name', 'expiry_date', 'location']],
            use_container_width=True,
            hide_index=True
        )
        
        with st.expander("🔧 تعديل كمية صنف"):
            col1, col2, col3 = st.columns(3)
            with col1:
                item_id = st.number_input("رقم الصنف", min_value=1, step=1)
            with col2:
                operation = st.selectbox("العملية", ["إضافة", "خصم", "تعيين"])
            with col3:
                quantity = st.number_input("الكمية", min_value=0, step=1)
            
            if st.button("تحديث الكمية"):
                try:
                    op_map = {"إضافة": "add", "خصم": "subtract", "تعيين": "set"}
                    crud.update_inventory_quantity(item_id, quantity, op_map[operation])
                    st.success(f"✅ تم {operation} الكمية بنجاح")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {str(e)}")
        
        with st.expander("🗑 حذف صنف"):
            del_item_id = st.number_input("رقم الصنف للحذف", min_value=1, step=1, key="del_item")
            if st.button("حذف الصنف", type="secondary"):
                crud.delete_inventory_item(del_item_id)
                st.success("✅ تم إلغاء تفعيل الصنف")
                st.rerun()
    else:
        st.info("المخزون فارغ حالياً")

def render_add_item():
    """إضافة صنف جديد"""
    st.markdown("### ➕ إضافة صنف للمخزون")
    
    suppliers = crud.get_all_suppliers()
    
    col1, col2 = st.columns(2)
    
    with col1:
        item_name = st.text_input("اسم الصنف *")
        category = st.selectbox("الفئة", ["مستهلكات", "أدوية", "مواد طبية", "منتجات", "أخرى"])
        quantity = st.number_input("الكمية الأولية", min_value=0, step=1)
        unit_price = st.number_input("سعر الوحدة", min_value=0.0, step=1.0)
        min_stock = st.number_input("الحد الأدنى للمخزون", min_value=0, value=10, step=1)
    
    with col2:
        supplier_id = st.selectbox(
            "المورد",
            [None] + suppliers['id'].tolist(),
            format_func=lambda x: "لا يوجد" if x is None else suppliers[suppliers['id'] == x]['name'].iloc[0]
        ) if not suppliers.empty else None
        
        expiry_date = st.date_input("تاريخ الانتهاء (اختياري)", value=None)
        location = st.text_input("موقع التخزين", value="المخزن الرئيسي")
        barcode = st.text_input("الباركود (اختياري)")
    
    if st.button("💾 حفظ الصنف", type="primary", use_container_width=True):
        if item_name and quantity >= 0:
            try:
                crud.create_inventory_item(
                    item_name, category, quantity, unit_price, min_stock,
                    supplier_id, 
                    expiry_date.isoformat() if expiry_date else None,
                    location, barcode
                )
                st.success("✅ تم إضافة الصنف بنجاح")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ: {str(e)}")
        else:
            st.warning("⚠️ يرجى ملء الحقول المطلوبة")

def render_low_stock():
    """عرض الأصناف منخفضة المخزون"""
    st.markdown("### 📉 الأصناف المنخفضة")
    
    low_stock = crud.get_low_stock_items()
    
    if not low_stock.empty:
        st.warning(f"⚠️ يوجد {len(low_stock)} صنف تحت الحد الأدنى")
        st.dataframe(
            low_stock[['item_name', 'category', 'quantity', 'min_stock_level']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ جميع الأصناف في المستوى الآمن")

def render_expiring_items():
    """عرض الأصناف قريبة الانتهاء"""
    st.markdown("### ⏳ الأصناف قريبة الانتهاء")
    
    days = st.slider("عرض الأصناف التي تنتهي خلال (يوم)", 7, 90, 30)
    
    expiring = crud.get_expiring_inventory(days)
    
    if not expiring.empty:
        st.error(f"🚨 يوجد {len(expiring)} صنف ينتهي خلال {days} يوم")
        st.dataframe(
            expiring[['item_name', 'category', 'quantity', 'expiry_date', 'days_to_expire']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success(f"✅ لا توجد أصناف تنتهي خلال {days} يوم")