import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.config import settings
    print("config.py: OK -", settings.APP_NAME)
except Exception as e:
    print("config.py ERROR:", e)

try:
    from app.database import Base, get_db
    print("database.py: OK")
except Exception as e:
    print("database.py ERROR:", e)

try:
    from app.models.user import User, Role, RoleName
    print("models/user.py: OK")
except Exception as e:
    print("models/user.py ERROR:", e)

try:
    from app.models.company import Company
    print("models/company.py: OK")
except Exception as e:
    print("models/company.py ERROR:", e)

try:
    from app.models.sale import Sale, SaleItem, PaymentMethod
    print("models/sale.py: OK")
except Exception as e:
    print("models/sale.py ERROR:", e)

try:
    from app.models.employee import Employee, Contract, SalaryPayment, VacationRequest
    print("models/employee.py: OK")
except Exception as e:
    print("models/employee.py ERROR:", e)

try:
    from app.services.auth_service import authenticate_user, create_access_token
    print("services/auth_service.py: OK")
except Exception as e:
    print("services/auth_service.py ERROR:", e)

print("\nSintaxis verificada. Para correr el sistema usa: docker compose up -d")
