#!/bin/bash

# ==============================================================================
# --- CONFIGURE YOUR DETAILS HERE ---
#
# Fill in the names for your source (old) and target (new) App Services.
# You MUST also provide the resource group for each app.
# ==============================================================================

# --- Source App Service (The OLD one) ---
SOURCE_APP_NAME="AQStoryWrite"
SOURCE_RESOURCE_GROUP="whisperwsCanada"

# --- Target App Service (The NEW one) ---
TARGET_APP_NAME="AQSTDEV1"
TARGET_RESOURCE_GROUP="aqstv1"

# ==============================================================================
# --- SCRIPT LOGIC (No changes needed below this line) ---
# ==============================================================================

echo "-> Starting App Settings transfer..."
echo "   From: $SOURCE_APP_NAME (in RG: $SOURCE_RESOURCE_GROUP)"
echo "   To:   $TARGET_APP_NAME (in RG: $TARGET_RESOURCE_GROUP)"
echo ""

# --- Step 1: Export settings from the source app ---
echo "-> Step 1/4: Exporting settings from '$SOURCE_APP_NAME'..."
az webapp config appsettings list \
    --name $SOURCE_APP_NAME \
    --resource-group $SOURCE_RESOURCE_GROUP \
    --output json > temp_appsettings.json

# Check if the export was successful
if [ $? -ne 0 ]; then
    echo "   [ERROR] Failed to export settings. Please check the names and your permissions."
    exit 1
fi
echo "   ...Export complete."
echo ""

# --- Step 2: Process the settings for the import command ---
# The 'set' command requires a different format, so we use 'jq' to transform the file.
echo "-> Step 2/4: Processing settings file..."
jq "from_entries" temp_appsettings.json > settings_to_apply.json

if [ $? -ne 0 ]; then
    echo "   [ERROR] Failed to process settings. Is 'jq' installed? (See instructions)."
    exit 1
fi
echo "   ...Processing complete."
echo ""

# --- Step 3: Apply the settings to the target app ---
echo "-> Step 3/4: Applying settings to '$TARGET_APP_NAME'..."
az webapp config appsettings set \
    --resource-group $TARGET_RESOURCE_GROUP \
    --name $TARGET_APP_NAME \
    --settings "@settings_to_apply.json"

if [ $? -ne 0 ]; then
    echo "   [ERROR] Failed to apply settings to the new app."
    exit 1
fi
echo "   ...Settings applied successfully."
echo ""

# --- Step 4: Clean up temporary files ---
echo "-> Step 4/4: Cleaning up temporary files..."
rm temp_appsettings.json
rm settings_to_apply.json
echo "   ...Cleanup complete."
echo ""

echo "✅  SUCCESS: All application settings have been transferred."