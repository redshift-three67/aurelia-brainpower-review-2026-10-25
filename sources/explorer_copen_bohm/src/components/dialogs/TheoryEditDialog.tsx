
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

interface TheoryEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editingData: any;
  onSave: (data: any) => void;
  onCancel: () => void;
  title?: string;
}

const TheoryEditDialog: React.FC<TheoryEditDialogProps> = ({
  open,
  onOpenChange,
  editingData,
  onSave,
  onCancel,
  title = "Theorie bearbeiten"
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
            Bearbeiten Sie die Details der Theorie. Klicken Sie auf Speichern, um die Änderungen zu übernehmen.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="title">Titel</Label>
            <Input
              id="title"
              value={formData.title || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Theorie-Titel eingeben..."
            />
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="description">Beschreibung</Label>
            <Textarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Beschreibung eingeben..."
              rows={4}
            />
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="content">Inhalt</Label>
            <Textarea
              id="content"
              value={formData.content || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
              placeholder="Theorieinhalt eingeben..."
              rows={6}
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

export default TheoryEditDialog;
