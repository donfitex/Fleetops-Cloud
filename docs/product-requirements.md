# FleetOps Cloud — Product Requirements Document (PRD)

## 1. Product Summary
FleetOps Cloud is an intuitive, reliable, and secure multi-tenant fleet operations management SaaS platform.

## 2. Target Audience
- Logistics and delivery fleets.
- Construction and field service fleets.
- Corporate vehicle departments.
- Small to mid-sized businesses managing company cars, vans, or trucks.

## 3. High-Level Requirements & Modules
- **Authentication & RBAC**: Granular roles (Owner, Administrator, Fleet Manager, Driver, Viewer).
- **Organizations**: Complete tenant separation for data, configuration, documents, and reporting.
- **Fleet Management**: Vehicle profiles, registration, status tracking, VIN, and odometer tracking.
- **Driver Management**: Driver records, licence classes, expiry tracking, and status.
- **Assignments**: Vehicle-driver check-out and check-in with conflict prevention and historical records.
- **Maintenance**: Preventative schedules, work orders, service logs, downtime, and cost tracking.
- **Operations & Expenses**: Fuel logs, odometer progressions, trips, expenses categorization.
- **Dashboard & Reporting**: Visual metrics with Chart.js, operational KPIs, safe CSV data exports.
- **Secure Documents**: Restricted storage for driver and vehicle documentation.
- **REST API**: Documented v1 API with OpenAPI schemas.
