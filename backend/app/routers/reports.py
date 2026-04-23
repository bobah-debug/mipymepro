from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.export_service import export_inventory_excel, export_inventory_csv, export_sales_excel
from app.utils.deps import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reportes"])


@router.get("/inventory/excel")
def inventory_excel(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    data = export_inventory_excel(db)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventario.xlsx"},
    )


@router.get("/inventory/csv")
def inventory_csv(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    data = export_inventory_csv(db)
    return Response(
        content=data.encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventario.csv"},
    )


@router.get("/sales/excel")
def sales_excel(
    year: int = Query(default=None),
    month: int = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    now = datetime.now()
    y = year or now.year
    m = month or now.month
    data = export_sales_excel(db, y, m)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=ventas_{y}_{m:02d}.xlsx"},
    )


@router.get("/salary-payments/bulk-pdf")
def bulk_salary_pdf(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    import zipfile
    import io
    from app.models.employee import SalaryPayment
    from app.services.pdf_service import generate_liquidacion_pdf

    payments = db.query(SalaryPayment).filter(
        SalaryPayment.period_year == year,
        SalaryPayment.period_month == month,
    ).all()

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in payments:
            pdf_path = p.pdf_path or generate_liquidacion_pdf(db, p)
            emp = p.employee
            filename = f"liquidacion_{emp.rut}_{year}_{month:02d}.pdf"
            with open(pdf_path, "rb") as f:
                zf.writestr(filename, f.read())

    buf.seek(0)
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=liquidaciones_{year}_{month:02d}.zip"},
    )
