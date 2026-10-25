import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface ClientVector {
  physical: number;
  emotional: number;
  stress: number;
  energy: number;
  mental: number;
}

interface MeridianImbalance {
  meridianId: string;
  meridianName: string;
  element: string;
  yinYang: string;
  imbalanceScore: number;
  imbalanceType: 'excess' | 'deficiency' | 'stagnation';
  affectedOrgan: string;
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { clientVector, imbalances } = await req.json() as {
      clientVector: ClientVector;
      imbalances: MeridianImbalance[];
    };

    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY is not configured");
    }

    // Erstelle einen detaillierten Kontext für die KI
    const vectorDescription = `
    Klient-Vektor-Analyse:
    - Physische Dimension: ${(clientVector.physical * 100).toFixed(0)}% (${clientVector.physical > 0 ? 'Yang-Überschuss' : 'Yin-Mangel'})
    - Emotionale Dimension: ${(clientVector.emotional * 100).toFixed(0)}% (${clientVector.emotional > 0 ? 'aufsteigende Emotion' : 'unterdrückte Emotion'})
    - Stress-Level: ${(Math.abs(clientVector.stress) * 100).toFixed(0)}%
    - Energie-Level: ${(clientVector.energy * 100).toFixed(0)}% (${clientVector.energy > 0 ? 'Überfülle' : 'Erschöpfung'})
    - Mentale Klarheit: ${(clientVector.mental * 100).toFixed(0)}%
    `;

    const imbalancesList = imbalances
      .slice(0, 5)
      .map((m, i) => `${i + 1}. ${m.meridianName} (${m.element}/${m.yinYang}): ${m.imbalanceType} - Score: ${(m.imbalanceScore * 100).toFixed(0)}%`)
      .join('\n');

    const systemPrompt = `Du bist ein erfahrener TCM-Diagnostiker und Energiemedizin-Spezialist. 
Du analysierst Meridian-Imbalancen basierend auf biometrischen Vektordaten und gibst präzise, 
aber verständliche Behandlungsempfehlungen. Antworte auf Deutsch.

Beachte die Fünf-Elemente-Lehre (Wu Xing) und deren Wechselwirkungen:
- Holz (Leber/Gallenblase) nährt Feuer, kontrolliert Erde
- Feuer (Herz/Dünndarm) nährt Erde, kontrolliert Metall
- Erde (Milz/Magen) nährt Metall, kontrolliert Wasser
- Metall (Lunge/Dickdarm) nährt Wasser, kontrolliert Holz
- Wasser (Niere/Blase) nährt Holz, kontrolliert Feuer

Gib konkrete, umsetzbare Empfehlungen für:
1. Primäre Akupunkturpunkte zur Behandlung
2. Unterstützende Frequenzen (basierend auf den Meridian-Frequenzen)
3. Ergänzende Maßnahmen (Ernährung, Qigong, Lifestyle)`;

    const userPrompt = `Analysiere folgende Meridian-Diagnose und erstelle einen Behandlungsplan:

${vectorDescription}

Identifizierte Meridian-Imbalancen (nach Schweregrad):
${imbalancesList}

Bitte erstelle eine strukturierte Analyse mit:
1. **Hauptdiagnose**: Was ist das zentrale energetische Muster?
2. **Betroffene Elemente**: Welche Wu-Xing-Dynamiken sind gestört?
3. **Prioritäre Behandlungspunkte**: Die 3-5 wichtigsten Akupunkturpunkte mit Begründung
4. **Frequenz-Empfehlungen**: Welche Frequenzen sollten angewendet werden?
5. **Harmonisierungssequenz**: In welcher Reihenfolge behandeln?
6. **Ergänzende Maßnahmen**: Lifestyle, Ernährung, Übungen`;

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
        stream: true,
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(
          JSON.stringify({ error: "Rate-Limit erreicht. Bitte versuchen Sie es später erneut." }),
          { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
      if (response.status === 402) {
        return new Response(
          JSON.stringify({ error: "Guthaben erschöpft. Bitte laden Sie Ihr Konto auf." }),
          { status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
      const errorText = await response.text();
      console.error("AI Gateway Error:", response.status, errorText);
      return new Response(
        JSON.stringify({ error: "KI-Gateway-Fehler" }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Stream die Antwort zurück
    return new Response(response.body, {
      headers: { ...corsHeaders, "Content-Type": "text/event-stream" },
    });

  } catch (error) {
    console.error("Meridian diagnosis error:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unbekannter Fehler" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
