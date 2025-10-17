# database/crud.py

import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
from .models import db

class CRUDOperations:
    def __init__(self):
        self.db = db
    
    # ========== عمليات الأطباء ==========
    def create_doctor(self, name, specialization, phone, email, address, hire_date, salary, commission_rate=0.0):
        """إضافة طبيب جديد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO doctors (name, specialization, phone, email, address, hire_date, salary, commission_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, specialization, phone, email, address, hire_date, salary, commission_rate))
            
            doctor_id = cursor.lastrowid
            
            # إنشاء حساب مالي للطبيب
            self.create_or_update_account('doctor', doctor_id, name)
            
            # تسجيل النشاط
            self.log_activity(conn, "إضافة طبيب", "doctors", doctor_id, f"تم إضافة طبيب: {name}")
            
            conn.commit()
            return doctor_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_all_doctors(self, active_only=True):
        """الحصول على جميع الأطباء"""
        conn = self.db.get_connection()
        query = "SELECT * FROM doctors"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_doctor_by_id(self, doctor_id):
        """الحصول على طبيب بواسطة ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_doctor(self, doctor_id, name, specialization, phone, email, address, salary, commission_rate):
        """تحديث بيانات طبيب"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE doctors 
            SET name=?, specialization=?, phone=?, email=?, address=?, salary=?, commission_rate=?
            WHERE id=?
        ''', (name, specialization, phone, email, address, salary, commission_rate, doctor_id))
        self.log_activity(conn, "تحديث طبيب", "doctors", doctor_id, f"تم تحديث بيانات الطبيب: {name}")
        conn.commit()
        conn.close()
    
    def delete_doctor(self, doctor_id):
        """حذف طبيب (soft delete)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE doctors SET is_active = 0 WHERE id = ?", (doctor_id,))
        self.log_activity(conn, "حذف طبيب", "doctors", doctor_id, f"تم إلغاء تفعيل الطبيب")
        conn.commit()
        conn.close()
    
    # ========== عمليات المرضى ==========
    def create_patient(self, name, phone, email, address, date_of_birth, gender, medical_history="", 
                      emergency_contact="", blood_type="", allergies="", notes=""):
        """إضافة مريض جديد مع إنشاء حساب مالي"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO patients (name, phone, email, address, date_of_birth, gender, medical_history, 
                                    emergency_contact, blood_type, allergies, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, address, date_of_birth, gender, medical_history, 
                  emergency_contact, blood_type, allergies, notes))
            
            patient_id = cursor.lastrowid
            
            account_id = self.create_or_update_account('patient', patient_id, name)
            
            if account_id:
                self.log_activity(conn, "إضافة مريض وحساب", "patients", patient_id, 
                                 f"تم إضافة مريض: {name} (حساب مالي: {account_id})")
            
            conn.commit()
            return patient_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_all_patients(self, active_only=True):
        """الحصول على جميع المرضى"""
        conn = self.db.get_connection()
        query = "SELECT * FROM patients"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_patient_by_id(self, patient_id):
        """الحصول على مريض بواسطة ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_patient(self, patient_id, name, phone, email, address, date_of_birth, gender, 
                      medical_history, emergency_contact, blood_type="", allergies="", notes=""):
        """تحديث بيانات مريض"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE patients 
            SET name=?, phone=?, email=?, address=?, date_of_birth=?, gender=?, 
                medical_history=?, emergency_contact=?, blood_type=?, allergies=?, notes=?
            WHERE id=?
        ''', (name, phone, email, address, date_of_birth, gender, medical_history, 
              emergency_contact, blood_type, allergies, notes, patient_id))
        self.log_activity(conn, "تحديث مريض", "patients", patient_id, f"تم تحديث بيانات المريض: {name}")
        conn.commit()
        conn.close()
    
    def delete_patient(self, patient_id):
        """حذف مريض (soft delete)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE patients SET is_active = 0 WHERE id = ?", (patient_id,))
        self.log_activity(conn, "حذف مريض", "patients", patient_id, f"تم إلغاء تفعيل المريض")
        conn.commit()
        conn.close()
    
    def search_patients(self, search_term):
        """البحث عن مرضى"""
        conn = self.db.get_connection()
        query = '''
            SELECT * FROM patients 
            WHERE is_active = 1 
            AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)
            ORDER BY name
        '''
        search_pattern = f"%{search_term}%"
        df = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern, search_pattern))
        conn.close()
        return df
    
    # ========== عمليات العلاجات ==========
    def create_treatment(self, name, description, base_price, duration_minutes, category, 
                        doctor_percentage=50.0, clinic_percentage=50.0):
        """إضافة علاج جديد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO treatments (name, description, base_price, duration_minutes, category, 
                                  doctor_percentage, clinic_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, base_price, duration_minutes, category, doctor_percentage, clinic_percentage))
        treatment_id = cursor.lastrowid
        self.log_activity(conn, "إضافة علاج", "treatments", treatment_id, f"تم إضافة علاج: {name}")
        conn.commit()
        conn.close()
        return treatment_id
    
    def get_all_treatments(self, active_only=True):
        """الحصول على جميع العلاجات"""
        conn = self.db.get_connection()
        query = "SELECT * FROM treatments"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_treatment_by_id(self, treatment_id):
        """الحصول على علاج بواسطة ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM treatments WHERE id = ?", (treatment_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_treatment(self, treatment_id, name, description, base_price, duration_minutes, 
                        category, doctor_percentage=50.0, clinic_percentage=50.0):
        """تحديث علاج"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE treatments 
            SET name=?, description=?, base_price=?, duration_minutes=?, category=?, 
                doctor_percentage=?, clinic_percentage=?
            WHERE id=?
        ''', (name, description, base_price, duration_minutes, category, 
              doctor_percentage, clinic_percentage, treatment_id))
        self.log_activity(conn, "تحديث علاج", "treatments", treatment_id, f"تم تحديث علاج: {name}")
        conn.commit()
        conn.close()
    
    def delete_treatment(self, treatment_id):
        """حذف علاج (soft delete)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE treatments SET is_active = 0 WHERE id = ?", (treatment_id,))
        self.log_activity(conn, "حذف علاج", "treatments", treatment_id, f"تم إلغاء تفعيل العلاج")
        conn.commit()
        conn.close()
    
    # ========== عمليات المواعيد ==========
    def create_appointment(self, patient_id, doctor_id, treatment_id, appointment_date, 
                          appointment_time, notes="", total_cost=0.0):
        """إضافة موعد جديد مع تسجيل الدين على المريض"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, 
                                        appointment_time, notes, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, notes, total_cost))
            appointment_id = cursor.lastrowid
            conn.commit()
            
            if total_cost > 0:
                patient_name = pd.read_sql_query("SELECT name FROM patients WHERE id = ?", conn, params=(patient_id,)).iloc[0]['name']
                account_id = self.create_or_update_account('patient', patient_id, patient_name)
                if account_id:
                    self.add_financial_transaction(
                        account_id, 'debit', total_cost,
                        f"تكلفة علاج (موعد رقم {appointment_id})",
                        'appointment', appointment_id
                    )
            
            self.log_activity(conn, "إضافة موعد", "appointments", appointment_id, f"موعد لـ {patient_name} بتكلفة {total_cost}")
            return appointment_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_all_appointments(self):
        """الحصول على جميع المواعيد"""
        conn = self.db.get_connection()
        query = '''
            SELECT a.id, p.name as patient_name, d.name as doctor_name, t.name as treatment_name,
                   a.appointment_date, a.appointment_time, a.status, a.total_cost
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_appointments_by_date(self, target_date):
        """الحصول على مواعيد يوم محدد"""
        conn = self.db.get_connection()
        query = '''
            SELECT a.id, p.name as patient_name, d.name as doctor_name, t.name as treatment_name,
                   a.appointment_time, a.status
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
        '''
        df = pd.read_sql_query(query, conn, params=(target_date,))
        conn.close()
        return df
    
    def update_appointment_status(self, appointment_id, status):
        """تحديث حالة الموعد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
        self.log_activity(conn, "تحديث موعد", "appointments", appointment_id, f"تم تغيير الحالة إلى: {status}")
        conn.commit()
        conn.close()
    
    # ========== عمليات المدفوعات ==========
    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date, notes=""):
        """إضافة دفعة جديدة مع تكاملها مع نظام الحسابات"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            doctor_share, clinic_share, doctor_percentage, clinic_percentage, doctor_id = 0.0, 0.0, 0.0, 0.0, None
            
            if appointment_id:
                cursor.execute('''
                    SELECT t.doctor_percentage, t.clinic_percentage, a.doctor_id
                    FROM appointments a
                    LEFT JOIN treatments t ON a.treatment_id = t.id
                    WHERE a.id = ?
                ''', (appointment_id,))
                result = cursor.fetchone()
                
                if result and result[0] is not None:
                    doctor_percentage, clinic_percentage, doctor_id = result
                    doctor_share = (amount * doctor_percentage) / 100.0
                    clinic_share = amount - doctor_share
                else:
                    cursor.execute("SELECT doctor_id FROM appointments WHERE id = ?", (appointment_id,))
                    doc_res = cursor.fetchone()
                    if doc_res:
                        doctor_id = doc_res[0]
                    doctor_share = amount * 0.5
                    clinic_share = amount * 0.5
            else:
                clinic_share = amount
                
            cursor.execute('''
                INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date, notes, doctor_share, clinic_share, doctor_percentage, clinic_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (appointment_id, patient_id, amount, payment_method, payment_date, notes, doctor_share, clinic_share, doctor_percentage, clinic_percentage))
            payment_id = cursor.lastrowid
            conn.commit()
            
            patient_name = pd.read_sql_query("SELECT name FROM patients WHERE id = ?", conn, params=(patient_id,)).iloc[0]['name']
            patient_account_id = self.create_or_update_account('patient', patient_id, patient_name)
            if patient_account_id:
                self.add_financial_transaction(
                    patient_account_id, 'payment', amount,
                    f"دفعة لعلاج (موعد رقم {appointment_id or 'N/A'})", 'payment', payment_id, payment_method, notes
                )
            
            if doctor_id and doctor_share > 0:
                doctor_name = pd.read_sql_query("SELECT name FROM doctors WHERE id = ?", conn, params=(doctor_id,)).iloc[0]['name']
                doctor_account_id = self.create_or_update_account('doctor', doctor_id, doctor_name)
                if doctor_account_id:
                    self.add_financial_transaction(
                        doctor_account_id, 'credit', doctor_share,
                        f"عمولة من دفعة (رقم {payment_id})", 'payment', payment_id, None, f"حصة من دفعة {amount}"
                    )
            
            clinic_account_id = self.create_or_update_account('clinic', 1, 'حساب العيادة العام')
            if clinic_account_id:
                self.add_financial_transaction(
                    clinic_account_id, 'credit', clinic_share,
                    f"إيراد من دفعة (رقم {payment_id})", 'payment', payment_id, None, f"حصة من دفعة {amount}"
                )
            
            self.log_activity(conn, "إضافة دفعة متكاملة", "payments", payment_id, f"دفعة {amount} لـ {patient_name}")
            return payment_id

        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
            
    def get_all_payments(self):
        """الحصول على جميع المدفوعات"""
        conn = self.db.get_connection()
        query = '''
            SELECT pay.id, p.name as patient_name, pay.amount, pay.doctor_share, pay.clinic_share,
                   pay.payment_method, pay.payment_date, pay.status, pay.appointment_id
            FROM payments pay
            LEFT JOIN patients p ON pay.patient_id = p.id
            ORDER BY pay.payment_date DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    # ========== نظام الحسابات المالي الشامل ==========
    def create_or_update_account(self, account_type, holder_id, holder_name):
        """إنشاء أو تحديث حساب مالي"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''SELECT id FROM accounts WHERE account_type = ? AND account_holder_id = ?''', (account_type, holder_id))
            existing = cursor.fetchone()
            if existing:
                return existing[0]
            else:
                cursor.execute('''
                    INSERT INTO accounts (account_type, account_holder_id, account_holder_name) VALUES (?, ?, ?)
                ''', (account_type, holder_id, holder_name))
                account_id = cursor.lastrowid
                conn.commit()
                return account_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_financial_transaction(self, account_id, transaction_type, amount, 
                                 description, reference_type=None, reference_id=None,
                                 payment_method=None, notes=None):
        """إضافة حركة مالية مع تحديث رصيد الحساب"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO financial_transactions 
                (account_id, transaction_type, amount, description, reference_type, 
                 reference_id, transaction_date, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?, date('now'), ?, ?)
            ''', (account_id, transaction_type, amount, description, reference_type, reference_id, payment_method, notes))
            
            cursor.execute("SELECT account_type, balance, total_dues, total_paid FROM accounts WHERE id = ?", (account_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"الحساب رقم {account_id} غير موجود")
            
            account_type, current_balance, total_dues, total_paid = result
            
            if account_type == 'patient':
                if transaction_type == 'payment':
                    new_balance = current_balance + amount
                    new_total_paid = total_paid + amount
                    cursor.execute('UPDATE accounts SET total_paid = ?, balance = ? WHERE id = ?', (new_total_paid, new_balance, account_id))
                elif transaction_type == 'debit':
                    new_balance = current_balance - amount
                    new_total_dues = total_dues + amount
                    cursor.execute('UPDATE accounts SET total_dues = ?, balance = ? WHERE id = ?', (new_total_dues, new_balance, account_id))
            
            elif account_type == 'doctor':
                if transaction_type == 'credit':
                    new_balance = current_balance + amount
                    cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
                elif transaction_type == 'withdrawal':
                    new_balance = current_balance - amount
                    cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_account_statement(self, account_type, holder_id):
        """الحصول على كشف حساب"""
        conn = self.db.get_connection()
        try:
            account_id_query = "SELECT id FROM accounts WHERE account_type = ? AND account_holder_id = ?"
            df_id = pd.read_sql_query(account_id_query, conn, params=(account_type, holder_id))
            if df_id.empty:
                return None
            
            account_id = df_id.iloc[0]['id']
            transactions_query = "SELECT * FROM financial_transactions WHERE account_id = ? ORDER BY transaction_date DESC"
            transactions = pd.read_sql_query(transactions_query, conn, params=(account_id,))
            
            account_info_query = "SELECT * FROM accounts WHERE id = ?"
            account_info = pd.read_sql_query(account_info_query, conn, params=(account_id,)).iloc[0].to_dict()

            return {'account': account_info, 'transactions': transactions}
        finally:
            conn.close()
    
    def get_patient_financial_summary(self, patient_id):
        """ملخص مالي للمريض"""
        conn = self.db.get_connection()
        try:
            treatments_query = "SELECT COALESCE(SUM(total_cost), 0) as total_cost FROM appointments WHERE patient_id = ? AND status IN ('مكتمل', 'مؤكد')"
            total_treatments = pd.read_sql_query(treatments_query, conn, params=(patient_id,)).iloc[0]['total_cost']
            
            payments_query = "SELECT COALESCE(SUM(amount), 0) as total_paid FROM payments WHERE patient_id = ? AND status = 'مكتمل'"
            total_paid = pd.read_sql_query(payments_query, conn, params=(patient_id,)).iloc[0]['total_paid']
            
            outstanding = total_treatments - total_paid
            
            return {
                'total_treatments_cost': total_treatments,
                'total_paid': total_paid,
                'outstanding_balance': outstanding,
                'payment_status': 'مدفوع بالكامل' if outstanding <= 0 else f'متبقي {outstanding:.2f} ج.م'
            }
        finally:
            conn.close()
    
    def get_doctor_financial_summary(self, doctor_id):
        """ملخص مالي للطبيب"""
        conn = self.db.get_connection()
        try:
            earnings_query = '''
                SELECT COALESCE(SUM(p.doctor_share), 0) as total_earnings
                FROM payments p JOIN appointments a ON p.appointment_id = a.id
                WHERE a.doctor_id = ? AND p.status = 'مكتمل'
            '''
            total_earnings = pd.read_sql_query(earnings_query, conn, params=(doctor_id,)).iloc[0]['total_earnings']
            
            withdrawals_query = '''
                SELECT COALESCE(SUM(amount), 0) as total_withdrawn
                FROM financial_transactions ft JOIN accounts a ON ft.account_id = a.id
                WHERE a.account_type = 'doctor' AND a.account_holder_id = ? AND ft.transaction_type = 'withdrawal'
            '''
            total_withdrawn = pd.read_sql_query(withdrawals_query, conn, params=(doctor_id,)).iloc[0]['total_withdrawn']
            
            current_balance = total_earnings - total_withdrawn
            
            monthly_earnings_query = '''
                SELECT strftime('%Y-%m', p.payment_date) as month, SUM(p.doctor_share) as earnings
                FROM payments p JOIN appointments a ON p.appointment_id = a.id
                WHERE a.doctor_id = ? AND p.status = 'مكتمل'
                GROUP BY month ORDER BY month DESC LIMIT 6
            '''
            monthly_earnings = pd.read_sql_query(monthly_earnings_query, conn, params=(doctor_id,))
            
            return {
                'total_earnings': total_earnings,
                'total_withdrawn': total_withdrawn,
                'current_balance': current_balance,
                'monthly_earnings': monthly_earnings
            }
        finally:
            conn.close()

    def get_all_accounts_summary(self):
        """ملخص جميع الحسابات"""
        conn = self.db.get_connection()
        try:
            return pd.read_sql_query("SELECT * FROM accounts", conn)
        finally:
            conn.close()
            
    def get_monthly_comparison(self, months=1):
        """مقارنة شهرية"""
        conn = self.db.get_connection()
        try:
            if months == 1:
                today = date.today()
                current_month_start = today.replace(day=1).isoformat()
                current_month_end = today.isoformat()
                last_month_end = (today.replace(day=1) - timedelta(days=1))
                last_month_start = last_month_end.replace(day=1).isoformat()
                last_month_end_iso = last_month_end.isoformat()
                
                current_revenue = pd.read_sql_query("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE payment_date BETWEEN ? AND ?", conn, params=(current_month_start, current_month_end)).iloc[0]['total']
                last_revenue = pd.read_sql_query("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE payment_date BETWEEN ? AND ?", conn, params=(last_month_start, last_month_end_iso)).iloc[0]['total']
                
                # ... (باقي الحسابات للمقارنة السريعة)
                
                return {
                    'current_revenue': current_revenue,
                    'last_revenue': last_revenue,
                    # ...
                }
            
            # ... (باقي الكود للحصول على DataFrame)
        finally:
            conn.close()

    # ... باقي الدوال ...

# إنشاء مثيل
crud = CRUDOperations()