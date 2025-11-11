from typing import Iterable
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from app.models import Sale, Product
from sqlmodel import Session


def sales_to_csv(sales: Iterable[Sale], filename: str = "sales_report.csv")\
        -> str:
    rows = []
    for s in sales:
        rows.append({
            "id": s.id,
            "product_id": s.product_id,
            "quantity": s.quantity,
            "total_value": s.total_value,
            "timestamp": s.timestamp.isoformat()
        })
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    return filename


def sales_to_pdf(sales: Iterable[Sale], db: Session, filename: str =
                 "sales_report.pdf") -> str:
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 40, "Relatório de Vendas")
    c.setFont("Helvetica", 10)
    y = height - 70
    c.drawString(40, y, "ID")
    c.drawString(80, y, "Produto")
    c.drawString(250, y, "Qtd")
    c.drawString(300, y, "Total")
    c.drawString(360, y, "Data")
    y -= 20
    for s in sales:
        product = db.get(Product, s.product_id)
        name = product.name if product else f"#{s.product_id}"
        c.drawString(40, y, str(s.id))
        c.drawString(80, y, name[:25])
        c.drawString(250, y, str(s.quantity))
        c.drawString(300, y, f"{s.total_value:.2f}")
        c.drawString(360, y, s.timestamp.strftime("%Y-%m-%d %H:%M"))
        y -= 18
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 40
    c.save()
    return filename
