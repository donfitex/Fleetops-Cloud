# FleetOps Cloud — Roles & Permission Matrix

## 1. Role Definitions
FleetOps Cloud implements a clear Role-Based Access Control (RBAC) hierarchy scoped strictly to an **Organization**:

1. **Owner**: Full control over the organization, including billing, membership management, tenant settings, and asset deletion.
2. **Administrator**: Full operational and management access across all modules (fleet, maintenance, expenses, reports). Can invite and manage members (except the Owner).
3. **Fleet Manager**: Manages vehicles, drivers, assignments, maintenance schedules, work orders, and fuel/expense logs. Cannot edit organization-level settings or billing.
4. **Driver**: Read-only view of their personal assigned vehicle and assignments. Can submit fuel logs, expense receipts, and vehicle inspections.
5. **Viewer**: Read-only access across the organization's assets and reports for audit or oversight purposes. Cannot create, edit, or delete any operational records.

## 2. Resource Permission Matrix

| Resource | Action | Owner | Admin | Fleet Manager | Driver | Viewer |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Organization Settings** | View / Edit | ✅ / ✅ | ✅ / ❌ | ❌ / ❌ | ❌ / ❌ | ❌ / ❌ |
| **User Memberships** | Invite / Remove | ✅ / ✅ | ✅ / ✅ | ❌ / ❌ | ❌ / ❌ | ❌ / ❌ |
| **Vehicles** | View / Create / Edit / Delete | ✅ / ✅ / ✅ / ✅ | ✅ / ✅ / ✅ / ✅ | ✅ / ✅ / ✅ / ❌ | ⚠️ (Assigned only) / ❌ / ❌ / ❌ | ✅ / ❌ / ❌ / ❌ |
| **Drivers** | View / Create / Edit / Delete | ✅ / ✅ / ✅ / ✅ | ✅ / ✅ / ✅ / ✅ | ✅ / ✅ / ✅ / ❌ | ⚠️ (Own profile) / ❌ / ❌ / ❌ | ✅ / ❌ / ❌ / ❌ |
| **Assignments** | View / Create / Edit | ✅ / ✅ / ✅ | ✅ / ✅ / ✅ | ✅ / ✅ / ✅ | ⚠️ (Own assignments) / ❌ / ❌ | ✅ / ❌ / ❌ |
| **Maintenance** | View / Create / Edit / Close | ✅ / ✅ / ✅ / ✅ | ✅ / ✅ / ✅ / ✅ | ✅ / ✅ / ✅ / ✅ | ❌ / ❌ / ❌ / ❌ | ✅ / ❌ / ❌ / ❌ |
| **Fuel & Mileage Logs** | View / Create / Edit | ✅ / ✅ / ✅ | ✅ / ✅ / ✅ | ✅ / ✅ / ✅ | ⚠️ (Own logs) / ✅ / ❌ | ✅ / ❌ / ❌ |
| **Expenses** | View / Create / Edit | ✅ / ✅ / ✅ | ✅ / ✅ / ✅ | ✅ / ✅ / ✅ | ⚠️ (Own logs) / ✅ / ❌ | ✅ / ❌ / ❌ |
| **Reports & Export** | View / Export CSV | ✅ / ✅ | ✅ / ✅ | ✅ / ✅ | ❌ / ❌ | ✅ / ❌ |
| **Audit Logs** | View | ✅ | ✅ | ❌ | ❌ | ❌ |

> **Note**: Tenant boundaries are always enforced first. A user with `Owner` privileges in Organization A has zero access to Organization B.
