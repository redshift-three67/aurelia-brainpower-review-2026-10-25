import { Helmet } from "react-helmet-async";
import { Link } from "react-router-dom";
import { ArrowLeft, Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const EXPORTS = {
  json: "/exports/who-meridian-points.json",
  csv: "/exports/who-meridian-points.csv",
};

const Export = () => {
  return (
    <>
      <Helmet>
        <title>WHO Meridianliste Export | Feldengine</title>
        <meta
          name="description"
          content="Download der vollständigen WHO-Akupunkturpunkt-Datenbank (Meridianliste) als JSON oder CSV."
        />
      </Helmet>

      <main className="min-h-screen bg-background">
        <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <Link to="/">
              <Button variant="ghost" className="gap-2">
                <ArrowLeft className="w-4 h-4" />
                Zurück
              </Button>
            </Link>
            <div className="w-[120px]" />
          </div>
        </header>

        <section className="container mx-auto px-4 py-10">
          <div className="max-w-2xl mx-auto">
            <h1 className="font-display text-2xl md:text-3xl text-foreground mb-2">
              WHO Meridianliste Export
            </h1>
            <p className="text-muted-foreground mb-6">
              Download der kompletten Akupunkturpunkt-Datenbank (WHO-Standard) als JSON oder CSV.
            </p>

            <Card className="p-6">
              <div className="flex flex-col sm:flex-row gap-3">
                <Button asChild className="gap-2 w-full">
                  <a href={EXPORTS.json} download>
                    <Download className="w-4 h-4" />
                    JSON herunterladen
                  </a>
                </Button>

                <Button asChild variant="secondary" className="gap-2 w-full">
                  <a href={EXPORTS.csv} download>
                    <Download className="w-4 h-4" />
                    CSV herunterladen
                  </a>
                </Button>
              </div>

              <div className="mt-6 text-sm text-muted-foreground space-y-1">
                <p>
                  Dateien liegen statisch unter <code className="font-mono">/exports/</code>.
                </p>
                <p>
                  CSV: Listenfelder (z.B. <code className="font-mono">functions</code>, <code className="font-mono">indications</code>,
                  <code className="font-mono">harmonicFrequencies</code>) sind per <code className="font-mono">; </code> zusammengeführt.
                </p>
              </div>
            </Card>
          </div>
        </section>
      </main>
    </>
  );
};

export default Export;
