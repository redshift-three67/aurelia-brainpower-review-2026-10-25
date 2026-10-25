-- Create storage bucket for client signature images
INSERT INTO storage.buckets (id, name, public)
VALUES ('client-signatures', 'client-signatures', false)
ON CONFLICT (id) DO NOTHING;

-- Allow authenticated users to upload their own signature images
CREATE POLICY "Users can upload own signature images"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'client-signatures' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow authenticated users to view their own signature images
CREATE POLICY "Users can view own signature images"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'client-signatures' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);

-- Allow authenticated users to delete their own signature images
CREATE POLICY "Users can delete own signature images"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'client-signatures' 
  AND auth.uid()::text = (storage.foldername(name))[1]
);