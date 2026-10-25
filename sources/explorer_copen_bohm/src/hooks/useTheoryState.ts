
import { useState, useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';

export interface EditingState {
  editingId: string | null;
  editingData: any;
  isEditing: boolean;
}

export interface TheoryStateManager {
  // Edit States
  editingStates: {
    theory: EditingState;
    section: EditingState;
    formula: EditingState;
  };
  
  // Actions
  startEdit: (type: 'theory' | 'section' | 'formula', id: string, data: any) => void;
  cancelEdit: (type: 'theory' | 'section' | 'formula') => void;
  saveEdit: (type: 'theory' | 'section' | 'formula', data: any) => Promise<void>;
  
  // Dialog States
  dialogStates: {
    theory: boolean;
    section: boolean;
    formula: boolean;
  };
  
  setDialogState: (type: 'theory' | 'section' | 'formula', state: boolean) => void;
}

export const useTheoryState = (): TheoryStateManager => {
  const { toast } = useToast();
  
  // Initialize edit states
  const [editingStates, setEditingStates] = useState({
    theory: { editingId: null, editingData: null, isEditing: false },
    section: { editingId: null, editingData: null, isEditing: false },
    formula: { editingId: null, editingData: null, isEditing: false },
  });
  
  // Initialize dialog states
  const [dialogStates, setDialogStates] = useState({
    theory: false,
    section: false,
    formula: false,
  });
  
  const startEdit = useCallback((type: 'theory' | 'section' | 'formula', id: string, data: any) => {
    setEditingStates(prev => ({
      ...prev,
      [type]: {
        editingId: id,
        editingData: { ...data },
        isEditing: true,
      }
    }));
    setDialogStates(prev => ({ ...prev, [type]: true }));
  }, []);
  
  const cancelEdit = useCallback((type: 'theory' | 'section' | 'formula') => {
    setEditingStates(prev => ({
      ...prev,
      [type]: {
        editingId: null,
        editingData: null,
        isEditing: false,
      }
    }));
    setDialogStates(prev => ({ ...prev, [type]: false }));
    
    toast({
      title: "Bearbeitung abgebrochen",
      description: "Änderungen wurden nicht gespeichert",
    });
  }, [toast]);
  
  const saveEdit = useCallback(async (type: 'theory' | 'section' | 'formula', data: any) => {
    try {
      // Simulate save operation
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setEditingStates(prev => ({
        ...prev,
        [type]: {
          editingId: null,
          editingData: null,
          isEditing: false,
        }
      }));
      setDialogStates(prev => ({ ...prev, [type]: false }));
      
      toast({
        title: "Erfolgreich gespeichert",
        description: `${type} wurde erfolgreich aktualisiert`,
      });
    } catch (error) {
      toast({
        title: "Fehler beim Speichern",
        description: "Bitte versuchen Sie es erneut",
        variant: "destructive",
      });
    }
  }, [toast]);
  
  const setDialogState = useCallback((type: 'theory' | 'section' | 'formula', state: boolean) => {
    setDialogStates(prev => ({ ...prev, [type]: state }));
    
    // If closing dialog without saving, also clear edit state
    if (!state && editingStates[type].isEditing) {
      setEditingStates(prev => ({
        ...prev,
        [type]: {
          editingId: null,
          editingData: null,
          isEditing: false,
        }
      }));
    }
  }, [editingStates]);
  
  return {
    editingStates,
    startEdit,
    cancelEdit,
    saveEdit,
    dialogStates,
    setDialogState,
  };
};
