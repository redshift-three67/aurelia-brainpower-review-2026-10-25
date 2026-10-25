
import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';

interface FormulaEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editingData: any;
  onSave: (data: any) => void;
  onCancel: () => void;
  title?: string;
}

const FormulaEditDialog: React.FC<FormulaEditDialogProps> = ({
  open,
  onOpenChange,
  editingData,
  onSave,
  onCancel,
  title = "Formel bearbeiten"
}) => {
  const [formData, setFormData] = React.useState(editingData || {});
  
  React.useEffect(() => {
    if (editingData) {
      setFormData({ ...editingData });
    }
  }, [editingData]);
  
  const handleSave = () => {
    onSave(formData);
  };
  
  const handleCancel = () => {
    setFormData(editingData || {});
    onCancel();
  };
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>
            Bearbeiten Sie die Formel und deren Parameter.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="formulaName">Formelname</Label>
            <Input
              id="formulaName"
              value={formData.name || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Formelname eingeben..."
            />
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="formula">Formel</Label>
            <Input
              id="formula"
              value={formData.formula || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, formula: e.target.value }))}
              placeholder="z.B. f = c / λ"
              className="font-mono"
            />
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="explanation">Erklärung</Label>
            <Textarea
              id="explanation"
              value={formData.explanation || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, explanation: e.target.value }))}
              placeholder="Formel-Erklärung eingeben..."
              rows={4}
            />
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="variables">Variablen</Label>
            <Textarea
              id="variables"
              value={formData.variables || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, variables: e.target.value }))}
              placeholder="Variable Erklärungen (z.B. f = Frequenz, c = Lichtgeschwindigkeit)"
              rows={3}
            />
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={handleCancel}>
            Abbrechen
          </Button>
          <Button onClick={handleSave}>
            Speichern
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default FormulaEditDialog;
