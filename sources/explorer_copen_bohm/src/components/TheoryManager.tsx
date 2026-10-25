
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Edit, Plus, Save, X } from 'lucide-react';
import { useTheoryState } from '@/hooks/useTheoryState';
import TheoryEditDialog from '@/components/dialogs/TheoryEditDialog';
import SectionEditDialog from '@/components/dialogs/SectionEditDialog';
import FormulaEditDialog from '@/components/dialogs/FormulaEditDialog';

const TheoryManager: React.FC = () => {
  const {
    editingStates,
    startEdit,
    cancelEdit,
    saveEdit,
    dialogStates,
    setDialogState,
  } = useTheoryState();
  
  // Sample data - in real application this would come from props or API
  const sampleTheories = [
    { id: '1', title: 'Quantenfeldtheorie', description: 'Grundlagen der Quantenfeldtheorie', content: 'Detaillierter Inhalt...' },
    { id: '2', title: 'Resonanzphysik', description: 'Prinzipien der Resonanz', content: 'Resonanz Erklärung...' }
  ];
  
  const sampleSections = [
    { id: '1', title: 'Einführung', content: 'Einführungstext zur Theorie' },
    { id: '2', title: 'Grundprinzipien', content: 'Grundlegende Prinzipien und Konzepte' }
  ];
  
  const sampleFormulas = [
    { id: '1', name: 'Frequenz-Wellenlänge', formula: 'f = c / λ', explanation: 'Beziehung zwischen Frequenz und Wellenlänge', variables: 'f = Frequenz, c = Lichtgeschwindigkeit, λ = Wellenlänge' }
  ];
  
  return (
    <div className="space-y-6">
      {/* Theories Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Theorien
            <Button
              onClick={() => startEdit('theory', 'new', { title: '', description: '', content: '' })}
              size="sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              Neue Theorie
            </Button>
          </CardTitle>
          <CardDescription>
            Verwalten Sie wissenschaftliche Theorien und deren Inhalte
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {sampleTheories.map((theory) => (
              <div key={theory.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-semibold">{theory.title}</h4>
                  <p className="text-sm text-muted-foreground">{theory.description}</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => startEdit('theory', theory.id, theory)}
                >
                  <Edit className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Sections */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Abschnitte
            <Button
              onClick={() => startEdit('section', 'new', { title: '', content: '' })}
              size="sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              Neuer Abschnitt
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {sampleSections.map((section) => (
              <div key={section.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-semibold">{section.title}</h4>
                  <p className="text-sm text-muted-foreground line-clamp-2">{section.content}</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => startEdit('section', section.id, section)}
                >
                  <Edit className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Formulas */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Formeln
            <Button
              onClick={() => startEdit('formula', 'new', { name: '', formula: '', explanation: '', variables: '' })}
              size="sm"
            >
              <Plus className="h-4 w-4 mr-2" />
              Neue Formel
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {sampleFormulas.map((formula) => (
              <div key={formula.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-semibold">{formula.name}</h4>
                  <p className="text-sm font-mono text-muted-foreground">{formula.formula}</p>
                  <p className="text-sm text-muted-foreground">{formula.explanation}</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => startEdit('formula', formula.id, formula)}
                >
                  <Edit className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
      
      {/* Edit Dialogs */}
      <TheoryEditDialog
        open={dialogStates.theory}
        onOpenChange={(open) => setDialogState('theory', open)}
        editingData={editingStates.theory.editingData}
        onSave={(data) => saveEdit('theory', data)}
        onCancel={() => cancelEdit('theory')}
      />
      
      <SectionEditDialog
        open={dialogStates.section}
        onOpenChange={(open) => setDialogState('section', open)}
        editingData={editingStates.section.editingData}
        onSave={(data) => saveEdit('section', data)}
        onCancel={() => cancelEdit('section')}
      />
      
      <FormulaEditDialog
        open={dialogStates.formula}
        onOpenChange={(open) => setDialogState('formula', open)}
        editingData={editingStates.formula.editingData}
        onSave={(data) => saveEdit('formula', data)}
        onCancel={() => cancelEdit('formula')}
      />
    </div>
  );
};

export default TheoryManager;
