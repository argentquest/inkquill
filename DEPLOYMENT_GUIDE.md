# Deployment Guide for RAG Story Application

This guide provides instructions for deploying the RAG Story Application to Azure App Service using various methods.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Azure Resources Setup](#azure-resources-setup)
- [Deployment Methods](#deployment-methods)
  - [Azure DevOps Pipeline](#azure-devops-pipeline)
  - [GitHub Actions](#github-actions)
  - [PowerShell Script](#powershell-script)
  - [Manual Deployment](#manual-deployment)
- [Configuration](#configuration)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

## Prerequisites

1. **Azure Subscription** with the following resources:
   - Azure App Service (Linux, Python 3.11)
   - Azure Database for PostgreSQL
   - Azure Storage Account
   - Azure Cognitive Search
   - Azure OpenAI Service
   - Azure Key Vault (recommended)

2. **Local Development Tools**:
   - Git
   - Python 3.11+
   - Azure CLI
   - PowerShell (for PS scripts)

3. **Service Connections**:
   - Azure DevOps Service Connection (for Azure DevOps)
   - GitHub Secrets (for GitHub Actions)

## Azure Resources Setup

### 1. Create App Service
```bash
# Create resource group
az group create --name rg-ragstory --location eastus

# Create App Service Plan
az appservice plan create \
  --name plan-ragstory \
  --resource-group rg-ragstory \
  --sku B2 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group rg-ragstory \
  --plan plan-ragstory \
  --name app-ragstory \
  --runtime "PYTHON:3.11"
```

### 2. Configure App Settings
```bash
# Set environment variables
az webapp config appsettings set \
  --resource-group rg-ragstory \
  --name app-ragstory \
  --settings \
    DATABASE_URL="postgresql+asyncpg://..." \
    AZURE_SEARCH_ENDPOINT="https://..." \
    OPENAI_API_BASE="https://..." \
    SECRET_KEY="your-secret-key"
```

### 3. Set Startup Command
```bash
az webapp config set \
  --resource-group rg-ragstory \
  --name app-ragstory \
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --timeout 120 app.main:app"
```

## Deployment Methods

### Azure DevOps Pipeline

1. **Create Pipeline**:
   - In Azure DevOps, create a new pipeline
   - Select your repository
   - Use the provided `azure-pipelines.yml`

2. **Configure Variables**:
   ```yaml
   # In Azure DevOps Pipeline Variables
   AZURE_SERVICE_CONNECTION: 'your-service-connection'
   AZURE_WEBAPP_NAME: 'app-ragstory'
   AZURE_RESOURCE_GROUP: 'rg-ragstory'
   ```

3. **Run Pipeline**:
   - Commit and push to trigger the pipeline
   - Monitor the deployment in Azure DevOps

### GitHub Actions

1. **Setup Secrets**:
   In GitHub repository settings, add these secrets:
   - `AZURE_WEBAPP_NAME`
   - `AZURE_CREDENTIALS` (Service Principal JSON)
   - `AZURE_WEBAPP_PUBLISH_PROFILE`

2. **Create Workflow**:
   ```bash
   mkdir -p .github/workflows
   cp scripts/github-actions-deploy.yml .github/workflows/deploy.yml
   ```

3. **Deploy**:
   - Push to `main` or `develop` branch
   - Check Actions tab for deployment status

### PowerShell Script

1. **Login to Azure**:
   ```powershell
   Connect-AzAccount
   ```

2. **Run Deployment**:
   ```powershell
   ./scripts/azure-deploy.ps1 `
     -ResourceGroup "rg-ragstory" `
     -AppServiceName "app-ragstory" `
     -Environment "production"
   ```

### Manual Deployment

1. **Create Deployment Package**:
   ```bash
   zip -r deploy.zip . -x ".git/*" ".venv/*" "*.pyc" "__pycache__/*"
   ```

2. **Deploy via Azure CLI**:
   ```bash
   az webapp deploy \
     --resource-group rg-ragstory \
     --name app-ragstory \
     --src-path deploy.zip \
     --type zip
   ```

## Configuration

### Environment Variables

Create `.env.production` with your production values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@server/dbname

# Azure Services
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_KEY_VAULT_URL=https://your-vault.vault.azure.net/
AZURE_STORAGE_ACCOUNT_NAME=yourstorageaccount
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net

# OpenAI
OPENAI_API_BASE=https://your-openai.openai.azure.com/
OPENAI_API_VERSION=2024-02-15-preview
OPENAI_DEPLOYMENT_NAME=gpt-4

# App Settings
SECRET_KEY=your-secret-key
ENVIRONMENT=production
```

### Using Azure Key Vault

Store sensitive values in Key Vault:

```bash
# Create Key Vault
az keyvault create \
  --name kv-ragstory \
  --resource-group rg-ragstory \
  --location eastus

# Add secrets
az keyvault secret set \
  --vault-name kv-ragstory \
  --name "DatabaseUrl" \
  --value "postgresql+asyncpg://..."

# Grant App Service access
az webapp identity assign \
  --resource-group rg-ragstory \
  --name app-ragstory

# Get identity principal ID
principalId=$(az webapp identity show \
  --resource-group rg-ragstory \
  --name app-ragstory \
  --query principalId -o tsv)

# Grant Key Vault access
az keyvault set-policy \
  --name kv-ragstory \
  --object-id $principalId \
  --secret-permissions get list
```

## Post-Deployment

### 1. Run Database Migrations

```bash
# SSH into App Service
az webapp ssh --resource-group rg-ragstory --name app-ragstory

# Run migrations
cd /home/site/wwwroot
alembic upgrade head
```

### 2. Verify Deployment

```bash
# Check app status
az webapp show --resource-group rg-ragstory --name app-ragstory --query state

# Test endpoints
curl https://app-ragstory.azurewebsites.net/docs
curl https://app-ragstory.azurewebsites.net/api/health
```

### 3. Monitor Logs

```bash
# Stream logs
az webapp log tail --resource-group rg-ragstory --name app-ragstory

# Download logs
az webapp log download --resource-group rg-ragstory --name app-ragstory
```

## Troubleshooting

### Common Issues

1. **"unicorn: not found" Error**
   - Fix: Change `unicorn` to `gunicorn` in startup command

2. **Database Connection Failed**
   - Check DATABASE_URL format
   - Verify PostgreSQL firewall rules
   - Ensure SSL mode is set correctly

3. **Module Import Errors**
   - Verify all dependencies in requirements.txt
   - Check Python version compatibility

4. **Static Files Not Serving**
   - Add whitenoise to requirements.txt
   - Configure static file handling in app

### Debug Commands

```bash
# Check app settings
az webapp config appsettings list \
  --resource-group rg-ragstory \
  --name app-ragstory

# View container logs
az webapp log show \
  --resource-group rg-ragstory \
  --name app-ragstory

# SSH into container
az webapp ssh \
  --resource-group rg-ragstory \
  --name app-ragstory
```

### Performance Optimization

1. **Enable Always On**:
   ```bash
   az webapp config set \
     --resource-group rg-ragstory \
     --name app-ragstory \
     --always-on true
   ```

2. **Configure Auto-scaling**:
   ```bash
   az monitor autoscale create \
     --resource-group rg-ragstory \
     --resource app-ragstory \
     --resource-type Microsoft.Web/serverfarms \
     --name autoscale-ragstory \
     --min-count 1 \
     --max-count 4 \
     --count 2
   ```

3. **Enable Application Insights**:
   ```bash
   az monitor app-insights component create \
     --app insights-ragstory \
     --location eastus \
     --resource-group rg-ragstory
   ```

## Security Best Practices

1. **Use Managed Identity** for Azure service authentication
2. **Store secrets in Key Vault**, not in app settings
3. **Enable HTTPS Only**:
   ```bash
   az webapp update \
     --resource-group rg-ragstory \
     --name app-ragstory \
     --https-only true
   ```
4. **Implement IP Restrictions** for admin endpoints
5. **Regular security updates** for dependencies

## Backup and Recovery

1. **Database Backup**:
   ```bash
   az postgres flexible-server backup list \
     --resource-group rg-ragstory \
     --name postgres-ragstory
   ```

2. **App Service Backup**:
   ```bash
   az webapp config backup create \
     --resource-group rg-ragstory \
     --webapp-name app-ragstory \
     --backup-name backup-$(date +%Y%m%d%H%M%S)
   ```

## Support

For issues or questions:
1. Check Azure App Service logs
2. Review application logs in `/home/LogFiles/`
3. Consult Azure documentation
4. Open an issue in the project repository