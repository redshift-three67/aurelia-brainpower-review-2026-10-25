import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Zap, Clock, Microscope, Cpu, Waves } from "lucide-react";
import KozyrevGrundlagen from "./KozyrevGrundlagen";
import KozyrevSpiegel from "./KozyrevSpiegel";
import KozyrevDioden from "./KozyrevDioden";
import KozyrevComputerhardware from "./KozyrevComputerhardware";
import KozyrevMorphogenetischesFeld from "./KozyrevMorphogenetischesFeld";

const KozyrevDiodenMain = () => {
  return (
    <Card className="w-full">
      <CardHeader className="text-center">
        <div className="flex items-center justify-center mb-4">
          <Clock className="h-12 w-12 text-primary animate-pulse" />
        </div>
        <CardTitle className="text-3xl bg-gradient-to-r from-primary via-primary/80 to-primary bg-clip-text text-transparent">
          Kozyrev-Dioden & Zeitenergie
        </CardTitle>
        <CardDescription className="text-lg">
          Zeitfluss als Energiequelle • Morphogenetische Feldeffekte • Quantencomputer-Integration
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="grundlagen" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="grundlagen" className="flex items-center gap-2">
              <Microscope className="h-4 w-4" />
              Grundlagen
            </TabsTrigger>
            <TabsTrigger value="spiegel" className="flex items-center gap-2">
              <Waves className="h-4 w-4" />
              Spiegel
            </TabsTrigger>
            <TabsTrigger value="dioden" className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Dioden
            </TabsTrigger>
            <TabsTrigger value="hardware" className="flex items-center gap-2">
              <Cpu className="h-4 w-4" />
              Hardware
            </TabsTrigger>
            <TabsTrigger value="feld" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Morpho-Feld
            </TabsTrigger>
          </TabsList>

          <div className="mt-6">
            <TabsContent value="grundlagen">
              <KozyrevGrundlagen />
            </TabsContent>
            
            <TabsContent value="spiegel">
              <KozyrevSpiegel />
            </TabsContent>
            
            <TabsContent value="dioden">
              <KozyrevDioden />
            </TabsContent>
            
            <TabsContent value="hardware">
              <KozyrevComputerhardware />
            </TabsContent>
            
            <TabsContent value="feld">
              <KozyrevMorphogenetischesFeld />
            </TabsContent>
          </div>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default KozyrevDiodenMain;
