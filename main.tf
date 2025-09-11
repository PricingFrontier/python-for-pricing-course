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
# App Service Plan (Linux)
# ------------------------
resource "azurerm_service_plan" "plan" {
  name                = "pricingdemo-fastapi-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "B1"
}

# ------------------------
# Linux Web App (Docker)
# ------------------------
resource "azurerm_linux_web_app" "app" {
  name                = "pricingdemo-fastapi-webapp"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      docker_image_name      = "fastapi-mlflow:latest"
      docker_registry_url    = "https://${azurerm_container_registry.acr.login_server}"
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
    }
  }

  app_settings = {
    WEBSITES_PORT = "80"
  }
}

# ------------------------
# Outputs
# ------------------------
output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "web_app_url" {
  value = azurerm_linux_web_app.app.default_hostname
}
