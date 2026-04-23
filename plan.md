# Sistema de Administración PyME Chile

## Descripción General
Sistema web local (client-server) para gestión de pequeñas y medianas empresas en Chile.
Instalado en una máquina "servidor" en la red local; los demás usuarios acceden vía navegador web.

## Stack Tecnológico
- **Backend**: Python 3.11+ · FastAPI · SQLAlchemy 2.0 · Alembic · PostgreSQL
- **Frontend**: React 18 · TypeScript · Vite · Tailwind CSS · shadcn/ui · Recharts
- **PDF**: ReportLab + WeasyPrint
- **Excel/CSV**: openpyxl · pandas
- **Auth**: JWT (python-jose) + bcrypt
- **Barcode**: USB HID (keyboard emulation, sin lib especial) + python-barcode para generación
- **SII DTE**: lxml + signxml + zeep (SOAP WS del SII)
- **Empaquetado**: PyInstaller (backend) + Vite build (frontend) · Inno Setup (Windows .exe) · AppImage (Linux)

## Arquitectura
```
[Máquina Servidor]
  ├── PostgreSQL (puerto 5432)
  └── FastAPI app (puerto 8000)
        ├── /api/* → REST endpoints
        └── /* → Sirve React SPA

[Clientes en LAN]
  └── Navegador → http://servidor-ip:8000
```

## Módulos
1. **Auth & Empresa** – Login, roles (admin/vendedor/RRHH), configuración empresa
2. **Inventario** – Productos, categorías, stock, movimientos, lector barras
3. **Ventas / POS** – Crear venta, lector barras, boleta electrónica SII, impresión
4. **RRHH** – Empleados, contratos, sueldos, vacaciones, liquidaciones PDF
5. **Dashboard** – KPIs mensuales, gráficos ventas/gastos/utilidades
6. **Reportes** – Exportar Excel/CSV para contabilidad, informes PDF
7. **Configuración** – Empresa, impresoras, integración SII

---

### [x] Step 1: Setup del proyecto y estructura base
- Crear estructura de carpetas: `backend/`, `frontend/`, `installer/`, `docker/`
- Inicializar FastAPI con configuración, CORS, health check
- Inicializar React + Vite + TypeScript + Tailwind + shadcn/ui
- Configurar Docker Compose (PostgreSQL + backend + frontend en dev)
- Configurar Alembic para migraciones
- README con instrucciones de desarrollo

### [x] Step 2: Modelos de datos y autenticación
- Modelos SQLAlchemy: User, Role, Company, CompanySettings
- Endpoints: login (JWT), refresh token, logout, perfil usuario
- Middleware de autenticación y autorización por rol
- Frontend: pantalla de login, layout principal con sidebar, gestión de sesión
- Seeders: usuario admin por defecto, roles iniciales

### [x] Step 3: Módulo Inventario
- Modelos: Category, Product (con barcode EAN-13), StockMovement, Supplier
- CRUD productos con búsqueda, filtros, paginación
- Entrada de stock (compras) con soporte lector código de barras (input field HID)
- Alertas de stock mínimo
- Frontend: listado productos, formulario alta/edición, vista de movimientos
- Generación imagen código de barras (python-barcode)

### [x] Step 4: Módulo Ventas y POS
- Modelos: Sale, SaleItem, PaymentMethod
- Punto de venta: agregar productos por código de barras o búsqueda, carrito, total con IVA
- Integración SII: generación XML DTE boleta electrónica (Tipo 39), firma digital, envío WS SII
- Impresión boleta (formato térmico 80mm y A4)
- Historial de ventas con filtros por fecha
- Anulación de venta
- Frontend: interfaz POS táctil-friendly, historial

### [x] Step 5: Módulo RRHH
- Modelos: Employee, Contract, SalaryPayment, VacationRequest
- CRUD empleados con datos legales (RUT, AFP, ISAPRE, etc.)
- Cálculo liquidación de sueldo chilena (gratificación, descuentos legales AFP/ISAPRE/SIS)
- Generación liquidación en PDF (formato legal)
- Gestión solicitudes de vacaciones (solicitar, aprobar/rechazar, saldo días)
- Frontend: listado empleados, ficha empleado, módulo vacaciones, generación liquidaciones

### [x] Step 6: Dashboard y KPIs financieros
- Endpoints de agregación: ventas del mes, gastos, utilidad bruta, ticket promedio
- KPIs: unidades vendidas, productos más vendidos, comparativa mes anterior
- Gráficos Recharts: línea (ventas diarias), barras (top productos), dona (categorías)
- Resumen gastos vs ingresos del mes
- Frontend: dashboard principal con cards KPI + gráficos interactivos

### [x] Step 7: Reportes y exportación
- Exportar inventario a Excel (.xlsx) y CSV con openpyxl/pandas
- Exportar ventas del período a Excel
- Reporte de libro de ventas formato SII (F29 helper)
- Exportar liquidaciones en lote PDF (ZIP)
- Frontend: página de reportes con filtros de período y botones de descarga

### [x] Step 8: Empaquetado e instalador
- Script PyInstaller para crear ejecutable backend standalone (Windows + Linux)
- Build optimizado del frontend (Vite build)
- Script Inno Setup para instalador Windows (.exe): instala PostgreSQL, backend como servicio Windows, frontend estático
- Script para crear AppImage Linux
- Script de primera configuración (setup wizard: nombre empresa, usuario admin, puerto)
- Instrucciones de instalación en red local
