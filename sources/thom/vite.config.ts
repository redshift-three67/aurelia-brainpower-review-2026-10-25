import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";
import { mkdir, writeFile } from "node:fs/promises";
import { Buffer } from "node:buffer";
import { build } from "esbuild";
import type { AcupuncturePoint } from "./src/utils/meridianPointsDatabase";

type MeridianPointsModule = {
  COMPLETE_ACUPUNCTURE_DATABASE: AcupuncturePoint[];
};

function escapeCsv(value: unknown): string {
  if (value === null || value === undefined) return "";
  const str = String(value);
  // RFC4180-ish
  if (/[\n\r",]/.test(str)) return `"${str.replace(/"/g, '""')}"`;
  return str;
}

function arrayToCsvCell(arr?: unknown[]): string {
  if (!arr || !Array.isArray(arr)) return "";
  return arr.map((v) => String(v)).join("; ");
}

function generateWhoMeridianExports(): Plugin {
  async function loadPointsFromTypescript(): Promise<AcupuncturePoint[]> {
    // IMPORTANT:
    // Node cannot import .ts files directly in all environments. We bundle the TS entry
    // with esbuild to a single ESM module, then import it via a data: URL.
    const entry = path.resolve(__dirname, "./src/utils/meridianPoints/index.ts");

    const result = await build({
      entryPoints: [entry],
      bundle: true,
      platform: "node",
      format: "esm",
      target: "es2022",
      write: false,
      logLevel: "silent",
    });

    const output = result.outputFiles?.[0]?.text;
    if (!output) return [];

    const dataUrl = `data:text/javascript;base64,${Buffer.from(output).toString(
      "base64"
    )}`;
    const mod = (await import(dataUrl)) as MeridianPointsModule;
    return mod.COMPLETE_ACUPUNCTURE_DATABASE;
  }

  async function generateFiles(logger?: { info: (m: string) => void; warn: (m: string) => void }) {
    const logInfo = (m: string) => logger?.info?.(m);
    const logWarn = (m: string) => logger?.warn?.(m);

    const exportsDir = path.resolve(__dirname, "./public/exports");
    await mkdir(exportsDir, { recursive: true });

    const points = await loadPointsFromTypescript();

    if (!Array.isArray(points) || points.length === 0) {
      logWarn?.(
        "WHO export generation skipped: COMPLETE_ACUPUNCTURE_DATABASE is empty or not an array."
      );
      return;
    }

    const jsonPath = path.join(exportsDir, "who-meridian-points.json");
    await writeFile(jsonPath, JSON.stringify(points, null, 2), "utf8");

    const headers = [
      "id",
      "nameChinese",
      "nameEnglish",
      "nameGerman",
      "meridian",
      "element",
      "location",
      "depth",
      "frequency",
      "harmonicFrequencies",
      "pointTypes",
      "functions",
      "indications",
      "precautions",
      "chakraCorrespondence",
    ];

    const csvLines: string[] = [];
    csvLines.push(headers.join(","));
    for (const p of points) {
      csvLines.push(
        [
          escapeCsv(p.id),
          escapeCsv(p.nameChinese),
          escapeCsv(p.nameEnglish),
          escapeCsv(p.nameGerman),
          escapeCsv(p.meridian),
          escapeCsv(p.element),
          escapeCsv(p.location),
          escapeCsv(p.depth),
          escapeCsv(p.frequency),
          escapeCsv(arrayToCsvCell(p.harmonicFrequencies)),
          escapeCsv(arrayToCsvCell(p.pointTypes)),
          escapeCsv(arrayToCsvCell(p.functions)),
          escapeCsv(arrayToCsvCell(p.indications)),
          escapeCsv(arrayToCsvCell(p.precautions)),
          escapeCsv(p.chakraCorrespondence),
        ].join(",")
      );
    }

    const csvPath = path.join(exportsDir, "who-meridian-points.csv");
    await writeFile(csvPath, csvLines.join("\n"), "utf8");

    logInfo?.(
      `Generated WHO meridian exports: public/exports/who-meridian-points.json and public/exports/who-meridian-points.csv (${points.length} points)`
    );
  }

  return {
    name: "generate-who-meridian-exports",
    async configureServer(server) {
      // Ensure exports exist in dev/preview too (not only in production build).
      try {
        await generateFiles(server.config.logger);
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        server.config.logger.warn(
          `WHO export generation failed in dev (non-fatal): ${message}`
        );
      }
    },
    async buildStart() {
      try {
        await generateFiles(this);
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        this.warn(
          `WHO export generation failed (non-fatal): ${message}. The app will still run.`
        );
      }
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [generateWhoMeridianExports(), react(), mode === "development" && componentTagger()].filter(
    Boolean
  ),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
