
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import WissenschaftlicheGrundlagen from "./WissenschaftlicheGrundlagen";
import ChakraFrequenzen from "./ChakraFrequenzen";
import MeridianFrequenzen from "./MeridianFrequenzen";
import AkupunkturpunktFrequenzen from "./AkupunkturpunktFrequenzen";
import MesstechnikTherapie from "./MesstechnikTherapie";

const ChakrenMeridianeMain = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-4xl text-center text-white">
            Chakren-Meridian-Frequenztherapie
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Integrative Energiemedizin: Vereinigung von vedischen Chakren und chinesischen Meridianen
          </p>
        </CardHeader>
      </Card>

      <Tabs defaultValue="grundlagen" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 bg-white/10 border-white/20">
          <TabsTrigger value="grundlagen" className="text-white data-[state=active]:bg-white/20">
            Wissenschaftliche Grundlagen
          </TabsTrigger>
          <TabsTrigger value="chakren" className="text-white data-[state=active]:bg-white/20">
            Chakra-Frequenzen
          </TabsTrigger>
          <TabsTrigger value="meridiane" className="text-white data-[state=active]:bg-white/20">
            Meridian-Frequenzen
          </TabsTrigger>
          <TabsTrigger value="akupunktur" className="text-white data-[state=active]:bg-white/20">
            Akupunkturpunkt-Frequenzen
          </TabsTrigger>
          <TabsTrigger value="messtechnik" className="text-white data-[state=active]:bg-white/20">
            Messtechnik & Therapie
          </TabsTrigger>
        </TabsList>

        <TabsContent value="grundlagen">
          <WissenschaftlicheGrundlagen />
        </TabsContent>

        <TabsContent value="chakren">
          <ChakraFrequenzen />
        </TabsContent>

        <TabsContent value="meridiane">
          <MeridianFrequenzen />
        </TabsContent>

        <TabsContent value="akupunktur">
          <AkupunkturpunktFrequenzen />
        </TabsContent>

        <TabsContent value="messtechnik">
          <MesstechnikTherapie />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ChakrenMeridianeMain;
