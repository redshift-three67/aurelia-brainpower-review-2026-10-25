import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import Index from "./pages/Index";
import Analyse from "./pages/Analyse";
import KlientDashboard from "./pages/KlientDashboard";
import Login from "./pages/Login";
import Export from "./pages/Export";
import ZAnatomyWorkflow from "./pages/ZAnatomyWorkflow";
import PilotDataImport from "./pages/PilotDataImport";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";

const queryClient = new QueryClient();

const App = () => (
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/analyse" element={<ProtectedRoute><Analyse /></ProtectedRoute>} />
            <Route path="/export" element={<ProtectedRoute><Export /></ProtectedRoute>} />
            <Route path="/klient/:id" element={<ProtectedRoute><KlientDashboard /></ProtectedRoute>} />
            <Route path="/workflow" element={<ZAnatomyWorkflow />} />
            <Route path="/import" element={<PilotDataImport />} />
            {/* Backward/typo-friendly alias */}
            <Route path="/exports" element={<Navigate to="/export" replace />} />
            <Route path="/login" element={<Login />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>
);

export default App;
