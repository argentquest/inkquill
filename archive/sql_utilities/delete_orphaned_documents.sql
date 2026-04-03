-- SQL Query to Delete All Uploaded Documents Where the World Doesn't Exist
-- This query removes orphaned uploaded_documents records where the referenced world has been deleted

-- Option 1: Delete documents with world_id pointing to non-existent worlds
DELETE FROM uploaded_documents 
WHERE world_id IS NOT NULL 
  AND world_id NOT IN (SELECT id FROM worlds);

-- Option 2: Delete documents with NULL world_id (if you also want to clean those up)
-- Uncomment the following line if you want to also remove documents with no world reference:
-- DELETE FROM uploaded_documents WHERE world_id IS NULL;

-- Option 3: Safe version with a SELECT first to see what will be deleted
-- Run this first to see what records will be affected:
/*
SELECT 
    id,
    filename,
    world_id,
    user_id,
    uploaded_at,
    status
FROM uploaded_documents 
WHERE world_id IS NOT NULL 
  AND world_id NOT IN (SELECT id FROM worlds)
ORDER BY uploaded_at DESC;
*/

-- Option 4: More detailed analysis query to show the orphaned documents and their details
/*
SELECT 
    ud.id as document_id,
    ud.filename,
    ud.world_id as missing_world_id,
    ud.user_id,
    ud.status,
    ud.uploaded_at,
    ud.blob_storage_path,
    u.username as owner_username
FROM uploaded_documents ud
LEFT JOIN users u ON ud.user_id = u.id
WHERE ud.world_id IS NOT NULL 
  AND ud.world_id NOT IN (SELECT id FROM worlds)
ORDER BY ud.uploaded_at DESC;
*/

-- Option 5: Count how many orphaned documents exist before deletion
/*
SELECT COUNT(*) as orphaned_documents_count
FROM uploaded_documents 
WHERE world_id IS NOT NULL 
  AND world_id NOT IN (SELECT id FROM worlds);
*/