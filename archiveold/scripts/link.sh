#!/bin/bash

# Configuration
APP_NAME="AQDEVV2"
RESOURCE_GROUP="whisperwynd"

echo "Checking current Azure App Service settings..."
echo "==========================================="

# Get all app settings
echo "Fetching all app settings from Azure..."
az webapp config appsettings list \
  --name "$APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --output json > current_settings.json

# Check if BACKEND_CORS_ORIGINS exists
echo -e "\nChecking BACKEND_CORS_ORIGINS setting:"
CORS_SETTING=$(cat current_settings.json | jq -r '.[] | select(.name == "BACKEND_CORS_ORIGINS") | .value')

if [ -n "$CORS_SETTING" ]; then
    echo "Found BACKEND_CORS_ORIGINS:"
    echo "Raw value: $CORS_SETTING"
    echo "Length: ${#CORS_SETTING}"
    
    # Show hex dump of first few characters to debug
    echo -e "\nFirst 50 characters (hex dump):"
    echo -n "$CORS_SETTING" | head -c 50 | od -An -tx1
    
    # Try to validate as JSON
    echo -e "\n\nValidating as JSON:"
    if echo "$CORS_SETTING" | jq . >/dev/null 2>&1; then
        echo "✓ Valid JSON"
        echo "Parsed value:"
        echo "$CORS_SETTING" | jq .
    else
        echo "✗ Invalid JSON"
        echo "JSON Error:"
        echo "$CORS_SETTING" | jq . 2>&1
    fi
else
    echo "BACKEND_CORS_ORIGINS not found in app settings!"
fi

# Show a few other settings to compare format
echo -e "\n\nOther settings (first 5):"
cat current_settings.json | jq -r '.[:5] | .[] | "\(.name) = \(.value)"'

# Cleanup
rm -f current_settings.json

echo -e "\n\nTo fix BACKEND_CORS_ORIGINS, run:"
echo "az webapp config appsettings set \\"
echo "  --name $APP_NAME \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo '  --settings BACKEND_CORS_ORIGINS='\''["*"]'\'