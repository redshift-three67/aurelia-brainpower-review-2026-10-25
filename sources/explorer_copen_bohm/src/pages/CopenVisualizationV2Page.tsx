import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import CopenAlgorithmVisualizationV2 from "@/components/CopenAlgorithmVisualizationV2";
import { WorkerStatusMonitor } from "@/components/WorkerStatusMonitor";
import AnalysisArchiveCloud from "@/components/AnalysisArchiveCloud";
import SessionRecoveryDashboard from "@/components/SessionRecoveryDashboard";

const CopenVisualizationV2Page = () => {
  const navigate = useNavigate();
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <Button 
          variant="outline" 
          onClick={() => navigate("/")}
          className="mb-6 bg-white/10 border-white/20 text-white hover:bg-white/20"
        >
          ← Zurück zur Übersicht
        </Button>
        
        <CopenAlgorithmVisualizationV2 onPatientChange={setSelectedPatientId} />
        
        <div className="mt-6 space-y-4">
          <AnalysisArchiveCloud />
          <WorkerStatusMonitor />
          
          {/* Modul-spezifisches Session Dashboard - gefiltert nach aktivem Klienten */}
          <SessionRecoveryDashboard 
            sourceModuleFilter={['copen_v2', 'word_energy', 'session_transfer']}
            showControls={true}
            title={selectedPatientId ? "Sessions für ausgewählten Klienten" : "Copen V2 & Wortenergie Sessions"}
            compact={true}
            patientFilter={selectedPatientId}
          />
        </div>
      </div>
    </div>
  );
};

export default CopenVisualizationV2Page;
