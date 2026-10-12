# FleetOps Cloud — Architecture Documentation

## 1. Overview
FleetOps Cloud is a multi-tenant Software-as-a-Service (SaaS) platform designed for fleet and vehicle operations management. It allows companies, logistics providers, and organizations with vehicle fleets to track assets, assignments, maintenance, fuel consumption, operating expenses, and documents in an integrated system.

## 2. High-Level Architecture
- **Architecture Pattern**: Modular Django Monolith.
- **Backend**: Python 3.14+, Django 5.x, Django REST Framework.
- **Database**: PostgreSQL 18 with `psycopg` (v3).
- **Frontend Architecture**: Server-Side Rendering (SSR) via Django Templates + Tailwind CSS + HTMX for dynamic partial updates + Alpine.js for lightweight client state + Chart.js for data visualization.
- **Static Assets**: WhiteNoise (efficient caching & compression).
- **Asynchronous / Realtime (Future MVP+)**: Kept out of initial scope to avoid unnecessary infrastructure overhead.

## 3. Directory Layout
```text
Fleetops Cloud/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore specifications
├── AGENTS.md                 # Agent guidelines
├── README.md                 # Project quickstart
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development & testing dependencies
├── config/                   # Project configuration
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py           # Shared settings
│   │   ├── development.py    # Local development settings
│   │   └── production.py     # Production security settings
│   ├── __init__.py
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py               # WSGI entrypoint
│   └── asgi.py               # ASGI entrypoint
├── apps/                     # Application modules
│   ├── core/                 # Shared mixins, models, utils
│   ├── accounts/             # Custom User model & auth
│   ├── organizations/        # Multi-tenant Organization & Membership
│   ├── fleet/                # Vehicles & equipment
│   ├── drivers/              # Drivers & licenses
│   ├── assignments/          # Vehicle-driver assignments
│   ├── maintenance/          # Work orders & schedules
│   ├── operations/           # Trips & odometers
│   ├── expenses/             # Fuel & operational costs
│   ├── documents/            # Encrypted/restricted document storage
│   ├── reports/              # Aggregations, metrics & CSV export
│   └── api/                  # Versioned DRF endpoints (/api/v1/)
├── templates/                # Reusable Django templates & partials
├── static/                   # Compiled CSS/JS assets
├── tests/                    # Integration & test suites
└── docs/                     # Full project documentation
```

## 4. Multi-Tenant Security & Isolation
- Every tenant resource is linked to an `Organization`.
- Model inheritance with a base `TenantModel` providing `organization_id` foreign key.
- Querysets are strictly scoped using `for_organization(org)` manager methods or request context.
- Cross-tenant data leaks are prevented at database queries, forms, views, API serializers, and export tasks.
