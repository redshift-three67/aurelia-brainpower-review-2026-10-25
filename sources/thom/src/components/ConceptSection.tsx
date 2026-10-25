import { motion } from "framer-motion";
import ChreodeCard from "./ChreodeCard";
import { 
  Atom, 
  GitBranch, 
  Waves, 
  Orbit, 
  Layers, 
  Zap 
} from "lucide-react";

const ConceptSection = () => {
  const concepts = [
    {
      title: "Chreoden",
      description: "Topologische Pfade, die dynamische Systeme trotz Störungen zu stabilen Formen führen. Nach Waddington die 'Kanalkonstanten' biologischer Entwicklung.",
      icon: GitBranch,
      variant: "secondary" as const,
    },
    {
      title: "Attraktoren",
      description: "Stabile Endzustände im Phasenraum, zu denen das System konvergiert. In der Morphogenese repräsentieren sie gesunde Organformen.",
      icon: Orbit,
      variant: "primary" as const,
    },
    {
      title: "Bifurkationen",
      description: "Kritische Punkte, an denen das System zwischen verschiedenen stabilen Zuständen wechseln kann. Katastrophen im Thom'schen Sinne.",
      icon: Atom,
      variant: "accent" as const,
    },
    {
      title: "Morphogenetische Felder",
      description: "Nach Gurwitsch und Sheldrake: Felder, die die räumliche Organisation von Organismen steuern, jenseits genetischer Information.",
      icon: Waves,
      variant: "primary" as const,
    },
    {
      title: "Potenzialflächen",
      description: "Mathematische Landschaften, auf denen sich Systemzustände bewegen. Senken = Attraktoren, Kämme = instabile Gleichgewichte.",
      icon: Layers,
      variant: "secondary" as const,
    },
    {
      title: "Resonanzfrequenzen",
      description: "Kontrollparameter, die Übergänge zwischen Zuständen auslösen können. Basis der Frequenztherapie nach Baklayan.",
      icon: Zap,
      variant: "accent" as const,
    },
  ];

  return (
    <section id="konzept" className="py-24 relative">
      {/* Background */}
      <div className="absolute inset-0 bg-field-pattern opacity-30" />
      
      <div className="container mx-auto px-4 relative z-10">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <span className="text-primary text-sm font-medium uppercase tracking-wider mb-4 block">
            Theoretische Grundlagen
          </span>
          <h2 className="font-display text-3xl md:text-5xl font-bold text-foreground mb-6">
            Kernkonzepte der <span className="text-gradient-primary">Feldengine</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            Die mathematischen und biologischen Grundlagen, die Thoms Katastrophentheorie 
            mit morphogenetischen Prozessen und Frequenztherapie verbinden.
          </p>
        </motion.div>

        {/* Quote */}
        <motion.blockquote
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto mb-16 text-center"
        >
          <div className="relative px-8 py-6 bg-card border border-border rounded-2xl">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-background px-4">
              <span className="text-4xl text-chreode font-display">"</span>
            </div>
            <p className="text-foreground italic text-lg mb-4">
              Von einem gewissen Punkt an gibt es keine Rückkehr mehr. 
              Diesen Punkt gilt es zu erreichen.
            </p>
            <cite className="text-muted-foreground text-sm">
              — Franz Kafka (zitiert in Toth, 2007)
            </cite>
          </div>
        </motion.blockquote>

        {/* Concept cards grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {concepts.map((concept, index) => (
            <ChreodeCard
              key={concept.title}
              title={concept.title}
              description={concept.description}
              icon={concept.icon}
              variant={concept.variant}
              delay={index * 0.1}
            />
          ))}
        </div>

        {/* Historical context */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="mt-16 p-8 bg-card border border-border rounded-2xl"
        >
          <h3 className="font-display text-2xl font-bold text-foreground mb-4">
            Historischer Kontext
          </h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h4 className="text-primary font-semibold mb-2">Biologische Wurzeln</h4>
              <p className="text-muted-foreground text-sm leading-relaxed">
                Der Begriff des <em>morphogenetischen Feldes</em> wurde 1910 von <strong className="text-foreground">Alexander G. Gurwitsch</strong> 
                zur Beschreibung embryonaler Entwicklung eingeführt. Seine Nachfolger – Harrison, Weiss, Morgan – 
                betrachteten weniger die einzelnen Zellen als deren "Felder" als für die Organentwicklung verantwortlich.
              </p>
            </div>
            <div>
              <h4 className="text-chreode font-semibold mb-2">Semiotische Erweiterung</h4>
              <p className="text-muted-foreground text-sm leading-relaxed">
                <strong className="text-foreground">Max Bense</strong> (1979) und <strong className="text-foreground">Alfred Toth</strong> (2007) 
                entwickelten die <em>Semiomorphogenetik</em> – eine mathematisch-semiotische Theorie, 
                die Thoms Katastrophentheorie mit Zeichenprozessen verbindet. Mesozeichen werden als 
                Chreoden interpretiert, ihre Umgebungen als morphogenetische Felder.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default ConceptSection;
