
import React, { useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Upload, Calculator } from 'lucide-react';

interface BatchImportFormProps {
  csvInput: string;
  onCsvInputChange: (csv: string) => void;
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onBatchCalculate: () => void;
}

const BatchImportForm: React.FC<BatchImportFormProps> = ({
  csvInput,
  onCsvInputChange,
  onFileUpload,
  onBatchCalculate
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          CSV/Excel Import
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-4">
          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            className="flex-1"
          >
            <Upload className="h-4 w-4 mr-2" />
            CSV-Datei auswählen
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.txt"
            onChange={onFileUpload}
            className="hidden"
          />
        </div>
        
        <div>
          <Label htmlFor="csvInput">CSV-Daten (Format: Wort,Potenz,Typ,Alphabet)</Label>
          <Textarea
            id="csvInput"
            value={csvInput}
            onChange={(e) => onCsvInputChange(e.target.value)}
            placeholder="Arnica,6,D,latin
Belladonna,12,D,latin
Nux vomica,30,C,latin"
            rows={6}
          />
        </div>
        
        <Button onClick={onBatchCalculate} className="w-full">
          <Calculator className="h-4 w-4 mr-2" />
          Batch-Berechnung starten
        </Button>
      </CardContent>
    </Card>
  );
};

export default BatchImportForm;
