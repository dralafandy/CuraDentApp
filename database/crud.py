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
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO doctors (name, specialization, phone, email, address, hire_date, salary, commission_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, specialization, phone, email, address, hire_date, salary, commission_rate))
            doctor_id = cursor.lastrowid
            self.create_or_update_account('doctor', doctor_id, name)
            self.log_activity(conn, "إضافة طبيب", "doctors", doctor_id, f"تم إضافة طبيب: {name}")
            conn.commit()
            return doctor_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_all_doctors(self, active_only=True):
        conn = self.db.get_connection()
        query = "SELECT * FROM doctors"
        if active_only: query += " WHERE is_active = 1"
        df = pd.read_sql_query(query + " ORDER BY name", conn)
        conn.close()
        return df
    
    def get_doctor_by_id(self, doctor_id):
        conn = self.db.get_connection()
        result = pd.read_sql_query("SELECT * FROM doctors WHERE id = ?", conn, params=(doctor_id,))
        conn.close()
        return result.iloc[0] if not result.empty else None
    
    def update_doctor(self, doctor_id, name, specialization, phone, email, address, salary, commission_rate):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE doctors SET name=?, specialization=?, phone=?, email=?, address=?, salary=?, commission_rate=? WHERE id=?
        ''', (name, specialization, phone, email, address, salary, commission_rate, doctor_id))
        self.log_activity(conn, "تحديث طبيب", "doctors", doctor_id, f"تم تحديث بيانات الطبيب: {name}")
        conn.commit()
        conn.close()
    
    def delete_doctor(self, doctor_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE doctors SET is_active = 0 WHERE id = ?", (doctor_id,))
        self.log_activity(conn, "حذف طبيب", "doctors", doctor_id, "تم إلغاء تفعيل الطبيب")
        conn.commit()
        conn.close()
    
    # ========== عمليات المرضى ==========
    def create_patient(self, name, phone, email, address, date_of_birth, gender, **kwargs):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO patients (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact, blood_type, allergies, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, address, date_of_birth, gender, kwargs.get('medical_history'), kwargs.get('emergency_contact'), kwargs.get('blood_type'), kwargs.get('allergies'), kwargs.get('notes')))
            patient_id = cursor.lastrowid
            self.create_or_update_account('patient', patient_id, name)
            self.log_activity(conn, "إضافة مريض", "patients", patient_id, f"تم إضافة مريض: {name}")
            conn.commit()
            return patient_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_all_patients(self, active_only=True):
        conn = self.db.get_connection()
        query = "SELECT * FROM patients"
        if active_only: query += " WHERE is_active = 1"
        df = pd.read_sql_query(query + " ORDER BY name", conn)
        conn.close()
        return df
    
    def get_patient_by_id(self, patient_id):
        conn = self.db.get_connection()
        result = pd.read_sql_query("SELECT * FROM patients WHERE id = ?", conn, params=(patient_id,))
        conn.close()
        return result.iloc[0] if not result.empty else None
    
    def search_patients(self, search_term):
        conn = self.db.get_connection()
        search_pattern = f"%{search_term}%"
        df = pd.read_sql_query("SELECT * FROM patients WHERE is_active = 1 AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)", conn, params=(search_pattern, search_pattern, search_pattern))
        conn.close()
        return df
    
    # ========== عمليات العلاجات ==========
    def create_treatment(self, name, description, base_price, duration_minutes, category, doctor_percentage=50.0, clinic_percentage=50.0):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO treatments (name, description, base_price, duration_minutes, category, doctor_percentage, clinic_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, base_price, duration_minutes, category, doctor_percentage, clinic_percentage))
        treatment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return treatment_id
    
    def get_all_treatments(self, active_only=True):
        conn = self.db.get_connection()
        query = "SELECT * FROM treatments"
        if active_only: query += " WHERE is_active = 1"
        df = pd.read_sql_query(query + " ORDER BY name", conn)
        conn.close()
        return df
    
    def get_treatment_by_id(self, treatment_id):
        conn = self.db.get_connection()
        result = pd.read_sql_query("SELECT * FROM treatments WHERE id = ?", conn, params=(treatment_id,))
        conn.close()
        return result.iloc[0] if not result.empty else None
    
    # ========== عمليات المواعيد ==========
    def create_appointment(self, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, notes="", total_cost=0.0):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, notes, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, notes, total_cost))
            appointment_id = cursor.lastrowid
            conn.commit()
            
            if total_cost > 0:
                patient_name = self.get_patient_by_id(patient_id)['name']
                account_id = self.create_or_update_account('patient', patient_id, patient_name)
                if account_id:
                    self.add_financial_transaction(account_id, 'debit', total_cost, f"تكلفة موعد رقم {appointment_id}", 'appointment', appointment_id)
            return appointment_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_all_appointments(self):
        conn = self.db.get_connection()
        query = "SELECT a.*, p.name as patient_name, d.name as doctor_name FROM appointments a LEFT JOIN patients p ON a.patient_id=p.id LEFT JOIN doctors d ON a.doctor_id=d.id ORDER BY a.appointment_date DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    # ========== عمليات المدفوعات ==========
    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date, notes=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            doctor_share, clinic_share, doctor_id = 0.0, amount, None
            
            if appointment_id:
                app = pd.read_sql_query("SELECT * FROM appointments WHERE id = ?", conn, params=(appointment_id,)).iloc[0]
                treatment = self.get_treatment_by_id(app['treatment_id'])
                if treatment is not None:
                    doctor_id = app['doctor_id']
                    doctor_share = (amount * treatment['doctor_percentage']) / 100.0
                    clinic_share = amount - doctor_share
                
            cursor.execute('''
                INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date, notes, doctor_share, clinic_share)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (appointment_id, patient_id, amount, payment_method, payment_date, notes, doctor_share, clinic_share))
            payment_id = cursor.lastrowid
            conn.commit()

            patient_name = self.get_patient_by_id(patient_id)['name']
            patient_account_id = self.create_or_update_account('patient', patient_id, patient_name)
            if patient_account_id:
                self.add_financial_transaction(patient_account_id, 'payment', amount, f"دفعة (ID: {payment_id})", 'payment', payment_id)

            if doctor_id and doctor_share > 0:
                doctor_name = self.get_doctor_by_id(doctor_id)['name']
                doctor_account_id = self.create_or_update_account('doctor', doctor_id, doctor_name)
                if doctor_account_id:
                    self.add_financial_transaction(doctor_account_id, 'credit', doctor_share, f"عمولة من دفعة (ID: {payment_id})", 'payment', payment_id)
            
            return payment_id
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    # ========== نظام الحسابات المالي الشامل ==========
    def create_or_update_account(self, account_type, holder_id, holder_name):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM accounts WHERE account_type = ? AND account_holder_id = ?", (account_type, holder_id))
            existing = cursor.fetchone()
            if existing:
                return existing[0]
            else:
                cursor.execute("INSERT INTO accounts (account_type, account_holder_id, account_holder_name) VALUES (?, ?, ?)", (account_type, holder_id, holder_name))
                account_id = cursor.lastrowid
                conn.commit()
                return account_id
        finally:
            conn.close()

    def add_financial_transaction(self, account_id, transaction_type, amount, description, reference_type=None, reference_id=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO financial_transactions (account_id, transaction_type, amount, description, reference_type, reference_id, transaction_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (account_id, transaction_type, amount, description, reference_type, reference_id, date.today().isoformat()))
            
            cursor.execute("SELECT account_type, balance FROM accounts WHERE id = ?", (account_id,))
            account_type, current_balance = cursor.fetchone()

            if account_type == 'patient':
                new_balance = current_balance + amount if transaction_type == 'payment' else current_balance - amount
            elif account_type == 'doctor':
                new_balance = current_balance + amount if transaction_type == 'credit' else current_balance - amount
            else: # supplier, clinic
                new_balance = current_balance
            
            cursor.execute("UPDATE accounts SET balance = ?, last_transaction_date = ? WHERE id = ?", (new_balance, date.today().isoformat(), account_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_patient_financial_summary(self, patient_id):
        conn = self.db.get_connection()
        try:
            treatments_query = "SELECT COALESCE(SUM(total_cost), 0) FROM appointments WHERE patient_id = ?"
            payments_query = "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE patient_id = ?"
            total_cost = pd.read_sql_query(treatments_query, conn, params=(patient_id,)).iloc[0,0]
            total_paid = pd.read_sql_query(payments_query, conn, params=(patient_id,)).iloc[0,0]
            return {'total_cost': total_cost, 'total_paid': total_paid, 'balance': total_paid - total_cost}
        finally:
            conn.close()
    
    def get_doctor_financial_summary(self, doctor_id):
        conn = self.db.get_connection()
        try:
            earnings_query = "SELECT COALESCE(SUM(doctor_share), 0) FROM payments p JOIN appointments a ON p.appointment_id=a.id WHERE a.doctor_id = ?"
            withdrawals_query = "SELECT COALESCE(SUM(amount), 0) FROM financial_transactions ft JOIN accounts a ON ft.account_id=a.id WHERE a.account_type='doctor' AND a.account_holder_id=? AND ft.transaction_type='withdrawal'"
            total_earnings = pd.read_sql_query(earnings_query, conn, params=(doctor_id,)).iloc[0,0]
            total_withdrawn = pd.read_sql_query(withdrawals_query, conn, params=(doctor_id,)).iloc[0,0]
            return {'total_earnings': total_earnings, 'total_withdrawn': total_withdrawn, 'balance': total_earnings - total_withdrawn}
        finally:
            conn.close()

    def get_account_statement(self, account_type, holder_id):
        conn = self.db.get_connection()
        try:
            account_id_df = pd.read_sql_query("SELECT id FROM accounts WHERE account_type = ? AND account_holder_id = ?", conn, params=(account_type, holder_id))
            if account_id_df.empty:
                return None
            account_id = account_id_df.iloc[0,0]
            transactions = pd.read_sql_query("SELECT * FROM financial_transactions WHERE account_id = ? ORDER BY transaction_date DESC", conn, params=(account_id,))
            return transactions
        finally:
            conn.close()

    # ========== تقارير وإحصائيات ==========
    def get_dashboard_stats(self):
        conn = self.db.get_connection()
        today = date.today().isoformat()
        try:
            stats = {
                'total_patients': pd.read_sql("SELECT COUNT(*) FROM patients WHERE is_active=1", conn).iloc[0,0],
                'total_doctors': pd.read_sql("SELECT COUNT(*) FROM doctors WHERE is_active=1", conn).iloc[0,0],
                'today_appointments': pd.read_sql("SELECT COUNT(*) FROM appointments WHERE appointment_date = ?", conn, params=(today,)).iloc[0,0],
                'low_stock_items': pd.read_sql("SELECT COUNT(*) FROM inventory WHERE quantity <= min_stock_level AND is_active=1", conn).iloc[0,0],
                'expiring_items': pd.read_sql("SELECT COUNT(*) FROM inventory WHERE expiry_date <= date('now', '+30 days') AND is_active=1", conn).iloc[0,0]
            }
            return stats
        finally:
            conn.close()
    
    def get_monthly_comparison(self, months=1):
        conn = self.db.get_connection()
        try:
            if months == 1:
                today = date.today()
                current_start, current_end = today.replace(day=1), today
                last_end = current_start - timedelta(days=1)
                last_start = last_end.replace(day=1)
                
                def get_metric(table, date_col, start, end):
                    return pd.read_sql(f"SELECT COALESCE(SUM(amount), 0) FROM {table} WHERE {date_col} BETWEEN ? AND ?", conn, params=(start.isoformat(), end.isoformat())).iloc[0,0]

                current_revenue = get_metric('payments', 'payment_date', current_start, current_end)
                last_revenue = get_metric('payments', 'payment_date', last_start, last_end)
                
                return {'current_revenue': current_revenue, 'last_revenue': last_revenue}
            
            # For multiple months DataFrame
            end_date = date.today()
            start_date = end_date - timedelta(days=months*30)
            df = pd.read_sql("SELECT strftime('%Y-%m', payment_date) as month, SUM(amount) as revenue FROM payments WHERE payment_date BETWEEN ? AND ? GROUP BY month", conn, params=(start_date.isoformat(), end_date.isoformat()))
            return df
        finally:
            conn.close()
            
    # ========== سجل الأنشطة ==========
    def log_activity(self, conn, action, table_name, record_id, details, user_name="النظام"):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO activity_log (action, table_name, record_id, details, user_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (action, table_name, record_id, details, user_name))

# إنشاء مثيل
crud = CRUDOperations()
