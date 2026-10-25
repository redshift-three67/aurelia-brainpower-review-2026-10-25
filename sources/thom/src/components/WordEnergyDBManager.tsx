/**
 * Word Energy DB Manager
 * Verwaltung von Wort-Energie-Sammlungen als Multifokusse für die Feldanalyse
 */
import { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Database as DatabaseIcon,
  Plus,
  Trash2,
  Edit3,
  Check,
  X,
  Sparkles,
  FileText,
  ChevronDown,
  ChevronUp,
  Zap,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { supabase } from '@/integrations/supabase/client';
import { cn } from '@/lib/utils';
import type { VectorAnalysis } from '@/services/feldengine';
import type { Database } from '@/integrations/supabase/types';

type WordEnergyCollectionRow = Database['public']['Tables']['word_energy_collections']['Row'];
type WordEnergyCollectionInsert = Database['public']['Tables']['word_energy_collections']['Insert'];
type WordEnergyCollectionUpdate = Database['public']['Tables']['word_energy_collections']['Update'];

interface WordEnergyCollection {
  id: string;
  name: string;
  words: string[];
  description: string | null;
  createdAt: Date;
}

interface ResonanceMatch {
  word: string;
  score: number;
  frequency?: number;
  category?: string;
}

interface WordEnergyDBManagerProps {
  vectorAnalysis: VectorAnalysis | null;
  onMultiFociSelected?: (foci: string[]) => void;
}

const WordEnergyDBManager = ({ vectorAnalysis, onMultiFociSelected }: WordEnergyDBManagerProps) => {
  const [collections, setCollections] = useState<WordEnergyCollection[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [newName, setNewName] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editWords, setEditWords] = useState('');
  const [selectedCollectionId, setSelectedCollectionId] = useState<string | null>(null);
  const [resonanceResults, setResonanceResults] = useState<ResonanceMatch[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Load collections
  const loadCollections = useCallback(async () => {
    try {
      const { data, error } = await supabase
        .from('word_energy_collections')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;

      setCollections((data || []).map((c: WordEnergyCollectionRow) => ({
        id: c.id,
        name: c.name,
        words: c.words || [],
        description: c.description,
        createdAt: new Date(c.created_at),
      })));
    } catch (error) {
      console.error('Error loading collections:', error);
    }
  }, []);

  useEffect(() => {
    loadCollections();
  }, [loadCollections]);

  // Create collection
  const createCollection = useCallback(async () => {
    if (!newName.trim()) return;
    setIsLoading(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) throw new Error('Nicht authentifiziert');

      const newCollection: WordEnergyCollectionInsert = {
        name: newName.trim(),
        words: [],
        user_id: session.user.id,
      };

      const { error } = await supabase
        .from('word_energy_collections')
        .insert(newCollection);

      if (error) throw error;
      setNewName('');
      await loadCollections();
      toast.success(`Sammlung "${newName.trim()}" erstellt`);
    } catch (error) {
      console.error('Error creating collection:', error);
      toast.error('Fehler beim Erstellen');
    } finally {
      setIsLoading(false);
    }
  }, [newName, loadCollections]);

  // Delete collection
  const deleteCollection = useCallback(async (id: string) => {
    try {
      const { error } = await supabase
        .from('word_energy_collections')
        .delete()
        .eq('id', id);
      if (error) throw error;
      await loadCollections();
      if (selectedCollectionId === id) {
        setSelectedCollectionId(null);
        setResonanceResults([]);
      }
      toast.success('Sammlung gelöscht');
    } catch (error) {
      console.error('Error deleting collection:', error);
      toast.error('Fehler beim Löschen');
    }
  }, [loadCollections, selectedCollectionId]);

  // Save edited words
  const saveWords = useCallback(async (id: string) => {
    const words = editWords.split('\n').map(w => w.trim()).filter(Boolean);
    try {
      const updates: WordEnergyCollectionUpdate = {
        words,
        updated_at: new Date().toISOString(),
      };

      const { error } = await supabase
        .from('word_energy_collections')
        .update(updates)
        .eq('id', id);
      if (error) throw error;
      setEditingId(null);
      await loadCollections();
      toast.success('Wörter gespeichert');
    } catch (error) {
      console.error('Error saving words:', error);
      toast.error('Fehler beim Speichern');
    }
  }, [editWords, loadCollections]);

  // Resonance pre-analysis against client vector
  const analyzeResonance = useCallback(async (collection: WordEnergyCollection) => {
    if (!vectorAnalysis) {
      toast.info('Resonanz-Analyse benötigt einen Klienten-Vektor. Sammlung wird ohne Analyse angezeigt.');
      // Still allow viewing the collection words without vector analysis
      setSelectedCollectionId(collection.id);
      setResonanceResults(collection.words.map(word => ({ word, score: 0.5 })));
      return;
    }

    setIsAnalyzing(true);
    setSelectedCollectionId(collection.id);

    try {
      // Query word_energies table for matching words
      const { data: wordData } = await supabase
        .from('word_energies')
        .select('*')
        .in('word', collection.words);

      const dims = vectorAnalysis.clientVector.dimensions;
      const results: ResonanceMatch[] = collection.words.map(word => {
        const dbEntry = wordData?.find(w => w.word.toLowerCase() === word.toLowerCase());

        if (dbEntry) {
          // Calculate resonance based on vector dimensions and word properties
          const energyDim = Math.abs(dims[3] || 0);
          const emotionalDim = Math.abs(dims[1] || 0);
          const stressDim = Math.abs(dims[4] || 0);

          let score = 0.5;
          if (dbEntry.category === 'positive') {
            score += (1 - energyDim) * 0.2 + (1 - emotionalDim) * 0.15;
          } else if (dbEntry.category === 'negative') {
            score += energyDim * 0.2 + stressDim * 0.15;
          }
          // Frequency harmonic boost
          const stability = vectorAnalysis.attractorState.stability;
          score += (1 - stability) * 0.15;

          return {
            word,
            score: Math.min(1, score),
            frequency: dbEntry.frequency,
            category: dbEntry.category,
          };
        }

        // Fallback: hash-based pseudo-resonance for words not in DB
        const hash = word.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
        const pseudoScore = 0.3 + (hash % 40) / 100 + Math.abs(dims[0] || 0) * 0.1;
        return { word, score: Math.min(1, pseudoScore) };
      });

      results.sort((a, b) => b.score - a.score);
      setResonanceResults(results);
    } catch (error) {
      console.error('Resonance analysis error:', error);
      toast.error('Fehler bei der Resonanzanalyse');
    } finally {
      setIsAnalyzing(false);
    }
  }, [vectorAnalysis]);

  // Apply top-5 as multi-foci
  const applyMultiFoci = useCallback(() => {
    const top5 = resonanceResults.slice(0, 5).map(r => r.word);
    if (top5.length === 0) {
      toast.warning('Keine Resonanzergebnisse vorhanden');
      return;
    }
    onMultiFociSelected?.(top5);
    toast.success(`${top5.length} Multifokusse übernommen`, {
      description: top5.join(', '),
    });
  }, [resonanceResults, onMultiFociSelected]);

  return (
    <div className="border border-border rounded-lg bg-card/50 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-muted/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <DatabaseIcon className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-foreground">Wort-Energie DBs</span>
          <Badge variant="secondary" className="text-[10px]">{collections.length}</Badge>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 space-y-2">
              {/* Create new */}
              <div className="flex gap-2">
                <Input
                  placeholder="Neue Sammlung..."
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="h-8 text-sm"
                  onKeyDown={(e) => e.key === 'Enter' && createCollection()}
                />
                <Button
                  size="sm"
                  variant="outline"
                  onClick={createCollection}
                  disabled={!newName.trim() || isLoading}
                  className="h-8 px-2"
                >
                  <Plus className="w-3 h-3" />
                </Button>
              </div>

              {/* Collection list */}
              <div className="space-y-1 max-h-[280px] overflow-y-auto">
                {collections.map((col) => (
                  <div
                    key={col.id}
                    className={cn(
                      "rounded-md border border-transparent p-2 transition-colors",
                      selectedCollectionId === col.id
                        ? "bg-primary/10 border-primary/30"
                        : "bg-muted/20 hover:bg-muted/40"
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        <FileText className="w-3 h-3 text-muted-foreground shrink-0" />
                        <span className="text-sm text-foreground truncate">{col.name}</span>
                        <Badge variant="outline" className="text-[10px] shrink-0">
                          {col.words.length}
                        </Badge>
                      </div>
                      <div className="flex gap-1 shrink-0">
                        <button
                          onClick={() => {
                            if (editingId === col.id) {
                              setEditingId(null);
                            } else {
                              setEditingId(col.id);
                              setEditWords(col.words.join('\n'));
                            }
                          }}
                          className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
                        >
                          <Edit3 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => analyzeResonance(col)}
                          disabled={isAnalyzing}
                          className="p-1 hover:bg-primary/20 rounded text-muted-foreground hover:text-primary"
                          title="Resonanzanalyse"
                        >
                          <Sparkles className={cn("w-3 h-3", isAnalyzing && "animate-spin")} />
                        </button>
                        <button
                          onClick={() => deleteCollection(col.id)}
                          className="p-1 hover:bg-destructive/20 rounded text-muted-foreground hover:text-destructive"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>

                    {/* Edit mode */}
                    <AnimatePresence>
                      {editingId === col.id && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="mt-2"
                        >
                          <Textarea
                            value={editWords}
                            onChange={(e) => setEditWords(e.target.value)}
                            placeholder="Ein Wort pro Zeile..."
                            className="min-h-[80px] text-xs font-mono"
                          />
                          <div className="flex gap-1 mt-1">
                            <Button size="sm" variant="default" className="h-6 text-xs px-2" onClick={() => saveWords(col.id)}>
                              <Check className="w-3 h-3 mr-1" /> Speichern
                            </Button>
                            <Button size="sm" variant="ghost" className="h-6 text-xs px-2" onClick={() => setEditingId(null)}>
                              <X className="w-3 h-3" />
                            </Button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))}

                {collections.length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-3">
                    Noch keine Sammlungen erstellt
                  </p>
                )}
              </div>

              {/* Resonance Results */}
              <AnimatePresence>
                {resonanceResults.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 5 }}
                    className="border-t border-border pt-2 space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-muted-foreground">Resonanz-Ranking</span>
                      <Button
                        size="sm"
                        variant="default"
                        className="h-6 text-xs px-2 gap-1"
                        onClick={applyMultiFoci}
                      >
                        <Zap className="w-3 h-3" />
                        Top-5 übernehmen
                      </Button>
                    </div>
                    {resonanceResults.slice(0, 7).map((r, i) => (
                      <div
                        key={r.word}
                        className={cn(
                          "flex items-center justify-between px-2 py-1 rounded text-xs",
                          i < 5 ? "bg-primary/5" : "bg-muted/20"
                        )}
                      >
                        <div className="flex items-center gap-2">
                          {i < 5 && <span className="text-[10px] font-bold text-primary">#{i + 1}</span>}
                          <span className={cn("text-foreground", i < 5 && "font-medium")}>{r.word}</span>
                          {r.frequency && (
                            <span className="text-[10px] text-muted-foreground">{r.frequency.toFixed(0)} Hz</span>
                          )}
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-12 h-1.5 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary rounded-full"
                              style={{ width: `${r.score * 100}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-muted-foreground w-7 text-right">
                            {(r.score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default WordEnergyDBManager;
