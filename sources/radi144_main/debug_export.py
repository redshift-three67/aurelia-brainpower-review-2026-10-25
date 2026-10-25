import os
import sys

print("Debug Export Start")

# Ensure dir
out_dir = os.path.join(os.getcwd(), "Analysen")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
    print(f"Created {out_dir}")

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    
    pdf_path = os.path.join(out_dir, "debug_test.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    doc.build([Paragraph("Test", styles['Normal'])])
    print(f"PDF created at {pdf_path}")
except Exception as e:
    print(f"PDF Failed: {e}")

try:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws['A1'] = "Test"
    xlsx_path = os.path.join(out_dir, "debug_test.xlsx")
    wb.save(xlsx_path)
    print(f"Excel created at {xlsx_path}")
except Exception as e:
    print(f"Excel Failed: {e}")
