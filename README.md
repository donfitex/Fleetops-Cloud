# FleetOps Cloud

FleetOps Cloud is a professional, scalable, secure, multi-tenant SaaS platform for fleet and vehicle operations management built with Python, Django, PostgreSQL, Tailwind CSS, HTMX, Alpine.js, and Chart.js.

---

## Architecture & Technical Stack

- **Backend Framework**: Python 3.14+, Django 5.x, Django REST Framework
- **Database**: PostgreSQL with `psycopg` (v3)
- **Settings Management**: `django-environ` reading `.env`
- **Multi-Tenancy**: Tenant-isolated models linked to `Organization` with RBAC memberships
- **API Documentation**: OpenAPI 3.0 via `drf-spectacular`
- **Linting & Formatting**: `ruff`
- **Test Automation**: `pytest`, `pytest-django`, `factory-boy`

---

## Getting Started (Local Development)

### 1. Prerequisites
- Python 3.14+ (or compatible 3.12+)
- PostgreSQL 16+ or 18+
- Git

### 2. Environment Setup
```powershell
# Clone the repository and navigate into the folder
cd "Fleetops Cloud"

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Create your local environment file from the template
Copy-Item .env.example .env
```

Edit `.env` to configure your local PostgreSQL credentials:
```ini
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/fleetops_db
```

### 3. Database Migrations
```powershell
python manage.py migrate
```

### 4. Running the Development Server
```powershell
python manage.py runserver
```
Visit:
- Admin Portal: `http://127.0.0.1:8000/admin/`
- API Documentation (Swagger UI): `http://127.0.0.1:8000/api/docs/`
- API Redoc: `http://127.0.0.1:8000/api/redoc/`

### 5. Docker Quickstart
```powershell
# Build and start the app stack with PostgreSQL
 docker compose up --build

# Stop the stack
 docker compose down
```
The containerized app runs the Django app with Gunicorn, migrates the schema automatically, and serves traffic on `http://localhost:8000`.

---

## Testing & Quality Assurance

```powershell
# Run automated tests
pytest

# Run linter checks
ruff check .

# Check code formatting
ruff format --check .
```

---

## Documentation
- [Architecture Guide](docs/architecture.md)
- [Product Requirements](docs/product-requirements.md)
- [Data Model & Multi-Tenancy](docs/data-model.md)
- [Roles & Permissions](docs/permissions.md)
- [Testing Strategy](docs/testing.md)
- [Security Guidelines](docs/security.md)
- [Development Roadmap](docs/roadmap.md)
