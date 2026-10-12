# FleetOps Cloud — Testing & QA Strategy

## 1. Principles
- **No untested business rules**: Every calculation (fuel efficiency, odometer progression, assignment date collisions, maintenance intervals) must have test coverage.
- **Tenant isolation tests**: Every query, view, and API endpoint must be tested for multi-tenant isolation (Organization A user cannot access Organization B records).
- **Fast automated feedback**: Utilize `pytest`, `pytest-django`, and `factory-boy`.

## 2. Test Structure
```text
tests/
├── conftest.py            # Global fixtures (users, organizations, memberships, api clients)
├── accounts/              # User model & auth tests
├── organizations/         # Multi-tenant tests & membership permissions
├── fleet/                 # Vehicle and driver model/view tests
├── assignments/           # Assignment conflicts & history
├── maintenance/           # Maintenance schedules & work orders
├── expenses/              # Fuel and expense calculations & validation
└── api/                   # REST API tests using DRF APIClient
```

## 3. Running Tests
```bash
# Run full test suite
pytest

# Run with test coverage report
pytest --cov=apps --cov-report=term-missing

# Run Ruff linter and formatter checks
ruff check .
ruff format --check .
```
