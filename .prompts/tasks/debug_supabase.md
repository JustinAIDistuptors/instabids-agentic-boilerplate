## Task Prompt: Debug Supabase Integration Issues

### Goal

Diagnose and fix Supabase-related errors in ADK agents and tools.

### Common Supabase Issues

1. **Row Level Security (RLS) Violations**
2. **Missing Tables or Columns**
3. **Authentication Failures**
4. **Connection Timeouts**
5. **Storage Access Errors**

### Debugging Process

#### Step 1: Identify Error Type

```python
# Common error patterns
if "permission denied for table" in error_message:
    issue_type = "RLS_VIOLATION"
elif "relation does not exist" in error_message:
    issue_type = "MISSING_TABLE"
elif "column does not exist" in error_message:
    issue_type = "MISSING_COLUMN"
elif "JWT" in error_message:
    issue_type = "AUTH_ERROR"
else:
    issue_type = "UNKNOWN"
```

#### Step 2: Check Environment

```python
import os
from supabase import create_client

# Verify credentials
print(f"URL set: {'SUPABASE_URL' in os.environ}")
print(f"Service key set: {'SUPABASE_SERVICE_KEY' in os.environ}")

# Test connection
try:
    client = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"]
    )
    # Simple query to test
    result = client.table('projects').select('count').execute()
    print(f"Connection successful: {result}")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Fix Patterns

#### RLS Violation Fix

```sql
-- Check existing policies
SELECT * FROM pg_policies WHERE tablename = 'your_table';

-- Add service role bypass
CREATE POLICY "Service role bypass" ON your_table
    FOR ALL USING (auth.role() = 'service_role');

-- Add user access policy
CREATE POLICY "Users access own data" ON your_table
    FOR ALL USING (auth.uid() = user_id);
```

#### Missing Table Fix

```sql
-- Create missing table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES auth.users(id),
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
```

#### Authentication Fix

```python
# Use service role for backend operations
client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_KEY"]  # Not anon key!
)

# For user context operations
user_client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"]
)
user_client.auth.sign_in_with_password({
    "email": user_email,
    "password": user_password
})
```

### Tool-Specific Debugging

#### save_project Tool

```python
def debug_save_project(tool_context, project_data):
    """Debug version with extensive logging."""
    import json
    
    print(f"Input data: {json.dumps(project_data, indent=2)}")
    print(f"User ID: {tool_context.state.get('user:id')}")
    
    try:
        client = get_supabase_client()
        
        # Test insert
        result = client.table('projects').insert({
            "owner_id": tool_context.state.get('user:id'),
            "title": project_data.get('title'),
            "description": project_data.get('description')
        }).execute()
        
        print(f"Success: {result.data}")
        return {"status": "success", "data": result.data}
        
    except Exception as e:
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Full error: {repr(e)}")
        
        # Check specific issues
        if "permission denied" in str(e):
            print("\nRLS Issue detected. Check policies.")
        
        return {"status": "error", "message": str(e)}
```

### Testing Fixes

```python
# Test RLS policies
async def test_rls_policies():
    # Test as service role
    service_client = create_client(url, service_key)
    result = service_client.table('projects').select('*').execute()
    print(f"Service role can access: {len(result.data)} projects")
    
    # Test as anon role
    anon_client = create_client(url, anon_key)
    try:
        result = anon_client.table('projects').select('*').execute()
        print(f"Anon role can access: {len(result.data)} projects")
    except Exception as e:
        print(f"Anon role blocked (expected): {e}")
```

### Storage Debugging

```python
def debug_storage_upload():
    """Debug storage access issues."""
    client = get_supabase_client()
    
    # List buckets
    buckets = client.storage.list_buckets()
    print(f"Available buckets: {[b.name for b in buckets]}")
    
    # Check bucket policy
    bucket_name = "project-images"
    
    # Test upload
    try:
        test_file = b"test content"
        result = client.storage.from_(bucket_name).upload(
            "test/debug.txt",
            test_file
        )
        print(f"Upload successful: {result}")
    except Exception as e:
        print(f"Upload failed: {e}")
        
        if "Bucket not found" in str(e):
            print("\nCreate bucket with:")
            print(f"INSERT INTO storage.buckets (id, name, public)")
            print(f"VALUES ('{bucket_name}', '{bucket_name}', false);")
```

### Migration Debugging

```bash
# Check migration status
supabase db diff

# Reset local database
supabase db reset

# Apply specific migration
supabase db push --file db/migrations/001_initial.sql
```

### Common Fixes Summary

1. **Always use service role key for backend**
2. **Enable RLS with proper policies**
3. **Create tables before using them**
4. **Check bucket existence for storage**
5. **Validate environment variables**
6. **Use proper error handling**

### Final Validation

- [ ] Connection test passes
- [ ] RLS policies allow service role
- [ ] All tables exist with correct schema
- [ ] Storage buckets are accessible
- [ ] Error messages are helpful
- [ ] Tests cover the fix