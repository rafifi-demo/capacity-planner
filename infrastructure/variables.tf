# =============================================================================
# Zava Capacity Planner - Terraform Variables
# =============================================================================

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "westus"  # GPT-5-mini available in West US
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "demo"
}

# =============================================================================
# PostgreSQL Configuration
# =============================================================================

variable "postgres_admin_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "zava_admin"
}

variable "postgres_admin_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true
}

# =============================================================================
# API Management Configuration
# =============================================================================

variable "apim_publisher_email" {
  description = "Email for API Management publisher"
  type        = string
  default     = "admin@zava-logistics.com"
}
