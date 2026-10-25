
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import CopenGrundlagen from "./CopenGrundlagen";
import CopenAlgorithmus from "./CopenAlgorithmus";
import CopenGeraete from "./CopenGeraete";
import CopenAnwendung from "./CopenAnwendung";
import CopenFrequenzen from "./CopenFrequenzen";

const RadionikCopenMain = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-4xl text-center text-white">
            Radionik nach Bruce Copen (1915-1998)
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Pionier der instrumentellen Radionik und Entwickler des authentischen Copen-Algorithmus
          </p>
        </CardHeader>
      </Card>

      <Tabs defaultValue="grundlagen" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 bg-white/10 border-white/20">
          <TabsTrigger value="grundlagen" className="text-white data-[state=active]:bg-white/20">
            Copen Grundlagen
          </TabsTrigger>
          <TabsTrigger value="algorithmus" className="text-white data-[state=active]:bg-white/20">
            Copen Algorithmus
          </TabsTrigger>
          <TabsTrigger value="geraete" className="text-white data-[state=active]:bg-white/20">
            Copen Geräte
          </TabsTrigger>
          <TabsTrigger value="anwendung" className="text-white data-[state=active]:bg-white/20">
            Praktische Anwendung
          </TabsTrigger>
          <TabsTrigger value="frequenzen" className="text-white data-[state=active]:bg-white/20">
            Copen Frequenzen
          </TabsTrigger>
        </TabsList>

        <TabsContent value="grundlagen">
          <CopenGrundlagen />
        </TabsContent>

        <TabsContent value="algorithmus">
          <CopenAlgorithmus />
        </TabsContent>

        <TabsContent value="geraete">
          <CopenGeraete />
        </TabsContent>

        <TabsContent value="anwendung">
          <CopenAnwendung />
        </TabsContent>

        <TabsContent value="frequenzen">
          <CopenFrequenzen />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RadionikCopenMain;
