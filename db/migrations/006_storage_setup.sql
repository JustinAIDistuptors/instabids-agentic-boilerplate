-- Create storage buckets for project files
INSERT INTO storage.buckets (id, name, public, allowed_mime_types)
VALUES 
    ('project-images', 'project-images', false, ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif']),
    ('bid-documents', 'bid-documents', false, ARRAY['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']),
    ('generated-artifacts', 'generated-artifacts', false, NULL)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for project-images bucket
CREATE POLICY "Users can upload images to own folder" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'project-images' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "Users can view own images" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'project-images' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "Users can update own images" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'project-images' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "Users can delete own images" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'project-images' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

-- Storage policies for bid-documents bucket
CREATE POLICY "Contractors can upload bid documents" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'bid-documents' AND
        EXISTS (
            SELECT 1 FROM contractors
            WHERE contractors.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view bid documents for their projects" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'bid-documents' AND
        EXISTS (
            SELECT 1 FROM bids b
            JOIN projects p ON b.project_id = p.id
            WHERE 
                (storage.foldername(name))[1] = b.id::text AND
                (p.owner_id = auth.uid() OR 
                 EXISTS (
                     SELECT 1 FROM contractors c
                     WHERE c.id = b.contractor_id AND c.user_id = auth.uid()
                 ))
        )
    );

-- Service role policies for all buckets
CREATE POLICY "Service role has full access to project-images" ON storage.objects
    FOR ALL USING (bucket_id = 'project-images' AND auth.role() = 'service_role');

CREATE POLICY "Service role has full access to bid-documents" ON storage.objects
    FOR ALL USING (bucket_id = 'bid-documents' AND auth.role() = 'service_role');

CREATE POLICY "Service role has full access to generated-artifacts" ON storage.objects
    FOR ALL USING (bucket_id = 'generated-artifacts' AND auth.role() = 'service_role');

-- Project images metadata table
CREATE TABLE project_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    original_name TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER,
    analysis_results JSONB DEFAULT '{}'::jsonb,
    uploaded_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_project_images_project_id ON project_images(project_id);
CREATE INDEX idx_project_images_uploaded_by ON project_images(uploaded_by);

-- Enable RLS
ALTER TABLE project_images ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view images for own projects" ON project_images
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = project_images.project_id
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Users can upload images to own projects" ON project_images
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = project_images.project_id
            AND projects.owner_id = auth.uid()
        )
    );

CREATE POLICY "Service role has full access to project_images" ON project_images
    FOR ALL USING (auth.role() = 'service_role');

-- Comments
COMMENT ON TABLE project_images IS 'Metadata for images uploaded to projects';
COMMENT ON COLUMN project_images.storage_path IS 'Path in storage bucket';
COMMENT ON COLUMN project_images.analysis_results IS 'AI vision analysis results';