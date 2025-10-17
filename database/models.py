import sqlite3
from datetime import datetime, date
import os
from datetime import timedelta

class Database:
    _instance = None
    
    def __new__(cls, db_path="clinic.db"):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_path = db_path
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self):
        """إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة"""
        if not self._initialized:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
                    cursor = conn.cursor()
                    
                    # جدول الأطباء
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS doctors (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            specialization TEXT NOT NULL,
                            phone TEXT,
                            email TEXT,
                            address TEXT,
                            hire_date DATE,
                            salary REAL,
                            commission_rate REAL DEFAULT 0.0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # جدول المرضى
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS patients (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            phone TEXT,
                            email TEXT,
                            address TEXT,
                            date_of_birth DATE,
                            gender TEXT,
                            medical_history TEXT,
                            emergency_contact TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # جدول العلاجات والخدمات
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS treatments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            description TEXT,
                            base_price REAL NOT NULL,
                            duration_minutes INTEGER,
                            category TEXT,
                            is_active BOOLEAN DEFAULT 1,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # جدول المواعيد
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS appointments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            patient_id INTEGER NOT NULL,
                            doctor_id INTEGER NOT NULL,
                            treatment_id INTEGER,
                            appointment_date DATE NOT NULL,
                            appointment_time TIME NOT NULL,
                            status TEXT DEFAULT 'مجدول',
                            notes TEXT,
                            total_cost REAL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (patient_id) REFERENCES patients (id),
                            FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                            FOREIGN KEY (treatment_id) REFERENCES treatments (id)
                        )
                    ''')
                    
                    # جدول المدفوعات
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS payments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            appointment_id INTEGER,
                            patient_id INTEGER NOT NULL,
                            amount REAL NOT NULL,
                            payment_method TEXT NOT NULL,
                            payment_date DATE NOT NULL,
                            status TEXT DEFAULT 'مكتمل',
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (appointment_id) REFERENCES appointments (id),
                            FOREIGN KEY (patient_id) REFERENCES patients (id)
                        )
                    ''')
                    
                    # جدول المخزون
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_name TEXT NOT NULL,
                            category TEXT,
                            quantity INTEGER NOT NULL DEFAULT 0,
                            unit_price REAL,
                            min_stock_level INTEGER DEFAULT 10,
                            supplier_id INTEGER,
                            expiry_date DATE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                        )
                    ''')
                    
                    # جدول الموردين
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS suppliers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            contact_person TEXT,
                            phone TEXT,
                            email TEXT,
                            address TEXT,
                            payment_terms TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # جدول المصروفات
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS expenses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            category TEXT NOT NULL,
                            description TEXT NOT NULL,
                            amount REAL NOT NULL,
                            expense_date DATE NOT NULL,
                            payment_method TEXT,
                            receipt_number TEXT,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # جدول استخدام المخزون
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS inventory_usage (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            inventory_id INTEGER NOT NULL,
                            appointment_id INTEGER,
                            quantity_used INTEGER NOT NULL,
                            usage_date DATE NOT NULL,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                            FOREIGN KEY (appointment_id) REFERENCES appointments (id)
                        )
                    ''')
                    
                    # إضافة بيانات تجريبية
                    self.add_sample_data(conn, cursor)
                    self._initialized = True
            except sqlite3.Error as e:
                print(f"Database initialization error: {e}")
                raise
    
    def add_sample_data(self, conn, cursor):
        """إضافة بيانات تجريبية"""
        cursor.execute("SELECT COUNT(*) FROM doctors")
        if cursor.fetchone()[0] == 0:
            # أطباء
            sample_doctors = [
                ("د. أحمد محمد", "طب الأسنان العام", "01234567890", "ahmed@clinic.com", "القاهرة", "2023-01-01", 15000.0, 10.0),
                ("د. فاطمة علي", "تقويم الأسنان", "01234567891", "fatma@clinic.com", "الجيزة", "2023-02-01", 18000.0, 15.0)
            ]
            cursor.executemany('INSERT INTO doctors (name, specialization, phone, email, address, hire_date, salary, commission_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', sample_doctors)
            
            # مرضى
            sample_patients = [
                ("محمد علي", "01234567892", "mohamed@patient.com", "القاهرة", "1990-05-15", "ذكر", "لا يوجد", "01012345678"),
                ("سارة حسن", "01234567893", "sarah@patient.com", "الجيزة", "1995-08-20", "أنثى", "حساسية", "01012345679")
            ]
            cursor.executemany('INSERT INTO patients (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', sample_patients)
            
            # علاجات
            sample_treatments = [
                ("فحص وتنظيف", "فحص شامل وتنظيف الأسنان", 200.0, 60, "وقائي"),
                ("حشو عادي", "حشو الأسنان", 300.0, 45, "علاجي")
            ]
            cursor.executemany('INSERT INTO treatments (name, description, base_price, duration_minutes, category) VALUES (?, ?, ?, ?, ?)', sample_treatments)
            
            # مواعيد
            today = date.today().isoformat()  # Explicitly using date.today() for clarity
            tomorrow = (date.today() + timedelta(days=1)).isoformat()
            cursor.execute('INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, total_cost) VALUES (?, ?, ?, ?, ?, ?)',
                          (1, 1, 1, today, "10:00", 200.0))
            cursor.execute('INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, total_cost) VALUES (?, ?, ?, ?, ?, ?)',
                          (2, 2, 2, tomorrow, "14:00", 300.0))
            
            # مخزون
            sample_inventory = [
                ("قفازات طبية", "مستهلكات", 100, 0.5, 20, 1, "2025-12-31"),
                ("حقن تخدير", "أدوية", 50, 15.0, 10, 1, "2025-06-30")
            ]
            cursor.executemany('INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date) VALUES (?, ?, ?, ?, ?, ?, ?)', sample_inventory)
            
            # موردين
            cursor.execute('INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms) VALUES (?, ?, ?, ?, ?, ?)',
                          ("شركة المستلزمات", "علي عبدالله", "01234567894", "supplies@co.com", "القاهرة", "آجل 30 يوم"))
            
            # مصروفات
            cursor.execute('INSERT INTO expenses (category, description, amount, expense_date, payment_method) VALUES (?, ?, ?, ?, ?)',
                          ("رواتب", "راتب أطباء", 30000.0, today, "تحويل بنكي"))
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        return sqlite3.connect(self.db_path)

# تأخير التهيئة حتى الاستدعاء الصريح
db = Database()
db.initialize()