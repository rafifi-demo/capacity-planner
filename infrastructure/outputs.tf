# =============================================================================
# Zava Capacity Planner - Terraform Outputs
# =============================================================================

# =============================================================================
# Resource Group
# =============================================================================
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the resource group"
  value       = azurerm_resource_group.main.location
}

# =============================================================================
# Application URLs
# =============================================================================
output "frontend_url" {
  description = "URL of the frontend application"
  value       = "https://${azurerm_container_app.frontend.ingress[0].fqdn}"
}

output "backend_url" {
  description = "URL of the backend API"
  value       = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
}

output "apim_gateway_url" {
  description = "URL of the API Management gateway"
  value       = azurerm_api_management.main.gateway_url
}

# =============================================================================
# Azure AI Foundry
# =============================================================================
output "ai_project_endpoint" {
  description = "Azure AI Foundry project endpoint"
  value       = "https://${azurerm_cognitive_account.openai.custom_subdomain_name}.openai.azure.com/"
}

output "ai_model_deployment_name" {
  description = "GPT-5-mini model deployment name"
  value       = azapi_resource.gpt5_mini_deployment.name
}

# =============================================================================
# Database
# =============================================================================
output "postgres_host" {
  description = "PostgreSQL server hostname"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "postgres_database" {
  description = "PostgreSQL database name"
  value       = azurerm_postgresql_flexible_server_database.zava.name
}

# =============================================================================
# Monitoring
# =============================================================================
output "application_insights_connection_string" {
  description = "Application Insights connection string"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

# =============================================================================
# Container Registry
# =============================================================================
output "acr_login_server" {
  description = "Container registry login server"
  value       = azurerm_container_registry.main.login_server
}

output "acr_admin_username" {
  description = "Container registry admin username"
  value       = azurerm_container_registry.main.admin_username
}

# =============================================================================
# Storage
# =============================================================================
output "storage_account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.main.name
}

output "documents_container_name" {
  description = "Name of the documents container"
  value       = azurerm_storage_container.documents.name
}

# =============================================================================
# Managed Identity
# =============================================================================
output "backend_identity_principal_id" {
  description = "Principal ID of the backend Container App managed identity"
  value       = azurerm_container_app.backend.identity[0].principal_id
}

output "mcp_identity_principal_id" {
  description = "Principal ID of the MCP Container App managed identity"
  value       = azurerm_container_app.mcp.identity[0].principal_id
}

# =============================================================================
# Deployment Commands (for reference)
# =============================================================================
output "deployment_commands" {
  description = "Commands to deploy containers after infrastructure is ready"
  value       = <<-EOT

    # Login to Azure Container Registry
    az acr login --name ${azurerm_container_registry.main.name}

    # Build and push backend image
    cd backend
    docker build -t ${azurerm_container_registry.main.login_server}/zava-backend:latest .
    docker push ${azurerm_container_registry.main.login_server}/zava-backend:latest

    # Build and push frontend image
    cd ../frontend
    docker build -t ${azurerm_container_registry.main.login_server}/zava-frontend:latest .
    docker push ${azurerm_container_registry.main.login_server}/zava-frontend:latest

    # Seed the database (using password auth)
    psql "postgresql://${var.postgres_admin_username}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${azurerm_postgresql_flexible_server_database.zava.name}?sslmode=require" < ../data/seed_database.sql

    # =========================================================================
    # MANAGED IDENTITY SETUP (Required for passwordless auth)
    # =========================================================================
    # Connect as Azure AD administrator to create database roles:
    #
    # 1. Get your Azure AD token:
    #    az account get-access-token --resource-type oss-rdbms
    #
    # 2. Connect to PostgreSQL as Azure AD admin:
    #    psql "host=${azurerm_postgresql_flexible_server.main.fqdn} dbname=${azurerm_postgresql_flexible_server_database.zava.name} user=<your-azure-email> sslmode=require"
    #
    # 3. Run the managed identity setup script:
    #    \i ../data/create_managed_identity_user.sql
    #
    # After this, Container Apps will authenticate using Managed Identity
    # instead of password-based authentication.
    # =========================================================================

    # Open the application
    open https://${azurerm_container_app.frontend.ingress[0].fqdn}

  EOT
}
