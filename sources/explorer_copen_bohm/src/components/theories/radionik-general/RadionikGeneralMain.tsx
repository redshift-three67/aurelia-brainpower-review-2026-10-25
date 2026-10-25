
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RadionikGrundlagen from "./RadionikGrundlagen";
import GeraeteUndTechnologie from "./GeraeteUndTechnologie";
import RatenSysteme from "./RatenSysteme";
import DiagnoseVerfahren from "./DiagnoseVerfahren";
import TherapieProtokolle from "./TherapieProtokolle";

const RadionikGeneralMain = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="bg-white/10 border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-4xl text-center text-white">
            Allgemeine Radionik-Prinzipien
          </CardTitle>
          <p className="text-center text-blue-200 text-lg">
            Fundamentale Grundlagen der Radionischen Analyse und Behandlung
          </p>
        </CardHeader>
      </Card>

      <Tabs defaultValue="grundlagen" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 bg-white/10 border-white/20">
          <TabsTrigger value="grundlagen" className="text-white data-[state=active]:bg-white/20">
            Radionik-Grundlagen
          </TabsTrigger>
          <TabsTrigger value="geraete" className="text-white data-[state=active]:bg-white/20">
            Geräte & Technologie
          </TabsTrigger>
          <TabsTrigger value="raten" className="text-white data-[state=active]:bg-white/20">
            Raten-Systeme
          </TabsTrigger>
          <TabsTrigger value="diagnose" className="text-white data-[state=active]:bg-white/20">
            Diagnose-Verfahren
          </TabsTrigger>
          <TabsTrigger value="therapie" className="text-white data-[state=active]:bg-white/20">
            Therapie-Protokolle
          </TabsTrigger>
        </TabsList>

        <TabsContent value="grundlagen">
          <RadionikGrundlagen />
        </TabsContent>

        <TabsContent value="geraete">
          <GeraeteUndTechnologie />
        </TabsContent>

        <TabsContent value="raten">
          <RatenSysteme />
        </TabsContent>

        <TabsContent value="diagnose">
          <DiagnoseVerfahren />
        </TabsContent>

        <TabsContent value="therapie">
          <TherapieProtokolle />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default RadionikGeneralMain;
