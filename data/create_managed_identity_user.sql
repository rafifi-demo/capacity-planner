-- =============================================================================
-- Create Managed Identity Database Roles for Azure Container Apps
-- =============================================================================
--
-- This script creates database roles for Azure Container Apps with System-Assigned
-- Managed Identity. Run this script AFTER deploying the infrastructure with Terraform.
--
-- Prerequisites:
-- 1. PostgreSQL Flexible Server must have Microsoft Entra authentication enabled
-- 2. You must be connected as an Azure AD administrator
-- 3. Container Apps must be deployed with System-Assigned Managed Identity enabled
--
-- Connection command (as Azure AD admin):
--   psql "host=<server>.postgres.database.azure.com dbname=zava_logistics \
--         user=<your-azure-username> password=<your-azure-ad-token> sslmode=require"
--
-- To get an Azure AD token:
--   az account get-access-token --resource-type oss-rdbms
--
-- =============================================================================

-- ============================================================================
-- Step 1: Create database roles for Container App Managed Identities
-- ============================================================================

-- Note: The principal name should match the Container App name
-- Format: pgaadauth_create_principal('<container_app_name>', is_admin, is_external)
--   - container_app_name: The name of the Container App (e.g., 'zava-backend')
--   - is_admin: false (not a database admin)
--   - is_external: false (system-assigned managed identity)

-- Create role for Backend Container App
-- Replace 'zava-backend' with actual Container App name if different
SELECT * FROM pgaadauth_create_principal('zava-backend', false, false);

-- Create role for MCP Server Container App
-- Replace 'zava-mcp' with actual Container App name if different
SELECT * FROM pgaadauth_create_principal('zava-mcp', false, false);


-- ============================================================================
-- Step 2: Grant permissions to the managed identity roles
-- ============================================================================

-- Grant permissions for Backend Container App
GRANT CONNECT ON DATABASE zava_logistics TO "zava-backend";
GRANT USAGE ON SCHEMA public TO "zava-backend";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "zava-backend";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "zava-backend";

-- Grant default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "zava-backend";
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO "zava-backend";


-- Grant permissions for MCP Server Container App
GRANT CONNECT ON DATABASE zava_logistics TO "zava-mcp";
GRANT USAGE ON SCHEMA public TO "zava-mcp";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "zava-mcp";  -- Read-only for MCP
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "zava-mcp";

-- Grant default privileges for future tables (read-only)
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO "zava-mcp";
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO "zava-mcp";


-- ============================================================================
-- Step 3: Verify the roles were created
-- ============================================================================

-- List all Azure AD principals
SELECT
    rolname,
    rolcanlogin,
    rolcreatedb,
    rolcreaterole
FROM pg_roles
WHERE rolname LIKE 'zava%';


-- ============================================================================
-- Troubleshooting Notes
-- ============================================================================
--
-- If you see "permission denied" errors:
-- 1. Ensure you're connected as an Azure AD administrator
-- 2. Verify the Container App names match exactly
-- 3. Check that the Container Apps have System-Assigned MI enabled
--
-- To check if Entra auth is enabled on your PostgreSQL:
--   az postgres flexible-server show --name <server> --resource-group <rg> \
--      --query "authConfig"
--
-- To verify a Container App has Managed Identity:
--   az containerapp show --name <app> --resource-group <rg> \
--      --query "identity"
--
-- Common issues:
-- - "role does not exist": The Container App MI hasn't been registered yet
--   Solution: Wait for Container App deployment to complete, then retry
--
-- - "permission denied for function pgaadauth_create_principal":
--   Solution: Connect as an Azure AD administrator, not a PostgreSQL admin
--
-- =============================================================================
