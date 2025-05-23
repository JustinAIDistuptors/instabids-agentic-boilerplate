-- Project knowledge base for RAG
CREATE TABLE project_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI text-embedding-ada-002 dimension
    metadata JSONB DEFAULT '{}'::jsonb,
    source_type TEXT NOT NULL CHECK (source_type IN ('project', 'contractor', 'material', 'regulation', 'pricing')),
    source_id UUID, -- Reference to the source record
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for project_knowledge
CREATE INDEX idx_knowledge_source_type ON project_knowledge(source_type);
CREATE INDEX idx_knowledge_source_id ON project_knowledge(source_id);
CREATE INDEX idx_knowledge_created_at ON project_knowledge(created_at DESC);

-- Vector similarity search index (IVFFlat)
CREATE INDEX idx_knowledge_embedding ON project_knowledge 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Add updated_at trigger
CREATE TRIGGER update_project_knowledge_updated_at BEFORE UPDATE ON project_knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE project_knowledge ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Anyone can read public knowledge" ON project_knowledge
    FOR SELECT USING (
        source_type IN ('material', 'regulation', 'pricing')
    );

CREATE POLICY "Users can read project knowledge for own projects" ON project_knowledge
    FOR SELECT USING (
        source_type = 'project' AND
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = project_knowledge.source_id
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Service role has full access to knowledge" ON project_knowledge
    FOR ALL USING (auth.role() = 'service_role');

-- Similarity search function
CREATE OR REPLACE FUNCTION match_project_knowledge(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_source_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    source_type TEXT,
    source_id UUID,
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
        pk.source_type,
        pk.source_id,
        1 - (pk.embedding <=> query_embedding) AS similarity
    FROM project_knowledge pk
    WHERE 
        1 - (pk.embedding <=> query_embedding) > match_threshold
        AND (filter_source_type IS NULL OR pk.source_type = filter_source_type)
    ORDER BY pk.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Agent sessions table for persistent memory
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_key TEXT UNIQUE NOT NULL,
    agent_name TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    state JSONB DEFAULT '{}'::jsonb,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for agent_sessions
CREATE INDEX idx_agent_sessions_session_key ON agent_sessions(session_key);
CREATE INDEX idx_agent_sessions_user_id ON agent_sessions(user_id);
CREATE INDEX idx_agent_sessions_agent_name ON agent_sessions(agent_name);
CREATE INDEX idx_agent_sessions_last_accessed ON agent_sessions(last_accessed);

-- Enable RLS
ALTER TABLE agent_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can access own sessions" ON agent_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Service role has full access to sessions" ON agent_sessions
    FOR ALL USING (auth.role() = 'service_role');

-- Comments
COMMENT ON TABLE project_knowledge IS 'Vector embeddings for semantic search and RAG';
COMMENT ON COLUMN project_knowledge.embedding IS 'Vector embedding from text-embedding-ada-002';
COMMENT ON FUNCTION match_project_knowledge IS 'Semantic similarity search using cosine distance';

COMMENT ON TABLE agent_sessions IS 'Persistent session state for ADK agents';
COMMENT ON COLUMN agent_sessions.session_key IS 'Unique identifier for the session';
COMMENT ON COLUMN agent_sessions.state IS 'JSON state data with user:, app:, temp: prefixes';