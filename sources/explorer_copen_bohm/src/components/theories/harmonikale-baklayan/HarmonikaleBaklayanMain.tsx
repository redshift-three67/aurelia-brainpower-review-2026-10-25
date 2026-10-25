
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import HarmonikaleFrequenzlehre from "./HarmonikaleFrequenzlehre";
import MusikalischeTherapie from "./MusikalischeTherapie";
import BehandlungsstrategienProtokoll from "./BehandlungsstrategienProtokoll";
import MeridianpunktFrequenzen from "./MeridianpunktFrequenzen";
import ChakraHarmonikaleFrequenzen from "./ChakraHarmonikaleFrequenzen";

const HarmonikaleBaklayanMain = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-4xl text-center text-white">
            Harmonikale Frequenztherapie nach Alan E. Baklayan
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Umfassendes Kompendium der Musikalischen Harmonielehre in der Frequenzmedizin
          </p>
        </CardHeader>
      </Card>

      <Tabs defaultValue="grundlagen" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 bg-white/10 border-white/20">
          <TabsTrigger value="grundlagen" className="text-white data-[state=active]:bg-white/20">
            Harmonikale Grundlagen
          </TabsTrigger>
          <TabsTrigger value="therapie" className="text-white data-[state=active]:bg-white/20">
            Musikalische Therapie
          </TabsTrigger>
          <TabsTrigger value="behandlung" className="text-white data-[state=active]:bg-white/20">
            Behandlungsstrategien
          </TabsTrigger>
          <TabsTrigger value="meridianpunkte" className="text-white data-[state=active]:bg-white/20">
            Meridianpunkt-Frequenzen
          </TabsTrigger>
          <TabsTrigger value="chakren" className="text-white data-[state=active]:bg-white/20">
            Chakra-Frequenzen
          </TabsTrigger>
        </TabsList>

        <TabsContent value="grundlagen">
          <HarmonikaleFrequenzlehre />
        </TabsContent>

        <TabsContent value="therapie">
          <MusikalischeTherapie />
        </TabsContent>

        <TabsContent value="behandlung">
          <BehandlungsstrategienProtokoll />
        </TabsContent>

        <TabsContent value="meridianpunkte">
          <MeridianpunktFrequenzen />
        </TabsContent>

        <TabsContent value="chakren">
          <ChakraHarmonikaleFrequenzen />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default HarmonikaleBaklayanMain;
