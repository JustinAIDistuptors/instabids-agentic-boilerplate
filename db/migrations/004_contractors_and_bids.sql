-- Contractors table
CREATE TABLE contractors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    business_name TEXT NOT NULL,
    license_number TEXT,
    categories project_category[] NOT NULL DEFAULT '{}',
    service_areas JSONB DEFAULT '[]'::jsonb, -- Array of {city, state, zip_codes[]}
    rating FLOAT CHECK (rating >= 0 AND rating <= 5),
    verified BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for contractors
CREATE INDEX idx_contractors_user_id ON contractors(user_id);
CREATE INDEX idx_contractors_categories ON contractors USING GIN(categories);
CREATE INDEX idx_contractors_verified ON contractors(verified);
CREATE INDEX idx_contractors_rating ON contractors(rating DESC);

-- Add updated_at trigger
CREATE TRIGGER update_contractors_updated_at BEFORE UPDATE ON contractors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE contractors ENABLE ROW LEVEL SECURITY;

-- RLS Policies for contractors
CREATE POLICY "Anyone can view verified contractors" ON contractors
    FOR SELECT USING (verified = true);

CREATE POLICY "Contractors can view own profile" ON contractors
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Contractors can update own profile" ON contractors
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Service role has full access to contractors" ON contractors
    FOR ALL USING (auth.role() = 'service_role');

-- Bids table
CREATE TABLE bids (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
    currency TEXT DEFAULT 'USD',
    timeline_days INTEGER,
    proposal TEXT,
    status bid_status DEFAULT 'pending',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, contractor_id) -- One bid per contractor per project
);

-- Indexes for bids
CREATE INDEX idx_bids_project_id ON bids(project_id);
CREATE INDEX idx_bids_contractor_id ON bids(contractor_id);
CREATE INDEX idx_bids_status ON bids(status);
CREATE INDEX idx_bids_amount ON bids(amount);
CREATE INDEX idx_bids_created_at ON bids(created_at DESC);

-- Add updated_at trigger
CREATE TRIGGER update_bids_updated_at BEFORE UPDATE ON bids
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE bids ENABLE ROW LEVEL SECURITY;

-- RLS Policies for bids
CREATE POLICY "Project owners can view all bids" ON bids
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects 
            WHERE projects.id = bids.project_id 
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Contractors can view own bids" ON bids
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM contractors 
            WHERE contractors.id = bids.contractor_id 
            AND contractors.user_id = auth.uid()
        )
    );

CREATE POLICY "Contractors can create bids" ON bids
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM contractors 
            WHERE contractors.id = bids.contractor_id 
            AND contractors.user_id = auth.uid()
        )
    );

CREATE POLICY "Contractors can update own pending bids" ON bids
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM contractors 
            WHERE contractors.id = bids.contractor_id 
            AND contractors.user_id = auth.uid()
        ) AND status = 'pending'
    );

CREATE POLICY "Service role has full access to bids" ON bids
    FOR ALL USING (auth.role() = 'service_role');

-- Comments
COMMENT ON TABLE contractors IS 'Registered contractors who can bid on projects';
COMMENT ON COLUMN contractors.categories IS 'Types of work the contractor performs';
COMMENT ON COLUMN contractors.service_areas IS 'Geographic areas where contractor operates';

COMMENT ON TABLE bids IS 'Contractor bids on projects';
COMMENT ON COLUMN bids.timeline_days IS 'Estimated days to complete the project';
COMMENT ON COLUMN bids.metadata IS 'Additional info like materials breakdown, labor hours, etc';