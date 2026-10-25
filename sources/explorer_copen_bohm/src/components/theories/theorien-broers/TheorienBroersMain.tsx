
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import BroersGrundlagen from "./BroersGrundlagen";
import Bewusstseinsforschung from "./Bewusstseinsforschung";
import ElektromagnetischeFelder from "./ElektromagnetischeFelder";
import SolareBeeinflussung from "./SolareBeeinflussung";
import QuantenBewusstsein from "./QuantenBewusstsein";

const TheorienBroersMain = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-4xl text-center text-white">
            Theorien nach Dr. Dieter Broers
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Bewusstseinsforschung, Elektromagnetische Felder und Quantenphysik des Bewusstseins
          </p>
        </CardHeader>
      </Card>

      <Tabs defaultValue="grundlagen" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 bg-white/10 border-white/20">
          <TabsTrigger value="grundlagen" className="text-white data-[state=active]:bg-white/20">
            Broers Grundlagen
          </TabsTrigger>
          <TabsTrigger value="bewusstsein" className="text-white data-[state=active]:bg-white/20">
            Bewusstseinsforschung
          </TabsTrigger>
          <TabsTrigger value="felder" className="text-white data-[state=active]:bg-white/20">
            Elektromagnetische Felder
          </TabsTrigger>
          <TabsTrigger value="solar" className="text-white data-[state=active]:bg-white/20">
            Solare Beeinflussung
          </TabsTrigger>
          <TabsTrigger value="quanten" className="text-white data-[state=active]:bg-white/20">
            Quanten-Bewusstsein
          </TabsTrigger>
        </TabsList>

        <TabsContent value="grundlagen">
          <BroersGrundlagen />
        </TabsContent>

        <TabsContent value="bewusstsein">
          <Bewusstseinsforschung />
        </TabsContent>

        <TabsContent value="felder">
          <ElektromagnetischeFelder />
        </TabsContent>

        <TabsContent value="solar">
          <SolareBeeinflussung />
        </TabsContent>

        <TabsContent value="quanten">
          <QuantenBewusstsein />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TheorienBroersMain;
