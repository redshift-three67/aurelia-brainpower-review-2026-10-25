/**
 * Hook für Klienten-Datenbank-Operationen
 */

import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';
import type { BiometricClientData, FieldSignature, StateDimensions } from '@/services/feldengine';
import { ThomVectorEngine } from '@/services/feldengine';
import { useAuth } from '@/hooks/useAuth';

export interface ClientRecord {
  id: string;
  firstName: string;
  lastName: string;
  birthDate: Date;
  birthPlace: string;
  photoUrl?: string;
  fieldSignature?: string;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ClientVectorRecord {
  id: string;
  clientId: string;
  dimensions: number[];
  attractorDistance: number;
  phase: 'approach' | 'transition' | 'stable';
  primaryConcern?: string;
  notes?: string;
  sessionId: string;
  createdAt: Date;
}

export function useClientDatabase() {
  const [isLoading, setIsLoading] = useState(false);
  const [clients, setClients] = useState<ClientRecord[]>([]);
  const { user } = useAuth();

  // Klient erstellen
  const createClient = useCallback(async (
    biometricData: BiometricClientData,
    notes?: string
  ): Promise<ClientRecord | null> => {
    setIsLoading(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('Nicht authentifiziert');
      
      const fieldSignature = ThomVectorEngine.calculateFieldSignature(biometricData);

      const { data, error } = await supabase
        .from('clients')
        .insert({
          first_name: biometricData.firstName,
          last_name: biometricData.lastName,
          birth_date: biometricData.birthDate.toISOString().split('T')[0],
          birth_place: biometricData.birthPlace,
          photo_url: null, // Photo URL set after storage upload
          field_signature: fieldSignature.hash,
          notes,
          user_id: session.user.id,
        })
        .select()
        .single();

      if (error) throw error;

      const client: ClientRecord = {
        id: data.id,
        firstName: data.first_name,
        lastName: data.last_name,
        birthDate: new Date(data.birth_date),
        birthPlace: data.birth_place,
        photoUrl: data.photo_url || undefined,
        fieldSignature: data.field_signature || undefined,
        notes: data.notes || undefined,
        createdAt: new Date(data.created_at),
        updatedAt: new Date(data.updated_at),
      };

      toast.success(`Klient ${client.firstName} ${client.lastName} erstellt`);
      return client;
    } catch (error) {
      console.error('Error creating client:', error);
      toast.error('Fehler beim Erstellen des Klienten');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Alle Klienten laden
  const loadClients = useCallback(async (): Promise<ClientRecord[]> => {
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('clients')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;

      const mappedClients: ClientRecord[] = (data || []).map((c) => ({
        id: c.id,
        firstName: c.first_name,
        lastName: c.last_name,
        birthDate: new Date(c.birth_date),
        birthPlace: c.birth_place,
        photoUrl: c.photo_url || undefined,
        fieldSignature: c.field_signature || undefined,
        notes: c.notes || undefined,
        createdAt: new Date(c.created_at),
        updatedAt: new Date(c.updated_at),
      }));

      setClients(mappedClients);
      return mappedClients;
    } catch (error) {
      console.error('Error loading clients:', error);
      toast.error('Fehler beim Laden der Klienten');
      return [];
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Klient nach ID laden
  const getClient = useCallback(async (clientId: string): Promise<ClientRecord | null> => {
    try {
      const { data, error } = await supabase
        .from('clients')
        .select('*')
        .eq('id', clientId)
        .single();

      if (error) throw error;

      return {
        id: data.id,
        firstName: data.first_name,
        lastName: data.last_name,
        birthDate: new Date(data.birth_date),
        birthPlace: data.birth_place,
        photoUrl: data.photo_url || undefined,
        fieldSignature: data.field_signature || undefined,
        notes: data.notes || undefined,
        createdAt: new Date(data.created_at),
        updatedAt: new Date(data.updated_at),
      };
    } catch (error) {
      console.error('Error loading client:', error);
      return null;
    }
  }, []);

  // Vektor für Klient speichern
  const saveClientVector = useCallback(async (
    clientId: string,
    stateDimensions: StateDimensions,
    biometricData: BiometricClientData,
    options?: {
      primaryConcern?: string;
      notes?: string;
      hrvValue?: number;
      gsrValue?: number;
    }
  ): Promise<ClientVectorRecord | null> => {
    setIsLoading(true);
    try {
      const sessionId = `session-${Date.now()}`;
      const analysis = ThomVectorEngine.calculateClientVector(
        biometricData,
        stateDimensions,
        sessionId
      );

      const { data, error } = await supabase
        .from('client_vectors')
        .insert({
          client_id: clientId,
          dimension_physical: analysis.clientVector.dimensions[0],
          dimension_emotional: analysis.clientVector.dimensions[1],
          dimension_mental: analysis.clientVector.dimensions[2],
          dimension_energy: analysis.clientVector.dimensions[3],
          dimension_stress: analysis.clientVector.dimensions[4],
          attractor_distance: analysis.attractorState.stability,
          phase: analysis.attractorState.phase,
          primary_concern: options?.primaryConcern,
          notes: options?.notes,
          hrv_value: options?.hrvValue,
          gsr_value: options?.gsrValue,
          session_id: sessionId,
        })
        .select()
        .single();

      if (error) throw error;

      toast.success('Vektor gespeichert');
      
      return {
        id: data.id,
        clientId: data.client_id,
        dimensions: [
          data.dimension_physical,
          data.dimension_emotional,
          data.dimension_mental,
          data.dimension_energy,
          data.dimension_stress,
        ],
        attractorDistance: data.attractor_distance || 0,
        phase: data.phase as 'approach' | 'transition' | 'stable',
        primaryConcern: data.primary_concern || undefined,
        notes: data.notes || undefined,
        sessionId: data.session_id,
        createdAt: new Date(data.created_at),
      };
    } catch (error) {
      console.error('Error saving vector:', error);
      toast.error('Fehler beim Speichern des Vektors');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Vektor-Historie für Klient laden
  const loadClientVectors = useCallback(async (clientId: string): Promise<ClientVectorRecord[]> => {
    try {
      const { data, error } = await supabase
        .from('client_vectors')
        .select('*')
        .eq('client_id', clientId)
        .order('created_at', { ascending: false });

      if (error) throw error;

      return (data || []).map((v) => ({
        id: v.id,
        clientId: v.client_id,
        dimensions: [
          v.dimension_physical,
          v.dimension_emotional,
          v.dimension_mental,
          v.dimension_energy,
          v.dimension_stress,
        ],
        attractorDistance: v.attractor_distance || 0,
        phase: v.phase as 'approach' | 'transition' | 'stable',
        primaryConcern: v.primary_concern || undefined,
        notes: v.notes || undefined,
        sessionId: v.session_id,
        createdAt: new Date(v.created_at),
      }));
    } catch (error) {
      console.error('Error loading vectors:', error);
      return [];
    }
  }, []);

  // Foto hochladen
  const uploadClientPhoto = useCallback(async (
    clientId: string,
    file: File
  ): Promise<string | null> => {
    try {
      const fileExt = file.name.split('.').pop();
      const fileName = `${clientId}/${Date.now()}.${fileExt}`;

      const { error: uploadError } = await supabase.storage
        .from('client-photos')
        .upload(fileName, file);

      if (uploadError) throw uploadError;

      const { data } = supabase.storage
        .from('client-photos')
        .getPublicUrl(fileName);

      // Update client record
      await supabase
        .from('clients')
        .update({ photo_url: data.publicUrl })
        .eq('id', clientId);

      toast.success('Foto hochgeladen');
      return data.publicUrl;
    } catch (error) {
      console.error('Error uploading photo:', error);
      toast.error('Fehler beim Hochladen des Fotos');
      return null;
    }
  }, []);

  // Klient aktualisieren
  const updateClient = useCallback(async (
    clientId: string,
    updates: Partial<{
      firstName: string;
      lastName: string;
      birthDate: Date;
      birthPlace: string;
      notes: string;
    }>
  ): Promise<boolean> => {
    setIsLoading(true);
    try {
      const dbUpdates: Record<string, unknown> = {};
      if (updates.firstName !== undefined) dbUpdates.first_name = updates.firstName;
      if (updates.lastName !== undefined) dbUpdates.last_name = updates.lastName;
      if (updates.birthDate !== undefined) dbUpdates.birth_date = updates.birthDate.toISOString().split('T')[0];
      if (updates.birthPlace !== undefined) dbUpdates.birth_place = updates.birthPlace;
      if (updates.notes !== undefined) dbUpdates.notes = updates.notes;

      const { error } = await supabase
        .from('clients')
        .update(dbUpdates)
        .eq('id', clientId);

      if (error) throw error;
      toast.success('Klient aktualisiert');
      return true;
    } catch (error) {
      console.error('Error updating client:', error);
      toast.error('Fehler beim Aktualisieren');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Klient löschen
  const deleteClient = useCallback(async (clientId: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const { error } = await supabase
        .from('clients')
        .delete()
        .eq('id', clientId);

      if (error) throw error;
      toast.success('Klient gelöscht');
      return true;
    } catch (error) {
      console.error('Error deleting client:', error);
      toast.error('Fehler beim Löschen');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    clients,
    createClient,
    updateClient,
    deleteClient,
    loadClients,
    getClient,
    saveClientVector,
    loadClientVectors,
    uploadClientPhoto,
  };
}

export default useClientDatabase;
