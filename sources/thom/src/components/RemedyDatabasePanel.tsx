/**
 * RemedyDatabasePanel – Verwaltung der Mittel-Datenbank
 * Phase 4b: Homöopathie, Bachblüten, Nosoden mit Frequenzzuordnung
 */
import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Search, Plus, Pill, Filter, Waves, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { useRemedyDatabase, type Remedy, type RemedyCategory } from '@/hooks/useRemedyDatabase';

const CATEGORIES: { value: RemedyCategory; label: string }[] = [
  { value: 'homeopathy', label: 'Homöopathie' },
  { value: 'bach_flower', label: 'Bachblüten' },
  { value: 'nosode', label: 'Nosoden' },
  { value: 'tissue_salt', label: 'Schüßler-Salze' },
  { value: 'herbal', label: 'Phytotherapie' },
  { value: 'other', label: 'Sonstiges' },
];

const ELEMENTS = ['Holz', 'Feuer', 'Erde', 'Metall', 'Wasser'];

interface RemedyDatabasePanelProps {
  onSelectFrequency?: (frequency: number) => void;
}

const RemedyDatabasePanel = ({ onSelectFrequency }: RemedyDatabasePanelProps) => {
  const { remedies, isLoading, loadRemedies, addRemedy, categoryLabels } = useRemedyDatabase();
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [showAddDialog, setShowAddDialog] = useState(false);

  // Form state for adding
  const [newRemedy, setNewRemedy] = useState({
    name: '', nameLatin: '', category: 'homeopathy' as RemedyCategory,
    potency: '', frequency: '', element: '',
    meridianAssociations: '', organAssociations: '',
    emotionalPattern: '', description: '', contraindications: '', source: '',
  });

  useEffect(() => {
    loadRemedies(categoryFilter === 'all' ? undefined : categoryFilter, search || undefined);
  }, [categoryFilter, search, loadRemedies]);

  const handleAdd = useCallback(async () => {
    if (!newRemedy.name.trim()) return;
    await addRemedy({
      name: newRemedy.name,
      nameLatin: newRemedy.nameLatin || null,
      category: newRemedy.category,
      potency: newRemedy.potency || null,
      frequency: newRemedy.frequency ? parseFloat(newRemedy.frequency) : null,
      meridianAssociations: newRemedy.meridianAssociations ? newRemedy.meridianAssociations.split(',').map(s => s.trim()) : [],
      organAssociations: newRemedy.organAssociations ? newRemedy.organAssociations.split(',').map(s => s.trim()) : [],
      element: newRemedy.element || null,
      emotionalPattern: newRemedy.emotionalPattern || null,
      description: newRemedy.description || null,
      contraindications: newRemedy.contraindications || null,
      source: newRemedy.source || null,
    });
    setShowAddDialog(false);
    setNewRemedy({
      name: '', nameLatin: '', category: 'homeopathy', potency: '', frequency: '',
      element: '', meridianAssociations: '', organAssociations: '',
      emotionalPattern: '', description: '', contraindications: '', source: '',
    });
  }, [newRemedy, addRemedy]);

  return (
    <section className="py-8 px-4">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-card rounded-xl border border-border p-6"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Pill className="w-5 h-5 text-primary" />
              <h2 className="font-display text-xl text-foreground">Mittel-Datenbank</h2>
              <Badge variant="outline" className="text-xs">{remedies.length} Einträge</Badge>
            </div>
            <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
              <DialogTrigger asChild>
                <Button size="sm" className="gap-2">
                  <Plus className="w-4 h-4" />
                  Mittel hinzufügen
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Neues Mittel hinzufügen</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label>Name *</Label>
                      <Input value={newRemedy.name} onChange={e => setNewRemedy(p => ({ ...p, name: e.target.value }))} placeholder="z.B. Arnica" />
                    </div>
                    <div>
                      <Label>Lat. Name</Label>
                      <Input value={newRemedy.nameLatin} onChange={e => setNewRemedy(p => ({ ...p, nameLatin: e.target.value }))} placeholder="z.B. Arnica montana" />
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <div>
                      <Label>Kategorie</Label>
                      <Select value={newRemedy.category} onValueChange={v => setNewRemedy(p => ({ ...p, category: v as RemedyCategory }))}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          {CATEGORIES.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Potenz</Label>
                      <Input value={newRemedy.potency} onChange={e => setNewRemedy(p => ({ ...p, potency: e.target.value }))} placeholder="D6, C30..." />
                    </div>
                    <div>
                      <Label>Frequenz (Hz)</Label>
                      <Input type="number" value={newRemedy.frequency} onChange={e => setNewRemedy(p => ({ ...p, frequency: e.target.value }))} placeholder="432" />
                    </div>
                  </div>
                  <div>
                    <Label>Element (Wu Xing)</Label>
                    <Select value={newRemedy.element} onValueChange={v => setNewRemedy(p => ({ ...p, element: v }))}>
                      <SelectTrigger><SelectValue placeholder="Wählen..." /></SelectTrigger>
                      <SelectContent>
                        {ELEMENTS.map(e => <SelectItem key={e} value={e}>{e}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Meridiane (kommagetrennt)</Label>
                    <Input value={newRemedy.meridianAssociations} onChange={e => setNewRemedy(p => ({ ...p, meridianAssociations: e.target.value }))} placeholder="Leber, Gallenblase..." />
                  </div>
                  <div>
                    <Label>Organe (kommagetrennt)</Label>
                    <Input value={newRemedy.organAssociations} onChange={e => setNewRemedy(p => ({ ...p, organAssociations: e.target.value }))} placeholder="Leber, Milz..." />
                  </div>
                  <div>
                    <Label>Emotionales Muster</Label>
                    <Input value={newRemedy.emotionalPattern} onChange={e => setNewRemedy(p => ({ ...p, emotionalPattern: e.target.value }))} placeholder="Angst, Trauma..." />
                  </div>
                  <div>
                    <Label>Beschreibung</Label>
                    <Textarea value={newRemedy.description} onChange={e => setNewRemedy(p => ({ ...p, description: e.target.value }))} rows={3} />
                  </div>
                  <div>
                    <Label>Kontraindikationen</Label>
                    <Input value={newRemedy.contraindications} onChange={e => setNewRemedy(p => ({ ...p, contraindications: e.target.value }))} />
                  </div>
                  <Button onClick={handleAdd} className="w-full">Speichern</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {/* Filters */}
          <div className="flex gap-3 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Mittel suchen..."
                className="pl-10"
              />
            </div>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle Kategorien</SelectItem>
                {CATEGORIES.map(c => <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Remedy List */}
          {isLoading ? (
            <div className="text-center text-muted-foreground py-8">Laden...</div>
          ) : remedies.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              Keine Mittel gefunden. Fügen Sie Ihr erstes Mittel hinzu.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[500px] overflow-y-auto">
              {remedies.map(remedy => (
                <div key={remedy.id} className="bg-muted/20 rounded-lg border border-border p-3 hover:border-primary/30 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium text-foreground text-sm">{remedy.name}</h4>
                      {remedy.nameLatin && (
                        <p className="text-xs text-muted-foreground italic">{remedy.nameLatin}</p>
                      )}
                    </div>
                    <Badge variant="outline" className="text-[10px]">
                      {categoryLabels[remedy.category] || remedy.category}
                    </Badge>
                  </div>
                  
                  <div className="flex flex-wrap gap-1 mb-2">
                    {remedy.potency && <Badge variant="secondary" className="text-[10px]">{remedy.potency}</Badge>}
                    {remedy.element && <Badge variant="secondary" className="text-[10px]">{remedy.element}</Badge>}
                  </div>

                  {remedy.frequency && (
                    <button
                      onClick={() => onSelectFrequency?.(remedy.frequency!)}
                      className="flex items-center gap-1 text-xs text-primary hover:underline"
                    >
                      <Waves className="w-3 h-3" />
                      {remedy.frequency} Hz
                    </button>
                  )}

                  {remedy.description && (
                    <p className="text-xs text-muted-foreground mt-2 line-clamp-2">{remedy.description}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </section>
  );
};

export default RemedyDatabasePanel;
