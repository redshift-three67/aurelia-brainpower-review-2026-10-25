import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import SessionRecoveryDashboard from "@/components/SessionRecoveryDashboard";

const SessionRecoveryPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <Button 
          variant="outline" 
          onClick={() => navigate('/')}
          className="mb-6 bg-white/10 border-white/20 text-white hover:bg-white/20"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Zurück zur Übersicht
        </Button>
        
        <h1 className="text-3xl font-bold text-white mb-6">Session Recovery Dashboard</h1>
        
        <SessionRecoveryDashboard />
      </div>
    </div>
  );
};

export default SessionRecoveryPage;
