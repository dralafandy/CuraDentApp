# doctors.py

import streamlit as st
import pandas as pd
from database.crud import crud
from datetime import date

def render():
    """صفحة إدارة الأطباء"""
    st.markdown("## 👨‍⚕️ إدارة الأطباء")
    
    tab1, tab2, tab3 = st.tabs([
        "📋 قائمة الأطباء", 
        "➕ إضافة طبيب جديد",
        "💰 الحسابات المالية"
    ])

    with tab1:
        render_doctor_list()

    with tab2:
        render_add_doctor()
    
    with tab3:
        render_doctor_financial_accounts()

def render_doctor_list():
    """عرض جميع الأطباء"""
    doctors = crud.get_all_doctors()
    if not doctors.empty:
        # إضافة خيار عرض الأرصدة
        show_balances = st.checkbox("عرض الأرصدة المالية للأطباء")
        
        if show_balances:
            # إضافة معلومات مالية لكل طبيب
            financial_data = []
            for _, doctor in doctors.iterrows():
                summary = crud.get_doctor_financial_summary(doctor['id'])
                financial_data.append({
                    'الاسم': doctor['name'],
                    'التخصص': doctor['specialization'],
                    'إجمالي المستحقات': f"{summary['total_earnings']:.2f} ج.م",
                    'المسحوب': f"{summary['total_withdrawn']:.2f} ج.م",
                    'الرصيد الحالي': f"{summary['current_balance']:.2f} ج.م"
                })
            
            financial_df = pd.DataFrame(financial_data)
            st.dataframe(financial_df, use_container_width=True, hide_index=True)
            
            # إحصائيات إجمالية
            total_balance = sum([crud.get_doctor_financial_summary(d['id'])['current_balance'] 
                               for _, d in doctors.iterrows()])
            if total_balance > 0:
                st.info(f"💰 إجمالي المستحقات غير المسحوبة: {total_balance:,.2f} ج.م")
        else:
            st.dataframe(
                doctors[['id', 'name', 'specialization', 'phone', 'email', 'salary', 'commission_rate']],
                use_container_width=True,
                hide_index=True
            )
        
        # تعديل بيانات طبيب
        with st.expander("🛠 تحديث بيانات طبيب"):
            selected_id = st.number_input("رقم الطبيب", min_value=1, step=1)
            doctor = crud.get_doctor_by_id(selected_id)
            if doctor:
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("الاسم", value=doctor[1])
                    spec = st.text_input("التخصص", value=doctor[2])
                    phone = st.text_input("الهاتف", value=doctor[3])
                    email = st.text_input("البريد الإلكتروني", value=doctor[4])
                
                with col2:
                    address = st.text_input("العنوان", value=doctor[5])
                    salary = st.number_input("الراتب", value=float(doctor[7]))
                    commission = st.number_input("نسبة العمولة %", value=float(doctor[8]))

                if st.button("💾 تحديث", type="primary"):
                    try:
                        crud.update_doctor(selected_id, name, spec, phone, email, address, salary, commission)
                        st.success("✅ تم تحديث بيانات الطبيب")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ خطأ: {e}")
                
                if st.button("🗑 حذف الطبيب", type="secondary"):
                    crud.delete_doctor(selected_id)
                    st.success("🚫 تم إلغاء تفعيل الطبيب")
                    st.rerun()
            else:
                st.warning("لم يتم العثور على الطبيب")

    else:
        st.info("لا يوجد أطباء في النظام حالياً.")

def render_add_doctor():
    """إضافة طبيب جديد"""
    st.markdown("### ➕ إضافة طبيب جديد")
    
    with st.form("add_doctor_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("اسم الطبيب *")
            specialization = st.text_input("التخصص *")
            phone = st.text_input("رقم الهاتف")
            email = st.text_input("البريد الإلكتروني")
        
        with col2:
            address = st.text_input("العنوان")
            hire_date = st.date_input("تاريخ التعيين", value=date.today())
            salary = st.number_input("الراتب الأساسي", min_value=0.0, step=100.0)
            commission_rate = st.number_input("نسبة العمولة %", min_value=0.0, max_value=100.0, step=1.0, value=10.0)

        submitted = st.form_submit_button("💾 حفظ الطبيب", type="primary", use_container_width=True)
        
        if submitted:
            if name and specialization:
                try:
                    doctor_id = crud.create_doctor(
                        name, specialization, phone, email, address,
                        hire_date.isoformat(), salary, commission_rate
                    )
                    st.success(f"✅ تم إضافة الطبيب بنجاح! رقم الطبيب: {doctor_id}")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {str(e)}")
            else:
                st.warning("⚠️ يرجى إدخال الاسم والتخصص كحد أدنى.")

def render_doctor_financial_accounts():
    """إدارة الحسابات المالية للأطباء"""
    st.markdown("### 💰 الحسابات المالية للأطباء")
    
    doctors = crud.get_all_doctors()
    if doctors.empty:
        st.info("لا يوجد أطباء")
        return
    
    doctor_id = st.selectbox(
        "اختر الطبيب",
        doctors['id'].tolist(),
        format_func=lambda x: doctors[doctors['id'] == x]['name'].iloc[0],
        key="doc_fin_select"
    )
    
    if st.button("عرض الحساب المالي", key="show_doctor_fin_account"):
        summary = crud.get_doctor_financial_summary(doctor_id)
        
        # عرض البطاقات
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "إجمالي المستحقات",
                f"{summary['total_earnings']:,.2f} ج.م",
                help="من عمولات العلاجات"
            )
        
        with col2:
            st.metric(
                "المسحوب",
                f"{summary['total_withdrawn']:,.2f} ج.م",
                help="المبالغ المسحوبة"
            )
        
        with col3:
            balance = summary['current_balance']
            st.metric(
                "الرصيد الحالي",
                f"{balance:,.2f} ج.م",
                delta=f"+{balance:,.2f}" if balance > 0 else None,
                help="المستحق للطبيب"
            )
        
        # عرض الأرباح الشهرية
        if not summary['monthly_earnings'].empty:
            st.markdown("#### 📊 الأرباح الشهرية")
            try:
                import plotly.express as px
                fig = px.bar(summary['monthly_earnings'], x='month', y='earnings', 
                            title='الأرباح آخر 6 أشهر')
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning("لا يمكن عرض الرسم البياني")
        
        # كشف حساب تفصيلي
        st.markdown("---")
        st.markdown("#### 📋 كشف الحساب")
        
        doctor_name = doctors[doctors['id'] == doctor_id]['name'].iloc[0]
        
        # إنشاء الحساب والتحقق من نجاح العملية
        try:
            account_id = crud.create_or_update_account('doctor', doctor_id, doctor_name)
            
            if not account_id:
                st.error("❌ فشل في إنشاء الحساب المالي للطبيب")
                return
            
            # عرض معرف الحساب للتأكد
            st.caption(f"معرف الحساب: {account_id}")
            
        except Exception as e:
            st.error(f"❌ خطأ في إنشاء الحساب: {str(e)}")
            return
        
        statement = crud.get_account_statement('doctor', doctor_id)
        
        if statement and not statement['transactions'].empty:
            st.dataframe(
                statement['transactions'][['transaction_date', 'transaction_type', 
                                          'amount', 'description', 'payment_method']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("لا توجد حركات مالية مسجلة")
        
        # إضافة سحب
        st.markdown("---")
        with st.expander("💸 تسجيل سحب مستحقات", expanded=True):
            if balance > 0:
                with st.form("withdrawal_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        withdrawal_amount = st.number_input(
                            "المبلغ المسحوب",
                            min_value=0.0,
                            max_value=float(balance),
                            step=100.0,
                            key="doc_withdrawal_amount"
                        )
                    
                    with col2:
                        withdrawal_method = st.selectbox(
                            "طريقة السحب",
                            ["نقدي", "تحويل بنكي", "شيك"],
                            key="doc_withdrawal_method"
                        )
                    
                    notes = st.text_area("ملاحظات السحب", key="doc_withdrawal_notes")
                    
                    submitted = st.form_submit_button("💾 تسجيل السحب", type="primary", use_container_width=True)
                    
                    if submitted:
                        if withdrawal_amount > 0:
                            try:
                                # تسجيل الحركة المالية
                                crud.add_financial_transaction(
                                    account_id, 
                                    'withdrawal', 
                                    withdrawal_amount,
                                    f"سحب مستحقات د. {doctor_name}",
                                    'withdrawal', 
                                    None, 
                                    withdrawal_method, 
                                    notes
                                )
                                
                                # إنشاء سند صرف
                                voucher_no = crud.create_voucher(
                                    'payment', 
                                    account_id, 
                                    withdrawal_amount,
                                    withdrawal_method, 
                                    f"سحب مستحقات د. {doctor_name}",
                                    "النظام", 
                                    notes
                                )
                                
                                st.success(f"✅ تم تسجيل السحب بنجاح!")
                                st.info(f"📄 سند صرف رقم: {voucher_no}")
                                st.balloons()
                                
                                # الانتظار قليلاً ثم إعادة تحميل الصفحة
                                import time
                                time.sleep(2)
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ خطأ في تسجيل السحب: {str(e)}")
                                st.exception(e)  # عرض التفاصيل الكاملة للخطأ
                        else:
                            st.warning("⚠️ يرجى إدخال مبلغ أكبر من صفر")
            else:
                st.info("💡 لا توجد مستحقات متاحة للسحب حالياً")
                st.caption(f"الرصيد الحالي: {balance:.2f} ج.م")