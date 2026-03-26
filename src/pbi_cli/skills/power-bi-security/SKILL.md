---
name: Power BI Security
description: Configure row-level security (RLS) roles, manage object-level security, and set up perspectives for Power BI semantic models. Use when the user mentions Power BI security, RLS, access control, or data restrictions.
tools: pbi-cli
---

# Power BI Security Skill

Manage row-level security (RLS) and perspectives for Power BI models.

## Prerequisites

```bash
pip install pbi-cli
pbi setup
pbi connect --data-source localhost:54321
```

## Security Roles (RLS)

```bash
# List all security roles
pbi security-role list

# Get role details
pbi security-role get "Regional Manager"

# Create a new role
pbi security-role create "Regional Manager" \
  --description "Restricts data to user's region"

# Delete a role
pbi security-role delete "Regional Manager"

# Export role as TMDL
pbi security-role export-tmdl "Regional Manager"
```

## Perspectives

Perspectives control which tables and columns are visible to users:

```bash
# List all perspectives
pbi perspective list

# Create a perspective
pbi perspective create "Sales View"

# Delete a perspective
pbi perspective delete "Sales View"
```

## Workflow: Set Up RLS

```bash
# 1. Create roles
pbi security-role create "Sales Team" --description "Sales data only"
pbi security-role create "Finance Team" --description "Finance data only"

# 2. Verify roles were created
pbi --json security-role list

# 3. Export for version control
pbi security-role export-tmdl "Sales Team"
pbi security-role export-tmdl "Finance Team"
```

## Workflow: Create User-Focused Perspectives

```bash
# 1. Create perspectives for different audiences
pbi perspective create "Executive Dashboard"
pbi perspective create "Sales Detail"
pbi perspective create "Finance Overview"

# 2. Verify
pbi --json perspective list
```

## Common RLS Patterns

### Region-Based Security

Create a role that filters by the authenticated user's region:

```bash
pbi security-role create "Region Filter" \
  --description "Users see only their region's data"
```

Then define table permissions with DAX filter expressions in the model (via TMDL or Power BI Desktop).

### Department-Based Security

```bash
pbi security-role create "Department Filter" \
  --description "Users see only their department's data"
```

### Manager Hierarchy

```bash
pbi security-role create "Manager View" \
  --description "Managers see their direct reports' data"
```

## Best Practices

- Create roles with clear, descriptive names
- Always add descriptions explaining the access restriction
- Export roles as TMDL for version control
- Test RLS thoroughly before publishing to production
- Use perspectives to simplify the model for different user groups
- Document role-to-group mappings externally (RLS roles map to Azure AD groups in Power BI Service)
- Use `--json` output for automated security audits: `pbi --json security-role list`
