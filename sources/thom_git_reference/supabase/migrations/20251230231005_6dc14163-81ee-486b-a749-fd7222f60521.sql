-- Storage bucket für Klienten-Fotos
INSERT INTO storage.buckets (id, name, public)
VALUES ('client-photos', 'client-photos', true);

-- Storage policies
CREATE POLICY "Public read access for client photos"
ON storage.objects FOR SELECT
USING (bucket_id = 'client-photos');

CREATE POLICY "Authenticated upload for client photos"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'client-photos');

CREATE POLICY "Authenticated update for client photos"
ON storage.objects FOR UPDATE
USING (bucket_id = 'client-photos');

CREATE POLICY "Authenticated delete for client photos"
ON storage.objects FOR DELETE
USING (bucket_id = 'client-photos');