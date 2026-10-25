import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Users, Plus, Trash2, Edit2, Check, X } from 'lucide-react';
import { Patient } from '@/types/patient';
import { useToast } from '@/hooks/use-toast';

interface PatientManagerProps {
  onSelectPatient: (patient: Patient | null) => void;
  selectedPatient: Patient | null;
}

const PatientManager: React.FC<PatientManagerProps> = ({ onSelectPatient, selectedPatient }) => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    birthDate: '',
    birthPlace: ''
  });
  const { toast } = useToast();

  // Lade Patienten aus localStorage
  useEffect(() => {
    const stored = localStorage.getItem('copen-patients');
    if (stored) {
      setPatients(JSON.parse(stored));
    }
  }, []);

  // Speichere Patienten in localStorage
  const savePatients = (updatedPatients: Patient[]) => {
    setPatients(updatedPatients);
    localStorage.setItem('copen-patients', JSON.stringify(updatedPatients));
  };

  const handleAdd = () => {
    if (!formData.firstName || !formData.lastName) {
      toast({
        title: "Fehler",
        description: "Vorname und Nachname sind erforderlich",
        variant: "destructive"
      });
      return;
    }

    const newPatient: Patient = {
      id: Date.now().toString(),
      ...formData,
      createdAt: new Date().toISOString()
    };

    savePatients([...patients, newPatient]);
    setFormData({ firstName: '', lastName: '', birthDate: '', birthPlace: '' });
    setIsAdding(false);
    toast({
      title: "Erfolg",
      description: "Patient hinzugefügt"
    });
  };

  const handleEdit = (patient: Patient) => {
    setEditingId(patient.id);
    setFormData({
      firstName: patient.firstName,
      lastName: patient.lastName,
      birthDate: patient.birthDate,
      birthPlace: patient.birthPlace
    });
  };

  const handleUpdate = () => {
    if (!editingId) return;

    const updatedPatients = patients.map(p => 
      p.id === editingId 
        ? { ...p, ...formData }
        : p
    );
    savePatients(updatedPatients);
    setEditingId(null);
    setFormData({ firstName: '', lastName: '', birthDate: '', birthPlace: '' });
    
    // Update selectedPatient wenn er editiert wurde
    if (selectedPatient?.id === editingId) {
      const updated = updatedPatients.find(p => p.id === editingId);
      if (updated) onSelectPatient(updated);
    }

    toast({
      title: "Erfolg",
      description: "Patient aktualisiert"
    });
  };

  const handleDelete = (id: string) => {
    if (confirm('Wirklich löschen?')) {
      const updatedPatients = patients.filter(p => p.id !== id);
      savePatients(updatedPatients);
      if (selectedPatient?.id === id) {
        onSelectPatient(null);
      }
      toast({
        title: "Erfolg",
        description: "Patient gelöscht"
      });
    }
  };

  const handleCancel = () => {
    setIsAdding(false);
    setEditingId(null);
    setFormData({ firstName: '', lastName: '', birthDate: '', birthPlace: '' });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Patientenverwaltung
          </span>
          {!isAdding && !editingId && (
            <Button onClick={() => setIsAdding(true)} size="sm">
              <Plus className="h-4 w-4 mr-1" />
              Neu
            </Button>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Formular für Neu/Bearbeiten */}
        {(isAdding || editingId) && (
          <div className="border-2 border-blue-300 rounded-lg p-4 bg-blue-50 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <Label>Vorname *</Label>
                <Input
                  value={formData.firstName}
                  onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                  placeholder="Vorname"
                />
              </div>
              <div>
                <Label>Nachname *</Label>
                <Input
                  value={formData.lastName}
                  onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                  placeholder="Nachname"
                />
              </div>
              <div>
                <Label>Geburtsdatum</Label>
                <Input
                  type="date"
                  value={formData.birthDate}
                  onChange={(e) => setFormData({...formData, birthDate: e.target.value})}
                />
              </div>
              <div>
                <Label>Geburtsort</Label>
                <Input
                  value={formData.birthPlace}
                  onChange={(e) => setFormData({...formData, birthPlace: e.target.value})}
                  placeholder="Geburtsort"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={editingId ? handleUpdate : handleAdd} size="sm">
                <Check className="h-4 w-4 mr-1" />
                {editingId ? 'Aktualisieren' : 'Hinzufügen'}
              </Button>
              <Button onClick={handleCancel} variant="outline" size="sm">
                <X className="h-4 w-4 mr-1" />
                Abbrechen
              </Button>
            </div>
          </div>
        )}

        {/* Patientenliste */}
        {patients.length === 0 ? (
          <p className="text-center text-muted-foreground py-4">
            Keine Patienten vorhanden
          </p>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {patients.map(patient => (
              <div
                key={patient.id}
                className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
                  selectedPatient?.id === patient.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
                onClick={() => onSelectPatient(patient)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-semibold">
                      {patient.firstName} {patient.lastName}
                    </div>
                    {patient.birthDate && (
                      <div className="text-sm text-muted-foreground">
                        Geboren: {new Date(patient.birthDate).toLocaleDateString('de-DE')}
                      </div>
                    )}
                    {patient.birthPlace && (
                      <div className="text-sm text-muted-foreground">
                        Ort: {patient.birthPlace}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-1">
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit(patient);
                      }}
                      variant="ghost"
                      size="sm"
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(patient.id);
                      }}
                      variant="ghost"
                      size="sm"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PatientManager;
