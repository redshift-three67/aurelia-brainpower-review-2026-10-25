/**
 * PDF/HTML Report Generator
 * Phase 7: Session-Reports exportieren
 */
import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { FileText, Download, Printer, Calendar, User, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { supabase } from '@/integrations/supabase/client';
import type { Database, Json } from '@/integrations/supabase/types';

type TreatmentSessionRow = Database['public']['Tables']['treatment_sessions']['Row'];

type ReportVectorSnapshot = SessionReportData['vectorSnapshot'];
type ReportDiagnosisSnapshot = SessionReportData['diagnosisSnapshot'];
type ReportTreatmentSummary = SessionReportData['treatmentSummary'];

interface SessionReportData {
  clientName: string;
  sessionNumber: number;
  sessionDate: string;
  duration: string;
  vectorSnapshot: {
    dimensions: number[];
    stability: number;
    phase: string;
    bifurcationRisk: number;
  } | null;
  diagnosisSnapshot: {
    overallPattern: string;
    imbalanceCount: number;
    imbalances: Array<{
      meridianName: string;
      element: string;
      imbalanceType: string;
      imbalanceScore: number;
    }>;
  } | null;
  treatmentSummary: {
    beforeDimensions?: number[];
    afterDimensions?: number[];
    cyclesCompleted?: number;
    pointsProcessed?: number;
  } | null;
}

interface SessionReportGeneratorProps {
  clientId: string | null;
  clientName?: string;
}

const DIMENSION_NAMES = ['Körperlich', 'Emotional', 'Mental', 'Energie', 'Stress'];

const isRecord = (value: unknown): value is { [key: string]: Json | undefined } =>
  typeof value === 'object' && value !== null && !Array.isArray(value);

const toNumber = (value: unknown, fallback: number): number =>
  typeof value === 'number' ? value : fallback;

const toString = (value: unknown, fallback: string): string =>
  typeof value === 'string' ? value : fallback;

const toNumberArray = (value: unknown): number[] =>
  Array.isArray(value) ? value.filter((item): item is number => typeof item === 'number') : [];

const parseVectorSnapshot = (snapshot: Json | null): ReportVectorSnapshot => {
  if (!isRecord(snapshot)) return null;

  return {
    dimensions: toNumberArray(snapshot.dimensions),
    stability: toNumber(snapshot.stability, 0),
    phase: toString(snapshot.phase, ''),
    bifurcationRisk: toNumber(snapshot.bifurcationRisk, 0),
  };
};

const parseDiagnosisSnapshot = (snapshot: Json | null): ReportDiagnosisSnapshot => {
  if (!isRecord(snapshot)) return null;

  const imbalances = Array.isArray(snapshot.imbalances)
    ? snapshot.imbalances.filter(isRecord).map((imbalance) => ({
      meridianName: toString(imbalance.meridianName, ''),
      element: toString(imbalance.element, ''),
      imbalanceType: toString(imbalance.imbalanceType, ''),
      imbalanceScore: toNumber(imbalance.imbalanceScore, 0),
    }))
    : [];

  return {
    overallPattern: toString(snapshot.overallPattern, ''),
    imbalanceCount: toNumber(snapshot.imbalanceCount, imbalances.length),
    imbalances,
  };
};

const parseTreatmentSummary = (snapshot: Json | null): ReportTreatmentSummary => {
  if (!isRecord(snapshot)) return null;

  return {
    beforeDimensions: toNumberArray(snapshot.beforeDimensions),
    afterDimensions: toNumberArray(snapshot.afterDimensions),
    cyclesCompleted: typeof snapshot.cyclesCompleted === 'number' ? snapshot.cyclesCompleted : undefined,
    pointsProcessed: typeof snapshot.pointsProcessed === 'number' ? snapshot.pointsProcessed : undefined,
  };
};

const SessionReportGenerator = ({ clientId, clientName }: SessionReportGeneratorProps) => {
  const [reports, setReports] = useState<SessionReportData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState<SessionReportData | null>(null);

  const loadReports = useCallback(async () => {
    if (!clientId) return;
    setIsLoading(true);
    try {
      const { data, error } = await supabase
        .from('treatment_sessions')
        .select('*')
        .eq('client_id', clientId)
        .eq('status', 'completed')
        .order('session_date', { ascending: false })
        .limit(20);

      if (error) throw error;

      const mapped: SessionReportData[] = (data || []).map((s: TreatmentSessionRow) => ({
        clientName: clientName || 'Unbekannt',
        sessionNumber: s.session_number,
        sessionDate: new Date(s.session_date).toLocaleDateString('de-DE', {
          year: 'numeric', month: 'long', day: 'numeric',
        }),
        duration: s.duration_seconds
          ? `${Math.floor(s.duration_seconds / 60)}:${String(s.duration_seconds % 60).padStart(2, '0')} min`
          : 'Nicht erfasst',
        vectorSnapshot: parseVectorSnapshot(s.vector_snapshot),
        diagnosisSnapshot: parseDiagnosisSnapshot(s.diagnosis_snapshot),
        treatmentSummary: parseTreatmentSummary(s.treatment_summary),
      }));

      setReports(mapped);
    } catch (err) {
      console.error('Load reports error:', err);
    } finally {
      setIsLoading(false);
    }
  }, [clientId, clientName]);

  const generateHTML = useCallback((report: SessionReportData): string => {
    const dimLabels = DIMENSION_NAMES;
    const vectorSection = report.vectorSnapshot ? `
      <div class="section">
        <h3>Vektor-Analyse</h3>
        <table>
          <tr><th>Dimension</th><th>Wert</th></tr>
          ${report.vectorSnapshot.dimensions.map((d, i) =>
            `<tr><td>${dimLabels[i] || `D${i}`}</td><td>${(d * 100).toFixed(1)}%</td></tr>`
          ).join('')}
        </table>
        <p><strong>Stabilität:</strong> ${(report.vectorSnapshot.stability * 100).toFixed(0)}%</p>
        <p><strong>Phase:</strong> ${report.vectorSnapshot.phase}</p>
        <p><strong>Bifurkationsrisiko:</strong> ${(report.vectorSnapshot.bifurcationRisk * 100).toFixed(0)}%</p>
      </div>
    ` : '';

    const diagSection = report.diagnosisSnapshot ? `
      <div class="section">
        <h3>Meridian-Diagnose</h3>
        <p><strong>Muster:</strong> ${report.diagnosisSnapshot.overallPattern || 'Nicht bestimmt'}</p>
        <p><strong>Imbalancen:</strong> ${report.diagnosisSnapshot.imbalanceCount}</p>
        ${report.diagnosisSnapshot.imbalances?.length ? `
          <table>
            <tr><th>Meridian</th><th>Element</th><th>Typ</th><th>Score</th></tr>
            ${report.diagnosisSnapshot.imbalances.map(i =>
              `<tr><td>${i.meridianName}</td><td>${i.element}</td><td>${i.imbalanceType}</td><td>${(i.imbalanceScore * 100).toFixed(0)}%</td></tr>`
            ).join('')}
          </table>
        ` : ''}
      </div>
    ` : '';

    const treatmentSection = report.treatmentSummary ? `
      <div class="section">
        <h3>Behandlungsergebnis</h3>
        ${report.treatmentSummary.cyclesCompleted ? `<p><strong>Zyklen:</strong> ${report.treatmentSummary.cyclesCompleted}</p>` : ''}
        ${report.treatmentSummary.pointsProcessed ? `<p><strong>Behandelte Punkte:</strong> ${report.treatmentSummary.pointsProcessed}</p>` : ''}
        ${report.treatmentSummary.beforeDimensions && report.treatmentSummary.afterDimensions ? `
          <table>
            <tr><th>Dimension</th><th>Vorher</th><th>Nachher</th><th>Δ</th></tr>
            ${report.treatmentSummary.beforeDimensions.map((b, i) => {
              const a = report.treatmentSummary!.afterDimensions![i] || 0;
              const delta = a - b;
              return `<tr><td>${dimLabels[i]}</td><td>${(b*100).toFixed(0)}%</td><td>${(a*100).toFixed(0)}%</td><td style="color:${delta > 0 ? 'green' : delta < 0 ? 'red' : 'gray'}">${delta > 0 ? '+' : ''}${(delta*100).toFixed(0)}%</td></tr>`;
            }).join('')}
          </table>
        ` : ''}
      </div>
    ` : '';

    return `<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Sitzungsbericht #${report.sessionNumber} – ${report.clientName}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', system-ui, sans-serif; color: #1a1a2e; background: #fff; padding: 40px; max-width: 800px; margin: 0 auto; }
    .header { border-bottom: 3px solid #6366f1; padding-bottom: 20px; margin-bottom: 30px; }
    .header h1 { font-size: 24px; color: #6366f1; }
    .header h2 { font-size: 16px; color: #64748b; margin-top: 4px; }
    .meta { display: flex; gap: 24px; margin-top: 12px; font-size: 13px; color: #64748b; }
    .section { margin-bottom: 24px; }
    .section h3 { font-size: 16px; color: #1e293b; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-bottom: 12px; }
    table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 13px; }
    th, td { padding: 6px 10px; border: 1px solid #e2e8f0; text-align: left; }
    th { background: #f8fafc; font-weight: 600; }
    .footer { margin-top: 40px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; text-align: center; }
    @media print { body { padding: 20px; } }
  </style>
</head>
<body>
  <div class="header">
    <h1>Feldengine – Sitzungsbericht</h1>
    <h2>Sitzung #${report.sessionNumber} – ${report.clientName}</h2>
    <div class="meta">
      <span>📅 ${report.sessionDate}</span>
      <span>⏱️ ${report.duration}</span>
    </div>
  </div>
  ${vectorSection}
  ${diagSection}
  ${treatmentSection}
  <div class="footer">
    Generiert am ${new Date().toLocaleDateString('de-DE')} | Feldengine &copy; ${new Date().getFullYear()}
  </div>
</body>
</html>`;
  }, []);

  const handlePrint = useCallback((report: SessionReportData) => {
    const html = generateHTML(report);
    const win = window.open('', '_blank');
    if (win) {
      win.document.write(html);
      win.document.close();
      setTimeout(() => win.print(), 500);
    }
  }, [generateHTML]);

  const handleDownload = useCallback((report: SessionReportData) => {
    const html = generateHTML(report);
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Sitzung_${report.sessionNumber}_${report.clientName.replace(/\s/g, '_')}.html`;
    a.click();
    URL.revokeObjectURL(url);
  }, [generateHTML]);

  if (!clientId) return null;

  return (
    <section className="py-8 px-4">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-card rounded-xl border border-border p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-primary" />
              <h2 className="font-display text-xl text-foreground">Sitzungsberichte</h2>
            </div>
            <Button variant="outline" size="sm" onClick={loadReports} disabled={isLoading}>
              {isLoading ? 'Laden...' : 'Berichte laden'}
            </Button>
          </div>

          {reports.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <FileText className="w-12 h-12 mx-auto mb-4 opacity-30" />
              <p>Klicken Sie "Berichte laden" um abgeschlossene Sitzungen anzuzeigen.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((report, idx) => (
                <div key={idx} className="flex items-center justify-between bg-muted/20 rounded-lg border border-border p-4 hover:border-primary/30 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <span className="text-sm font-bold text-primary">#{report.sessionNumber}</span>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-foreground">
                        Sitzung #{report.sessionNumber}
                      </h4>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" /> {report.sessionDate}
                        </span>
                        <span>{report.duration}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {report.vectorSnapshot && <Badge variant="outline" className="text-[10px]">Vektor</Badge>}
                    {report.diagnosisSnapshot && <Badge variant="outline" className="text-[10px]">Diagnose</Badge>}
                    {report.treatmentSummary && <Badge variant="outline" className="text-[10px]">Behandlung</Badge>}
                    <Button variant="outline" size="sm" onClick={() => handlePrint(report)}>
                      <Printer className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleDownload(report)}>
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </section>
  );
};

export default SessionReportGenerator;
