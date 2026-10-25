import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, Download, Upload, Box, CheckCircle2, ExternalLink, ChevronDown, FileText, Layers, Target, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState } from 'react';

const DOWNLOAD_SOURCES = [
  {
    id: 'z-anatomy-github',
    name: 'Z-Anatomy Blender-Datei',
    url: 'https://github.com/Z-Anatomy/Models-of-human-anatomy',
    format: '.blend (~1.5 GB)',
    license: 'CC BY-SA',
    description: 'Komplettes menschliches Anatomie-Modell mit benannten Collections pro Organsystem. Dies ist die Hauptquelle für alle Organ-GLBs.',
    priority: 'required',
  },
  {
    id: 'z-anatomy-sketchfab',
    name: 'Z-Anatomy Sketchfab (Einzelsysteme)',
    url: 'https://sketchfab.com/Z-Anatomy',
    format: 'GLB/GLTF',
    license: 'CC BY-SA',
    description: 'Fertig exportierte Einzelsystem-Modelle (Angiologie, Splanchnologie, Myologie, Neurologie). Direkt downloadbar ohne Blender.',
    priority: 'optional',
  },
  {
    id: 'bodyparts3d',
    name: 'BodyParts3D (Original-Datenquelle)',
    url: 'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html',
    format: 'OBJ/STL',
    license: 'CC BY-SA 2.1 JP',
    description: 'Originale anatomische Meshes sortiert nach FMA-ID. Höchste Detailtiefe für einzelne Strukturen.',
    priority: 'optional',
  },
];

const ORGAN_EXPORTS = [
  { organ: 'Herz', collection: 'Heart', fmaId: 'FMA_7088', fileName: 'heart_z-anatomy.glb', status: 'pending' as const },
  { organ: 'Gehirn', collection: 'Brain', fmaId: 'FMA_50801', fileName: 'brain_z-anatomy.glb', status: 'pending' as const },
  { organ: 'Leber', collection: 'Liver', fmaId: 'FMA_7197', fileName: 'liver_z-anatomy.glb', status: 'pending' as const },
  { organ: 'Niere', collection: 'Kidney', fmaId: 'FMA_7203', fileName: 'kidney_z-anatomy.glb', status: 'pending' as const },
  { organ: 'Lunge', collection: 'Lung', fmaId: 'FMA_7195', fileName: 'lung_z-anatomy.glb', status: 'pending' as const },
  { organ: 'Wirbelsäule', collection: 'Vertebral column', fmaId: 'FMA_11966', fileName: 'spine_z-anatomy.glb', status: 'pending' as const },
  { organ: 'Ganzkörper', collection: 'Body', fmaId: 'FMA_20394', fileName: 'wholebody_z-anatomy.glb', status: 'pending' as const },
  { organ: 'Haut (TCM)', collection: 'Integument', fmaId: 'FMA_24728', fileName: 'skin_z-anatomy.glb', status: 'pending' as const },
];

const BLENDER_STEPS = [
  { step: 1, title: 'Blender öffnen', detail: 'Blender >= 3.6 starten (kostenlos unter blender.org)' },
  { step: 2, title: 'Z-Anatomy laden', detail: 'File → Open → Die heruntergeladene .blend Datei öffnen (dauert 1-2 Min.)' },
  { step: 3, title: 'Collection auswählen', detail: 'Im Outliner (rechts oben) die gewünschte Collection anklicken, z.B. "Heart"' },
  { step: 4, title: 'Objekte selektieren', detail: 'Alle Meshes in der Collection auswählen: Klick auf Collection → Rechtsklick → "Select Objects"' },
  { step: 5, title: 'Export starten', detail: 'File → Export → glTF 2.0 (.glb)' },
  { step: 6, title: 'Export-Einstellungen', detail: 'Siehe Checkliste unten — alle Einstellungen müssen exakt stimmen!' },
  { step: 7, title: 'Speichern', detail: 'Datei benennen nach Schema: organname_z-anatomy.glb (z.B. heart_z-anatomy.glb)' },
  { step: 8, title: 'Hochladen', detail: 'Die GLB-Datei über die Modell-Bibliothek in der Analyse-Seite hochladen' },
];

const EXPORT_CHECKLIST = [
  { setting: 'Include: Selected Objects', enabled: true, critical: true },
  { setting: 'Mesh: Apply Modifiers', enabled: true, critical: true },
  { setting: 'Compression: Draco (Level 6)', enabled: true, critical: true },
  { setting: 'Animation', enabled: false, critical: true },
  { setting: 'Shape Keys', enabled: false, critical: false },
  { setting: 'Skelett / Armature', enabled: false, critical: false },
];

export default function ZAnatomyWorkflow() {
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const toggleStep = (step: number) => {
    setCompletedSteps(prev => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      return next;
    });
  };

  const progress = Math.round((completedSteps.size / BLENDER_STEPS.length) * 100);

  return (
    <>
      <Helmet>
        <title>Z-Anatomy Workflow – Modell-Integration</title>
        <meta name="description" content="Schritt-für-Schritt Anleitung zur Integration von Z-Anatomy 3D-Modellen in das Feldengine NLS-System." />
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
              <h1 className="text-xl font-semibold text-foreground">Z-Anatomy Integration</h1>
              <p className="text-sm text-muted-foreground">3D-Modelle für NLS-Analyse vorbereiten & hochladen</p>
            </div>
            <Link to="/import">
              <Button variant="outline" size="sm" className="gap-2">
                <FileText className="w-4 h-4" /> Pilotdaten-Import
              </Button>
            </Link>
          </div>
        </header>

        <div className="container mx-auto max-w-6xl px-4 py-8 space-y-8">

          {/* Overview */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layers className="w-6 h-6 text-primary" />
                  Übersicht: Was wird benötigt?
                </CardTitle>
                <CardDescription>
                  Um anatomische 3D-Modelle mit den NLS-Scan-Punkten zu verknüpfen, werden GLB-Dateien aus dem Z-Anatomy Projekt benötigt.
                  Jedes Organ wird einzeln exportiert und über die Modell-Bibliothek hochgeladen.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-background/60 border border-border">
                    <Download className="w-5 h-5 text-primary mt-0.5 shrink-0" />
                    <div>
                      <p className="font-medium text-sm text-foreground">1. Herunterladen</p>
                      <p className="text-xs text-muted-foreground">Z-Anatomy Blender-Datei von GitHub laden</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-background/60 border border-border">
                    <Box className="w-5 h-5 text-secondary mt-0.5 shrink-0" />
                    <div>
                      <p className="font-medium text-sm text-foreground">2. Exportieren</p>
                      <p className="text-xs text-muted-foreground">Organe einzeln als GLB aus Blender exportieren</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-background/60 border border-border">
                    <Upload className="w-5 h-5 text-accent mt-0.5 shrink-0" />
                    <div>
                      <p className="font-medium text-sm text-foreground">3. Hochladen</p>
                      <p className="text-xs text-muted-foreground">GLB-Dateien über Modell-Bibliothek importieren</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <Tabs defaultValue="download" className="space-y-6">
            <TabsList className="grid grid-cols-3 w-full max-w-lg">
              <TabsTrigger value="download" className="gap-1.5">
                <Download className="w-4 h-4" /> Downloads
              </TabsTrigger>
              <TabsTrigger value="export" className="gap-1.5">
                <Box className="w-4 h-4" /> Blender Export
              </TabsTrigger>
              <TabsTrigger value="upload" className="gap-1.5">
                <Upload className="w-4 h-4" /> Upload
              </TabsTrigger>
            </TabsList>

            {/* Tab: Downloads */}
            <TabsContent value="download" className="space-y-4">
              <div className="grid gap-4">
                {DOWNLOAD_SOURCES.map((src) => (
                  <Card key={src.id} className={src.priority === 'required' ? 'border-primary/30' : ''}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">{src.name}</CardTitle>
                          <CardDescription className="mt-1">{src.description}</CardDescription>
                        </div>
                        <Badge variant={src.priority === 'required' ? 'default' : 'secondary'}>
                          {src.priority === 'required' ? 'Erforderlich' : 'Optional'}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap items-center gap-3">
                        <Badge variant="outline">{src.format}</Badge>
                        <Badge variant="outline">{src.license}</Badge>
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

              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Target className="w-5 h-5 text-primary" />
                    Benötigte Organ-Exporte
                  </CardTitle>
                  <CardDescription>Diese 8 Organsysteme müssen als einzelne GLB-Dateien exportiert werden</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid sm:grid-cols-2 gap-2">
                    {ORGAN_EXPORTS.map((o) => (
                      <div key={o.fmaId} className="flex items-center gap-3 p-2.5 rounded-md border border-border bg-background/50 text-sm">
                        <Box className="w-4 h-4 text-muted-foreground shrink-0" />
                        <div className="flex-1 min-w-0">
                          <span className="font-medium text-foreground">{o.organ}</span>
                          <span className="text-muted-foreground ml-2 text-xs">→ {o.collection}</span>
                        </div>
                        <code className="text-xs text-muted-foreground">{o.fmaId}</code>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Tab: Blender Export */}
            <TabsContent value="export" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Blender Export-Workflow</CardTitle>
                  <CardDescription>
                    Klicke auf jeden Schritt um ihn als erledigt zu markieren
                  </CardDescription>
                  <Progress value={progress} className="mt-3" />
                  <p className="text-xs text-muted-foreground mt-1">{completedSteps.size} / {BLENDER_STEPS.length} Schritte erledigt</p>
                </CardHeader>
                <CardContent className="space-y-2">
                  {BLENDER_STEPS.map((s) => (
                    <button
                      key={s.step}
                      onClick={() => toggleStep(s.step)}
                      className={`w-full text-left flex items-start gap-3 p-3 rounded-lg border transition-colors ${
                        completedSteps.has(s.step)
                          ? 'bg-primary/10 border-primary/30'
                          : 'bg-background/50 border-border hover:border-primary/20'
                      }`}
                    >
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-sm font-semibold ${
                        completedSteps.has(s.step)
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        {completedSteps.has(s.step) ? <CheckCircle2 className="w-4 h-4" /> : s.step}
                      </div>
                      <div>
                        <p className="font-medium text-sm text-foreground">{s.title}</p>
                        <p className="text-xs text-muted-foreground">{s.detail}</p>
                      </div>
                    </button>
                  ))}
                </CardContent>
              </Card>

              <Card className="border-secondary/30">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-secondary" />
                    Export-Einstellungen Checkliste
                  </CardTitle>
                  <CardDescription>Diese Einstellungen sind im glTF-Export-Dialog zu setzen</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {EXPORT_CHECKLIST.map((c) => (
                      <div key={c.setting} className="flex items-center gap-3 text-sm">
                        <span className={`text-lg ${c.enabled ? 'text-green-500' : 'text-destructive'}`}>
                          {c.enabled ? '✅' : '❌'}
                        </span>
                        <span className={`${c.critical ? 'font-medium text-foreground' : 'text-muted-foreground'}`}>
                          {c.setting}
                        </span>
                        {c.critical && <Badge variant="outline" className="text-xs">Wichtig</Badge>}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Collapsible>
                <Card>
                  <CollapsibleTrigger className="w-full">
                    <CardHeader className="flex flex-row items-center justify-between">
                      <CardTitle className="text-base">Blender kostenlos herunterladen</CardTitle>
                      <ChevronDown className="w-5 h-5 text-muted-foreground" />
                    </CardHeader>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <CardContent>
                      <p className="text-sm text-muted-foreground mb-3">
                        Blender ist eine kostenlose, professionelle 3D-Software. Du benötigst mindestens Version 3.6.
                      </p>
                      <a href="https://www.blender.org/download/" target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" size="sm" className="gap-2">
                          <ExternalLink className="w-3.5 h-3.5" /> blender.org/download
                        </Button>
                      </a>
                    </CardContent>
                  </CollapsibleContent>
                </Card>
              </Collapsible>
            </TabsContent>

            {/* Tab: Upload */}
            <TabsContent value="upload" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Modell hochladen</CardTitle>
                  <CardDescription>
                    Exportierte GLB-Dateien werden über die Modell-Bibliothek auf der Analyse-Seite hochgeladen.
                    Das System normalisiert die Koordinaten automatisch und verknüpft die vorhandenen Organ-Landmarks.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 rounded-lg border border-border bg-muted/30 space-y-3">
                    <p className="text-sm font-medium text-foreground">So geht's:</p>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground">
                      <li>Gehe zur <Link to="/analyse" className="text-primary hover:underline">Analyse-Seite</Link></li>
                      <li>Öffne die <strong>Modell-Bibliothek</strong> im rechten Panel</li>
                      <li>Klicke auf <strong>„Modell hochladen"</strong></li>
                      <li>Wähle die GLB-Datei aus (max. 100 MB)</li>
                      <li>Fülle Kategorie, Quelle und Beschreibung aus</li>
                      <li>Das Modell wird automatisch mit den Landmarks verknüpft</li>
                    </ol>
                  </div>

                  <Link to="/analyse">
                    <Button className="gap-2 w-full sm:w-auto">
                      <Upload className="w-4 h-4" /> Zur Analyse-Seite & Modell-Bibliothek
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Erwartete Dateinamen</CardTitle>
                  <CardDescription>Verwende diese Namenskonvention für konsistente Zuordnung</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid sm:grid-cols-2 gap-2">
                    {ORGAN_EXPORTS.map((o) => (
                      <div key={o.fileName} className="flex items-center gap-2 p-2 rounded border border-border text-sm">
                        <Box className="w-4 h-4 text-primary shrink-0" />
                        <code className="text-xs font-mono text-foreground">{o.fileName}</code>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </>
  );
}
