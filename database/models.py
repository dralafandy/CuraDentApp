# database/models.py

import sqlite3
from datetime import datetime, date, timedelta
import os

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
                    conn.execute("PRAGMA foreign_keys = ON")
                    cursor = conn.cursor()
                    
                    # الجداول الأساسية
                    self.create_base_tables(cursor)
                    
                    # الجداول المتقدمة للميزات الجديدة
                    self.create_advanced_tables(cursor)
                    
                    # جداول نظام الحسابات المالي
                    self.create_financial_tables(cursor)
                    
                    # إضافة بيانات تجريبية
                    self.add_sample_data(conn, cursor)
                    self.add_default_settings(conn, cursor)
                    
                    self._initialized = True
                    
            except sqlite3.Error as e:
                print(f"Database initialization error: {e}")
                raise
    
    def create_base_tables(self, cursor):
        """إنشاء الجداول الأساسية"""
        
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
                is_active BOOLEAN DEFAULT 1,
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
                blood_type TEXT,
                allergies TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول العلاجات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                base_price REAL NOT NULL,
                duration_minutes INTEGER,
                category TEXT,
                doctor_percentage REAL DEFAULT 50.0,
                clinic_percentage REAL DEFAULT 50.0,
                color_code TEXT DEFAULT '#667eea',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                reminder_sent BOOLEAN DEFAULT 0,
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
                doctor_share REAL DEFAULT 0.0,
                clinic_share REAL DEFAULT 0.0,
                doctor_percentage REAL DEFAULT 0.0,
                clinic_percentage REAL DEFAULT 0.0,
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
                location TEXT,
                barcode TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
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
                approved_by TEXT,
                is_recurring BOOLEAN DEFAULT 0,
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
        
        # جدول الإعدادات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول سجل الأنشطة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id INTEGER,
                details TEXT,
                user_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def create_advanced_tables(self, cursor):
        """إنشاء الجداول المتقدمة للميزات الجديدة"""
        
        # جدول الملفات المرفقة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                category TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # جدول قائمة الانتظار
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waiting_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER,
                treatment_id INTEGER,
                preferred_date DATE,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'waiting',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                FOREIGN KEY (treatment_id) REFERENCES treatments (id)
            )
        ''')
        
        # جدول الإشعارات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                priority TEXT DEFAULT 'normal',
                is_read BOOLEAN DEFAULT 0,
                target_date DATE,
                related_id INTEGER,
                action_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول سجل النسخ الاحتياطي
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_type TEXT,
                backup_path TEXT,
                file_size INTEGER,
                status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def create_financial_tables(self, cursor):
        """إنشاء جداول نظام الحسابات المالي"""
        
        # جدول الحسابات المالية الرئيسي
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_type TEXT NOT NULL,
                account_holder_id INTEGER NOT NULL,
                account_holder_name TEXT NOT NULL,
                total_dues REAL DEFAULT 0.0,
                total_paid REAL DEFAULT 0.0,
                balance REAL DEFAULT 0.0,
                last_transaction_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الحركات المالية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                reference_type TEXT,
                reference_id INTEGER,
                transaction_date DATE NOT NULL,
                payment_method TEXT,
                receipt_number TEXT,
                notes TEXT,
                created_by TEXT DEFAULT 'النظام',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        ''')
        
        # جدول كشف الحساب للمرضى
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_account_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                total_treatments_cost REAL DEFAULT 0.0,
                total_paid REAL DEFAULT 0.0,
                outstanding_balance REAL DEFAULT 0.0,
                last_payment_date DATE,
                payment_status TEXT DEFAULT 'pending',
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # جدول كشف حساب الأطباء  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_account_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id INTEGER NOT NULL,
                total_earnings REAL DEFAULT 0.0,
                total_withdrawn REAL DEFAULT 0.0,
                current_balance REAL DEFAULT 0.0,
                last_withdrawal_date DATE,
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doctor_id) REFERENCES doctors (id)
            )
        ''')
        
        # جدول كشف حساب الموردين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_account_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER NOT NULL,
                total_purchases REAL DEFAULT 0.0,
                total_paid REAL DEFAULT 0.0,
                outstanding_balance REAL DEFAULT 0.0,
                last_payment_date DATE,
                payment_terms TEXT,
                credit_limit REAL DEFAULT 0.0,
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')
        
        # جدول سندات القبض والصرف
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vouchers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voucher_type TEXT NOT NULL,
                voucher_number TEXT UNIQUE NOT NULL,
                account_id INTEGER,
                amount REAL NOT NULL,
                payment_method TEXT,
                description TEXT,
                voucher_date DATE NOT NULL,
                created_by TEXT,
                approved_by TEXT,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        ''')
    
    def add_sample_data(self, conn, cursor):
        """إضافة بيانات تجريبية"""
        cursor.execute("SELECT COUNT(*) FROM doctors")
        if cursor.fetchone()[0] == 0:
            
            # أطباء
            sample_doctors = [
                ("د. أحمد محمد", "طب الأسنان العام", "01234567890", "ahmed@clinic.com", "القاهرة", "2023-01-01", 15000.0, 10.0, 1),
                ("د. فاطمة علي", "تقويم الأسنان", "01234567891", "fatma@clinic.com", "الجيزة", "2023-02-01", 18000.0, 15.0, 1),
                ("د. محمود حسن", "جراحة الفم والأسنان", "01234567892", "mahmoud@clinic.com", "القاهرة", "2023-03-01", 20000.0, 12.0, 1)
            ]
            cursor.executemany('''
                INSERT INTO doctors (name, specialization, phone, email, address, hire_date, salary, commission_rate, is_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_doctors)
            
            # مرضى
            sample_patients = [
                ("محمد علي", "01234567892", "mohamed@patient.com", "القاهرة، مدينة نصر", "1990-05-15", "ذكر", "لا يوجد", "01012345678", "A+", "لا يوجد", "", 1),
                ("سارة حسن", "01234567893", "sarah@patient.com", "الجيزة، الدقي", "1995-08-20", "أنثى", "حساسية من البنسلين", "01012345679", "O+", "بنسلين", "", 1),
                ("أحمد كمال", "01234567894", "ahmed@patient.com", "القاهرة، مصر الجديدة", "1988-03-10", "ذكر", "ضغط دم مرتفع", "01012345680", "B+", "لا يوجد", "", 1),
                ("منى إبراهيم", "01234567895", "mona@patient.com", "الجيزة، المهندسين", "1992-11-25", "أنثى", "لا يوجد", "01012345681", "AB+", "لا يوجد", "", 1)
            ]
            cursor.executemany('''
                INSERT INTO patients (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact, blood_type, allergies, notes, is_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_patients)
            
            # علاجات مع ألوان
            sample_treatments = [
                ("فحص وتنظيف", "فحص شامل للأسنان وتنظيف بالموجات فوق الصوتية", 200.0, 60, "وقائي", 40.0, 60.0, "#10b981", 1),
                ("حشو عادي", "حشو الأسنان بالحشو الأبيض", 300.0, 45, "علاجي", 50.0, 50.0, "#3b82f6", 1),
                ("حشو عصب", "علاج جذور الأسنان وحشو العصب", 800.0, 90, "علاجي", 60.0, 40.0, "#f59e0b", 1),
                ("تبييض الأسنان", "تبييض الأسنان بالليزر", 1500.0, 120, "تجميلي", 70.0, 30.0, "#ec4899", 1),
                ("خلع سن", "خلع الأسنان البسيط", 150.0, 30, "جراحي", 45.0, 55.0, "#ef4444", 1),
                ("تركيب تقويم", "تركيب تقويم الأسنان الثابت", 5000.0, 180, "تجميلي", 65.0, 35.0, "#8b5cf6", 1),
                ("أشعة بانوراما", "أشعة بانوراما للفكين", 250.0, 30, "تشخيصي", 30.0, 70.0, "#06b6d4", 1),
                ("تنظيف الجير", "إزالة الجير وتلميع الأسنان", 180.0, 45, "وقائي", 40.0, 60.0, "#14b8a6", 1)
            ]
            cursor.executemany('''
                INSERT INTO treatments (name, description, base_price, duration_minutes, category, doctor_percentage, clinic_percentage, color_code, is_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_treatments)
            
            # موردين
            sample_suppliers = [
                ("شركة المستلزمات الطبية", "علي عبدالله", "01234567896", "supplies@medical.com", "القاهرة، وسط البلد", "آجل 30 يوم", 1),
                ("مؤسسة الأدوات الطبية", "محمد صلاح", "01234567897", "info@medtools.com", "الجيزة، المهندسين", "نقدي", 1),
                ("شركة الأدوية والمستلزمات", "هدى أحمد", "01234567898", "contact@pharmaco.com", "القاهرة، مصر الجديدة", "آجل 60 يوم", 1)
            ]
            cursor.executemany('''
                INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms, is_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_suppliers)
            
            # مواعيد
            today = date.today()
            yesterday = today - timedelta(days=1)
            tomorrow = today + timedelta(days=1)
            next_week = today + timedelta(days=7)
            
            sample_appointments = [
                (1, 1, 1, yesterday.isoformat(), "09:00", "مكتمل", "فحص دوري", 200.0, 1),
                (2, 2, 2, yesterday.isoformat(), "11:00", "مكتمل", "", 300.0, 1),
                (3, 1, 1, today.isoformat(), "10:00", "مؤكد", "", 200.0, 0),
                (4, 3, 5, today.isoformat(), "14:00", "مجدول", "خلع ضرس العقل", 150.0, 0),
                (1, 2, 3, tomorrow.isoformat(), "09:30", "مؤكد", "", 800.0, 0),
                (2, 1, 4, next_week.isoformat(), "15:00", "مجدول", "تبييض كامل", 1500.0, 0)
            ]
            cursor.executemany('''
                INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, notes, total_cost, reminder_sent) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_appointments)
            
            # مخزون
            sample_inventory = [
                ("قفازات طبية (علبة 100 قطعة)", "مستهلكات", 50, 25.0, 20, 1, "2026-12-31", "مخزن A", "BAR001", 1),
                ("كمامات طبية (علبة 50 قطعة)", "مستهلكات", 40, 15.0, 15, 1, "2026-06-30", "مخزن A", "BAR002", 1),
                ("حقن تخدير موضعي", "أدوية", 100, 12.0, 30, 3, "2025-12-31", "ثلاجة الأدوية", "BAR003", 1),
                ("خيوط جراحية", "مستهلكات", 80, 8.0, 25, 2, "2027-01-31", "مخزن B", "BAR004", 1),
                ("حشو أبيض (كمبوزيت)", "مواد طبية", 30, 150.0, 10, 2, "2026-08-31", "مخزن B", "BAR005", 1),
                ("مطهر طبي (ليتر)", "مستهلكات", 25, 45.0, 10, 1, "2025-09-30", "مخزن A", "BAR006", 1),
                ("إبر حقن", "مستهلكات", 5, 0.5, 50, 1, "2026-03-31", "مخزن A", "BAR007", 1),
                ("قطن طبي (كيلو)", "مستهلكات", 15, 35.0, 5, 1, "2027-12-31", "مخزن A", "BAR008", 1)
            ]
            cursor.executemany('''
                INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date, location, barcode, is_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_inventory)
            
            # مدفوعات مع التقسيم
            sample_payments = [
                (1, 1, 200.0, "نقدي", yesterday.isoformat(), "مكتمل", 80.0, 120.0, 40.0, 60.0, ""),
                (2, 2, 300.0, "بطاقة ائتمان", yesterday.isoformat(), "مكتمل", 150.0, 150.0, 50.0, 50.0, ""),
                (None, 3, 500.0, "تحويل بنكي", (today - timedelta(days=3)).isoformat(), "مكتمل", 0.0, 500.0, 0.0, 100.0, "دفعة مقدمة للتقويم")
            ]
            cursor.executemany('''
                INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date, status, doctor_share, clinic_share, doctor_percentage, clinic_percentage, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_payments)
            
            # مصروفات
            last_month = today - timedelta(days=30)
            two_weeks_ago = today - timedelta(days=14)
            
            sample_expenses = [
                ("رواتب", "رواتب الأطباء - شهر سابق", 53000.0, last_month.isoformat(), "تحويل بنكي", "SAL-001", "", "الإدارة", 1),
                ("إيجار", "إيجار العيادة - شهري", 8000.0, last_month.isoformat(), "تحويل بنكي", "RENT-001", "", "الإدارة", 1),
                ("كهرباء ومياه", "فواتير الخدمات", 1500.0, two_weeks_ago.isoformat(), "نقدي", "UTIL-001", "", "الإدارة", 0),
                ("صيانة", "صيانة جهاز الأشعة", 2500.0, two_weeks_ago.isoformat(), "نقدي", "MAINT-001", "", "الإدارة", 0)
            ]
            cursor.executemany('''
                INSERT INTO expenses (category, description, amount, expense_date, payment_method, receipt_number, notes, approved_by, is_recurring) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_expenses)
            
            conn.commit()
            print("✅ تم إضافة البيانات التجريبية بنجاح!")
    
    def add_default_settings(self, conn, cursor):
        """إضافة الإعدادات الافتراضية"""
        try:
            cursor.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                default_settings = [
                    ("clinic_name", "عيادة Cura الطبية", "اسم العيادة"),
                    ("clinic_address", "القاهرة، مصر", "عنوان العيادة"),
                    ("clinic_phone", "01234567890", "هاتف العيادة"),
                    ("clinic_email", "info@curaclinic.com", "بريد العيادة"),
                    ("working_hours", "السبت - الخميس: 9 صباحاً - 9 مساءً", "ساعات العمل"),
                    ("currency", "ج.م", "العملة"),
                    ("theme", "blue", "ثيم الألوان"),
                    ("notifications_enabled", "1", "تفعيل الإشعارات"),
                    ("auto_backup", "1", "النسخ الاحتياطي التلقائي")
                ]
                cursor.executemany('''
                    INSERT INTO settings (key, value, description) 
                    VALUES (?, ?, ?)
                ''', default_settings)
                conn.commit()
                print("✅ تم إضافة الإعدادات الافتراضية!")
        except sqlite3.Error as e:
            print(f"❌ خطأ في إضافة الإعدادات: {e}")
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        return sqlite3.connect(self.db_path)
    
    def backup_database(self, backup_path=None):
        """إنشاء نسخة احتياطية"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("backups", exist_ok=True)
            backup_path = f"backups/clinic_backup_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            file_size = os.path.getsize(backup_path)
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO backup_log (backup_type, backup_path, file_size, status)
                VALUES (?, ?, ?, ?)
            ''', ("local", backup_path, file_size, "success"))
            conn.commit()
            conn.close()
            
            print(f"✅ تم إنشاء نسخة احتياطية: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ خطأ في إنشاء النسخة الاحتياطية: {e}")
            return None

# تهيئة قاعدة البيانات
db = Database()
db.initialize()