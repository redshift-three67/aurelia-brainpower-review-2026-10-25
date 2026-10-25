import { motion } from "framer-motion";
import { ArrowRight, Zap, Waves, Target, RefreshCw } from "lucide-react";

const FrequencyTherapySection = () => {
  const steps = [
    {
      icon: Target,
      phase: "Testphase",
      model: "Bifurkationsset prüfen",
      explanation: "Das Körperfeld zeigt Störkanäle – Frequenzen scannen die Attraktoren und identifizieren pathologische Muster.",
      color: "primary",
    },
    {
      icon: Zap,
      phase: "Frequenzgabe",
      model: "Katastrophen-Übergang",
      explanation: "Die Resonanzfrequenz kippt das Potenzial – wie ein Schalter, der das System abrupt in einen gesunden Zustand überführt.",
      color: "chreode",
    },
    {
      icon: RefreshCw,
      phase: "Nachsorge",
      model: "Stabilisierung im Chreod",
      explanation: "Das morphogenetische Feld speichert die neue Ordnung. Regelmäßige Impulse halten den Kanal offen.",
      color: "accent",
    },
  ];

  const getColorClasses = (color: string) => {
    switch (color) {
      case "primary":
        return { bg: "bg-primary/10", text: "text-primary", border: "border-primary/30", glow: "shadow-glow-primary" };
      case "chreode":
        return { bg: "bg-chreode/10", text: "text-chreode", border: "border-chreode/30", glow: "shadow-glow-secondary" };
      case "accent":
        return { bg: "bg-accent/10", text: "text-accent", border: "border-accent/30", glow: "shadow-[0_0_30px_hsl(270_60%_55%/0.3)]" };
      default:
        return { bg: "bg-primary/10", text: "text-primary", border: "border-primary/30", glow: "shadow-glow-primary" };
    }
  };

  return (
    <section className="py-20 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-field-pattern opacity-50" />
      
      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="text-chreode text-sm font-medium uppercase tracking-wider mb-4 block">
            Praktische Anwendung
          </span>
          <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            Frequenztherapie als <span className="text-gradient-secondary">Thom-Modell</span>
          </h2>
          <p className="text-muted-foreground max-w-3xl mx-auto">
            Die Katastrophentheorie erklärt, wie Frequenzen gestörte biologische Systeme 
            durch Bifurkationen in stabile Attraktoren (Chreoden) zurückführen können.
          </p>
        </motion.div>

        {/* Mathematical Foundation Box */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-16 p-8 bg-card border border-border rounded-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl from-primary/10 to-transparent rounded-bl-full" />
          
          <div className="flex flex-col lg:flex-row gap-8 items-center">
            <div className="flex-1">
              <h3 className="font-display text-2xl font-bold text-foreground mb-4">
                Das Kuspen-Modell
              </h3>
              <p className="text-muted-foreground mb-6">
                Thoms Potenzialfunktion beschreibt, wie Kontrollparameter (Frequenzen) 
                das System zwischen stabilen Zuständen wechseln lassen:
              </p>
              
              {/* Mathematical formula */}
              <div className="bg-muted/50 border border-border rounded-xl p-6 font-mono text-center">
                <div className="text-xl md:text-2xl text-foreground mb-2">
                  V(x; a, b) = x<sup>4</sup> + ax<sup>2</sup> + bx
                </div>
                <div className="text-sm text-muted-foreground mt-4">
                  <span className="text-primary">a, b</span> = Kontrollparameter (Frequenzen) | 
                  <span className="text-chreode ml-2">V</span> = Potenzialfläche | 
                  <span className="text-accent ml-2">x</span> = Systemzustand
                </div>
              </div>
            </div>
            
            {/* Visual representation */}
            <div className="w-full lg:w-80 h-60 relative">
              <svg viewBox="0 0 200 150" className="w-full h-full">
                {/* Cusp surface approximation */}
                <defs>
                  <linearGradient id="cuspGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="hsl(192, 82%, 45%)" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="hsl(38, 92%, 50%)" stopOpacity="0.3" />
                  </linearGradient>
                </defs>
                
                {/* Cusp fold visualization */}
                <path
                  d="M20,130 Q50,100 100,60 Q150,20 180,30 Q160,50 140,80 Q120,110 100,120 Q80,130 60,125 Q40,120 20,130"
                  fill="url(#cuspGradient)"
                  stroke="hsl(192, 82%, 45%)"
                  strokeWidth="1.5"
                />
                
                {/* Bifurcation set */}
                <path
                  d="M100,60 L100,120"
                  stroke="hsl(38, 92%, 50%)"
                  strokeWidth="2"
                  strokeDasharray="5,5"
                />
                
                {/* Attractor points */}
                <circle cx="60" cy="110" r="6" fill="hsl(192, 82%, 45%)" opacity="0.8">
                  <animate attributeName="r" values="6;8;6" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle cx="140" cy="50" r="6" fill="hsl(38, 92%, 50%)" opacity="0.8">
                  <animate attributeName="r" values="6;8;6" dur="2s" repeatCount="indefinite" begin="0.5s" />
                </circle>
                
                {/* Labels */}
                <text x="55" y="130" fill="hsl(192, 82%, 55%)" fontSize="10" fontFamily="Inter">Gesund</text>
                <text x="125" y="40" fill="hsl(38, 92%, 55%)" fontSize="10" fontFamily="Inter">Pathologisch</text>
                <text x="90" y="145" fill="hsl(270, 60%, 55%)" fontSize="9" fontFamily="Inter">Bifurkation</text>
              </svg>
            </div>
          </div>
        </motion.div>

        {/* Therapy Steps */}
        <div className="grid md:grid-cols-3 gap-6">
          {steps.map((step, index) => {
            const colors = getColorClasses(step.color);
            const Icon = step.icon;
            
            return (
              <motion.div
                key={step.phase}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.15 }}
                viewport={{ once: true }}
                className={`relative bg-card border ${colors.border} rounded-2xl p-6 hover:${colors.glow} transition-all duration-500`}
              >
                {/* Step number */}
                <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-background border border-border flex items-center justify-center text-sm font-bold text-foreground">
                  {index + 1}
                </div>

                {/* Icon */}
                <div className={`w-14 h-14 rounded-xl ${colors.bg} ${colors.text} flex items-center justify-center mb-4`}>
                  <Icon className="w-7 h-7" />
                </div>

                {/* Content */}
                <h3 className="font-display text-xl font-bold text-foreground mb-1">
                  {step.phase}
                </h3>
                <p className={`text-sm ${colors.text} mb-3 font-medium`}>
                  {step.model}
                </p>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {step.explanation}
                </p>

                {/* Arrow connector (except last) */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                    <ArrowRight className="w-6 h-6 text-muted-foreground" />
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Integration note */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          viewport={{ once: true }}
          className="mt-12 text-center"
        >
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-muted/50 border border-border rounded-full">
            <Waves className="w-5 h-5 text-primary" />
            <span className="text-sm text-muted-foreground">
              Integration mit <span className="text-foreground font-medium">Mitochondrien-Modellen</span> (Kuklinski) und 
              <span className="text-foreground font-medium"> Quantenfeld-Theorie</span> (Warnke)
            </span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default FrequencyTherapySection;
