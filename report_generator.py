from datetime import datetime
import pandas as pd

class PatientReportGenerator:
    """مولد تقارير المرضى المفصلة"""
    
    @staticmethod
    def generate_html_report(report_data):
        """توليد تقرير HTML شامل للمريض"""
        
        patient_data = report_data['patient']
        appointments_data = report_data['appointments']
        payments_data = report_data['payments']
        treatments_data = report_data['treatments']
        
        # معلومات المريض
        patient_info = f"""
        <div class='patient-report'>
            <div class='report-header'>
                <h2>📋 تقرير شامل للمريض</h2>
                <h3>{patient_data.get('name', 'N/A')}</h3>
                <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <div class='report-section'>
                <h3>👤 المعلومات الشخصية</h3>
                <table class='report-table'>
                    <tr><th>الاسم</th><td>{patient_data.get('name', '')}</td></tr>
                    <tr><th>الهاتف</th><td>{patient_data.get('phone', '')}</td></tr>
                    <tr><th>البريد</th><td>{patient_data.get('email', 'N/A')}</td></tr>
                    <tr><th>تاريخ الميلاد</th><td>{patient_data.get('date_of_birth', 'N/A')}</td></tr>
                    <tr><th>فصيلة الدم</th><td>{patient_data.get('blood_type', 'N/A')}</td></tr>
                    <tr><th>الحساسية</th><td>{patient_data.get('allergies', 'لا يوجد')}</td></tr>
                </table>
            </div>
            
            <div class='report-section'>
                <h3>📊 الإحصائيات العامة</h3>
                <table class='report-table'>
                    <tr><th>إجمالي الزيارات</th><td>{report_data['visits_stats']['total_visits']} زيارة</td></tr>
                    <tr><th>إجمالي التكاليف</th><td>{report_data['total_cost']:,.2f} ج.م</td></tr>
                    <tr><th>المبلغ المدفوع</th><td>{report_data['total_paid']:,.2f} ج.م</td></tr>
                    <tr><th>المبلغ المتبقي</th><td style='color: {"red" if report_data['outstanding'] > 0 else "green"}; font-weight: bold;'>{report_data['outstanding']:,.2f} ج.م</td></tr>
                </table>
            </div>
        """
        
        # التاريخ الطبي
        if patient_data.get('medical_history'):
            patient_info += f"""
            <div class='report-section'>
                <h3>📝 التاريخ الطبي</h3>
                <p>{patient_data['medical_history']}</p>
            </div>
            """
        
        # سجل المواعيد
        if not appointments_data.empty:
            appointments_html = """
            <div class='report-section'>
                <h3>📅 سجل المواعيد</h3>
                <table class='report-table'>
                    <thead><tr><th>التاريخ</th><th>الوقت</th><th>الطبيب</th><th>العلاج</th><th>الحالة</th><th>التكلفة</th></tr></thead>
                    <tbody>
            """
            for _, apt in appointments_data.iterrows():
                appointments_html += f"""
                    <tr>
                        <td>{apt['appointment_date']}</td>
                        <td>{apt['appointment_time']}</td>
                        <td>{apt['doctor_name']}</td>
                        <td>{apt['treatment_name']}</td>
                        <td>{apt['status']}</td>
                        <td>{apt.get('total_cost', 0):,.2f} ج.م</td>
                    </tr>
                """
            appointments_html += "</tbody></table></div>"
            patient_info += appointments_html
        
        # سجل المدفوعات
        if not payments_data.empty:
            payments_html = """
            <div class='report-section'>
                <h3>💰 سجل المدفوعات</h3>
                <table class='report-table'>
                    <thead><tr><th>التاريخ</th><th>المبلغ</th><th>طريقة الدفع</th><th>الحالة</th></tr></thead>
                    <tbody>
            """
            for _, pay in payments_data.iterrows():
                payments_html += f"""
                    <tr>
                        <td>{pay['payment_date']}</td>
                        <td>{pay.get('amount', 0):,.2f} ج.م</td>
                        <td>{pay['payment_method']}</td>
                        <td>{pay['status']}</td>
                    </tr>
                """
            payments_html += "</tbody></table></div>"
            patient_info += payments_html
        
        # ملخص العلاجات
        if not treatments_data.empty:
            treatments_html = """
            <div class='report-section'>
                <h3>💉 ملخص العلاجات</h3>
                <table class='report-table'>
                    <thead><tr><th>العلاج</th><th>الفئة</th><th>عدد المرات</th><th>التكلفة الإجمالية</th><th>آخر استخدام</th></tr></thead>
                    <tbody>
            """
            for _, treat in treatments_data.iterrows():
                treatments_html += f"""
                    <tr>
                        <td>{treat['treatment_name']}</td>
                        <td>{treat['category']}</td>
                        <td>{treat['usage_count']}</td>
                        <td>{treat.get('total_cost', 0):,.2f} ج.م</td>
                        <td>{treat['last_used']}</td>
                    </tr>
                """
            treatments_html += "</tbody></table></div>"
            patient_info += treatments_html
        
        patient_info += "</div>"
        
        return patient_info