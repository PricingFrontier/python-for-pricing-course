provider "azurerm" {
  features {}

  subscription_id = "1bfa4a42-039e-4cb4-aaa2-3721db1a4c51"
  tenant_id       = "9e2012b9-0af5-4f8b-985c-43cc6fb1afad"
}

# ------------------------
# Resource Group
# ------------------------
resource "azurerm_resource_group" "rg" {
  name     = "demo-fastapi"
  location = "UK South"
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
# Storage Account (required for Function App)
# ------------------------
resource "azurerm_storage_account" "storage" {
  name                     = "pricedemofastapistorage"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# ------------------------
# App Service Plan (for Function App)
# ------------------------
resource "azurerm_service_plan" "plan" {
  name                = "pricingdemo-fastapi-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "Y1"       # Dynamic consumption plan
}

# ------------------------
# Function App (Linux, Docker)
# ------------------------
resource "azurerm_function_app" "func" {
  name                       = "pricingdemo-fastapi-function"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  app_service_plan_id        = azurerm_service_plan.plan.id
  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key
  version                    = "~4"
  os_type                    = "linux"

  site_config {
    linux_fx_version = "DOCKER|pricingdemofastapiregistry.azurecr.io/fastapi-mlflow:latest"
  }

  app_settings = {
    FUNCTIONS_WORKER_RUNTIME = "python"
    WEBSITE_RUN_FROM_PACKAGE  = "1"
  }
}

# ------------------------
# Outputs
# ------------------------
output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "function_app_url" {
  value = azurerm_function_app.func.default_hostname
}
