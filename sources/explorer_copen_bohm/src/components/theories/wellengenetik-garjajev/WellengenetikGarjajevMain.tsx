
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import WellengenetikGrundlagen from "./WellengenetikGrundlagen";
import QuantenbiologieAnwendung from "./QuantenbiologieAnwendung";

const WellengenetikGarjajevMain = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-4xl text-center text-white">
            Wellengenetik nach Dr. Peter Garjajev
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            DNA als Quanteninformationsspeicher und Wellenantenne
          </p>
        </CardHeader>
      </Card>

      <Tabs defaultValue="grundlagen" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2 bg-white/10 border-white/20">
          <TabsTrigger value="grundlagen" className="text-white data-[state=active]:bg-white/20">
            Wellengenetik-Grundlagen
          </TabsTrigger>
          <TabsTrigger value="anwendung" className="text-white data-[state=active]:bg-white/20">
            Quantenbiologie-Anwendung
          </TabsTrigger>
        </TabsList>

        <TabsContent value="grundlagen">
          <WellengenetikGrundlagen />
        </TabsContent>

        <TabsContent value="anwendung">
          <QuantenbiologieAnwendung />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default WellengenetikGarjajevMain;
