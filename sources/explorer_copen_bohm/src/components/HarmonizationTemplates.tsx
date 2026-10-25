import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { BookTemplate, Save, Trash2, Download, Loader2, Plus } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/hooks/useAuth';

interface TemplateSession {
  word: string;
  tested_potency: string;
  duration_seconds: number;
  copen_rate?: string;
}

interface Template {
  id: string;
  name: string;
  description?: string;
  sessions: TemplateSession[];
  created_at: string;
}

interface HarmonizationTemplatesProps {
  patientId: string;
  onLoadTemplate?: (sessions: TemplateSession[]) => void;
}

const HarmonizationTemplates: React.FC<HarmonizationTemplatesProps> = ({ 
  patientId, 
  onLoadTemplate 
}) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');
  const [newTemplateDesc, setNewTemplateDesc] = useState('');
  const [selectedSessions, setSelectedSessions] = useState<string[]>([]);
  const [availableSessions, setAvailableSessions] = useState<TemplateSession[]>([]);
  const { toast } = useToast();
  const { user } = useAuth();

  useEffect(() => {
    if (user && patientId) {
      loadTemplates();
      loadAvailableSessions();
    }
  }, [user, patientId]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('harmonization_templates')
        .select('*')
        .eq('patient_id', patientId)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setTemplates((data || []).map(t => ({
        ...t,
        sessions: t.sessions as unknown as TemplateSession[]
      })));
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableSessions = async () => {
    try {
      // Lade abgeschlossene Harmonisierungen
      const { data: harmonizations, error: harmError } = await supabase
        .from('harmonization_sessions')
        .select('word, tested_potency, duration_seconds, copen_rate')
        .eq('patient_id', patientId)
        .eq('status', 'completed')
        .order('completed_at', { ascending: false })
        .limit(50);

      if (harmError) throw harmError;

      // Lade auch aus dem Archiv
      const { data: archives, error: archError } = await supabase
        .from('analysis_archives')
        .select('word, tested_potency, copen_rate')
        .eq('patient_id', patientId)
        .order('created_at', { ascending: false })
        .limit(50);

      if (archError) throw archError;

      // Kombiniere beide Listen
      const combined: TemplateSession[] = [
        ...(harmonizations || []).map(h => ({
          word: h.word,
          tested_potency: h.tested_potency || 'D30',
          duration_seconds: h.duration_seconds || 3600,
          copen_rate: h.copen_rate,
        })),
        ...(archives || []).map(a => ({
          word: a.word,
          tested_potency: a.tested_potency || 'D30',
          duration_seconds: 3600, // Default 1 Stunde
          copen_rate: a.copen_rate,
        })),
      ];

      // Dedupliziere nach Wort
      const unique = Array.from(
        new Map(combined.map(item => [item.word, item])).values()
      );

      setAvailableSessions(unique);
    } catch (error: any) {
      console.error('Fehler beim Laden der Sitzungen:', error);
    }
  };

  const handleSaveTemplate = async () => {
    if (!newTemplateName.trim()) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: 'Bitte geben Sie einen Namen ein',
      });
      return;
    }

    if (selectedSessions.length === 0) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: 'Bitte wählen Sie mindestens eine Sitzung aus',
      });
      return;
    }

    try {
      setSaving(true);
      const sessions = availableSessions.filter(s => 
        selectedSessions.includes(s.word)
      );

      const { error } = await supabase
        .from('harmonization_templates')
        .insert([{
          user_id: user!.id,
          patient_id: patientId,
          name: newTemplateName,
          description: newTemplateDesc || null,
          sessions: sessions as any,
        }]);

      if (error) throw error;

      toast({
        title: 'Erfolg',
        description: `Template "${newTemplateName}" gespeichert`,
      });

      setNewTemplateName('');
      setNewTemplateDesc('');
      setSelectedSessions([]);
      await loadTemplates();
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: error.message,
      });
    } finally {
      setSaving(false);
    }
  };

  const handleLoadTemplate = (template: Template) => {
    if (onLoadTemplate) {
      onLoadTemplate(template.sessions);
      toast({
        title: 'Template geladen',
        description: `${template.sessions.length} Harmonisierungen bereit`,
      });
    }
  };

  const handleDeleteTemplate = async (id: string) => {
    if (!confirm('Template wirklich löschen?')) return;

    try {
      const { error } = await supabase
        .from('harmonization_templates')
        .delete()
        .eq('id', id);

      if (error) throw error;

      toast({
        title: 'Erfolg',
        description: 'Template gelöscht',
      });

      await loadTemplates();
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: error.message,
      });
    }
  };

  const toggleSessionSelection = (word: string) => {
    setSelectedSessions(prev => 
      prev.includes(word) 
        ? prev.filter(w => w !== word)
        : [...prev, word]
    );
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
    <div className="space-y-4">
      {/* Neues Template erstellen */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Neues Template erstellen
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Template-Name</Label>
            <Input
              value={newTemplateName}
              onChange={(e) => setNewTemplateName(e.target.value)}
              placeholder="z.B. Akut-Protokoll"
            />
          </div>
          <div>
            <Label>Beschreibung (optional)</Label>
            <Textarea
              value={newTemplateDesc}
              onChange={(e) => setNewTemplateDesc(e.target.value)}
              placeholder="Beschreibung des Templates..."
              className="min-h-20"
            />
          </div>
          
          <div>
            <Label className="mb-2 block">
              Sitzungen auswählen ({selectedSessions.length} ausgewählt)
            </Label>
            <div className="border rounded-lg max-h-60 overflow-y-auto p-2 space-y-1">
              {availableSessions.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Keine Sitzungen verfügbar. Führen Sie zuerst Harmonisierungen durch.
                </p>
              ) : (
                availableSessions.map((session) => (
                  <div
                    key={session.word}
                    onClick={() => toggleSessionSelection(session.word)}
                    className={`p-2 border rounded cursor-pointer transition-colors ${
                      selectedSessions.includes(session.word)
                        ? 'bg-primary/10 border-primary'
                        : 'hover:bg-muted'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{session.word}</span>
                      <span className="text-sm text-muted-foreground">
                        {session.tested_potency}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <Button 
            onClick={handleSaveTemplate} 
            disabled={saving}
            className="w-full"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Template speichern
          </Button>
        </CardContent>
      </Card>

      {/* Gespeicherte Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookTemplate className="h-5 w-5" />
            Gespeicherte Templates
            <span className="text-sm font-normal text-muted-foreground ml-2">
              ({templates.length})
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {templates.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">
              Keine Templates gespeichert
            </p>
          ) : (
            <div className="space-y-2">
              {templates.map((template) => (
                <div key={template.id} className="border rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <h4 className="font-semibold">{template.name}</h4>
                      {template.description && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {template.description}
                        </p>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">
                        {template.sessions.length} Harmonisierungen • {' '}
                        {new Date(template.created_at).toLocaleDateString('de-DE')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 mt-2">
                    <Button
                      onClick={() => handleLoadTemplate(template)}
                      variant="secondary"
                      size="sm"
                      className="flex-1"
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Laden
                    </Button>
                    <Button
                      onClick={() => handleDeleteTemplate(template.id)}
                      variant="destructive"
                      size="sm"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default HarmonizationTemplates;
