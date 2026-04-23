import os
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.models.employee import SalaryPayment, Employee
from app.models.sale import Sale


MESES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def _fmt_clp(amount: Decimal) -> str:
    return f"$ {int(amount):,}".replace(",", ".")


def generate_liquidacion_pdf(db: Session, payment: SalaryPayment) -> str:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm

    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(
        settings.REPORTS_DIR,
        f"liquidacion_{payment.employee_id}_{payment.period_year}_{payment.period_month:02d}.pdf"
    )

    emp: Employee = payment.employee
    company = db.execute(
        __import__("sqlalchemy").text("SELECT * FROM company LIMIT 1")
    ).fetchone()

    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Heading1"], fontSize=14, spaceAfter=6)
    normal = styles["Normal"]
    bold_style = ParagraphStyle("bold", parent=normal, fontName="Helvetica-Bold")

    elements = []

    company_name = company.razon_social if company else "Empresa"
    company_rut = company.rut if company else ""

    elements.append(Paragraph(f"LIQUIDACIÓN DE SUELDO", title_style))
    elements.append(Paragraph(f"{company_name} | RUT: {company_rut}", normal))
    elements.append(Paragraph(
        f"Período: {MESES[payment.period_month]} {payment.period_year}", normal
    ))
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("Datos del Trabajador", bold_style))
    worker_data = [
        ["Nombre:", f"{emp.first_name} {emp.last_name}", "RUT:", emp.rut],
        ["Cargo:", emp.position, "AFP:", emp.afp.value if emp.afp else "-"],
        ["ISAPRE/FONASA:", emp.isapre.value if emp.isapre else "-", "", ""],
    ]
    t = Table(worker_data, colWidths=[4*cm, 8*cm, 3*cm, 5*cm])
    t.setStyle(TableStyle([("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey)]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("Haberes", bold_style))
    haberes_data = [
        ["Concepto", "Monto"],
        ["Sueldo Base", _fmt_clp(payment.sueldo_base)],
        ["Horas Extra", _fmt_clp(payment.horas_extra * payment.valor_hora_extra)],
        ["Gratificación Legal", _fmt_clp(payment.gratificacion)],
        ["Bono Colación", _fmt_clp(payment.bono_colacion)],
        ["Bono Movilización", _fmt_clp(payment.bono_movilizacion)],
        ["Otros Haberes", _fmt_clp(payment.otros_haberes)],
        ["TOTAL HABERES", _fmt_clp(payment.total_haberes)],
    ]
    t2 = Table(haberes_data, colWidths=[12*cm, 8*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightblue),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 0.3*cm))

    elements.append(Paragraph("Descuentos", bold_style))
    descuentos_data = [
        ["Concepto", "Tasa", "Monto"],
        ["AFP", f"{float(payment.afp_porcentaje)*100:.2f}%", _fmt_clp(payment.afp_monto)],
        ["SIS", "0.87%", _fmt_clp(payment.sis_monto)],
        ["ISAPRE/FONASA", "", _fmt_clp(payment.isapre_monto)],
        ["Seguro de Cesantía", "0.60%", _fmt_clp(payment.cesantia_trabajador)],
        ["Otros Descuentos", "", _fmt_clp(payment.otros_descuentos)],
        ["TOTAL DESCUENTOS", "", _fmt_clp(payment.total_descuentos)],
    ]
    t3 = Table(descuentos_data, colWidths=[9*cm, 4*cm, 7*cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkred),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightyellow),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 0.5*cm))

    liquido_data = [["LÍQUIDO A PAGAR", _fmt_clp(payment.liquido_pagar)]]
    t4 = Table(liquido_data, colWidths=[12*cm, 8*cm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 14),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(t4)
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        ParagraphStyle("footer", parent=normal, fontSize=8, textColor=colors.grey)
    ))

    doc.build(elements)
    return filepath


def generate_sale_receipt_pdf(db: Session, sale: Sale) -> str:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm

    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    filepath = os.path.join(settings.REPORTS_DIR, f"boleta_{sale.id}.pdf")

    company = db.execute(
        __import__("sqlalchemy").text("SELECT * FROM company LIMIT 1")
    ).fetchone()

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    company_name = company.razon_social if company else "Empresa"
    company_rut = company.rut if company else ""

    elements.append(Paragraph(company_name, styles["Title"]))
    elements.append(Paragraph(f"RUT: {company_rut}", styles["Normal"]))
    elements.append(Paragraph("BOLETA DE VENTA", styles["Heading2"]))
    if sale.folio:
        elements.append(Paragraph(f"N° {sale.folio}", styles["Normal"]))
    elements.append(Paragraph(f"Fecha: {sale.created_at.strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 0.5*cm))

    data = [["Producto", "Cant.", "P.Unit", "Total"]]
    for item in sale.items:
        data.append([
            item.product.name if item.product else f"ID {item.product_id}",
            str(item.quantity),
            _fmt_clp(item.unit_price_with_iva),
            _fmt_clp(item.total),
        ])
    data.append(["", "", "Subtotal:", _fmt_clp(sale.subtotal)])
    data.append(["", "", "IVA (19%):", _fmt_clp(sale.iva_amount)])
    data.append(["", "", "TOTAL:", _fmt_clp(sale.total)])

    t = Table(data, colWidths=[10*cm, 2*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    elements.append(t)
    doc.build(elements)
    return filepath
