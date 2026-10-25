
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, Trash2 } from 'lucide-react';
import { alphabetSystems } from '@/utils/alphabetSystems';
import { type CopenRateResult } from '@/utils/copenRateGenerator';

interface ResultsTableProps {
  results: CopenRateResult[];
  onExport: () => void;
  onClear: () => void;
}

const ResultsTable: React.FC<ResultsTableProps> = ({
  results,
  onExport,
  onClear
}) => {
  if (results.length === 0) return null;

  return (
    <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-white">
          Berechnete Copen-Raten ({results.length})
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onExport}
              className="bg-white/10 border-white/20 text-white hover:bg-white/20"
            >
              <Download className="h-4 w-4 mr-2" />
              CSV Export
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onClear}
              className="bg-white/10 border-white/20 text-white hover:bg-white/20"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Löschen
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/20">
                <th className="text-left p-2 text-white">Wortenergie</th>
                <th className="text-left p-2 text-white">Potenz</th>
                <th className="text-left p-2 text-white">Typ</th>
                <th className="text-left p-2 text-white">Alphabet</th>
                <th className="text-left p-2 text-white">Copen-Rate</th>
                <th className="text-left p-2 text-white">Details</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr key={index} className="border-b border-white/10 hover:bg-white/5">
                  <td className="p-2 font-medium text-white">{result.word}</td>
                  <td className="p-2 text-blue-200">{result.potency}</td>
                  <td className="p-2 text-blue-200">{result.potencyType}</td>
                  <td className="p-2 text-xs text-blue-200">
                    {alphabetSystems[result.alphabetType].name}
                  </td>
                  <td className="p-2 font-mono text-blue-300 font-semibold">{result.rate.toLocaleString()}</td>
                  <td className="p-2 text-xs text-blue-300">
                    Σ:{result.calculation.letterSum} → 
                    Base:{result.calculation.baseRate.toLocaleString()} → 
                    Fib:{result.calculation.fibonacciRate.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default ResultsTable;
