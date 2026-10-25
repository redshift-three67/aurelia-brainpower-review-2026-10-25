import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Users, Plus, Trash2, Edit2, Check, X, Loader2, Image as ImageIcon, Sparkles, Settings, Zap } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/hooks/useAuth';
import { z } from 'zod';
import { analyzeImageWithOllama, checkOllamaConnection } from '@/utils/ollamaClient';
import { PatientHardwareConfig } from './PatientHardwareConfig';
import { DEFAULT_HARDWARE_CONFIG, HardwareConfig } from '@/utils/hardwareAlgorithms';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { calculateClientRate } from '@/utils/clientRateCalculation';

// DSGVO-konforme Input-Validierung
const patientSchema = z.object({
  first_name: z.string()
    .trim()
    .min(1, { message: "Vorname ist erforderlich" })
    .max(100, { message: "Vorname zu lang" }),
  last_name: z.string()
    .trim()
    .min(1, { message: "Nachname ist erforderlich" })
    .max(100, { message: "Nachname zu lang" }),
  birth_date: z.string().optional(),
  birth_place: z.string().max(200, { message: "Geburtsort zu lang" }).optional(),
});

interface Patient {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  birth_date: string;
  birth_place: string;
  image_signature?: string | null;
  image_signature_active?: boolean;
  hardware_config?: any | null; // Supabase JSONB type
  personal_rate?: string | null; // Optionale personalisierte Rate (8-12 Stellen)
  created_at: string;
  updated_at: string;
}

// Helper to parse hardware config from database
const parseHardwareConfig = (config: any): { rateGenerator: HardwareConfig; analysis: HardwareConfig } | null => {
  if (!config) return null;
  try {
    if (typeof config === 'string') {
      config = JSON.parse(config);
    }
    return config as { rateGenerator: HardwareConfig; analysis: HardwareConfig };
  } catch {
    return null;
  }
};

interface PatientManagerCloudV2Props {
  onSelectPatient: (patient: Patient | null) => void;
  selectedPatient: Patient | null;
  rateGeneratorEnabled: boolean;
  analysisEnabled: boolean;
}

const PatientManagerCloudV2: React.FC<PatientManagerCloudV2Props> = ({ 
  onSelectPatient, 
  selectedPatient,
  rateGeneratorEnabled,
  analysisEnabled
}) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    birth_date: '',
    birth_place: '',
    image_signature: '',
    personal_rate: ''
  });
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [analyzingImage, setAnalyzingImage] = useState(false);
  const [ollamaConnected, setOllamaConnected] = useState(false);
  const [imageSignatureActive, setImageSignatureActive] = useState(true);
  const [hardwareConfig, setHardwareConfig] = useState<{
    rateGenerator: HardwareConfig;
    analysis: HardwareConfig;
  }>({
    rateGenerator: DEFAULT_HARDWARE_CONFIG,
    analysis: DEFAULT_HARDWARE_CONFIG
  });
  const [hardwareConfigOpen, setHardwareConfigOpen] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { toast } = useToast();
  const { user } = useAuth();

  // Prüfe Ollama-Verbindung beim Start
  useEffect(() => {
    checkOllamaConnection().then(setOllamaConnected);
  }, []);

  // Lade Patienten von Cloud (V2 Tabelle)
  useEffect(() => {
    if (user) {
      loadPatients();
      
      // Realtime-Updates
      const channel = supabase
        .channel('patients-v2-changes')
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'public',
            table: 'patients_v2',
          },
          () => {
            loadPatients();
          }
        )
        .subscribe();

      return () => {
        supabase.removeChannel(channel);
      };
    }
  }, [user]);

  const loadPatients = async () => {
    try {
      const { data, error } = await supabase
        .from('patients_v2')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      // Parse patients with proper types
      const parsedPatients = (data || []).map(p => ({
        ...p,
        hardware_config: parseHardwareConfig(p.hardware_config)
      }));
      setPatients(parsedPatients);
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Fehler",
        description: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    try {
      patientSchema.parse(formData);
      setErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        error.errors.forEach((err) => {
          if (err.path[0]) {
            newErrors[err.path[0].toString()] = err.message;
          }
        });
        setErrors(newErrors);
      }
      return false;
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImageFile(file);
    setAnalyzingImage(true);

    try {
      const result = await analyzeImageWithOllama(file);
      
      if (result.error) {
        throw new Error(result.error);
      }

      setFormData(prev => ({ ...prev, image_signature: result.signature }));
      
      const isPerceptualHash = result.signature.startsWith('PHASH:');
      toast({
        title: "Bild analysiert",
        description: isPerceptualHash 
          ? "Perceptual Hash Signatur erstellt (Ollama Fallback)" 
          : "Bildsignatur wurde mit Ollama llava erstellt",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Bildanalyse fehlgeschlagen",
        description: error.message,
      });
    } finally {
      setAnalyzingImage(false);
    }
  };

  const handleAdd = async () => {
    if (!validateForm()) return;
    if (!user) return;

    setSubmitting(true);
    try {
      const { data, error } = await supabase
        .from('patients_v2')
        .insert([{
          user_id: user.id,
          first_name: formData.first_name,
          last_name: formData.last_name,
          birth_date: formData.birth_date,
          birth_place: formData.birth_place,
          image_signature: formData.image_signature || null,
          image_signature_active: imageSignatureActive,
          hardware_config: hardwareConfig as any,
          personal_rate: formData.personal_rate || null,
        }])
        .select()
        .single();

      if (error) throw error;

      setFormData({ first_name: '', last_name: '', birth_date: '', birth_place: '', image_signature: '', personal_rate: '' });
      setImageFile(null);
      setHardwareConfig({
        rateGenerator: DEFAULT_HARDWARE_CONFIG,
        analysis: DEFAULT_HARDWARE_CONFIG
      });
      setIsAdding(false);
      toast({
        title: "Erfolg",
        description: "Patient hinzugefügt",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Fehler",
        description: error.message,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (patient: Patient) => {
    setEditingId(patient.id);
    setFormData({
      first_name: patient.first_name,
      last_name: patient.last_name,
      birth_date: patient.birth_date,
      birth_place: patient.birth_place,
      image_signature: patient.image_signature || '',
      personal_rate: patient.personal_rate || ''
    });
    setImageSignatureActive(patient.image_signature_active ?? true);
    const parsedConfig = parseHardwareConfig(patient.hardware_config);
    setHardwareConfig(parsedConfig || {
      rateGenerator: DEFAULT_HARDWARE_CONFIG,
      analysis: DEFAULT_HARDWARE_CONFIG
    });
  };

  const handleUpdate = async () => {
    if (!editingId || !validateForm()) return;

    setSubmitting(true);
    try {
      const updateData: any = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        birth_date: formData.birth_date,
        birth_place: formData.birth_place,
        image_signature_active: imageSignatureActive,
        hardware_config: hardwareConfig as any,
        personal_rate: formData.personal_rate || null,
      };
      if (formData.image_signature && formData.image_signature.trim() !== '') {
        updateData.image_signature = formData.image_signature;
      }
      const { error } = await supabase
        .from('patients_v2')
        .update(updateData)
        .eq('id', editingId);

      if (error) throw error;

      // Aktive Harmonisierungs-Sessions: copen_rate nachziehen
      // Sicher: nur Sessions die noch nicht abgeschlossen sind, nur dieser Patient,
      // nur dieser User. Bei Fehlern wird der Patient-Update NICHT zurückgerollt –
      // wir loggen lediglich und informieren den Nutzer.
      const syncedPatient = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        birth_date: formData.birth_date,
        birth_place: formData.birth_place,
        personal_rate: formData.personal_rate || null,
      };
      let updatedSessionCount = 0;
      try {
        const activeStatuses = ['pending', 'queued', 'running', 'paused'];
        const tables = ['harmonization_sessions_v2', 'morphic_field_sessions'] as const;
        for (const table of tables) {
          const { data: sessions, error: loadErr } = await supabase
            .from(table)
            .select('id, word, copen_rate')
            .eq('patient_id', editingId)
            .eq('user_id', user!.id)
            .in('status', activeStatuses);

          if (loadErr || !sessions) continue;

          for (const s of sessions) {
            const newRate = calculateClientRate(syncedPatient, s.word).toString();
            if (newRate !== (s.copen_rate ?? '')) {
              const { error: updErr } = await supabase
                .from(table)
                .update({ copen_rate: newRate })
                .eq('id', s.id);
              if (!updErr) updatedSessionCount++;
            }
          }
        }
      } catch (syncErr) {
        console.error('Fehler beim Aktualisieren der Klienten-Rate in laufenden Sessions:', syncErr);
      }

      setEditingId(null);
      setFormData({ first_name: '', last_name: '', birth_date: '', birth_place: '', image_signature: '', personal_rate: '' });
      setHardwareConfig({
        rateGenerator: DEFAULT_HARDWARE_CONFIG,
        analysis: DEFAULT_HARDWARE_CONFIG
      });

      // Update selectedPatient wenn er editiert wurde
      if (selectedPatient?.id === editingId) {
        const updated = patients.find(p => p.id === editingId);
        if (updated) {
          onSelectPatient({
            ...updated,
            ...formData,
            image_signature: (formData.image_signature && formData.image_signature.trim() !== '') ? formData.image_signature : updated.image_signature,
            image_signature_active: imageSignatureActive,
            hardware_config: hardwareConfig
          });
        }
      }

      toast({
        title: "Erfolg",
        description: updatedSessionCount > 0
          ? `Patient aktualisiert. Klienten-Rate in ${updatedSessionCount} laufender Harmonisierung${updatedSessionCount === 1 ? '' : 'en'} nachgezogen.`
          : "Patient aktualisiert",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Fehler",
        description: error.message,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Patient wirklich löschen? (DSGVO-konform)')) return;

    try {
      const { error } = await supabase
        .from('patients_v2')
        .delete()
        .eq('id', id);

      if (error) throw error;

      if (selectedPatient?.id === id) {
        onSelectPatient(null);
      }
      toast({
        title: "Erfolg",
        description: "Patient gelöscht",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Fehler",
        description: error.message,
      });
    }
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingId(null);
    setFormData({ first_name: '', last_name: '', birth_date: '', birth_place: '', image_signature: '', personal_rate: '' });
    setImageFile(null);
    setErrors({});
    setHardwareConfig({
      rateGenerator: DEFAULT_HARDWARE_CONFIG,
      analysis: DEFAULT_HARDWARE_CONFIG
    });
    setHardwareConfigOpen(false);
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Patientenverwaltung V2 (Cloud)
          </span>
          {!isAdding && !editingId && (
            <Button onClick={() => setIsAdding(true)} size="sm" disabled={submitting}>
              <Plus className="h-4 w-4 mr-1" />
              Neu
            </Button>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Formular für Neu/Bearbeiten */}
        {(isAdding || editingId) && (
          <div className="border-2 border-primary/30 rounded-lg p-4 bg-primary/5 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <Label>Vorname *</Label>
                <Input
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  placeholder="Vorname"
                  disabled={submitting}
                />
                {errors.first_name && (
                  <p className="text-sm text-destructive mt-1">{errors.first_name}</p>
                )}
              </div>
              <div>
                <Label>Nachname *</Label>
                <Input
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                  placeholder="Nachname"
                  disabled={submitting}
                />
                {errors.last_name && (
                  <p className="text-sm text-destructive mt-1">{errors.last_name}</p>
                )}
              </div>
              <div>
                <Label>Geburtsdatum</Label>
                <Input
                  type="date"
                  value={formData.birth_date}
                  onChange={(e) => setFormData({...formData, birth_date: e.target.value})}
                  disabled={submitting}
                />
              </div>
              <div>
                <Label>Geburtsort</Label>
                <Input
                  value={formData.birth_place}
                  onChange={(e) => setFormData({...formData, birth_place: e.target.value})}
                  placeholder="Geburtsort"
                  disabled={submitting}
                />
                {errors.birth_place && (
                  <p className="text-sm text-destructive mt-1">{errors.birth_place}</p>
                )}
              </div>
              
              {/* Bild-Upload für Ollama-Analyse */}
              <div className="col-span-full">
                <Label className="flex items-center gap-2">
                  <ImageIcon className="h-4 w-4" />
                  Patientenbild (Optional - Ollama llava Analyse)
                  {ollamaConnected && <Sparkles className="h-3 w-3 text-green-500" />}
                </Label>
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  disabled={submitting || analyzingImage || !ollamaConnected}
                />
                {analyzingImage && (
                  <p className="text-sm text-muted-foreground mt-1 flex items-center gap-2">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Analysiere Bild mit Ollama llava...
                  </p>
                )}
                {!ollamaConnected && (
                  <p className="text-sm text-yellow-600 mt-1">
                    ⚠️ Ollama nicht verbunden. Starten Sie: OLLAMA_ORIGINS=* ollama serve
                  </p>
                )}
                {formData.image_signature && (
                  <div className="mt-2 p-3 bg-primary/10 rounded-lg border border-primary/30 space-y-2">
                    <div className="text-xs text-muted-foreground">
                      <strong className="text-foreground">Bildsignatur:</strong>
                      <div className="mt-1 p-2 bg-background/50 rounded font-mono text-xs break-all">
                        {formData.image_signature.substring(0, 200)}...
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-2 bg-background/30 rounded">
                      <span className="text-sm font-medium">Bildsignatur in Resonanzanalyse verwenden:</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={imageSignatureActive}
                          onChange={(e) => setImageSignatureActive(e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                        <span className="ml-3 text-sm font-medium">
                          {imageSignatureActive ? 'Aktiv' : 'Inaktiv'}
                        </span>
                      </label>
                    </div>
                  </div>
                 )}
              </div>
              
              {/* Personalisierte Rate (Optional) */}
              <div>
                <Label>Personalisierte Rate (Optional, 8-12 Stellen)</Label>
                <Input
                  value={formData.personal_rate}
                  onChange={(e) => {
                    const value = e.target.value;
                    // Nur Zahlen erlauben und auf 12 Stellen begrenzen
                    if (/^\d{0,12}$/.test(value)) {
                      setFormData({...formData, personal_rate: value});
                    }
                  }}
                  placeholder="z.B. 12345678"
                  disabled={submitting}
                  maxLength={12}
                />
                {formData.personal_rate && formData.personal_rate.length < 8 && (
                  <p className="text-sm text-yellow-600 mt-1">
                    Mindestens 8 Stellen erforderlich
                  </p>
                )}
                {formData.personal_rate && formData.personal_rate.length >= 8 && (
                  <p className="text-sm text-green-600 mt-1">
                    ✓ Personalisierte Rate wird in Berechnungen einbezogen
                  </p>
                )}
              </div>
            </div>

            {/* Hardware-Konfiguration (Collapsible) */}
            <Collapsible open={hardwareConfigOpen} onOpenChange={setHardwareConfigOpen}>
              <CollapsibleTrigger asChild>
                <Button variant="outline" className="w-full">
                  <Settings className="h-4 w-4 mr-2" />
                  Hardware-Algorithmen Konfiguration
                  {hardwareConfigOpen ? ' (Schließen)' : ' (Öffnen)'}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3">
                <PatientHardwareConfig
                  patientName={editingId 
                    ? `${formData.first_name} ${formData.last_name}` 
                    : 'Neuer Patient'}
                  config={hardwareConfig}
                  onChange={setHardwareConfig}
                  rateGeneratorEnabled={rateGeneratorEnabled}
                  analysisEnabled={analysisEnabled}
                />
              </CollapsibleContent>
            </Collapsible>

            <div className="flex gap-2">
              <Button 
                onClick={editingId ? handleUpdate : handleAdd} 
                size="sm"
                disabled={submitting}
              >
                {submitting ? (
                  <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                ) : (
                  <Check className="h-4 w-4 mr-1" />
                )}
                {editingId ? 'Aktualisieren' : 'Hinzufügen'}
              </Button>
              <Button 
                onClick={handleCancel} 
                variant="outline" 
                size="sm"
                disabled={submitting}
              >
                <X className="h-4 w-4 mr-1" />
                Abbrechen
              </Button>
            </div>
          </div>
        )}

        {/* Patientenliste */}
        {patients.length === 0 ? (
          <p className="text-center text-muted-foreground py-4">
            Keine Patienten vorhanden
          </p>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {patients.map(patient => (
              <div
                key={patient.id}
                className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
                  selectedPatient?.id === patient.id
                    ? 'border-primary bg-primary/10'
                    : 'border-border hover:border-primary/50'
                }`}
                onClick={() => onSelectPatient(patient)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-semibold">
                      {patient.first_name} {patient.last_name}
                    </div>
                    {patient.birth_date && (
                      <div className="text-sm text-muted-foreground">
                        Geboren: {new Date(patient.birth_date).toLocaleDateString('de-DE')}
                      </div>
                    )}
                    {patient.birth_place && (
                      <div className="text-sm text-muted-foreground">
                        Ort: {patient.birth_place}
                      </div>
                    )}
                    {patient.image_signature && (
                      <div className="text-xs text-primary mt-1 flex items-center gap-1">
                        <ImageIcon className="h-3 w-3" />
                        Bildsignatur vorhanden
                      </div>
                    )}
                     {patient.hardware_config && (
                      <div className="text-xs text-blue-500 mt-1 flex items-center gap-1">
                        <Settings className="h-3 w-3" />
                        Hardware-Algorithmen konfiguriert
                      </div>
                    )}
                    {patient.personal_rate && patient.personal_rate.length >= 8 && (
                      <div className="text-xs text-purple-500 mt-1 flex items-center gap-1">
                        <Zap className="h-3 w-3" />
                        Personalisierte Rate: {patient.personal_rate}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit(patient);
                      }}
                      variant="ghost"
                      size="sm"
                      disabled={submitting}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(patient.id);
                      }}
                      variant="ghost"
                      size="sm"
                      disabled={submitting}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PatientManagerCloudV2;
