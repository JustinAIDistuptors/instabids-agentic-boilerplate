-- Messages table for chat history
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    sender_role sender_role NOT NULL,
    sender_id UUID, -- Can be user_id or agent_id
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for messages
CREATE INDEX idx_messages_project_id ON messages(project_id);
CREATE INDEX idx_messages_sender_role ON messages(sender_role);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);

-- Enable RLS
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies for messages
CREATE POLICY "Users can view messages for own projects" ON messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects 
            WHERE projects.id = messages.project_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages for own projects" ON messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects 
            WHERE projects.id = messages.project_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Service role has full access to messages" ON messages
    FOR ALL USING (auth.role() = 'service_role');

-- User preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    preference_key TEXT NOT NULL,
    preference_value JSONB NOT NULL,
    confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
    source TEXT DEFAULT 'user_provided',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, preference_key)
);

-- Indexes for user_preferences
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_key ON user_preferences(preference_key);
CREATE INDEX idx_user_preferences_updated_at ON user_preferences(updated_at DESC);

-- Add updated_at trigger
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_preferences
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own preferences" ON user_preferences
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Service role has full access to preferences" ON user_preferences
    FOR ALL USING (auth.role() = 'service_role');

-- Comments
COMMENT ON TABLE messages IS 'Chat messages between users and agents';
COMMENT ON COLUMN messages.sender_role IS 'Who sent the message: homeowner, agent, contractor, system';
COMMENT ON COLUMN messages.metadata IS 'Additional data like tool calls, attachments, etc';

COMMENT ON TABLE user_preferences IS 'Learned or provided user preferences';
COMMENT ON COLUMN user_preferences.preference_key IS 'e.g., default_budget, preferred_timeline, location';
COMMENT ON COLUMN user_preferences.confidence IS 'How confident we are in this preference (0-1)';
COMMENT ON COLUMN user_preferences.source IS 'How we learned this: user_provided, inferred, imported';