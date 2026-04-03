# Deployment and Infrastructure Architecture

## Table of Contents
- [Infrastructure Overview](#infrastructure-overview)
- [Azure Architecture](#azure-architecture)
- [Container Architecture](#container-architecture)
- [Deployment Pipeline](#deployment-pipeline)
- [Environment Configuration](#environment-configuration)
- [Infrastructure as Code](#infrastructure-as-code)
- [Monitoring and Observability](#monitoring-and-observability)

## Infrastructure Overview

The storytelling platform is deployed on Microsoft Azure using a containerized architecture with Azure App Service, providing scalable, managed hosting with integrated CI/CD pipelines.

### Architecture Principles

#### Cloud-Native Design
- **Managed Services**: Leveraging Azure PaaS services for reduced operational overhead
- **Scalability**: Auto-scaling capabilities for handling variable workloads
- **Resilience**: Multi-region deployment options and built-in redundancy
- **Security**: Azure security features and compliance standards

#### Container-First Approach
- **Docker Containerization**: Application packaged as Docker containers
- **Consistent Environments**: Same container runs in dev, staging, and production
- **Resource Efficiency**: Optimized container images for faster deployments
- **Portability**: Easy migration between environments and cloud providers

## Azure Architecture

### High-Level Azure Infrastructure

The platform utilizes multiple Azure services organized within the "whisperwynd" resource group:

#### Compute Services
- **Azure App Service**: Linux-based container hosting with Python 3.11 runtime
- **App Service Plan**: B2 tier providing shared infrastructure with auto-scaling

#### Data Services
- **Azure Database for PostgreSQL**: Flexible Server with automated backups and SSL encryption
- **Azure Storage Account**: Blob storage for files and static content

#### AI Services
- **Azure OpenAI Service**: GPT-4 models and embedding models with content filtering
- **Azure Cognitive Search**: Vector search capabilities with full-text search and AI enrichment

#### Security Services
- **Azure Key Vault**: Secret management and certificate storage
- **Managed Identity**: Service authentication with zero-credential access

#### Monitoring Services
- **Application Insights**: Performance monitoring and error tracking
- **Azure Monitor**: Log aggregation and alerting rules

### Azure Service Configuration

#### App Service Configuration
```yaml
app_service:
  name: "AQDEVV2"
  resource_group: "whisperwynd"
  plan: "B2"
  runtime: "PYTHON|3.11"
  platform: "Linux"
  
  settings:
    always_on: true
    https_only: true
    http20_enabled: true
    ftps_state: "Disabled"
    
  startup_command: |
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker 
    -b 0.0.0.0:8000 --timeout 120 app.main:app
    
  scaling:
    min_instances: 1
    max_instances: 4
    scale_out_cpu_threshold: 70
    scale_in_cpu_threshold: 30
```

#### Database Configuration
```yaml
postgresql:
  server_name: "postgres-ragstory"
  version: "14"
  tier: "Burstable"
  sku: "Standard_B2s"
  
  configuration:
    ssl_enforcement: "Enabled"
    backup_retention_days: 7
    geo_redundant_backup: "Disabled"
    auto_grow: "Enabled"
    
  firewall_rules:
    - name: "AllowAzureServices"
      start_ip: "0.0.0.0"
      end_ip: "0.0.0.0"
```##
 Container Architecture

### Docker Container Design

#### Multi-Stage Dockerfile
The application uses a multi-stage Docker build process for optimization:

**Build Stage**: Optimized for dependency installation
- Uses Python 3.11 slim base image
- Installs build dependencies (build-essential, libpq-dev)
- Creates wheel files for all Python dependencies
- Minimizes build context and layer size

**Runtime Stage**: Minimal production image
- Clean Python 3.11 slim base image
- Installs only runtime dependencies (libpq5)
- Copies pre-built wheel files from build stage
- Creates non-root user for security
- Exposes port 8000 for application access

#### Container Security Features
- **Non-root execution**: Application runs as dedicated user (appuser:appgroup)
- **Minimal attack surface**: Only essential packages installed
- **Layer optimization**: Efficient Docker layer caching
- **Resource constraints**: CPU and memory limits configured

### Local Development with Docker Compose

The docker-compose.yml provides a complete local development environment:

#### Application Service
- Hot reload enabled for development
- Environment variables loaded from .env file
- Port mapping for local access (8000:8000)
- Volume mounting for code changes

#### Database Service
- PostgreSQL 15 Alpine image for lightweight footprint
- Persistent data volume for development continuity
- Health checks for service readiness
- Port exposure for direct database access

## Deployment Pipeline

### Azure DevOps Pipeline Architecture

The deployment pipeline follows a multi-stage approach:

#### Build Stage
1. **Code Checkout**: Clean repository checkout with submodule support
2. **Environment Setup**: Python 3.11 installation and virtual environment creation
3. **Dependency Installation**: Requirements installation with caching
4. **Quality Checks**: Linting with flake8 and code style validation
5. **Testing**: Unit test execution with pytest and coverage reporting
6. **Artifact Creation**: Application packaging with exclusion of development files

#### Quality Gates
- **Code Linting**: Flake8 checks for code style and potential issues
- **Unit Testing**: Comprehensive test suite execution with coverage metrics
- **Security Scanning**: Dependency vulnerability checks and SAST analysis

#### Deployment Stages
- **Development Deployment**: Automatic deployment on develop branch commits
- **Production Deployment**: Manual approval required for main branch deployments
- **Database Migrations**: Automated Alembic migrations post-deployment
- **Health Verification**: Endpoint checks and smoke tests

### Pipeline Configuration

#### Build Stage Configuration
```yaml
stages:
- stage: Build
  displayName: 'Build stage'
  jobs:
  - job: BuildJob
    displayName: 'Build Job'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - checkout: self
      displayName: 'Checkout code'
      clean: true

    - task: UsePythonVersion@0
      displayName: 'Use Python 3.11'
      inputs:
        versionSpec: '3.11'
        addToPath: true

    - script: |
        python -m venv venv
        source venv/bin/activate
        python -m pip install --upgrade pip
        pip install -r requirements.txt
      displayName: 'Install dependencies'

    - script: |
        source venv/bin/activate
        pip install flake8
        flake8 app --config=.flake8
      displayName: 'Run linting'

    - script: |
        source venv/bin/activate
        pytest tests/ -v --junitxml=test-results.xml
      displayName: 'Run tests'
```

#### Deployment Configuration
```yaml
- stage: DeployProd
  displayName: 'Deploy to Production'
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeploymentJob
    displayName: 'Deploy to Production Environment'
    pool:
      vmImage: 'ubuntu-latest'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            displayName: 'Deploy to Azure App Service'
            inputs:
              azureSubscription: '$(azureServiceConnectionId)'
              appType: 'webAppLinux'
              appName: '$(webAppName)'
              package: '$(Pipeline.Workspace)/drop/$(Build.BuildId).zip'
              runtimeStack: 'PYTHON|3.11'
              startUpCommand: 'gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 120 app.main:app'
```#
# Environment Configuration

### Environment-Specific Settings

#### Development Environment
```yaml
environment: development
debug: true
log_level: DEBUG

database:
  url: "postgresql+asyncpg://dev_user:dev_pass@localhost:5432/dev_db"
  echo_sql: true
  pool_size: 5

azure_services:
  use_emulator: true
  storage_account: "devstorageaccount"
  search_service: "dev-search-service"

ai_services:
  openai_endpoint: "https://dev-openai.openai.azure.com/"
  model_deployment: "gpt-4-dev"
  rate_limits:
    requests_per_minute: 100
```

#### Production Environment
```yaml
environment: production
debug: false
log_level: INFO

database:
  url: "${DATABASE_URL}"  # From Key Vault
  echo_sql: false
  pool_size: 20
  pool_timeout: 30

azure_services:
  use_managed_identity: true
  storage_account: "${AZURE_STOContextE_ACCOUNT_NAME}"
  search_service: "${AZURE_SEARCH_SERVICE_NAME}"

ai_services:
  openai_endpoint: "${AZURE_OPENAI_ENDPOINT}"
  model_deployment: "gpt-4-production"
  rate_limits:
    requests_per_minute: 1000

security:
  https_only: true
  cors_origins: ["https://yourdomain.com"]
  trusted_hosts: ["yourdomain.com", "*.yourdomain.com"]
```

### Configuration Management

#### Azure Key Vault Integration
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class ConfigurationManager:
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.key_vault_url = os.getenv("AZURE_KEY_VAULT_URL")
        self.secret_client = SecretClient(
            vault_url=self.key_vault_url,
            credential=self.credential
        ) if self.key_vault_url else None
    
    def get_secret(self, secret_name: str, default: str = None) -> str:
        """Get secret from Key Vault or environment variable."""
        # Try Key Vault first
        if self.secret_client:
            try:
                secret = self.secret_client.get_secret(secret_name)
                return secret.value
            except Exception as e:
                logger.warning(f"Failed to get secret {secret_name} from Key Vault: {e}")
        
        # Fallback to environment variable
        return os.getenv(secret_name, default)
```

## Infrastructure as Code

### ARM Templates

#### Resource Group Template
```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "appServiceName": {
            "type": "string",
            "metadata": {
                "description": "Name of the App Service"
            }
        },
        "appServicePlanName": {
            "type": "string",
            "metadata": {
                "description": "Name of the App Service Plan"
            }
        },
        "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources"
            }
        }
    },
    "resources": [
        {
            "type": "Microsoft.Web/serverfarms",
            "apiVersion": "2021-02-01",
            "name": "[parameters('appServicePlanName')]",
            "location": "[parameters('location')]",
            "sku": {
                "name": "B2",
                "tier": "Basic"
            },
            "kind": "linux",
            "properties": {
                "reserved": true
            }
        },
        {
            "type": "Microsoft.Web/sites",
            "apiVersion": "2021-02-01",
            "name": "[parameters('appServiceName')]",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[resourceId('Microsoft.Web/serverfarms', parameters('appServicePlanName'))]"
            ],
            "properties": {
                "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', parameters('appServicePlanName'))]",
                "siteConfig": {
                    "linuxFxVersion": "PYTHON|3.11",
                    "alwaysOn": true,
                    "httpsOnly": true
                }
            }
        }
    ]
}
```

### Terraform Configuration

#### Main Infrastructure
```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

# App Service Plan
resource "azurerm_service_plan" "main" {
  name                = var.app_service_plan_name
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  os_type            = "Linux"
  sku_name           = "B2"
}

# App Service
resource "azurerm_linux_web_app" "main" {
  name                = var.app_service_name
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_service_plan.main.location
  service_plan_id    = azurerm_service_plan.main.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
    always_on = true
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STOContextE" = "false"
    "DATABASE_URL"                        = var.database_url
    "AZURE_OPENAI_ENDPOINT"              = var.openai_endpoint
  }

  identity {
    type = "SystemAssigned"
  }
}
```

## Monitoring and Observability

### Application Insights Integration

The platform integrates with Azure Application Insights for comprehensive monitoring:

#### Monitoring Components
- **Application Performance Monitoring**: Request tracking, response times, and dependency calls
- **Error Tracking**: Exception capture and error rate monitoring
- **Custom Events**: Business logic tracking and user interaction metrics
- **Distributed Tracing**: End-to-end request flow visualization

#### Monitoring Configuration
```python
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer

class MonitoringService:
    def __init__(self):
        self.connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        self.tracer = Tracer(
            exporter=AzureExporter(connection_string=self.connection_string),
            sampler=ProbabilitySampler(1.0)
        )
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.addHandler(
            AzureLogHandler(connection_string=self.connection_string)
        )
    
    def track_custom_event(self, name: str, properties: dict = None):
        """Track custom application events."""
        from applicationinsights import TelemetryClient
        tc = TelemetryClient(self.connection_string)
        tc.track_event(name, properties)
        tc.flush()
    
    def track_dependency(self, name: str, data: str, duration: float, success: bool):
        """Track external dependency calls."""
        from applicationinsights import TelemetryClient
        tc = TelemetryClient(self.connection_string)
        tc.track_dependency(name, data, duration, success)
        tc.flush()
```

### Alerting and Dashboard Configuration

#### Alert Rules
- **Error Rate Alerts**: Trigger when error rate exceeds 5% over 5 minutes
- **Performance Alerts**: Trigger when average response time exceeds 2 seconds
- **Availability Alerts**: Trigger when availability drops below 99%
- **Dependency Alerts**: Trigger when external service calls fail

#### Dashboard Metrics
- **Request Volume**: Real-time request count and trends
- **Response Times**: Average, 95th percentile, and maximum response times
- **Error Rates**: Error percentage and error count over time
- **Resource Utilization**: CPU, memory, and disk usage metrics

---
**Document Information:**
- Last Updated: 2025-07-14
- Version: 1.0.0
- Author: Architecture Team
- Reviewers: DevOps Team, Infrastructure Team
