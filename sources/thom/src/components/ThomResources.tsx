import { motion } from "framer-motion";
import { ExternalLink, Download, FileText, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ResourceItem {
  title: string;
  year?: string;
  type: "book" | "article" | "collection";
  language: string;
  url: string;
  description?: string;
}

const resources: ResourceItem[] = [
  {
    title: "Structural Stability and Morphogenesis",
    year: "1975",
    type: "book",
    language: "Englisch",
    url: "https://uberty.org/wp-content/uploads/2015/12/Thom-Structural-Stability-and-Morphogenesis.compressed.pdf",
    description: "Thoms Hauptwerk – modelliert Morphogenese als stabile Attraktoren in dynamischen Systemen"
  },
  {
    title: "Stabilité structurelle et morphogénèse",
    year: "1972",
    type: "book",
    language: "Französisch (Original)",
    url: "https://archive.org/details/structuralstabil0000thom",
    description: "Das französische Original von Thoms bahnbrechender Arbeit"
  },
  {
    title: "Mathematical Models of Morphogenesis",
    year: "1983",
    type: "book",
    language: "Englisch",
    url: "https://archive.org/details/mathematicalmode0000thom",
    description: "Erweiterung zu biologischen Modellen und Chreoden"
  },
  {
    title: "Frühe Artikel zur Morphogenese (1966-1970)",
    year: "1966-1970",
    type: "collection",
    language: "Mehrsprachig",
    url: "https://jeanpetitot.com/ArticlesPDF/Petitot_Thom_1966-1970.pdf",
    description: "Sammlung: Dynamical theory for morphogenesis, Topological models in biology"
  },
  {
    title: "Semiomorphogenetische Stabilität und Instabilität",
    year: "2007",
    type: "article",
    language: "Deutsch",
    url: "#",
    description: "Alfred Toth – Mathematisch-semiotische Weiterführung der Katastrophentheorie"
  },
];

const ThomResources = () => {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case "book":
        return BookOpen;
      case "article":
        return FileText;
      default:
        return FileText;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "book":
        return "bg-primary/10 text-primary border-primary/20";
      case "article":
        return "bg-chreode/10 text-chreode border-chreode/20";
      default:
        return "bg-accent/10 text-accent border-accent/20";
    }
  };

  return (
    <section className="py-20 relative">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <span className="text-primary text-sm font-medium uppercase tracking-wider mb-4 block">
            Primärtexte & Ressourcen
          </span>
          <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            René Thom: <span className="text-gradient-primary">Katastrophentheorie</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Die fundamentalen Werke zur Morphogenese und deren mathematische Grundlagen – 
            frei verfügbar auf wissenschaftlichen Archiven.
          </p>
        </motion.div>

        <div className="space-y-4">
          {resources.map((resource, index) => {
            const Icon = getTypeIcon(resource.type);
            return (
              <motion.div
                key={resource.title}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group relative bg-card border border-border rounded-xl p-5 hover:border-primary/30 transition-all duration-300 hover:shadow-card"
              >
                <div className="flex flex-col md:flex-row md:items-center gap-4">
                  {/* Icon & Type */}
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 ${getTypeColor(resource.type)} border`}>
                    <Icon className="w-5 h-5" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-display text-lg font-semibold text-foreground truncate">
                        {resource.title}
                      </h3>
                      {resource.year && (
                        <span className="text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded-full flex-shrink-0">
                          {resource.year}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {resource.description}
                    </p>
                    <span className="text-xs text-primary/70">
                      {resource.language}
                    </span>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 flex-shrink-0">
                    {resource.url !== "#" ? (
                      <>
                        <Button
                          variant="field"
                          size="sm"
                          asChild
                        >
                          <a href={resource.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="w-4 h-4" />
                            Öffnen
                          </a>
                        </Button>
                        <Button
                          variant="glow"
                          size="sm"
                          asChild
                        >
                          <a href={resource.url} download>
                            <Download className="w-4 h-4" />
                          </a>
                        </Button>
                      </>
                    ) : (
                      <span className="text-xs text-muted-foreground italic">
                        Im Projekt enthalten
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Additional Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-8 p-6 bg-muted/50 border border-border rounded-xl"
        >
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-chreode/10 text-chreode flex items-center justify-center flex-shrink-0">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-display text-lg font-semibold text-foreground mb-2">
                Vollständige Bibliographie
              </h4>
              <p className="text-sm text-muted-foreground mb-3">
                Eine umfassende Bibliographie von Thoms Werken (über 100 Arbeiten) ist verfügbar auf:
              </p>
              <a 
                href="https://webhomes.maths.ed.ac.uk/~v1ranick/papers/thom/data/biblio.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:text-primary/80 underline underline-offset-2"
              >
                webhomes.maths.ed.ac.uk – Thom Bibliography (PDF)
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default ThomResources;
