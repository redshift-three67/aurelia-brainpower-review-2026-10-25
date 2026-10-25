import { motion } from "framer-motion";
import { Mail, ExternalLink, FileText, Users } from "lucide-react";
import { Button } from "@/components/ui/button";

const Footer = () => {
  const links = [
    { label: "Archive.org", url: "https://archive.org/details/structuralstabil0000thom", icon: ExternalLink },
    { label: "Jean Petitot Archiv", url: "https://jeanpetitot.com/ArticlesPDF/", icon: FileText },
    { label: "PhilPapers", url: "https://philpapers.org/rec/THOSSA-12", icon: Users },
  ];

  return (
    <footer className="py-16 border-t border-border relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
      <div className="absolute top-0 right-0 w-64 h-64 bg-chreode/5 rounded-full blur-3xl" />

      <div className="container mx-auto px-4 relative z-10">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
            >
              <h3 className="font-display text-3xl font-bold text-foreground mb-4">
                Feld<span className="text-gradient-primary">Engine</span>
              </h3>
              <p className="text-muted-foreground mb-6 max-w-md">
                Ein konzeptuelles Framework zur Verbindung von René Thoms Katastrophentheorie 
                mit morphogenetischen Feldern und frequenzbasierter Therapie.
              </p>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="w-4 h-4 text-primary" />
                <span>Basierend auf Toth (2007): Semiomorphogenetische Stabilität</span>
              </div>
            </motion.div>
          </div>

          {/* Resources */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
            >
              <h4 className="font-display text-lg font-semibold text-foreground mb-4">
                Archive & Ressourcen
              </h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors text-sm"
                    >
                      <link.icon className="w-4 h-4" />
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>

          {/* Legal */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <h4 className="font-display text-lg font-semibold text-foreground mb-4">
                Rechtliche Hinweise
              </h4>
              <p className="text-muted-foreground text-sm mb-4">
                Die verlinkten PDFs stammen aus öffentlichen Archiven und dienen 
                Bildungszwecken. Für kommerzielle Nutzung beachten Sie die jeweiligen Urheberrechte.
              </p>
              <p className="text-xs text-muted-foreground/70">
                Archive.org ist anonym zugänglich. Scribd/Academia erfordern oft Login.
              </p>
            </motion.div>
          </div>
        </div>

        {/* Bottom bar */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          viewport={{ once: true }}
          className="mt-12 pt-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <p className="text-sm text-muted-foreground">
            © 2024 Feldengine Konzept. Inspiriert von René Thom, Max Bense & Alfred Toth.
          </p>
          <div className="flex items-center gap-4">
            <span className="text-xs text-muted-foreground/50">
              Chreoden • Attraktoren • Bifurkationen
            </span>
          </div>
        </motion.div>
      </div>
    </footer>
  );
};

export default Footer;
