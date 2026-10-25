from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

try:
    if not os.path.exists("Analysen"):
        os.makedirs("Analysen")
    
    doc = SimpleDocTemplate("Analysen/test_report.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("PDF Export Test Successful", styles['Normal'])]
    doc.build(story)
    print("PDF Created Successfully")
except Exception as e:
    print(f"PDF Error: {e}")
