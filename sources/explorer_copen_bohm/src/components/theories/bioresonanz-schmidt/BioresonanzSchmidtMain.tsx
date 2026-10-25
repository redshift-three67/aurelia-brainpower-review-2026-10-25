
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import GrundlagenUndTheorie from "./GrundlagenUndTheorie";
import FrequenzKompendium from "./FrequenzKompendium";
import PraktischeAnwendung from "./PraktischeAnwendung";
import GeraeteTechnologie from "./GeraeteTechnologie";
import WissenschaftlicheValidation from "./WissenschaftlicheValidation";

const BioresonanzSchmidtMain = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-4xl text-center text-white">
            Bioresonanz nach Paul Schmidt - Rayonex
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Wissenschaftliches Kompendium und praktische Anwendung
          </p>
        </CardHeader>
      </Card>

      <Tabs defaultValue="grundlagen" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 bg-white/10 border-white/20">
          <TabsTrigger value="grundlagen" className="text-white data-[state=active]:bg-white/20">
            Grundlagen
          </TabsTrigger>
          <TabsTrigger value="frequenzen" className="text-white data-[state=active]:bg-white/20">
            Frequenzen
          </TabsTrigger>
          <TabsTrigger value="anwendung" className="text-white data-[state=active]:bg-white/20">
            Anwendung
          </TabsTrigger>
          <TabsTrigger value="geraete" className="text-white data-[state=active]:bg-white/20">
            Geräte
          </TabsTrigger>
          <TabsTrigger value="validation" className="text-white data-[state=active]:bg-white/20">
            Studien
          </TabsTrigger>
        </TabsList>

        <TabsContent value="grundlagen">
          <GrundlagenUndTheorie />
        </TabsContent>

        <TabsContent value="frequenzen">
          <FrequenzKompendium />
        </TabsContent>

        <TabsContent value="anwendung">
          <PraktischeAnwendung />
        </TabsContent>

        <TabsContent value="geraete">
          <GeraeteTechnologie />
        </TabsContent>

        <TabsContent value="validation">
          <WissenschaftlicheValidation />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BioresonanzSchmidtMain;
