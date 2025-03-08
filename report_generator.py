from fpdf import FPDF
import os
from datetime import datetime

def generate_report(target, results):
    """Generates a professional security report (TXT & PDF)."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_folder = "reports"
    os.makedirs(report_folder, exist_ok=True)

    txt_report_path = os.path.join(report_folder, f"Security_Report_{target}_{timestamp}.txt")
    pdf_report_path = os.path.join(report_folder, f"Security_Report_{target}_{timestamp}.pdf")

    # Generate TXT report
    with open(txt_report_path, "w", encoding="utf-8") as f:
        f.write(f"Security Report - {target}\n")
        f.write("="*60 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for section, data in results.items():
            f.write(f"[+] {section}\n")
            f.write("-"*60 + "\n")
            f.write(data if data else "No data found.\n")
            f.write("\n\n")

    # Generate PDF report
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Security Report - {target}", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(10)

    for section, data in results.items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, f"[+] {section}", ln=True, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 10, data if data else "No data found.")
        pdf.ln(5)

    pdf.output(pdf_report_path)

    return pdf_report_path
