import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Archive, Loader2, Trash2, Eye, Download } from 'lucide-react';
import { supabase } from '@/integrations/supabase/client';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/hooks/useAuth';
import { LEVELS, getLevelDisplayName, getLevelDescription } from '@/utils/levelResonance';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';

interface AnalysisArchive {
  id: string;
  word: string;
  copen_rate: string;
  tested_potency: string | null;
  highest_resonance_level: number | null;
  highest_resonance_value: number | null;
  analysis_timestamp: string;
  patient_data: any;
  level_1_physical_particles: number | null;
  level_2_physical_structure: number | null;
  level_3_etheric_prana: number | null;
  level_4_etheric_meridians: number | null;
  level_5_astral_emotions: number | null;
  level_6_astral_thoughts: number | null;
  level_7_mental_time: number | null;
  level_8_mental_constructs: number | null;
  level_9_causal_blueprints: number | null;
  level_10_causal_alchemy: number | null;
  level_11_atmic_identity: number | null;
  level_12_atmic_love: number | null;
  level_13_creator: number | null;
}

export const AnalysisArchiveCloud = () => {
  const [archives, setArchives] = useState<AnalysisArchive[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedArchive, setSelectedArchive] = useState<AnalysisArchive | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadArchives();
    }
  }, [user]);

  const loadArchives = async () => {
    try {
      const { data, error } = await supabase
        .from('analysis_archives')
        .select('*')
        .order('analysis_timestamp', { ascending: false });

      if (error) throw error;
      setArchives(data || []);
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

  const handleDelete = async (id: string) => {
    if (!confirm('Analyse wirklich löschen?')) return;

    try {
      const { error } = await supabase
        .from('analysis_archives')
        .delete()
        .eq('id', id);

      if (error) throw error;

      toast({
        title: 'Erfolg',
        description: 'Analyse gelöscht',
      });
      
      loadArchives();
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Fehler',
        description: error.message,
      });
    }
  };

  const handleViewDetails = (archive: AnalysisArchive) => {
    setSelectedArchive(archive);
    setDetailsOpen(true);
  };

  const exportToCSV = () => {
    if (!selectedArchive) return;

    const levelData = LEVELS.map(level => {
      const key = `level_${level.id}_${level.name.toLowerCase().replace(/[^a-z]/g, '_').substring(0, 30)}`;
      const value = (selectedArchive as any)[key] || 0;
      return `${level.germanName},${value}`;
    }).join('\n');

    const csv = `Wortenergie,${selectedArchive.word}\nCopen-Rate,${selectedArchive.copen_rate}\nPotenz,${selectedArchive.tested_potency || 'N/A'}\nHöchste Resonanzebene,${getLevelDisplayName(selectedArchive.highest_resonance_level || 1)}\nResonanzwert,${selectedArchive.highest_resonance_value || 0}\n\nEbene,Resonanz (%)\n${levelData}`;

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analyse_${selectedArchive.word}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
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
    <>
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="flex items-center justify-between gap-2 text-sm">
            <span className="flex items-center gap-2">
              <Archive className="h-4 w-4" />
              Analysearchiv (12+1 Ebenen)
            </span>
            {archives.length > 0 && (
              <Button
                variant="destructive"
                size="sm"
                onClick={async () => {
                  if (!confirm('Alle Archiveinträge löschen?')) return;
                  try {
                    const { error } = await supabase
                      .from('analysis_archives')
                      .delete()
                      .eq('user_id', user!.id);
                    if (error) throw error;
                    toast({ title: 'Erfolg', description: 'Alle Archiveinträge gelöscht' });
                    loadArchives();
                  } catch (e: any) {
                    toast({ variant: 'destructive', title: 'Fehler', description: e.message });
                  }
                }}
              >
                Alle löschen
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="max-h-80 overflow-y-auto">
          {archives.length === 0 ? (
            <p className="text-center text-muted-foreground py-4 text-xs">
              Keine archivierten Analysen vorhanden
            </p>
          ) : (
            <Table className="text-xs">
              <TableHeader>
                <TableRow>
                  <TableHead className="text-xs">Wortenergie</TableHead>
                  <TableHead className="text-xs">Copen-Rate</TableHead>
                  <TableHead className="text-xs">Höchste Ebene</TableHead>
                  <TableHead className="text-xs">Resonanz</TableHead>
                  <TableHead className="text-xs">Datum</TableHead>
                  <TableHead className="text-right text-xs">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {archives.map((archive) => (
                  <TableRow key={archive.id}>
                    <TableCell className="font-medium text-xs">{archive.word}</TableCell>
                    <TableCell className="text-xs">{archive.copen_rate}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs">
                        {getLevelDisplayName(archive.highest_resonance_level || 1)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs">{archive.highest_resonance_value?.toFixed(1)}%</TableCell>
                    <TableCell className="text-xs">
                      {new Date(archive.analysis_timestamp).toLocaleDateString('de-DE')}
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleViewDetails(archive)}
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDelete(archive.id)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog open={detailsOpen} onOpenChange={setDetailsOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Ebenen-Resonanz-Analyse</DialogTitle>
            <DialogDescription>
              Detaillierte Resonanzwerte für alle 12+1 Ebenen
            </DialogDescription>
          </DialogHeader>
          
          {selectedArchive && (
            <div className="space-y-6">
              {/* Grunddaten */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-primary/5 rounded-lg">
                <div>
                  <p className="text-sm text-muted-foreground">Wortenergie</p>
                  <p className="font-semibold">{selectedArchive.word}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Copen-Rate</p>
                  <p className="font-semibold">{selectedArchive.copen_rate}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Potenz</p>
                  <p className="font-semibold">{selectedArchive.tested_potency || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Analysezeitpunkt</p>
                  <p className="font-semibold">
                    {new Date(selectedArchive.analysis_timestamp).toLocaleString('de-DE')}
                  </p>
                </div>
              </div>

              {/* Höchste Resonanzebene */}
              <div className="p-4 bg-green-500/10 border-2 border-green-500/30 rounded-lg">
                <h3 className="font-bold text-lg mb-2">Höchste Resonanzebene</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold text-green-600">
                      {getLevelDisplayName(selectedArchive.highest_resonance_level || 1)}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {getLevelDescription(selectedArchive.highest_resonance_level || 1)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-green-600">
                      {selectedArchive.highest_resonance_value?.toFixed(1)}%
                    </p>
                    <p className="text-sm text-muted-foreground">Resonanzstärke</p>
                  </div>
                </div>
              </div>

              {/* Alle Ebenen */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-lg">Resonanz auf allen Ebenen</h3>
                  <Button size="sm" variant="outline" onClick={exportToCSV}>
                    <Download className="h-4 w-4 mr-2" />
                    CSV Export
                  </Button>
                </div>
                <div className="space-y-3">
                  {LEVELS.map((level) => {
                    const fieldNames = [
                      'level_1_physical_particles',
                      'level_2_physical_structure',
                      'level_3_etheric_prana',
                      'level_4_etheric_meridians',
                      'level_5_astral_emotions',
                      'level_6_astral_thoughts',
                      'level_7_mental_time',
                      'level_8_mental_constructs',
                      'level_9_causal_blueprints',
                      'level_10_causal_alchemy',
                      'level_11_atmic_identity',
                      'level_12_atmic_love',
                      'level_13_creator'
                    ];
                    const value = (selectedArchive as any)[fieldNames[level.id - 1]] || 0;
                    const isHighest = level.id === selectedArchive.highest_resonance_level;

                    return (
                      <div
                        key={level.id}
                        className={`p-3 rounded-lg border ${
                          isHighest ? 'bg-green-500/10 border-green-500/30' : 'bg-muted/30'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex-1">
                            <p className="font-semibold text-sm">{level.germanName}</p>
                            <p className="text-xs text-muted-foreground">{level.description}</p>
                          </div>
                          <Badge variant={isHighest ? 'default' : 'outline'}>
                            {typeof value === 'number' ? value.toFixed(1) : 0}%
                          </Badge>
                        </div>
                        <div className="w-full bg-muted/50 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${
                              isHighest ? 'bg-green-500' : 'bg-primary'
                            }`}
                            style={{ width: `${Math.min(100, typeof value === 'number' ? value : 0)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default AnalysisArchiveCloud;
