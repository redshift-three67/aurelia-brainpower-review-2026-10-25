import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ArrowLeft, FileText, Upload, Database, ExternalLink, ChevronDown, Info, Layers, Globe } from 'lucide-react';
import { motion } from 'framer-motion';

const PILOT_DATA_SOURCES = [
  {
    name: 'Allen Human Brain Atlas',
    url: 'https://human.brain-map.org/',
    type: 'Gehirn',
    format: 'CSV / API',
    detail: '3D-Koordinaten mit Genexpression — ermöglicht hochauflösende S-Punkte für das Gehirn mit funktionalen Annotationen.',
  },
  {
    name: 'IT\'IS Virtual Population',
    url: 'https://itis.swiss/virtual-population/',
    type: 'Ganzkörper',
    format: 'Proprietär → CSV konvertierbar',
    detail: '>300 Gewebetypen mit dielektrischen Eigenschaften. Ideal für frequenzbasierte Scan-Punkte.',
  },
  {
    name: 'Visible Human Project',
    url: 'https://www.nlm.nih.gov/research/visible/getting_data.html',
    type: 'Ganzkörper',
    format: 'CT/MRT Slices',
    detail: 'Cryosection-Daten mit CT- und MRT-Korrelation. Referenz für anatomische Koordinaten-Validierung.',
  },
  {
    name: 'WHO Standard Acupuncture Point Locations',
    url: 'https://iris.who.int/bitstream/handle/10665/353407/9789290613831-eng.pdf',
    type: 'TCM / Akupunktur',
    format: 'PDF (361 Punkte)',
    detail: 'Offizielle WHO-Publikation mit standardisierten Akupunkturpunkt-Lokalisierungen (Western Pacific Region). Bereits teilweise im System integriert.',
  },
  {
    name: 'Standardized Acupuncture Points (CT-basiert)',
    url: 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3929431/',
    type: 'TCM / Akupunktur',
    format: 'CT-Koordinaten / PDF',
    detail: 'CT-basiertes 3D-Mapping standardisierter Akupunkturpunkte am gesamten Körper (PubMed Central).',
  },
  {
    name: 'BodyParts3D FMA-Browser',
    url: 'https://lifesciencedb.jp/bp3d/',
    type: 'Sub-Organ',
    format: 'OBJ + FMA-IDs',
    detail: 'Sub-Organ-Ebene bis Gewebetyp. Ideal für die automatische S-Punkt-Generierung via FMA Part-Of Hierarchie.',
  },
  {
    name: 'Open Anatomy Project',
    url: 'https://www.openanatomy.org/',
    type: 'Diverse',
    format: 'NRRD / STL',
    detail: 'Kuratierte anatomische Atlanten verschiedener Institutionen. Gute Ergänzung für fehlende Organsysteme.',
  },
];

const IMPORT_FORMATS = [
  {
    format: 'Schema JSON',
    extension: '.json',
    description: 'Organ-Schema-Definition mit Regionen, Koordinatensystem und Konfiguration',
    example: `{
  "organ_code": "HEART",
  "organ_name": "Heart",
  "source_dataset": "BodyParts3D",
  "source_concept_id": "FMA_7088",
  "coordinate_system": "RAS",
  "regions": { ... },
  "point_classes": ["A", "S", "V"]
}`,
  },
  {
    format: 'Landmark CSV',
    extension: '.csv',
    description: 'Anatomische Landmarks mit 3D-Koordinaten, FMA-IDs und Frequenzen',
    example: `point_id,label,region_code,x,y,z,point_class,confidence,scan_frequency,fma_id
HEART_A01,Apex of Heart,APEX,0.01,-0.02,-0.05,A,0.95,639.75,FMA_7170
HEART_A02,Base of Heart,BASE,0.0,0.04,0.03,A,0.92,528.0,FMA_7163`,
  },
  {
    format: 'Manifest CSV',
    extension: '.csv',
    description: 'Übersicht aller exportierten Organ-Schemas und Landmark-Zählungen',
    example: `organ_code,organ_name,a_landmarks,s_landmarks,v_landmarks,total
HEART,Heart,10,0,0,10
BRAIN,Brain,8,0,0,8`,
  },
];

const IMPORT_STEPS = [
  {
    step: 1,
    title: 'Datenquelle auswählen',
    detail: 'Wähle eine der oben gelisteten Quellen oder bereite eigene Daten im korrekten Format vor.',
  },
  {
    step: 2,
    title: 'Daten in CSV/JSON konvertieren',
    detail: 'Stelle sicher, dass die Koordinaten im RAS-System (Right-Anterior-Superior) vorliegen. Verwende die Vorlagen unten.',
  },
  {
    step: 3,
    title: 'FMA-IDs zuordnen',
    detail: 'Jeder Landmark sollte eine FMA-ID aus der BodyParts3D-Ontologie haben. Nutze den FMA-Browser zur Verifizierung.',
  },
  {
    step: 4,
    title: 'Dateien hier hochladen',
    detail: 'Lade Schema-JSON und Landmark-CSV als Nachricht im Chat hoch. Das System integriert die Daten automatisch.',
  },
  {
    step: 5,
    title: 'Validierung prüfen',
    detail: 'Nach dem Import werden die Punkte im 3D-Viewer angezeigt. Prüfe die Positionen visuell auf Korrektheit.',
  },
];

export default function PilotDataImport() {
  return (
    <>
      <Helmet>
        <title>Pilotdaten-Import – Neue Organsysteme & Landmarks</title>
        <meta name="description" content="Import-Workflow für neue anatomische Pilotdaten, Organ-Schemas und Landmarks in das NLS-System." />
      </Helmet>

      <main className="min-h-screen bg-background">
        <div className="fixed top-4 right-4 z-50"><ThemeToggle /></div>

        {/* Header */}
        <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-40">
          <div className="container mx-auto max-w-6xl px-4 py-4 flex items-center gap-4">
            <Link to="/">
              <Button variant="ghost" size="sm" className="gap-2">
                <ArrowLeft className="w-4 h-4" /> Startseite
              </Button>
            </Link>
            <div className="flex-1">
              <h1 className="text-xl font-semibold text-foreground">Pilotdaten-Import</h1>
              <p className="text-sm text-muted-foreground">Neue Organ-Schemas & Landmarks importieren</p>
            </div>
            <Link to="/workflow">
              <Button variant="outline" size="sm" className="gap-2">
                <Layers className="w-4 h-4" /> Z-Anatomy Workflow
              </Button>
            </Link>
          </div>
        </header>

        <div className="container mx-auto max-w-6xl px-4 py-8 space-y-8">

          {/* Current Status */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="w-6 h-6 text-primary" />
                  Aktueller Datenbestand
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="text-center p-3 rounded-lg bg-muted/50">
                    <p className="text-2xl font-bold text-primary">8</p>
                    <p className="text-xs text-muted-foreground">Organsysteme</p>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-muted/50">
                    <p className="text-2xl font-bold text-primary">57</p>
                    <p className="text-xs text-muted-foreground">A-Landmarks</p>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-muted/50">
                    <p className="text-2xl font-bold text-secondary">0</p>
                    <p className="text-xs text-muted-foreground">S-Punkte</p>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-muted/50">
                    <p className="text-2xl font-bold text-accent">0</p>
                    <p className="text-xs text-muted-foreground">V-Punkte</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <Tabs defaultValue="workflow" className="space-y-6">
            <TabsList className="grid grid-cols-3 w-full max-w-lg">
              <TabsTrigger value="workflow" className="gap-1.5">
                <FileText className="w-4 h-4" /> Workflow
              </TabsTrigger>
              <TabsTrigger value="formats" className="gap-1.5">
                <Database className="w-4 h-4" /> Formate
              </TabsTrigger>
              <TabsTrigger value="sources" className="gap-1.5">
                <Globe className="w-4 h-4" /> Datenquellen
              </TabsTrigger>
            </TabsList>

            {/* Tab: Workflow */}
            <TabsContent value="workflow" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Import-Schritte</CardTitle>
                  <CardDescription>So fügst du neue Organsysteme oder Landmarks hinzu</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {IMPORT_STEPS.map((s) => (
                    <div key={s.step} className="flex items-start gap-3 p-3 rounded-lg border border-border bg-background/50">
                      <div className="w-7 h-7 rounded-full bg-primary/10 text-primary flex items-center justify-center shrink-0 text-sm font-semibold">
                        {s.step}
                      </div>
                      <div>
                        <p className="font-medium text-sm text-foreground">{s.title}</p>
                        <p className="text-xs text-muted-foreground">{s.detail}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="border-secondary/20">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Info className="w-5 h-5 text-secondary" />
                    Koordinatensystem: RAS
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-muted-foreground space-y-2">
                  <p><strong>R</strong>ight – X-Achse zeigt nach rechts (vom Betrachter aus)</p>
                  <p><strong>A</strong>nterior – Y-Achse zeigt nach vorne (Bauchseite)</p>
                  <p><strong>S</strong>uperior – Z-Achse zeigt nach oben (Kopf)</p>
                  <p className="text-xs mt-3 text-muted-foreground/70">
                    Alle Koordinaten sind auf eine normalisierte Körperhöhe von 1.0 skaliert.
                    Der Ursprung liegt im geometrischen Zentrum des Organs.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Tab: Formate */}
            <TabsContent value="formats" className="space-y-4">
              {IMPORT_FORMATS.map((f) => (
                <Card key={f.format}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-base">{f.format}</CardTitle>
                      <Badge variant="outline">{f.extension}</Badge>
                    </div>
                    <CardDescription>{f.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Collapsible>
                      <CollapsibleTrigger asChild>
                        <Button variant="ghost" size="sm" className="gap-2 text-xs">
                          <ChevronDown className="w-3.5 h-3.5" /> Beispiel anzeigen
                        </Button>
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        <pre className="mt-2 p-3 rounded-lg bg-muted/50 border border-border text-xs font-mono overflow-x-auto whitespace-pre">
                          {f.example}
                        </pre>
                      </CollapsibleContent>
                    </Collapsible>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>

            {/* Tab: Datenquellen */}
            <TabsContent value="sources" className="space-y-4">
              <div className="grid gap-4">
                {PILOT_DATA_SOURCES.map((src) => (
                  <Card key={src.name}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <CardTitle className="text-base">{src.name}</CardTitle>
                          <CardDescription className="mt-1">{src.detail}</CardDescription>
                        </div>
                        <Badge variant="secondary">{src.type}</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap items-center gap-3">
                        <Badge variant="outline">{src.format}</Badge>
                        <a href={src.url} target="_blank" rel="noopener noreferrer">
                          <Button size="sm" variant="outline" className="gap-2">
                            <ExternalLink className="w-3.5 h-3.5" /> Öffnen
                          </Button>
                        </a>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </>
  );
}
