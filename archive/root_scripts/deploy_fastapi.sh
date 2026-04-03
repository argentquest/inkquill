#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
APP_NAME="AQDEVV2"
RESOURCE_GROUP="whisperwynd"
ZIP_FILE="app.zip"
APP_DIR="."

# --- Script Logic ---


echo "Step 1/6: Preparing deployment package..."
zip -r "$ZIP_FILE" . -x "*.venv/*" ".git/*" "**/__pycache__/*" "*.DS_Store" "tests/*" "docs/*" "Documentation/*" "*.log" "logs/*" "Social/*" "Video/*"

echo "Step 2/6: Deploying application code to Azure App Service: $APP_NAME..."
az webapp deployment source config-zip --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src "$ZIP_FILE"

echo "Step 3/6: Preparing environment variables..."
SETTINGS_STRING=$(grep -v '^#' .env | grep -v '^$' | sed 's/\r$//' | awk '{printf "%s ", $0}')

if [ -n "$SETTINGS_STRING" ]; then
    echo "Step 4/6: Injecting environment variables into Azure App Service..."
    az webapp config appsettings set \
      --resource-group "$RESOURCE_GROUP" \
      --name "$APP_NAME" \
      --settings $SETTINGS_STRING
else
    echo "Step 4/6: Warning - No environment variables found in .env file to set."
fi

echo "Step 5/6: Setting startup command..."
az webapp config set \
  --resource-group "$RESOURCE_GROUP" \
  --name "$APP_NAME" \
  --startup-file "startup.sh"

echo "Step 6/6: Cleaning up local deployment package..."
rm "$ZIP_FILE"

echo "✅ Deployment script finished successfully!"