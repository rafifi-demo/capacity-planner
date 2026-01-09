# =============================================================================
# Zava Capacity Planner - Main Terraform Configuration
# =============================================================================
# This configuration deploys all Azure resources for the demo application.
#
# Resources deployed:
# - Resource Group
# - Azure AI Foundry Project (V1)
# - Azure OpenAI with GPT-5-mini deployment
# - PostgreSQL Flexible Server
# - Azure Storage Account (for documents)
# - API Management (Consumption tier)
# - Application Insights
# - Container Apps Environment
# - Container Registry
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    azapi = {
      source  = "azure/azapi"
      version = "~> 1.10"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    cognitive_account {
      purge_soft_delete_on_destroy = true
    }
  }
  subscription_id = var.subscription_id
}

provider "azapi" {}

# =============================================================================
# Random suffix for unique names
# =============================================================================
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  resource_suffix = random_string.suffix.result
  name_prefix     = "zava"

  tags = {
    Environment = var.environment
    Project     = "Zava Capacity Planner"
    ManagedBy   = "Terraform"
  }
}

# =============================================================================
# Resource Group
# =============================================================================
resource "azurerm_resource_group" "main" {
  name     = "${local.name_prefix}-rg-${local.resource_suffix}"
  location = var.location

  tags = local.tags
}

# =============================================================================
# Log Analytics Workspace (for Application Insights)
# =============================================================================
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.name_prefix}-logs-${local.resource_suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = local.tags
}

# =============================================================================
# Application Insights
# =============================================================================
resource "azurerm_application_insights" "main" {
  name                = "${local.name_prefix}-insights-${local.resource_suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"

  tags = local.tags
}

# =============================================================================
# Azure Cognitive Services Account (for AI Foundry)
# =============================================================================
resource "azurerm_cognitive_account" "openai" {
  name                  = "${local.name_prefix}-openai-${local.resource_suffix}"
  location              = var.location
  resource_group_name   = azurerm_resource_group.main.name
  kind                  = "OpenAI"
  sku_name              = "S0"
  custom_subdomain_name = "${local.name_prefix}-openai-${local.resource_suffix}"

  network_acls {
    default_action = "Allow"
  }

  tags = local.tags
}

# =============================================================================
# GPT-5-mini Model Deployment (using azapi due to azurerm compatibility issues)
# =============================================================================
resource "azapi_resource" "gpt5_mini_deployment" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2024-06-01-preview"
  name      = "gpt-5-mini"
  parent_id = azurerm_cognitive_account.openai.id

  body = {
    properties = {
      model = {
        format  = "OpenAI"
        name    = "gpt-5-mini"
        version = "2025-08-07"
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"
    }
    sku = {
      name     = "GlobalStandard"
      capacity = 10
    }
  }
}

# =============================================================================
# Azure AI Foundry Hub (required parent for Projects)
# =============================================================================
resource "azapi_resource" "ai_hub" {
  type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01"
  name      = "${local.name_prefix}-ai-hub-${local.resource_suffix}"
  location  = azurerm_resource_group.main.location
  parent_id = azurerm_resource_group.main.id

  identity {
    type = "SystemAssigned"
  }

  body = jsonencode({
    properties = {
      friendlyName        = "Zava AI Hub"
      description         = "AI Foundry Hub for Zava capacity planning"
      publicNetworkAccess = "Enabled"
      applicationInsights = azurerm_application_insights.main.id
      keyVault            = azurerm_key_vault.main.id
      storageAccount      = azurerm_storage_account.main.id
    }
    kind = "Hub"
    sku = {
      name = "Basic"
      tier = "Basic"
    }
  })

  tags = local.tags

  depends_on = [
    azurerm_application_insights.main,
    azurerm_key_vault.main,
    azurerm_storage_account.main
  ]
}

# =============================================================================
# Azure AI Foundry Project (using azapi for V1 features)
# =============================================================================
resource "azapi_resource" "ai_project" {
  type      = "Microsoft.MachineLearningServices/workspaces@2024-04-01"
  name      = "${local.name_prefix}-ai-project-${local.resource_suffix}"
  location  = azurerm_resource_group.main.location
  parent_id = azurerm_resource_group.main.id

  identity {
    type = "SystemAssigned"
  }

  body = jsonencode({
    properties = {
      friendlyName        = "Zava Capacity Planner AI Project"
      description         = "AI Foundry project for capacity planning agents"
      publicNetworkAccess = "Enabled"
      hubResourceId       = azapi_resource.ai_hub.id
    }
    kind = "Project"
    sku = {
      name = "Basic"
      tier = "Basic"
    }
  })

  tags = local.tags

  depends_on = [
    azapi_resource.ai_hub
  ]
}

# =============================================================================
# Key Vault (required for AI project)
# =============================================================================
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                       = "${local.name_prefix}kv${local.resource_suffix}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge"
    ]
  }

  tags = local.tags
}

# =============================================================================
# Storage Account (for documents and File Search)
# =============================================================================
resource "azurerm_storage_account" "main" {
  name                     = "${local.name_prefix}stor${local.resource_suffix}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  blob_properties {
    cors_rule {
      allowed_headers    = ["*"]
      allowed_methods    = ["GET", "HEAD", "POST", "PUT"]
      allowed_origins    = ["*"]
      exposed_headers    = ["*"]
      max_age_in_seconds = 3600
    }
  }

  tags = local.tags
}

resource "azurerm_storage_container" "documents" {
  name                  = "documents"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# =============================================================================
# PostgreSQL Flexible Server
# =============================================================================
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${local.name_prefix}-postgres-${local.resource_suffix}"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "16"
  administrator_login    = var.postgres_admin_username
  administrator_password = var.postgres_admin_password

  sku_name   = "B_Standard_B1ms"  # Burstable tier - cost effective for demo
  storage_mb = 32768

  backup_retention_days = 7
  # zone removed - let Azure choose available zone

  # Enable Microsoft Entra (Azure AD) authentication for Managed Identity
  authentication {
    active_directory_auth_enabled = true
    password_auth_enabled         = true  # Keep password auth as fallback
    tenant_id                     = data.azurerm_client_config.current.tenant_id
  }

  tags = local.tags
}

# Microsoft Entra Administrator for PostgreSQL
# This allows the Terraform user to create managed identity roles
resource "azurerm_postgresql_flexible_server_active_directory_administrator" "main" {
  server_name         = azurerm_postgresql_flexible_server.main.name
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  object_id           = data.azurerm_client_config.current.object_id
  principal_name      = "terraform-admin"
  principal_type      = "User"
}

resource "azurerm_postgresql_flexible_server_database" "zava" {
  name      = "zava_logistics"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Allow Azure services to access PostgreSQL
resource "azurerm_postgresql_flexible_server_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# =============================================================================
# API Management (Consumption Tier)
# =============================================================================
resource "azurerm_api_management" "main" {
  name                = "${local.name_prefix}-apim-${local.resource_suffix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  publisher_name      = "Zava Logistics"
  publisher_email     = var.apim_publisher_email
  sku_name            = "Consumption_0"

  tags = local.tags
}

# API for MCP Server
resource "azurerm_api_management_api" "mcp" {
  name                = "mcp-api"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main.name
  revision            = "1"
  display_name        = "MCP PostgreSQL API"
  path                = "mcp"
  protocols           = ["https"]
  service_url         = "https://${azurerm_container_app.mcp.ingress[0].fqdn}"

  subscription_required = true
}

# =============================================================================
# Container Registry
# =============================================================================
resource "azurerm_container_registry" "main" {
  name                = "${local.name_prefix}acr${local.resource_suffix}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = local.tags
}

# =============================================================================
# Container Apps Environment
# =============================================================================
resource "azurerm_container_app_environment" "main" {
  name                       = "${local.name_prefix}-cae-${local.resource_suffix}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  tags = local.tags
}

# =============================================================================
# Container App - Backend API
# =============================================================================
resource "azurerm_container_app" "backend" {
  name                         = "${local.name_prefix}-backend"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  # Enable System-Assigned Managed Identity for passwordless PostgreSQL auth
  identity {
    type = "SystemAssigned"
  }

  template {
    container {
      name   = "backend"
      image  = "${azurerm_container_registry.main.login_server}/zava-backend:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "AZURE_AI_PROJECT_ENDPOINT"
        value = "https://${azurerm_cognitive_account.openai.custom_subdomain_name}.openai.azure.com/"
      }
      env {
        name  = "AZURE_AI_MODEL_DEPLOYMENT_NAME"
        value = azapi_resource.gpt5_mini_deployment.name
      }
      env {
        name  = "POSTGRES_HOST"
        value = azurerm_postgresql_flexible_server.main.fqdn
      }
      env {
        name  = "POSTGRES_DATABASE"
        value = azurerm_postgresql_flexible_server_database.zava.name
      }
      # Managed Identity: User is the Container App name
      env {
        name  = "POSTGRES_USER"
        value = "${local.name_prefix}-backend"
      }
      # Enable Managed Identity authentication
      env {
        name  = "USE_MANAGED_IDENTITY"
        value = "true"
      }
      # Keep password for fallback (optional, can be removed once MI is verified)
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "postgres-password"
      }
      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = azurerm_application_insights.main.connection_string
      }
    }

    min_replicas = 0
    max_replicas = 3
  }

  secret {
    name  = "postgres-password"
    value = var.postgres_admin_password
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }

  tags = local.tags
}

# =============================================================================
# Container App - Frontend
# =============================================================================
resource "azurerm_container_app" "frontend" {
  name                         = "${local.name_prefix}-frontend"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    container {
      name   = "frontend"
      image  = "${azurerm_container_registry.main.login_server}/zava-frontend:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "VITE_API_URL"
        value = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
      }
    }

    min_replicas = 0
    max_replicas = 3
  }

  ingress {
    external_enabled = true
    target_port      = 80
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }

  tags = local.tags
}

# =============================================================================
# Container App - MCP Server
# =============================================================================
resource "azurerm_container_app" "mcp" {
  name                         = "${local.name_prefix}-mcp"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  # Enable System-Assigned Managed Identity for passwordless PostgreSQL auth
  identity {
    type = "SystemAssigned"
  }

  template {
    container {
      name   = "mcp"
      image  = "${azurerm_container_registry.main.login_server}/zava-backend:latest"
      cpu    = 0.25
      memory = "0.5Gi"

      command = ["python", "-m", "app.mcp.postgres_server"]

      env {
        name  = "POSTGRES_HOST"
        value = azurerm_postgresql_flexible_server.main.fqdn
      }
      env {
        name  = "POSTGRES_DATABASE"
        value = azurerm_postgresql_flexible_server_database.zava.name
      }
      # Managed Identity: User is the Container App name
      env {
        name  = "POSTGRES_USER"
        value = "${local.name_prefix}-mcp"
      }
      # Enable Managed Identity authentication
      env {
        name  = "USE_MANAGED_IDENTITY"
        value = "true"
      }
      # Keep password for fallback (optional, can be removed once MI is verified)
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "postgres-password"
      }
    }

    min_replicas = 0
    max_replicas = 2
  }

  secret {
    name  = "postgres-password"
    value = var.postgres_admin_password
  }

  ingress {
    external_enabled = false  # Only accessible through APIM
    target_port      = 8001
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  registry {
    server               = azurerm_container_registry.main.login_server
    username             = azurerm_container_registry.main.admin_username
    password_secret_name = "registry-password"
  }

  secret {
    name  = "registry-password"
    value = azurerm_container_registry.main.admin_password
  }

  tags = local.tags
}
