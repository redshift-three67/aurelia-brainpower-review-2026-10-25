import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Users, Plus, Trash2, Edit2, Check, X, Loader2, Image as ImageIcon, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/hooks/useAuth';
import { z } from 'zod';
import { analyzeImageWithOllama, checkOllamaConnection } from '@/utils/ollamaClient';

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
  created_at: string;
  updated_at: string;
}

interface PatientManagerCloudProps {
  onSelectPatient: (patient: Patient | null) => void;
  selectedPatient: Patient | null;
}

const PatientManagerCloud: React.FC<PatientManagerCloudProps> = ({ 
  onSelectPatient, 
  selectedPatient 
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
    image_signature: ''
  });
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [analyzingImage, setAnalyzingImage] = useState(false);
  const [ollamaConnected, setOllamaConnected] = useState(false);
  const [imageSignatureActive, setImageSignatureActive] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { toast } = useToast();
  const { user } = useAuth();

  // Prüfe Ollama-Verbindung beim Start
  useEffect(() => {
    checkOllamaConnection().then(setOllamaConnected);
  }, []);

  // Lade Patienten von Cloud
  useEffect(() => {
    if (user) {
      loadPatients();
      
      // Realtime-Updates
      const channel = supabase
        .channel('patients-changes')
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'public',
            table: 'patients',
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
        .from('patients')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      setPatients(data || []);
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

      // Aktualisiere formData mit Bildsignatur
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
        .from('patients')
        .insert({
          user_id: user.id,
          ...formData,
          image_signature_active: imageSignatureActive,
        })
        .select()
        .single();

      if (error) throw error;

      setFormData({ first_name: '', last_name: '', birth_date: '', birth_place: '', image_signature: '' });
      setImageFile(null);
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
      image_signature: patient.image_signature || ''
    });
    setImageSignatureActive(patient.image_signature_active ?? true);
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
      };
      if (formData.image_signature && formData.image_signature.trim() !== '') {
        updateData.image_signature = formData.image_signature;
      }
      const { error } = await supabase
        .from('patients')
        .update(updateData)
        .eq('id', editingId);

      if (error) throw error;

      setEditingId(null);
      setFormData({ first_name: '', last_name: '', birth_date: '', birth_place: '', image_signature: '' });

      // Update selectedPatient wenn er editiert wurde
      if (selectedPatient?.id === editingId) {
        const updated = patients.find(p => p.id === editingId);
        if (updated) {
          onSelectPatient({
            ...updated,
            ...formData,
            image_signature: (formData.image_signature && formData.image_signature.trim() !== '') ? formData.image_signature : updated.image_signature,
            image_signature_active: imageSignatureActive 
          });
        }
      }

      toast({
        title: "Erfolg",
        description: "Patient aktualisiert",
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
        .from('patients')
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
    setFormData({ first_name: '', last_name: '', birth_date: '', birth_place: '', image_signature: '' });
    setImageFile(null);
    setErrors({});
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
            Patientenverwaltung (Cloud)
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
            </div>
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

export default PatientManagerCloud;
