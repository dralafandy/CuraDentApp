# patients.py

import streamlit as st
import pandas as pd
from database.crud import crud
from datetime import date

def render():
    """صفحة إدارة المرضى"""
    st.markdown("## 👥 إدارة المرضى")
    
    # إضافة تبويب الحسابات المالية
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 قائمة المرضى", 
        "➕ مريض جديد", 
        "🔍 بحث متقدم",
        "📊 تقرير مريض",
        "💰 الحسابات المالية"
    ])
    
    with tab1:
        render_patient_list()
    with tab2:
        render_add_patient()
    with tab3:
        render_search_patient()
    with tab4:
        render_patient_report()
    with tab5:
        render_patient_financial_accounts()

def render_patient_list():
    """عرض جميع المرضى"""
    patients = crud.get_all_patients()
    if not patients.empty:
        # إضافة فلترة
        col1, col2 = st.columns(2)
        with col1:
            show_financial = st.checkbox("عرض الأرصدة المالية", key="show_fin_list")
        with col2:
            filter_debt = st.checkbox("عرض المدينين فقط", key="filter_debt")
        
        if show_financial:
            # إضافة معلومات مالية لكل مريض
            financial_data = []
            for _, patient in patients.iterrows():
                summary = crud.get_patient_financial_summary(patient['id'])
                financial_data.append({
                    'الاسم': patient['name'],
                    'الهاتف': patient['phone'],
                    'إجمالي العلاجات': f"{summary['total_treatments_cost']:.2f} ج.م",
                    'المدفوع': f"{summary['total_paid']:.2f} ج.م",
                    'المتبقي': f"{summary['outstanding_balance']:.2f} ج.م",
                    'الحالة': summary['payment_status']
                })
            
            financial_df = pd.DataFrame(financial_data)
            
            if filter_debt:
                # فلترة المدينين فقط
                financial_df = financial_df[financial_df['المتبقي'] != '0.00 ج.م']
            
            st.dataframe(financial_df, use_container_width=True, hide_index=True)
            
            # إحصائيات إجمالية
            total_debt = sum([crud.get_patient_financial_summary(p['id'])['outstanding_balance'] 
                            for _, p in patients.iterrows()])
            if total_debt > 0:
                st.error(f"🔴 إجمالي المديونيات: {total_debt:,.2f} ج.م")
        else:
            # عرض البيانات الأساسية
            st.dataframe(
                patients[['id', 'name', 'phone', 'email', 'gender', 'date_of_birth']],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("لا توجد بيانات مرضى حالياً.")

def render_add_patient():
    """إضافة مريض جديد"""
    st.markdown("### ➕ إضافة مريض جديد")
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("الاسم الكامل *")
            phone = st.text_input("رقم الهاتف *")
            email = st.text_input("البريد الإلكتروني")
            gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
            date_of_birth = st.date_input("تاريخ الميلاد", min_value=date(1900, 1, 1), max_value=date.today())
        
        with col2:
            address = st.text_input("العنوان")
            emergency_contact = st.text_input("جهة اتصال للطوارئ")
            blood_type = st.selectbox("فصيلة الدم", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            allergies = st.text_input("الحساسية إن وجدت")
            medical_history = st.text_area("التاريخ الطبي")
        
        notes = st.text_area("ملاحظات إضافية")
        
        submitted = st.form_submit_button("💾 حفظ المريض", type="primary", use_container_width=True)
        
        if submitted:
            if name and phone:
                try:
                    patient_id = crud.create_patient(
                        name=name, phone=phone, email=email, address=address,
                        date_of_birth=date_of_birth.isoformat(), gender=gender,
                        medical_history=medical_history, emergency_contact=emergency_contact,
                        blood_type=blood_type, allergies=allergies, notes=notes
                    )
                    st.success(f"✅ تم حفظ بيانات المريض بنجاح! رقم الملف: {patient_id}")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {str(e)}")
            else:
                st.warning("⚠️ يرجى ملء الحقول المطلوبة (*)")

def render_search_patient():
    """البحث في المرضى"""
    st.markdown("### 🔍 البحث عن مريض")
    
    search_term = st.text_input("أدخل الاسم أو رقم الهاتف أو البريد الإلكتروني للبحث")

    if search_term:
        results = crud.search_patients(search_term)
        if not results.empty:
            st.dataframe(
                results[['id', 'name', 'phone', 'email', 'gender', 'date_of_birth']],
                use_container_width=True,
                hide_index=True
            )
            
            # عرض الحساب المالي للنتائج
            if st.checkbox("عرض الحسابات المالية للنتائج"):
                for _, patient in results.iterrows():
                    with st.expander(f"💰 حساب {patient['name']}"):
                        summary = crud.get_patient_financial_summary(patient['id'])
                        col1, col2, col3 = st.columns(3)
                        col1.metric("إجمالي العلاجات", f"{summary['total_treatments_cost']:.2f} ج.م")
                        col2.metric("المدفوع", f"{summary['total_paid']:.2f} ج.م")
                        col3.metric("المتبقي", f"{summary['outstanding_balance']:.2f} ج.م")
        else:
            st.info("🔍 لم يتم العثور على نتائج.")

def render_patient_report():
    """عرض تقرير مفصل لمريض"""
    st.markdown("### 📊 تقرير مريض شامل")
    
    patients = crud.get_all_patients()
    if patients.empty:
        st.info("لا يوجد مرضى لعرض تقاريرهم.")
        return

    patient_id = st.selectbox(
        "اختر المريض لعرض تقريره",
        patients['id'].tolist(),
        format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0]
    )

    if st.button("📈 عرض التقرير", type="primary", use_container_width=True):
        with st.spinner("جاري إعداد التقرير..."):
            report = crud.get_patient_detailed_report(patient_id)

            if not report or not report.get('patient'):
                st.warning("لا توجد بيانات كافية لعرض تقرير هذا المريض.")
                return

            # معلومات المريض الأساسية
            patient_info = report['patient']
            st.markdown(f"#### 👤 {patient_info.get('name', 'بيانات المريض')}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("الهاتف", patient_info.get('phone', '-'))
            col2.metric("الجنس", patient_info.get('gender', '-'))
            col3.metric("فصيلة الدم", patient_info.get('blood_type', '-'))
            col4.metric("تاريخ الميلاد", patient_info.get('date_of_birth', '-'))

            st.markdown("---")
            
            # إحصائيات الزيارات
            visits_stats = report.get('visits_stats', {})
            st.markdown("#### 📅 إحصائيات الزيارات")
            col1, col2, col3 = st.columns(3)
            col1.metric("إجمالي الزيارات", visits_stats.get('total_visits', 0))
            col2.metric("الزيارات المكتملة", visits_stats.get('completed_visits', 0))
            col3.metric("الزيارات الملغية", visits_stats.get('cancelled_visits', 0))

            # الملخص المالي
            st.markdown("#### 💰 الملخص المالي")
            col1, col2, col3 = st.columns(3)
            col1.metric("التكلفة الإجمالية", f"{report.get('total_cost', 0):,.2f} ج.م")
            col2.metric("إجمالي المدفوعات", f"{report.get('total_paid', 0):,.2f} ج.م")
            col3.metric("المبلغ المتبقي", f"{report.get('outstanding', 0):,.2f} ج.م")

            # المواعيد
            if not report['appointments'].empty:
                with st.expander("📅 عرض سجل المواعيد التفصيلي"):
                    st.dataframe(
                        report['appointments'][['appointment_date', 'doctor_name', 'treatment_name', 'status', 'total_cost']],
                        use_container_width=True, hide_index=True
                    )
            
            # المدفوعات
            if not report['payments'].empty:
                with st.expander("💳 عرض سجل المدفوعات"):
                    st.dataframe(
                        report['payments'][['payment_date', 'amount', 'payment_method', 'status']],
                        use_container_width=True, hide_index=True
                    )

def render_patient_financial_accounts():
    """إدارة الحسابات المالية للمرضى"""
    st.markdown("### 💰 الحسابات المالية للمرضى")
    
    patients = crud.get_all_patients()
    if patients.empty:
        st.info("لا يوجد مرضى")
        return
    
    # اختيار المريض
    patient_id = st.selectbox(
        "اختر المريض",
        patients['id'].tolist(),
        format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0],
        key="fin_patient_select"
    )
    
    if st.button("عرض الحساب المالي", key="show_patient_fin_account"):
        # الملخص المالي
        summary = crud.get_patient_financial_summary(patient_id)
        
        # عرض البطاقات
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "إجمالي العلاجات",
                f"{summary['total_treatments_cost']:,.2f} ج.م"
            )
        
        with col2:
            st.metric(
                "المدفوع",
                f"{summary['total_paid']:,.2f} ج.م"
            )
        
        with col3:
            outstanding = summary['outstanding_balance']
            st.metric(
                "المتبقي",
                f"{outstanding:,.2f} ج.م",
                delta=f"-{outstanding:,.2f}" if outstanding > 0 else "✅"
            )
        
        with col4:
            st.metric(
                "الحالة",
                summary['payment_status']
            )
        
        # كشف حساب تفصيلي
        st.markdown("---")
        st.markdown("#### 📋 كشف الحساب التفصيلي")
        
        # إنشاء حساب للمريض إذا لم يكن موجود
        patient_name = patients[patients['id'] == patient_id]['name'].iloc[0]
        account_id = crud.create_or_update_account('patient', patient_id, patient_name)
        
        # عرض الحركات
        statement = crud.get_account_statement('patient', patient_id)
        
        if statement and not statement['transactions'].empty:
            st.dataframe(
                statement['transactions'][['transaction_date', 'transaction_type', 
                                          'amount', 'description', 'payment_method']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("لا توجد حركات مالية")
        
        # إضافة دفعة جديدة
        st.markdown("---")
        with st.expander("➕ إضافة دفعة جديدة"):
            col1, col2 = st.columns(2)
            
            with col1:
                payment_amount = st.number_input("المبلغ", min_value=0.0, step=10.0, key="pat_pay_amount")
                payment_method = st.selectbox("طريقة الدفع", 
                    ["نقدي", "بطاقة ائتمان", "تحويل بنكي", "شيك"], key="pat_pay_method")
            
            with col2:
                payment_date = st.date_input("التاريخ", value=date.today(), key="pat_pay_date")
                notes = st.text_area("ملاحظات", key="pat_pay_notes")
            
            if st.button("💾 حفظ الدفعة", type="primary", key="save_pat_payment"):
                if payment_amount > 0:
                    # إضافة الدفعة
                    crud.add_financial_transaction(
                        account_id, 'payment', payment_amount,
                        f"دفعة من المريض {patient_name}",
                        'payment', None, payment_method, notes
                    )
                    
                    # إنشاء سند قبض
                    voucher_no = crud.create_voucher(
                        'receipt', account_id, payment_amount,
                        payment_method, f"دفعة من {patient_name}",
                        "النظام", notes
                    )
                    
                    st.success(f"✅ تم حفظ الدفعة - سند قبض رقم: {voucher_no}")
                    st.rerun()
                else:
                    st.warning("⚠️ يرجى إدخال مبلغ صحيح")