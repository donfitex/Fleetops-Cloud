# FleetOps Cloud — Security Architecture & Guidelines

## 1. Multi-Tenant Isolation (Primary Defense)
- **Principle**: Access to data belonging to any tenant other than the authenticated user's active tenant must be strictly denied.
- **Enforcement Layers**:
  1. **ORM Layer**: Base `TenantModel` requiring an `organization` ForeignKey.
  2. **Queryset Layer**: Views filter using `.filter(organization=request.user.active_organization)`.
  3. **Object-Level Permissions**: Custom Django / DRF permission classes verify `obj.organization == request.user.active_organization`.
  4. **Relationship Integrity**: When updating a foreign key (e.g., assigning a driver to a vehicle), both objects must belong to the exact same organization.

## 2. Authentication & Authorization
- Password hashing with PBKDF2 (Django default).
- Secure session cookies (`HttpOnly`, `SameSite=Lax` / `Strict`).
- CSRF protection enabled across all state-mutating requests (`POST`, `PUT`, `PATCH`, `DELETE`).
- Role-based permissions strictly mapped to business roles (*Owner*, *Admin*, *Fleet Manager*, *Driver*, *Viewer*).

## 3. Secret Management
- Zero hardcoded secrets.
- Values loaded via `django-environ` from environment / `.env`.
- Production enforces HTTPS redirect, secure cookies, and strict HSTS headers.
