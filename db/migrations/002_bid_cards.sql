-- Bid cards table
CREATE TABLE bid_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    category project_category NOT NULL,
    job_type TEXT,
    budget_range JSONB DEFAULT '{"min": null, "max": null, "currency": "USD"}'::jsonb,
    timeline TEXT,
    group_bidding BOOLEAN DEFAULT FALSE,
    scope_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    photo_meta JSONB DEFAULT '[]'::jsonb,
    ai_confidence FLOAT CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'final')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for bid_cards
CREATE INDEX idx_bid_cards_project_id ON bid_cards(project_id);
CREATE INDEX idx_bid_cards_category ON bid_cards(category);
CREATE INDEX idx_bid_cards_status ON bid_cards(status);
CREATE INDEX idx_bid_cards_ai_confidence ON bid_cards(ai_confidence);

-- Add updated_at trigger
CREATE TRIGGER update_bid_cards_updated_at BEFORE UPDATE ON bid_cards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE bid_cards ENABLE ROW LEVEL SECURITY;

-- RLS Policies for bid_cards
CREATE POLICY "Users can view bid cards for own projects" ON bid_cards
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects 
            WHERE projects.id = bid_cards.project_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Service role has full access to bid_cards" ON bid_cards
    FOR ALL USING (auth.role() = 'service_role');

-- Comments
COMMENT ON TABLE bid_cards IS 'AI-generated structured summaries of projects for contractors';
COMMENT ON COLUMN bid_cards.category IS 'Type of work: repair, renovation, etc';
COMMENT ON COLUMN bid_cards.job_type IS 'Specific job type within category';
COMMENT ON COLUMN bid_cards.budget_range IS 'JSON with min, max, and currency';
COMMENT ON COLUMN bid_cards.group_bidding IS 'Whether multiple contractors can collaborate';
COMMENT ON COLUMN bid_cards.scope_json IS 'Full project details in structured format';
COMMENT ON COLUMN bid_cards.photo_meta IS 'Array of photo analysis results';
COMMENT ON COLUMN bid_cards.ai_confidence IS 'AI confidence score 0-1';
COMMENT ON COLUMN bid_cards.status IS 'draft (needs review) or final (ready for contractors)';