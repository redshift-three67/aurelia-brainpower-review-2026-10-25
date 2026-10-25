/**
 * 3D-Modell-Auswahl Komponente
 * Zeigt verfügbare Anatomie-Modelle gruppiert nach Kategorie
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Box, Check, Lock, Layers, GitBranch, Bone, Heart, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
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
import { supabase } from '@/integrations/supabase/client';
import { toast } from 'sonner';
import {
  type AnatomyModel,
  getCategoryLabel,
  getSourceLabel,
} from '@/hooks/useAnatomyModels';

const getErrorMessage = (error: unknown, fallback: string): string =>
  error instanceof Error && error.message ? error.message : fallback;

interface ModelSelectorProps {
  models: AnatomyModel[];
  selectedModel: AnatomyModel | null;
  onSelect: (model: AnatomyModel) => void;
  onDelete?: () => void;
  categories: string[];
  isLoading?: boolean;
}

const CATEGORY_ICONS: Record<string, typeof Heart> = {
  full_body: Layers,
  organ: Heart,
  skeleton: Bone,
  meridian_template: GitBranch,
};

export function ModelSelector({
  models,
  selectedModel,
  onSelect,
  onDelete,
  categories,
  isLoading,
}: ModelSelectorProps) {
  const [activeTab, setActiveTab] = useState(categories[0] || 'full_body');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (model: AnatomyModel) => {
    setDeletingId(model.id);
    try {
      if (model.storageType === 'cloud' && model.filePath) {
        const storagePath = model.filePath.replace('3d-models/', '');
        await supabase.storage.from('3d-models').remove([storagePath]);
      }
      const { error } = await supabase.from('anatomy_models').delete().eq('id', model.id);
      if (error) throw error;
      toast.success(`"${model.name}" gelöscht`);
      onDelete?.();
    } catch (err: unknown) {
      console.error('Lösch-Fehler:', err);
      toast.error(`Löschen fehlgeschlagen: ${getErrorMessage(err, 'Unbekannter Fehler')}`);
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin w-5 h-5 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-2">
        <Box className="w-4 h-4 text-primary" />
        <h3 className="text-sm font-semibold text-foreground">3D-Modell Bibliothek</h3>
      </div>

      {/* Category Dropdown */}
      <Select value={activeTab} onValueChange={setActiveTab}>
        <SelectTrigger className="h-9 text-xs">
          <SelectValue placeholder="Kategorie wählen" />
        </SelectTrigger>
        <SelectContent>
          {categories.map(cat => {
            const Icon = CATEGORY_ICONS[cat] || Box;
            const count = models.filter(m => m.category === cat).length;
            return (
              <SelectItem key={cat} value={cat} className="text-xs">
                <span className="flex items-center gap-2">
                  <Icon className="w-3.5 h-3.5" />
                  {getCategoryLabel(cat)}
                  <span className="text-muted-foreground">({count})</span>
                </span>
              </SelectItem>
            );
          })}
        </SelectContent>
      </Select>

      {/* Models for selected category */}
      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {models
            .filter(m => m.category === activeTab)
            .map(model => (
              <ModelCard
                key={model.id}
                model={model}
                isSelected={selectedModel?.id === model.id}
                isDeleting={deletingId === model.id}
                onSelect={() => onSelect(model)}
                onDelete={() => handleDelete(model)}
              />
            ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

function ModelCard({
  model,
  isSelected,
  isDeleting,
  onSelect,
  onDelete,
}: {
  model: AnatomyModel;
  isSelected: boolean;
  isDeleting: boolean;
  onSelect: () => void;
  onDelete: () => void;
}) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
    >
      <div
        className={`w-full text-left p-2.5 rounded-lg border transition-all ${
          isSelected
            ? 'border-primary bg-primary/10 shadow-sm'
            : model.isAvailable
            ? 'border-border bg-card hover:border-primary/40 hover:bg-muted/50'
            : 'border-border/50 bg-muted/30 opacity-60'
        }`}
      >
        <div className="flex items-start justify-between gap-2">
          <button
            onClick={onSelect}
            disabled={!model.isAvailable}
            className="flex-1 min-w-0 text-left"
          >
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-semibold text-foreground truncate">
                {model.name}
              </span>
              {isSelected && <Check className="w-3 h-3 text-primary shrink-0" />}
              {!model.isAvailable && <Lock className="w-3 h-3 text-muted-foreground shrink-0" />}
            </div>
            
            {model.description && (
              <p className="text-[10px] text-muted-foreground mt-0.5 line-clamp-2">
                {model.description}
              </p>
            )}

            <div className="flex flex-wrap gap-1 mt-1.5">
              <Badge variant="outline" className="text-[9px] px-1 py-0 h-4">
                {getSourceLabel(model.source)}
              </Badge>
              {model.gender !== 'neutral' && (
                <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4">
                  {model.gender === 'male' ? '♂' : '♀'}
                </Badge>
              )}
              {model.supportsMeridianMapping && (
                <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4">
                  Meridiane
                </Badge>
              )}
              {model.supportsOrganLayers && (
                <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4">
                  Organe
                </Badge>
              )}
              {model.dracoCompressed && (
                <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4">
                  Draco
                </Badge>
              )}
              {model.fileSize && (
                <Badge variant="outline" className="text-[9px] px-1 py-0 h-4">
                  {(model.fileSize / 1024 / 1024).toFixed(1)} MB
                </Badge>
              )}
            </div>
          </button>

          {!model.isDefault && (
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 shrink-0 text-muted-foreground hover:text-destructive"
                  disabled={isDeleting}
                >
                  {isDeleting ? (
                    <div className="animate-spin w-3 h-3 border-2 border-destructive border-t-transparent rounded-full" />
                  ) : (
                    <Trash2 className="w-3 h-3" />
                  )}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Modell löschen?</AlertDialogTitle>
                  <AlertDialogDescription>
                    „{model.name}" wird unwiderruflich aus der Bibliothek und dem Speicher entfernt.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                  <AlertDialogAction onClick={onDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                    Löschen
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          )}
        </div>

        {model.license && (
          <p className="text-[9px] text-muted-foreground/60 mt-1">
            Lizenz: {model.license}
          </p>
        )}
      </div>
    </motion.div>
  );
}

export default ModelSelector;
