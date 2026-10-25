import { Link } from 'react-router-dom';
import { ArrowRight, Activity } from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';
import { motion } from 'framer-motion';
import Hero from "@/components/Hero";
import ConceptSection from "@/components/ConceptSection";
import CuspVisualization from "@/components/CuspVisualization";
import CuspSurface3D from "@/components/CuspSurface3D";
import FrequencyTherapySection from "@/components/FrequencyTherapySection";
import SystemStatusDashboard from "@/components/SystemStatusDashboard";
import ThomResources from "@/components/ThomResources";
import Footer from "@/components/Footer";
import { Helmet } from "react-helmet-async";
import { Button } from "@/components/ui/button";

const Index = () => {
  return (
    <>
      <Helmet>
        <title>Feldengine – Morphogenese & Katastrophentheorie | René Thom</title>
        <meta 
          name="description" 
          content="Feldengine: Ein konzeptuelles Framework basierend auf René Thoms Katastrophentheorie. Chreoden, Attraktoren und morphogenetische Felder in der Frequenztherapie." 
        />
        <meta name="keywords" content="René Thom, Katastrophentheorie, Morphogenese, Chreoden, Attraktoren, Frequenztherapie, Semiomorphogenetik" />
      </Helmet>

      <main className="min-h-screen bg-background">
        {/* Theme Toggle */}
        <div className="fixed top-4 right-4 z-50">
          <ThemeToggle />
        </div>
        <Hero />
        <ConceptSection />
        <CuspVisualization />
        <CuspSurface3D />
        <FrequencyTherapySection />
        
        {/* Call-to-Action zur Analyse-Seite */}
        <section className="py-16 px-4">
          <div className="container mx-auto max-w-4xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="bg-gradient-to-br from-primary/10 via-secondary/10 to-accent/10 rounded-2xl border border-primary/20 p-8 md:p-12 text-center"
            >
              <Activity className="w-12 h-12 text-primary mx-auto mb-6" />
              <h2 className="font-display text-2xl md:text-3xl text-foreground mb-4">
                Klienten-<span className="text-gradient-primary">Feldanalyse</span> starten
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto mb-8">
                Berechnen Sie den individuellen Klienten-Vektor basierend auf biometrischen Daten, 
                analysieren Sie Meridian-Ungleichgewichte nach TCM und führen Sie eine 
                Frequenz-Harmonisierung mit der vollständigen WHO-409-Punkte-Datenbank durch.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link to="/analyse">
                  <Button size="lg" className="gap-2">
                    Zur Feldanalyse
                    <ArrowRight className="w-5 h-5" />
                  </Button>
                </Link>
                <Link to="/workflow">
                  <Button size="lg" variant="outline" className="gap-2">
                    Z-Anatomy Workflow
                  </Button>
                </Link>
                <Link to="/import">
                  <Button size="lg" variant="outline" className="gap-2">
                    Pilotdaten-Import
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
        
        <section id="ressourcen">
          <ThomResources />
        </section>
        <SystemStatusDashboard />
        <Footer />
      </main>
    </>
  );
};

export default Index;
