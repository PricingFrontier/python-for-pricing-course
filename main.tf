terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.70"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
}

variable "subscription_id" {}
variable "tenant_id" {}

# ------------------------
# Locals
# ------------------------
locals {
  rg_name     = "demo-fastapi"
  rg_location = "UK South"
}

# ------------------------
# Resource Group
# ------------------------
resource "azurerm_resource_group" "rg" {
  name     = local.rg_name
  location = local.rg_location
}

# ------------------------
# Azure Container Registry
# ------------------------
resource "azurerm_container_registry" "acr" {
  name                = "pricingdemofastapiregistry"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

# ------------------------
# Log Analytics Workspace (needed for Container Apps env)
# ------------------------
resource "azurerm_log_analytics_workspace" "log" {
  name                = "pricingdemo-logs"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# ------------------------
# Container App Environment
# ------------------------
resource "azurerm_container_app_environment" "env" {
  name                       = "pricingdemo-env"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log.id
}

# ------------------------
# Container App (replaces Linux Web App)
# ------------------------
resource "azurerm_container_app" "app" {
  name                        = "pricingdemo-fastapi"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "fastapi"
      image  = "${azurerm_container_registry.acr.login_server}/fastapi-mlflow:latest"
      cpu    = 0.5
      memory = "1.0Gi"
    }
  }

  registry {
    server             = azurerm_container_registry.acr.login_server
    username           = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-pwd"
  }

  secret {
    name  = "acr-pwd"
    value = azurerm_container_registry.acr.admin_password
  }

  ingress {
    external_enabled = true
    target_port      = 80

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

# ------------------------
# Outputs
# ------------------------
output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "web_app_url" {
  value = azurerm_container_app.app.latest_revision_fqdn
}
