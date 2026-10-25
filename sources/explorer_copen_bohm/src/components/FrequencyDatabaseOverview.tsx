import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Radio, 
  Waves, 
  Music, 
  Flower2, 
  Pill,
  Bug,
  Database,
  Download,
  Layers,
  ChevronRight,
  Sparkles,
  CheckSquare,
  Square,
  Save,
  FolderOpen,
  Trash2,
  BookTemplate
} from 'lucide-react';
import { 
  FREQUENCY_DATABASES, 
  getEntriesForFrequencyDatabase, 
  getFrequencyStatistics, 
  getAllFrequencyEntries 
} from '@/utils/frequencyDatabases';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/hooks/useAuth';
import { toast } from '@/hooks/use-toast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

interface FrequencyDatabaseOverviewProps {
  onLoadDatabase: (entries: string[], name: string, count: number) => void;
  disabled?: boolean;
}

interface SavedTemplate {
  id: string;
  name: string;
  entries: string[];
  created_at: string;
}

const DATABASE_ICONS: Record<string, React.ReactNode> = {
  paulSchmidt: <Radio className="w-5 h-5" />,
  rife: <Waves className="w-5 h-5" />,
  solfeggio: <Music className="w-5 h-5" />,
  bachBlueten: <Flower2 className="w-5 h-5" />,
  schuesslerSalze: <Pill className="w-5 h-5" />,
  nosoden: <Bug className="w-5 h-5" />,
};

const DATABASE_COLORS: Record<string, string> = {
  paulSchmidt: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  rife: 'text-green-500 bg-green-500/10 border-green-500/20',
  solfeggio: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
  bachBlueten: 'text-pink-500 bg-pink-500/10 border-pink-500/20',
  schuesslerSalze: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  nosoden: 'text-red-500 bg-red-500/10 border-red-500/20',
};

const FrequencyDatabaseOverview = ({ onLoadDatabase, disabled = false }: FrequencyDatabaseOverviewProps) => {
  const stats = getFrequencyStatistics();
  const { user } = useAuth();
  const [selectedSystems, setSelectedSystems] = useState<Set<string>>(new Set());
  const [savedTemplates, setSavedTemplates] = useState<SavedTemplate[]>([]);
  const [templateName, setTemplateName] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);

  // Load saved frequency templates on mount
  useEffect(() => {
    if (user) {
      loadSavedTemplates();
    }
  }, [user]);

  const loadSavedTemplates = async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('word_databases')
        .select('id, name, entries, created_at')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setSavedTemplates(data || []);
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveTemplate = async () => {
    if (!user || selectedSystems.size === 0 || !templateName.trim()) {
      toast({
        title: 'Fehler',
        description: 'Bitte wähle mindestens ein System und gib einen Namen ein.',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    try {
      const combinedEntries: string[] = [];
      const systemNames: string[] = [];
      
      selectedSystems.forEach(key => {
        const db = FREQUENCY_DATABASES[key];
        const entries = getEntriesForFrequencyDatabase(key);
        combinedEntries.push(...entries);
        systemNames.push(db.name);
      });

      const fullName = `Frequenz: ${templateName.trim()}`;
      
      const { error } = await supabase
        .from('word_databases')
        .insert({
          user_id: user.id,
          name: fullName,
          entries: combinedEntries,
        });

      if (error) throw error;

      toast({
        title: 'Template gespeichert',
        description: `"${templateName}" mit ${combinedEntries.length} Einträgen gespeichert.`,
      });

      setTemplateName('');
      setSaveDialogOpen(false);
      setSelectedSystems(new Set());
      loadSavedTemplates();
    } catch (error) {
      console.error('Error saving template:', error);
      toast({
        title: 'Fehler',
        description: 'Template konnte nicht gespeichert werden.',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleLoadTemplate = (template: SavedTemplate) => {
    const displayName = template.name.replace('Frequenz: ', '');
    onLoadDatabase(template.entries, displayName, template.entries.length);
    toast({
      title: 'Template geladen',
      description: `"${displayName}" mit ${template.entries.length} Einträgen geladen.`,
    });
  };

  const handleDeleteTemplate = async (templateId: string, templateName: string) => {
    try {
      const { error } = await supabase
        .from('word_databases')
        .delete()
        .eq('id', templateId);

      if (error) throw error;

      toast({
        title: 'Template gelöscht',
        description: `"${templateName.replace('Frequenz: ', '')}" wurde gelöscht.`,
      });

      loadSavedTemplates();
    } catch (error) {
      console.error('Error deleting template:', error);
      toast({
        title: 'Fehler',
        description: 'Template konnte nicht gelöscht werden.',
        variant: 'destructive',
      });
    }
  };
  
  const handleLoadAll = () => {
    const allEntries = getAllFrequencyEntries();
    onLoadDatabase(allEntries, 'Alle Frequenz-Datenbanken', allEntries.length);
  };

  const handleLoadSingle = (key: string) => {
    const db = FREQUENCY_DATABASES[key];
    const entries = getEntriesForFrequencyDatabase(key);
    onLoadDatabase(entries, db.name, entries.length);
  };

  const handleLoadSelected = () => {
    if (selectedSystems.size === 0) return;
    
    const combinedEntries: string[] = [];
    const names: string[] = [];
    
    selectedSystems.forEach(key => {
      const db = FREQUENCY_DATABASES[key];
      const entries = getEntriesForFrequencyDatabase(key);
      combinedEntries.push(...entries);
      names.push(db.name);
    });
    
    const combinedName = names.length <= 3 
      ? names.join(' + ') 
      : `${names.slice(0, 2).join(' + ')} +${names.length - 2} weitere`;
    
    onLoadDatabase(combinedEntries, combinedName, combinedEntries.length);
    setSelectedSystems(new Set());
  };

  const toggleSelection = (key: string) => {
    const newSelection = new Set(selectedSystems);
    if (newSelection.has(key)) {
      newSelection.delete(key);
    } else {
      newSelection.add(key);
    }
    setSelectedSystems(newSelection);
  };

  const selectAll = () => {
    const allKeys = stats.databases.map(d => d.key);
    setSelectedSystems(new Set(allKeys));
  };

  const clearSelection = () => {
    setSelectedSystems(new Set());
  };

  const selectedEntryCount = Array.from(selectedSystems).reduce((sum, key) => {
    return sum + (FREQUENCY_DATABASES[key]?.totalEntries || 0);
  }, 0);

  const maxEntries = Math.max(...stats.databases.map(d => d.totalEntries));

  return (
    <Card className="border-primary/20">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Frequenz-Datenbanken
            </CardTitle>
            <CardDescription>
              Bioresonanz, Rife, Solfeggio, Bach-Blüten, Schüssler-Salze & Nosoden
            </CardDescription>
          </div>
          <Badge variant="secondary" className="text-lg px-3 py-1">
            {stats.totalEntries.toLocaleString()} Einträge
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Gespeicherte Templates */}
        {savedTemplates.length > 0 && (
          <Card className="bg-secondary/30 border-secondary">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <BookTemplate className="w-4 h-4" />
                Gespeicherte Frequenz-Templates ({savedTemplates.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex flex-wrap gap-2">
                {savedTemplates.map((template) => (
                  <div key={template.id} className="flex items-center gap-1 bg-background rounded-lg border p-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleLoadTemplate(template)}
                      disabled={disabled}
                      className="h-7 px-2"
                    >
                      <FolderOpen className="w-3 h-3 mr-1" />
                      {template.name.replace('Frequenz: ', '')}
                      <Badge variant="outline" className="ml-1 text-[10px]">
                        {template.entries.length}
                      </Badge>
                    </Button>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive hover:text-destructive">
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Template löschen?</AlertDialogTitle>
                          <AlertDialogDescription>
                            Möchtest Du "{template.name.replace('Frequenz: ', '')}" wirklich löschen?
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                          <AlertDialogAction onClick={() => handleDeleteTemplate(template.id, template.name)}>
                            Löschen
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Gesamt-Statistik */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="pt-4 text-center">
              <p className="text-3xl font-bold text-primary">{stats.totalDatabases}</p>
              <p className="text-xs text-muted-foreground">Systeme</p>
            </CardContent>
          </Card>
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="pt-4 text-center">
              <p className="text-3xl font-bold text-primary">{stats.totalEntries.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">Frequenzen/Einträge</p>
            </CardContent>
          </Card>
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="pt-4 text-center">
              <p className="text-3xl font-bold text-primary">
                {stats.databases.reduce((sum, d) => sum + d.subcategoryCount, 0)}
              </p>
              <p className="text-xs text-muted-foreground">Kategorien</p>
            </CardContent>
          </Card>
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="pt-4 text-center">
              <p className="text-3xl font-bold text-primary">
                {Math.round(stats.totalEntries / stats.totalDatabases)}
              </p>
              <p className="text-xs text-muted-foreground">Ø pro System</p>
            </CardContent>
          </Card>
        </div>

        {/* Mehrfachauswahl Controls */}
        {selectedSystems.size > 0 && (
          <Card className="bg-primary/10 border-primary/30">
            <CardContent className="pt-4">
              <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-3">
                  <Badge variant="default" className="text-base px-3 py-1">
                    {selectedSystems.size} ausgewählt
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    ({selectedEntryCount.toLocaleString()} Einträge)
                  </span>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearSelection}
                  >
                    <Square className="w-4 h-4 mr-1" />
                    Leeren
                  </Button>
                  
                  {/* Save Template Dialog */}
                  <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant="secondary" size="sm" disabled={!user}>
                        <Save className="w-4 h-4 mr-1" />
                        Als Template speichern
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Frequenz-Template speichern</DialogTitle>
                        <DialogDescription>
                          Speichere die ausgewählten {selectedSystems.size} Systeme 
                          ({selectedEntryCount.toLocaleString()} Einträge) als Template.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <div className="space-y-2">
                          <Label htmlFor="freq-template-name">Template-Name</Label>
                          <Input
                            id="freq-template-name"
                            placeholder="z.B. Rife-Solfeggio-Kombi"
                            value={templateName}
                            onChange={(e) => setTemplateName(e.target.value)}
                          />
                        </div>
                        <div className="text-sm text-muted-foreground">
                          <p className="font-medium mb-1">Enthaltene Systeme:</p>
                          <div className="flex flex-wrap gap-1">
                            {Array.from(selectedSystems).map(key => (
                              <Badge key={key} variant="outline" className="text-xs">
                                {FREQUENCY_DATABASES[key]?.name}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setSaveDialogOpen(false)}>
                          Abbrechen
                        </Button>
                        <Button onClick={handleSaveTemplate} disabled={isSaving || !templateName.trim()}>
                          {isSaving ? 'Speichern...' : 'Speichern'}
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>

                  <Button
                    onClick={handleLoadSelected}
                    disabled={disabled}
                    size="sm"
                  >
                    <Download className="w-4 h-4 mr-1" />
                    Laden & Analysieren
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Alle/Keine Auswahl Buttons */}
        <div className="flex gap-2">
          <Button
            onClick={handleLoadAll}
            disabled={disabled}
            className="flex-1"
            size="lg"
          >
            <Layers className="w-5 h-5 mr-2" />
            Alle {stats.totalEntries.toLocaleString()} Einträge laden
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
          <Button
            variant="outline"
            onClick={selectedSystems.size === stats.databases.length ? clearSelection : selectAll}
            size="lg"
          >
            {selectedSystems.size === stats.databases.length ? (
              <>
                <Square className="w-4 h-4 mr-1" />
                Keine
              </>
            ) : (
              <>
                <CheckSquare className="w-4 h-4 mr-1" />
                Alle
              </>
            )}
          </Button>
        </div>

        {/* Datenbank-Tabelle mit Checkboxen */}
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]">Wahl</TableHead>
                <TableHead className="w-[250px]">System</TableHead>
                <TableHead>Kategorie</TableHead>
                <TableHead className="text-right">Einträge</TableHead>
                <TableHead className="text-right">Subkategorien</TableHead>
                <TableHead className="w-[150px]">Verteilung</TableHead>
                <TableHead className="text-right">Aktion</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stats.databases.map((db) => (
                <TableRow 
                  key={db.key} 
                  className={`hover:bg-muted/50 cursor-pointer ${selectedSystems.has(db.key) ? 'bg-primary/10' : ''}`}
                  onClick={() => toggleSelection(db.key)}
                >
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      checked={selectedSystems.has(db.key)}
                      onCheckedChange={() => toggleSelection(db.key)}
                    />
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded ${DATABASE_COLORS[db.key] || 'bg-muted'}`}>
                        {DATABASE_ICONS[db.key] || <Database className="w-5 h-5" />}
                      </div>
                      <span className="font-medium">{db.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-xs">
                      {db.category}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {db.totalEntries.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {db.subcategoryCount}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress 
                        value={(db.totalEntries / maxEntries) * 100} 
                        className="h-2 flex-1" 
                      />
                      <span className="text-xs text-muted-foreground w-10 text-right">
                        {Math.round((db.totalEntries / stats.totalEntries) * 100)}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleLoadSingle(db.key)}
                      disabled={disabled}
                    >
                      <Download className="w-4 h-4 mr-1" />
                      Laden
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Subkategorien Info für Top 3 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {stats.databases.slice(0, 3).map((db) => {
            const fullDb = FREQUENCY_DATABASES[db.key];
            const subcatKeys = Object.keys(fullDb.subcategories).slice(0, 4);
            return (
              <Card key={db.key} className={`border ${DATABASE_COLORS[db.key]?.split(' ')[2] || 'border-muted'}`}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <div className={`p-1 rounded ${DATABASE_COLORS[db.key] || 'bg-muted'}`}>
                      {DATABASE_ICONS[db.key]}
                    </div>
                    {db.name}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-1">
                    {subcatKeys.map((key) => (
                      <div key={key} className="flex justify-between text-xs">
                        <span className="text-muted-foreground truncate max-w-[150px]">
                          {fullDb.subcategories[key].name}
                        </span>
                        <span className="font-mono">
                          {fullDb.subcategories[key].entries.length}
                        </span>
                      </div>
                    ))}
                    {Object.keys(fullDb.subcategories).length > 4 && (
                      <p className="text-[10px] text-muted-foreground text-right">
                        +{Object.keys(fullDb.subcategories).length - 4} weitere
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default FrequencyDatabaseOverview;
