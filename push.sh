#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
APP_NAME="AQDEVV2"
RESOURCE_GROUP="whisperwynd"
ZIP_FILE="app.zip"
APP_DIR="."

# --- Script Logic ---

cd "$APP_DIR" || { echo "Error: Project directory not found." >&2; exit 1; }

echo "Processing environment variables from .env file..."

# Create an array to store settings
declare -a SETTINGS_ARRAY

# Read .env file line by line
while IFS= read -r line || [ -n "$line" ]; do
    # Remove any inline comments (everything after # that's not inside quotes)
    line=$(echo "$line" | sed 's/\([^"'"'"']*\)[[:space:]]*#.*/\1/')
    
    # Remove leading/trailing whitespace and carriage returns
    line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/\r$//')
    
    # Skip empty lines and lines that start with #
    if [[ -z "$line" ]] || [[ "$line" =~ ^# ]]; then
        continue
    fi
    
    # Check if line contains an equals sign
    if [[ "$line" == *"="* ]]; then
        # Extract key and value
        key="${line%%=*}"
        value="${line#*=}"
        
        # Trim whitespace from key
        key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Skip if key is empty
        if [[ -z "$key" ]]; then
            echo "Warning: Skipping line with empty key: $line"
            continue
        fi
        
        # Remove quotes from value if present
        value="${value#\"}"
        value="${value%\"}"
        value="${value#\'}"
        value="${value%\'}"
        
        # Check if value is a number (integer or decimal)
        if [[ $value =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
            # It's a number, keep it as is
            SETTINGS_ARRAY+=("$key=$value")
            echo "  Found: $key = $value (numeric)"
        else
            # It's not a number, add quotes for Azure CLI
            # Escape special characters for shell
            value="${value//\\/\\\\}"
            value="${value//\"/\\\"}"
            SETTINGS_ARRAY+=("$key=\"$value\"")
            echo "  Found: $key = ${value:0:50}... (string)"
        fi
    else
        echo "Warning: Skipping invalid line (no '=' found): $line"
    fi
done < .env

if [ ${#SETTINGS_ARRAY[@]} -gt 0 ]; then
    echo -e "\nStep 4/6: Injecting ${#SETTINGS_ARRAY[@]} environment variables into Azure App Service..."
    
    # Debug: Show first few settings
    echo "First few settings to be applied:"
    for i in {0..2}; do
        if [ $i -lt ${#SETTINGS_ARRAY[@]} ]; then
            echo "  ${SETTINGS_ARRAY[$i]}"
        fi
    done
    
    # Apply settings one by one to better handle errors
    echo -e "\nApplying settings..."
    SUCCESS_COUNT=0
    FAILED_COUNT=0
    
    for setting in "${SETTINGS_ARRAY[@]}"; do
        az webapp config appsettings set \
          --resource-group "$RESOURCE_GROUP" \
          --name "$APP_NAME" \
          --settings "$setting" 
    done
    
    echo -e "\n\nEnvironment variables update complete!"
    echo "  Successfully set: $SUCCESS_COUNT"
    echo "  Failed: $FAILED_COUNT"
else
    echo "Step 4/6: Warning - No valid environment variables found in .env file to set."
fi

echo -e "\nScript completed successfully!"