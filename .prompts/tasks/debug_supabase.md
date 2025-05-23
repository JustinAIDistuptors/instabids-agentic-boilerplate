## Task: Debug Supabase Integration Issue

### Goal

Diagnose and fix Supabase-related errors in the InstaBids system.

### Common Issues and Solutions

#### 1. RLS Policy Violations

**Symptom**: `new row violates row-level security policy`

**Diagnosis Steps**:
1. Check which table and operation
2. Verify user authentication
3. Review RLS policies
4. Check service role usage

**Solution**:
```sql
-- Add service role bypass
CREATE POLICY "Service role full access" ON {table_name}
    FOR ALL USING (auth.role() = 'service_role');

-- Or fix user-based policy
CREATE POLICY "Users can insert own records" ON {table_name}
    FOR INSERT WITH CHECK (
        auth.uid() = user_id OR 
        auth.role() = 'service_role'
    );
```

#### 2. Storage Access Denied

**Symptom**: `403 Forbidden` on file operations

**Diagnosis**:
```python
# Check bucket policies
client.storage.list_buckets()

# Verify path structure
print(f"Storage path: {user_id}/{project_id}/{filename}")
```

**Solution**:
```sql
-- Storage bucket policy
CREATE POLICY "Users upload to own folder" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'project-files' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

-- Service role bypass
CREATE POLICY "Service role storage access" ON storage.objects
    FOR ALL USING (auth.role() = 'service_role');
```

#### 3. Connection Issues

**Symptom**: `connection refused` or timeout

**Diagnosis**:
```python
# Check environment variables
import os
print(f"URL: {os.environ.get('SUPABASE_URL')}")
print(f"Key exists: {'SUPABASE_SERVICE_KEY' in os.environ}")

# Test connection
from supabase import create_client
client = create_client(url, key)
health = client.table('projects').select('count').limit(1).execute()
```

**Solution**:
```bash
# Local development
supabase status  # Check if running
supabase start   # Start if needed

# Environment setup
export SUPABASE_URL="http://localhost:54321"
export SUPABASE_SERVICE_KEY="your-service-key"
```

#### 4. Migration Failures

**Symptom**: `relation does not exist`

**Diagnosis**:
```bash
# Check migration status
supabase db migrations list

# View pending migrations
ls -la db/migrations/
```

**Solution**:
```bash
# Apply migrations
supabase db reset  # Local dev
# OR
supabase db push   # Remote

# Manual migration
psql $DATABASE_URL < db/migrations/001_schema.sql
```

#### 5. Data Type Mismatches

**Symptom**: `invalid input syntax for type`

**Diagnosis**:
```python
# Check data types
response = client.table('projects').select('*').limit(0).execute()
print("Schema:", response)

# Validate before insert
import json
try:
    json.dumps(data)  # Check JSON serializable
except TypeError as e:
    print(f"Non-serializable data: {e}")
```

**Solution**:
```python
# Type conversion helpers
from datetime import datetime
from decimal import Decimal

def prepare_for_supabase(data: dict) -> dict:
    """Convert Python types to Supabase-compatible."""
    prepared = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            prepared[key] = value.isoformat()
        elif isinstance(value, Decimal):
            prepared[key] = float(value)
        elif isinstance(value, set):
            prepared[key] = list(value)
        else:
            prepared[key] = value
    return prepared
```

### Debug Workflow

1. **Capture Full Error**
   ```python
   try:
       response = client.table('table').insert(data).execute()
   except Exception as e:
       print(f"Error type: {type(e)}")
       print(f"Error message: {str(e)}")
       print(f"Error details: {e.__dict__}")
   ```

2. **Check Logs**
   ```bash
   # Supabase logs
   supabase db logs
   
   # Application logs
   tail -f logs/app.log | grep -i supabase
   ```

3. **Test in Isolation**
   ```python
   # Minimal reproduction
   from supabase import create_client
   
   client = create_client(url, service_key)
   test_data = {"minimal": "data"}
   result = client.table('test').insert(test_data).execute()
   ```

4. **Verify Fixes**
   ```python
   # Run integration tests
   pytest tests/integration/test_supabase.py -v
   ```

### Prevention Checklist

- [ ] All tables have service role policies
- [ ] Storage buckets have proper RLS
- [ ] Environment variables are set
- [ ] Migrations are up to date
- [ ] Data types are validated
- [ ] Error handling is comprehensive
- [ ] Integration tests cover all operations
- [ ] Connection pooling is configured
- [ ] Rate limits are respected
- [ ] Backups are automated