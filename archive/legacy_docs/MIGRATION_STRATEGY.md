# Database Migration Strategy

## **Adopted Approach: Direct SQL Scripts**

Based on successful resolution of the story classes issue, we will use **direct SQL scripts** for all database migrations instead of relying on complex Python environments.

## **Why This Approach Works Better**

### **✅ Advantages**
- **Environment Independent**: No dependency on Python packages being installed
- **Reliable**: Direct SQL execution eliminates Python environment issues
- **Fast**: Immediate execution without setup overhead
- **Debuggable**: Clear SQL errors vs obscure Python stack traces
- **Portable**: Works with any PostgreSQL client (pgAdmin, psql, VS Code, etc.)
- **Version Control Friendly**: SQL files are easy to track and review

### **❌ Previous Issues with Python-based Migrations**
- Missing Python packages (asyncpg, sqlalchemy, etc.)
- Environment setup complexity
- Dependency conflicts
- Async/await complexity
- Import path issues

## **New Migration Workflow**

### **1. Create SQL Migration Files**
Format: `{timestamp}_{description}.sql`
```sql
-- Migration: Add new feature
-- Date: 2025-01-09
-- Description: Brief description of changes

-- Check if migration needed
SELECT 'checking_prerequisite' as status;

-- Apply changes with IF NOT EXISTS guards
CREATE TABLE IF NOT EXISTS new_table (...);
ALTER TABLE existing_table ADD COLUMN IF NOT EXISTS new_column INTEGER;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_name ON table_name (column);

-- Update alembic version (if needed)
UPDATE alembic_version SET version_num = 'new_version_id';

-- Verification query
SELECT 'migration_verification' as status,
       EXISTS(...) as table_created,
       EXISTS(...) as column_added;
```

### **2. Test SQL Scripts**
- Use `IF NOT EXISTS` clauses for idempotency
- Include verification queries
- Test on development database first
- Include rollback instructions in comments

### **3. Apply Migrations**
```bash
# Method 1: Using psql
psql -U username -d database_name -f migration_file.sql

# Method 2: Copy/paste in database client
# Method 3: Execute in pgAdmin or VS Code
```

### **4. Document Applied Migrations**
- Keep migration files in version control
- Document which migrations have been applied
- Include verification steps

## **Template for Future Migrations**

```sql
-- ============================================
-- Migration: {FEATURE_NAME}
-- Date: {DATE}
-- Description: {DETAILED_DESCRIPTION}
-- ============================================

-- Prerequisites check
DO $$ 
BEGIN 
    RAISE NOTICE 'Starting migration: {FEATURE_NAME}';
END $$;

-- Main migration logic
-- (Use IF NOT EXISTS for idempotency)

-- Example: Create table
CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Example: Add column
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'existing_table' AND column_name = 'new_column'
    ) THEN
        ALTER TABLE existing_table ADD COLUMN new_column INTEGER;
    END IF;
END $$;

-- Example: Create index
CREATE INDEX IF NOT EXISTS idx_new_table_name ON new_table (name);

-- Update alembic version if needed
-- UPDATE alembic_version SET version_num = 'new_version_hash';

-- Verification
SELECT 
    'Migration Verification' as status,
    EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'new_table') as table_created,
    EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'existing_table' AND column_name = 'new_column') as column_added;

-- Final message
DO $$ 
BEGIN 
    RAISE NOTICE 'Migration completed: {FEATURE_NAME}';
END $$;
```

## **Benefits Demonstrated**

### **Story Classes Migration Success**
- **Problem**: story_classes table missing, preventing saves
- **Old Approach**: Complex Python script with dependency issues
- **New Approach**: Simple SQL script executed directly
- **Result**: ✅ Immediate resolution, feature working perfectly

### **Future Confidence**
- All database changes will be reliable
- No environment setup required
- Faster development and deployment
- Easier troubleshooting

## **Integration with Development Workflow**

1. **During Development**: Create SQL migration files alongside code changes
2. **Testing**: Apply migrations to development database first  
3. **Deployment**: Include SQL migrations in deployment process
4. **Documentation**: Keep migration log in version control

## **Rollback Strategy**

Each migration should include rollback instructions:
```sql
-- ROLLBACK INSTRUCTIONS (if needed):
-- DROP TABLE IF EXISTS new_table;
-- ALTER TABLE existing_table DROP COLUMN IF EXISTS new_column;
-- UPDATE alembic_version SET version_num = 'previous_version';
```

---

## **Action Items**

1. ✅ **Adopted**: Direct SQL migration approach
2. ✅ **Resolved**: Story classes database issue  
3. ✅ **Template**: Created standard migration template
4. ⏭️ **Next**: Apply this approach to all future database changes

**This approach will prevent database-related issues and ensure reliable migrations going forward.**