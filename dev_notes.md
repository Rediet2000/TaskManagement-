# Developer Notes & Change Log

This file tracks significant changes, architectural decisions, and development progress for the Task Management System.

## [2026-02-09] - Organizational Hierarchy & Advanced Settings

### Added
- **Branch Management**: Introduced a `Branch` level between `Organization` and `Department`.
  - Added `Branch` model in backend (`core.py`).
  - Added CRUD endpoints for branches.
  - UI: Grouped departments under branches in the Hierarchy Manager.
- **Allowed Domains**: Added `AllowedDomain` model and UI management.
  - Admins can now strictly control which email domains can register.
- **SMTP Configuration & Testing**: Added `SMTPTest` schema and `test-smtp` endpoint in the backend. 
  - Implementation in `Settings`: Added "Test Connection" button with real-time feedback (success/error messages).
  - Backend uses `smtplib` to verify connection and send a test email.

### Fixed
- **Role Management**: 
  - Added backend checks in `rbac.py` to prevent deleting roles that have assigned users or child roles (hierarchical dependencies).
  - Enhanced UI feedback in `HierarchyManager`: added error alerts for role updates and deletions to help diagnose issues.
  - Corrected Pydantic schema configs to use `from_attributes` consistently.
- **Role Editing**: Corrected two-way binding issues in `HierarchyManager` and updated the `Role` interface to support `parent_role_id`.
- **Hierarchical Roles**: Implemented role inheritance and parent role selection in the UI.

### Changed
- **Database Schema**: Manually synchronized PostgreSQL tables to add SMTP columns and `branch_id` to departments.
- **Pydantic Schemas**: Updated `hierarchy.py` schemas to reflect new model relationships.

---

## [Initial Setup] - Core Infrastructure
- FastAPI backend with SQLAlchemy and PostgreSQL.
- Angular 17+ standalone components with Signals.
- Docker containerization for full-stack orchestration.
- RBAC foundation with Organizations, Users, Roles, and Permissions.
