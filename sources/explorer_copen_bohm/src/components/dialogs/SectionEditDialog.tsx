
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

interface SectionEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editingData: any;
  onSave: (data: any) => void;
  onCancel: () => void;
  title?: string;
}

const SectionEditDialog: React.FC<SectionEditDialogProps> = ({
  open,
  onOpenChange,
  editingData,
  onSave,
  onCancel,
  title = "Abschnitt bearbeiten"
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
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>
            Bearbeiten Sie die Details des Abschnitts.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="sectionTitle">Abschnittstitel</Label>
            <Input
              id="sectionTitle"
              value={formData.title || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Abschnittstitel eingeben..."
            />
          </div>
          
          <div className="grid gap-2">
            <Label htmlFor="sectionContent">Inhalt</Label>
            <Textarea
              id="sectionContent"
              value={formData.content || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
              placeholder="Abschnittsinhalt eingeben..."
              rows={8}
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

export default SectionEditDialog;
