# 🗄️ Supabase Integration Patterns for InstaBids

> **Best practices for integrating Supabase with Google ADK agents**

## 📋 Table of Contents

1. [Database Schema](#database-schema)
2. [Client Setup](#client-setup)
3. [Row Level Security (RLS)](#row-level-security)
4. [Tool Patterns](#tool-patterns)
5. [Vector Search (RAG)](#vector-search-rag)
6. [Storage Integration](#storage-integration)
7. [Real-time Subscriptions](#real-time-subscriptions)
8. [Testing Patterns](#testing-patterns)

## 🗃️ Database Schema

### Core Tables

```sql
-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bid cards table
CREATE TABLE bid_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    job_type TEXT,
    budget_range JSONB,
    timeline TEXT,
    group_bidding BOOLEAN DEFAULT FALSE,
    scope_json JSONB,
    photo_meta JSONB,
    ai_confidence FLOAT CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    sender_role TEXT NOT NULL CHECK (sender_role IN ('homeowner', 'agent', 'contractor')),
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    preference_key TEXT NOT NULL,
    preference_value JSONB NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, preference_key)
);

-- Indexes for performance
CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_bid_cards_project ON bid_cards(project_id);
CREATE INDEX idx_messages_project ON messages(project_id);
CREATE INDEX idx_preferences_user ON user_preferences(user_id);
```

## 🔧 Client Setup

### Basic Client Configuration

```python
# src/instabids/db/client.py
from supabase import create_client, Client
import os
from typing import Optional

class SupabaseClient:
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get singleton Supabase client."""
        if cls._instance is None:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_SERVICE_KEY")  # For backend
            
            if not url or not key:
                raise ValueError("Missing Supabase credentials")
            
            cls._instance = create_client(url, key)
        
        return cls._instance
```

### Context-Aware Client

```python
# For agents that need user context
class UserContextClient:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client = SupabaseClient.get_client()
    
    async def get_user_projects(self):
        """Get projects for authenticated user."""
        response = self.client.table('projects').select('*').eq(
            'owner_id', self.user_id
        ).execute()
        return response.data
```

## 🔐 Row Level Security (RLS)

### Essential RLS Policies

```sql
-- Enable RLS on all tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE bid_cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Projects: Users can only see their own
CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (auth.uid() = owner_id OR auth.role() = 'service_role');

CREATE POLICY "Users can create own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid() = owner_id OR auth.role() = 'service_role');

CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (auth.uid() = owner_id OR auth.role() = 'service_role');

-- Messages: Users can see messages for their projects
CREATE POLICY "Users can view project messages" ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects 
            WHERE projects.id = messages.project_id 
            AND projects.owner_id = auth.uid()
        ) OR auth.role() = 'service_role'
    );

-- Service role bypass for agents
CREATE POLICY "Service role full access" ON messages
    FOR ALL USING (auth.role() = 'service_role');

-- Storage bucket policies
INSERT INTO storage.buckets (id, name, public) 
VALUES ('project-images', 'project-images', false);

CREATE POLICY "Users can upload project images" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'project-images' AND 
        (storage.foldername(name))[1] = auth.uid()::text
    );
```

## 🛠️ Tool Patterns

### CRUD Operations Tool

```python
# src/instabids/tools/supabase_tools.py
from google.adk.types import ToolContext
from typing import Dict, Any, Optional
import json

def save_project(
    tool_context: ToolContext,
    title: str,
    description: str,
    owner_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Save a new project to Supabase.
    
    Args:
        tool_context (ToolContext): ADK context for state access.
        title (str): Project title (3-200 characters).
        description (str): Detailed project description.
        owner_id (Optional[str]): User ID, defaults to current user.
        
    Returns:
        dict: Operation result with project ID.
        Example: {
            "status": "success",
            "project_id": "uuid-here",
            "created_at": "2025-05-23T10:00:00Z"
        }
    """
    client = SupabaseClient.get_client()
    
    # Get owner_id from context if not provided
    if not owner_id:
        owner_id = tool_context.state.get("user:id")
    
    try:
        response = client.table('projects').insert({
            "owner_id": owner_id,
            "title": title,
            "description": description,
            "status": "draft"
        }).execute()
        
        project = response.data[0]
        
        # Store in agent state
        tool_context.state["user:current_project_id"] = project["id"]
        
        return {
            "status": "success",
            "project_id": project["id"],
            "created_at": project["created_at"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

### Batch Operations

```python
def save_user_preferences(
    tool_context: ToolContext,
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Batch save user preferences with upsert.
    
    Args:
        tool_context (ToolContext): ADK context.
        preferences (dict): Key-value pairs of preferences.
        
    Returns:
        dict: Status and number of preferences saved.
    """
    client = SupabaseClient.get_client()
    user_id = tool_context.state.get("user:id")
    
    # Prepare batch data
    batch_data = [
        {
            "user_id": user_id,
            "preference_key": key,
            "preference_value": json.dumps(value),
            "confidence": 0.8
        }
        for key, value in preferences.items()
    ]
    
    try:
        response = client.table('user_preferences').upsert(
            batch_data,
            on_conflict='user_id,preference_key'
        ).execute()
        
        return {
            "status": "success",
            "saved_count": len(response.data)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

## 🔍 Vector Search (RAG)

### Setting Up pgvector

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Knowledge base table
CREATE TABLE project_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI embeddings dimension
    metadata JSONB,
    source_type TEXT,  -- 'project', 'contractor', 'material', etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast similarity search
CREATE INDEX idx_knowledge_embedding ON project_knowledge 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Similarity search function
CREATE OR REPLACE FUNCTION match_project_knowledge(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pk.id,
        pk.content,
        pk.metadata,
        1 - (pk.embedding <=> query_embedding) AS similarity
    FROM project_knowledge pk
    WHERE 1 - (pk.embedding <=> query_embedding) > match_threshold
    ORDER BY pk.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### RAG Tool Implementation

```python
import openai
import numpy as np

def search_knowledge_base(
    tool_context: ToolContext,
    query: str,
    source_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search project knowledge base using semantic similarity.
    
    Args:
        tool_context (ToolContext): ADK context.
        query (str): Search query.
        source_type (Optional[str]): Filter by source type.
        
    Returns:
        dict: Matched documents with similarity scores.
    """
    # Generate embedding for query
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    query_embedding = response.data[0].embedding
    
    # Search in Supabase
    client = SupabaseClient.get_client()
    
    # Use RPC to call our function
    results = client.rpc(
        'match_project_knowledge',
        {
            'query_embedding': query_embedding,
            'match_threshold': 0.7,
            'match_count': 5
        }
    ).execute()
    
    # Filter by source type if specified
    if source_type and results.data:
        results.data = [
            r for r in results.data 
            if r.get('metadata', {}).get('source_type') == source_type
        ]
    
    return {
        "status": "success",
        "matches": results.data,
        "query": query
    }
```

## 📦 Storage Integration

### File Upload Tool

```python
def upload_project_image(
    tool_context: ToolContext,
    file_path: str,
    project_id: str
) -> Dict[str, Any]:
    """
    Upload project image to Supabase Storage.
    
    Args:
        tool_context (ToolContext): ADK context.
        file_path (str): Local path to image file.
        project_id (str): Associated project ID.
        
    Returns:
        dict: Upload result with public URL.
    """
    client = SupabaseClient.get_client()
    user_id = tool_context.state.get("user:id")
    
    # Construct storage path
    storage_path = f"{user_id}/{project_id}/{os.path.basename(file_path)}"
    
    try:
        # Upload file
        with open(file_path, 'rb') as f:
            response = client.storage.from_('project-images').upload(
                path=storage_path,
                file=f,
                file_options={"content-type": "image/jpeg"}
            )
        
        # Get public URL
        url = client.storage.from_('project-images').get_public_url(storage_path)
        
        # Save metadata to database
        client.table('project_images').insert({
            "project_id": project_id,
            "storage_path": storage_path,
            "url": url,
            "uploaded_by": user_id
        }).execute()
        
        return {
            "status": "success",
            "url": url,
            "storage_path": storage_path
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

## 📡 Real-time Subscriptions

### Message Subscription

```python
from typing import Callable
import asyncio

class RealtimeMessageHandler:
    def __init__(self, project_id: str, on_message: Callable):
        self.project_id = project_id
        self.on_message = on_message
        self.client = SupabaseClient.get_client()
        self.subscription = None
    
    async def start(self):
        """Start listening for new messages."""
        self.subscription = self.client.channel('messages').on(
            'postgres_changes',
            {
                'event': 'INSERT',
                'schema': 'public',
                'table': 'messages',
                'filter': f'project_id=eq.{self.project_id}'
            },
            self._handle_message
        ).subscribe()
    
    def _handle_message(self, payload):
        """Handle incoming message."""
        message = payload['new']
        asyncio.create_task(self.on_message(message))
    
    def stop(self):
        """Stop subscription."""
        if self.subscription:
            self.subscription.unsubscribe()
```

## 🧪 Testing Patterns

### Test Fixtures

```python
# tests/fixtures/supabase_fixtures.py
import pytest
from supabase import create_client
import os

@pytest.fixture
def test_client():
    """Provide test Supabase client."""
    url = os.environ.get("SUPABASE_TEST_URL", "http://localhost:54321")
    key = os.environ.get("SUPABASE_TEST_SERVICE_KEY")
    return create_client(url, key)

@pytest.fixture
def test_user(test_client):
    """Create test user for RLS testing."""
    response = test_client.auth.admin.create_user({
        "email": "test@instabids.com",
        "password": "testpass123"
    })
    user = response.user
    
    yield user
    
    # Cleanup
    test_client.auth.admin.delete_user(user.id)
```

### Integration Tests

```python
@pytest.mark.integration
class TestSupabaseTools:
    async def test_save_project(self, test_client, test_user):
        """Test project creation with RLS."""
        tool_context = MockToolContext(
            state={"user:id": test_user.id}
        )
        
        result = await save_project(
            tool_context,
            title="Test Project",
            description="Test Description"
        )
        
        assert result["status"] == "success"
        assert "project_id" in result
        
        # Verify in database
        project = test_client.table('projects').select('*').eq(
            'id', result["project_id"]
        ).single().execute()
        
        assert project.data["title"] == "Test Project"
```

## 🔑 Best Practices Summary

1. **Always use service role key** for backend agent operations
2. **Implement comprehensive RLS policies** including service role bypass
3. **Use upsert for preferences** to handle updates gracefully
4. **Batch operations** when possible to reduce API calls
5. **Store embeddings** for RAG capabilities with pgvector
6. **Handle storage paths carefully** to maintain user isolation
7. **Test with RLS enabled** to catch permission issues early
8. **Use transactions** for multi-table operations
9. **Monitor rate limits** and implement exponential backoff
10. **Cache frequently accessed data** to improve performance

## 🚀 Advanced Patterns

### Transaction Support

```python
async def create_project_with_bidcard(
    tool_context: ToolContext,
    project_data: dict,
    bid_card_data: dict
) -> Dict[str, Any]:
    """Create project and bid card in transaction."""
    client = SupabaseClient.get_client()
    
    # Note: Supabase doesn't support client-side transactions yet
    # Use database functions for true ACID transactions
    
    result = client.rpc(
        'create_project_with_bidcard',
        {
            'p_project': project_data,
            'p_bid_card': bid_card_data
        }
    ).execute()
    
    return {
        "status": "success",
        "data": result.data
    }
```

### Performance Optimization

```python
from functools import lru_cache
import time

class CachedSupabaseClient:
    def __init__(self, ttl: int = 300):  # 5 minute cache
        self.ttl = ttl
        self.cache = {}
    
    @lru_cache(maxsize=100)
    def get_user_preferences(self, user_id: str) -> dict:
        """Get cached user preferences."""
        cache_key = f"prefs:{user_id}"
        
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                return data
        
        # Fetch from Supabase
        client = SupabaseClient.get_client()
        response = client.table('user_preferences').select('*').eq(
            'user_id', user_id
        ).execute()
        
        # Cache result
        self.cache[cache_key] = (response.data, time.time())
        return response.data
```

Follow these patterns to build a robust, scalable Supabase integration for InstaBids!