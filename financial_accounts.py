# financial_accounts.py (Full Code with st.dialog)

import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud
import plotly.express as px
import plotly.graph_objects as go

# ====================
# نافذة إضافة دفعة لمريض (منبثقة)
# ====================
@st.dialog("➕ إضافة دفعة لمريض")
def patient_payment_dialog():
    patient_id = st.session_state.get('selected_patient_id')
    if not patient_id:
        st.error("لم يتم تحديد المريض. يرجى إغلاق النافذة واختيار مريض أولاً.")
        return

    patients = crud.get_all_patients()
    patient_name = patients[patients['id'] == patient_id]['name'].iloc[0]
    
    st.info(f"**المريض:** {patient_name}")
    
    amount = st.number_input("المبلغ", min_value=0.01, step=10.0, help="المبلغ الذي سيتم دفعه")
    payment_method = st.selectbox("طريقة الدفع", ["نقدي", "بطاقة ائتمان", "تحويل بنكي", "شيك"])
    notes = st.text_area("ملاحظات")
    
    if st.button("💾 حفظ الدفعة", type="primary", use_container_width=True):
        try:
            account_id = crud.create_or_update_account('patient', patient_id, patient_name)
            
            crud.add_financial_transaction(
                account_id, 'payment', amount,
                f"دفعة من المريض {patient_name}", 'payment', None, payment_method, notes
            )
            
            voucher_no = crud.create_voucher(
                'receipt', account_id, amount,
                payment_method, f"دفعة من {patient_name}", "النظام", notes
            )
            
            st.success(f"✅ تم حفظ الدفعة بنجاح! سند قبض رقم: {voucher_no}")
            st.session_state.show_patient_payment_dialog = False
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ خطأ أثناء الحفظ: {e}")

# ====================
# نافذة تسجيل سحب لطبيب (منبثقة)
# ====================
@st.dialog("💸 تسجيل سحب مستحقات")
def doctor_withdrawal_dialog():
    doctor_id = st.session_state.get('selected_doctor_id')
    if not doctor_id:
        st.error("لم يتم تحديد الطبيب. يرجى إغلاق النافذة واختيار طبيب أولاً.")
        return

    doctors = crud.get_all_doctors()
    doctor_name = doctors[doctors['id'] == doctor_id]['name'].iloc[0]
    
    summary = crud.get_doctor_financial_summary(doctor_id)
    balance = summary.get('current_balance', 0)
    
    st.info(f"**الطبيب:** {doctor_name}")
    st.info(f"الرصيد المتاح للسحب: **{balance:,.2f} ج.م**")
    
    if balance > 0:
        amount = st.number_input("المبلغ المسحوب", min_value=0.01, max_value=float(balance), step=100.0)
        method = st.selectbox("طريقة السحب", ["نقدي", "تحويل بنكي", "شيك"])
        notes = st.text_area("ملاحظات")
        
        if st.button("💾 تسجيل السحب", type="primary", use_container_width=True):
            try:
                account_id = crud.create_or_update_account('doctor', doctor_id, doctor_name)
                
                crud.add_financial_transaction(
                    account_id, 'withdrawal', amount,
                    f"سحب مستحقات د. {doctor_name}", 'withdrawal', None, method, notes
                )
                
                voucher_no = crud.create_voucher(
                    'payment', account_id, amount,
                    method, f"سحب مستحقات د. {doctor_name}", "النظام", notes
                )
                
                st.success(f"✅ تم تسجيل السحب بنجاح! سند صرف رقم: {voucher_no}")
                st.session_state.show_doctor_withdrawal_dialog = False
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ خطأ أثناء التسجيل: {e}")
    else:
        st.warning("لا يوجد رصيد متاح للسحب.")

# ====================
# نافذة تسجيل دفعة لمورد (منبثقة)
# ====================
@st.dialog("💰 تسجيل دفعة لمورد")
def supplier_payment_dialog():
    supplier_id = st.session_state.get('selected_supplier_id')
    if not supplier_id:
        st.error("لم يتم تحديد المورد.")
        return

    suppliers = crud.get_all_suppliers()
    supplier_name = suppliers[suppliers['id'] == supplier_id]['name'].iloc[0]
    
    summary = crud.get_supplier_financial_summary(supplier_id)
    outstanding = summary.get('outstanding_balance', 0)
    
    st.info(f"**المورد:** {supplier_name}")
    st.info(f"المبلغ المستحق للمورد: **{outstanding:,.2f} ج.م**")
    
    if outstanding > 0:
        amount = st.number_input("المبلغ المدفوع", min_value=0.01, max_value=float(outstanding), step=100.0)
        method = st.selectbox("طريقة الدفع", ["نقدي", "تحويل بنكي", "شيك"])
        notes = st.text_area("ملاحظات")
        
        if st.button("💾 حفظ الدفعة", type="primary", use_container_width=True):
            try:
                account_id = crud.create_or_update_account('supplier', supplier_id, supplier_name)
                
                crud.add_financial_transaction(
                    account_id, 'payment', amount,
                    f"دفعة للمورد {supplier_name}", 'payment', None, method, notes
                )
                
                voucher_no = crud.create_voucher(
                    'payment', account_id, amount,
                    method, f"دفعة للمورد {supplier_name}", "النظام", notes
                )
                
                st.success(f"✅ تم حفظ الدفعة للمورد! سند صرف رقم: {voucher_no}")
                st.session_state.show_supplier_payment_dialog = False
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ خطأ أثناء الحفظ: {e}")
    else:
        st.warning("لا توجد مديونيات مستحقة لهذا المورد.")

# ====================
# الدوال الرئيسية لعرض التبويبات
# ====================
def render_patient_accounts():
    st.markdown("### 👥 حسابات المرضى")
    
    patients = crud.get_all_patients()
    if patients.empty:
        st.info("لا يوجد مرضى.")
        return
        
    col1, col2 = st.columns([3, 1])
    
    with col1:
        patient_id = st.selectbox(
            "اختر المريض لعرض حسابه",
            patients['id'].tolist(),
            format_func=lambda x: f"{patients[patients['id'] == x]['name'].iloc[0]} (ID: {x})",
            key="fin_patient_select"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("➕ إضافة دفعة", use_container_width=True, help="إضافة دفعة للمريض المحدد"):
            st.session_state.show_patient_payment_dialog = True
            st.session_state.selected_patient_id = patient_id

    # عرض الحساب
    summary = crud.get_patient_financial_summary(patient_id)
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي العلاجات", f"{summary.get('total_treatments_cost', 0):,.2f} ج.م")
    col2.metric("إجمالي المدفوع", f"{summary.get('total_paid', 0):,.2f} ج.م")
    outstanding = summary.get('outstanding_balance', 0)
    col3.metric("المتبقي", f"{outstanding:,.2f} ج.م", delta=f"-{outstanding:,.2f}" if outstanding > 0 else "✅")
    
    # كشف الحساب
    st.markdown("#### 📋 كشف الحساب التفصيلي")
    account_id = crud.create_or_update_account('patient', patient_id, patients[patients['id'] == patient_id]['name'].iloc[0])
    statement = crud.get_account_statement('patient', patient_id)
    if statement and not statement['transactions'].empty:
        st.dataframe(statement['transactions'][['transaction_date', 'transaction_type', 'amount', 'description']], use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد حركات مالية مسجلة.")

def render_doctor_accounts():
    st.markdown("### 👨‍⚕️ حسابات الأطباء")
    
    doctors = crud.get_all_doctors()
    if doctors.empty:
        st.info("لا يوجد أطباء.")
        return
        
    col1, col2 = st.columns([3, 1])
    
    with col1:
        doctor_id = st.selectbox(
            "اختر الطبيب لعرض حسابه",
            doctors['id'].tolist(),
            format_func=lambda x: f"{doctors[doctors['id'] == x]['name'].iloc[0]} (ID: {x})",
            key="fin_doctor_select"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("💸 تسجيل سحب", use_container_width=True, help="تسجيل سحب مستحقات للطبيب المحدد"):
            st.session_state.show_doctor_withdrawal_dialog = True
            st.session_state.selected_doctor_id = doctor_id

    # عرض الحساب
    summary = crud.get_doctor_financial_summary(doctor_id)
    balance = summary.get('current_balance', 0)
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المستحقات", f"{summary.get('total_earnings', 0):,.2f} ج.م")
    col2.metric("إجمالي المسحوب", f"{summary.get('total_withdrawn', 0):,.2f} ج.م")
    col3.metric("الرصيد الحالي", f"{balance:,.2f} ج.م", delta=f"+{balance:,.2f}" if balance > 0 else None)

def render_supplier_accounts():
    st.markdown("### 🏪 حسابات الموردين")
    
    suppliers = crud.get_all_suppliers()
    if suppliers.empty:
        st.info("لا يوجد موردين.")
        return
        
    col1, col2 = st.columns([3, 1])
    
    with col1:
        supplier_id = st.selectbox(
            "اختر المورد لعرض حسابه",
            suppliers['id'].tolist(),
            format_func=lambda x: suppliers[suppliers['id'] == x]['name'].iloc[0],
            key="fin_supplier_select"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("💰 تسجيل دفعة", use_container_width=True, help="تسجيل دفعة للمورد المحدد"):
            st.session_state.show_supplier_payment_dialog = True
            st.session_state.selected_supplier_id = supplier_id

    # عرض الحساب
    summary = crud.get_supplier_financial_summary(supplier_id)
    outstanding = summary.get('outstanding_balance', 0)
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المشتريات", f"{summary.get('total_purchases', 0):,.2f} ج.م")
    col2.metric("إجمالي المدفوع", f"{summary.get('total_paid', 0):,.2f} ج.م")
    col3.metric("المتبقي", f"{outstanding:,.2f} ج.م", delta=f"-{outstanding:,.2f}" if outstanding > 0 else "✅")

def render_clinic_account():
    """عرض حساب العيادة"""
    st.markdown("### 🏥 حساب العيادة العام")
    
    summary = crud.get_clinic_financial_summary()
    
    # البطاقات الرئيسية
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📥 إجمالي إيرادات العيادة",
            f"{summary.get('total_revenue', 0):,.2f} ج.م",
            help="حصة العيادة من جميع العلاجات"
        )
    
    with col2:
        st.metric(
            "📤 إجمالي المصروفات",
            f"{summary.get('total_expenses', 0):,.2f} ج.م",
            help="جميع المصروفات التشغيلية"
        )
    
    with col3:
        profit = summary.get('net_profit', 0)
        st.metric(
            "💰 صافي الربح",
            f"{profit:,.2f} ج.م",
            delta=f"{'📈' if profit >= 0 else '📉'} {profit:,.2f}"
        )
    
    # رسم بياني للتدفق النقدي
    st.markdown("---")
    st.markdown("#### 📊 التدفق النقدي الشهري")
    
    # جلب بيانات شهرية
    monthly_data = crud.get_monthly_comparison()
    
    if isinstance(monthly_data, pd.DataFrame) and not monthly_data.empty:
        try:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='الإيرادات', x=monthly_data['month'], y=monthly_data['revenue']))
            fig.add_trace(go.Bar(name='المصروفات', x=monthly_data['month'], y=monthly_data['expenses']))
            fig.add_trace(go.Scatter(name='الربح', x=monthly_data['month'], y=monthly_data['profit'],
                                    mode='lines+markers', line=dict(width=3, color='green')))
            
            fig.update_layout(title="التدفق النقدي آخر 6 أشهر", barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.warning("لا يمكن عرض الرسم البياني للتدفق النقدي")
    else:
        st.info("لا توجد بيانات كافية لعرض التدفق النقدي الشهري")

def render_general_summary(summary):
    """عرض ملخص عام لجميع الحسابات"""
    st.markdown("### 📊 ملخص عام للحسابات")
    
    if summary is not None and not summary.empty:
        # عرض ملخص لكل نوع حساب
        st.dataframe(
            summary.rename(columns={
                'account_type': 'نوع الحساب',
                'accounts_count': 'عدد الحسابات',
                'total_dues': 'إجمالي المستحقات',
                'total_paid': 'إجمالي المدفوع',
                'total_balance': 'الرصيد'
            }),
            use_container_width=True,
            hide_index=True
        )
    
        # رسم بياني دائري للتوزيع
        st.markdown("---")
        st.markdown("#### 🥧 توزيع الأرصدة")
        
        try:
            fig = px.pie(
                summary,
                values='total_balance',
                names='account_type',
                title='توزيع الأرصدة حسب نوع الحساب'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.warning("لا يمكن عرض الرسم البياني لتوزيع الأرصدة")
    else:
        st.info("لا توجد حسابات مسجلة لعرض ملخص")

# ====================
# الدالة الرئيسية
# ====================
def render():
    st.markdown("## 💼 الحسابات المالية الشاملة")
    
    # التحقق من وجود دوال st.dialog (متاحة في Streamlit 1.33.0+)
    if not hasattr(st, 'dialog'):
        st.error("ميزة النوافذ المنبثقة (st.dialog) غير متاحة. يرجى تحديث Streamlit إلى إصدار 1.33.0 أو أعلى.")
        st.code("pip install --upgrade streamlit")
        return
        
    try:
        all_accounts_summary = crud.get_all_accounts_summary()
    except Exception as e:
        st.error(f"خطأ في جلب ملخص الحسابات: {e}")
        all_accounts_summary = pd.DataFrame()
        
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 حسابات المرضى",
        "👨‍⚕️ حسابات الأطباء",
        "🏪 حسابات الموردين",
        "🏥 حساب العيادة",
        "📊 ملخص عام"
    ])
    
    with tab1:
        render_patient_accounts()
        if 'show_patient_payment_dialog' in st.session_state and st.session_state.show_patient_payment_dialog:
            patient_payment_dialog()
    
    with tab2:
        render_doctor_accounts()
        if 'show_doctor_withdrawal_dialog' in st.session_state and st.session_state.show_doctor_withdrawal_dialog:
            doctor_withdrawal_dialog()
    
    with tab3:
        render_supplier_accounts()
        if 'show_supplier_payment_dialog' in st.session_state and st.session_state.show_supplier_payment_dialog:
            supplier_payment_dialog()
    
    with tab4:
        render_clinic_account()
    
    with tab5:
        render_general_summary(all_accounts_summary)