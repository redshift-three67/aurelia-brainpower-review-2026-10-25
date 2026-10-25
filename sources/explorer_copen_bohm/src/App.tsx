
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import ImportPage from "./pages/ImportPage";
import CopenGeneratorPage from "./pages/CopenGeneratorPage";
import CopenVisualizationV2Page from "./pages/CopenVisualizationV2Page";
import FormulasPage from "./pages/FormulasPage";
import MorphicFieldPage from "./pages/MorphicFieldPage";
import SessionRecoveryPage from "./pages/SessionRecoveryPage";
import AuthPage from "./pages/AuthPage";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/" element={<ProtectedRoute><Index /></ProtectedRoute>} />
          <Route path="/import" element={<ProtectedRoute><ImportPage /></ProtectedRoute>} />
          <Route path="/copen-generator" element={<ProtectedRoute><CopenGeneratorPage /></ProtectedRoute>} />
          <Route path="/copen-visualisierung-v2" element={<ProtectedRoute><CopenVisualizationV2Page /></ProtectedRoute>} />
          <Route path="/formulas" element={<ProtectedRoute><FormulasPage /></ProtectedRoute>} />
          <Route path="/morphic-field" element={<ProtectedRoute><MorphicFieldPage /></ProtectedRoute>} />
          <Route path="/session-recovery" element={<ProtectedRoute><SessionRecoveryPage /></ProtectedRoute>} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
