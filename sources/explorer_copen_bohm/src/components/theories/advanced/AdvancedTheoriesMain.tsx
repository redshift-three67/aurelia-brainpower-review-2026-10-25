import { useState } from "react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

import HolographicUniverse from "./HolographicUniverse";
import QuantentheorieAdvanced from "./QuantentheorieAdvanced";
import TeslaTechnologies from "./TeslaTechnologies";
import RoyalRifeMachine from "./RoyalRifeMachine";
import LakhovskyMultiwave from "./LakhovskyMultiwave";
import RadiationDetox from "./RadiationDetox";
import ElectroMetaboGraph from "./ElectroMetaboGraph";
import TheoriesCommonalities from "./TheoriesCommonalities";

const AdvancedTheoriesMain = () => {
  const [activeSection, setActiveSection] = useState("holographicUniverse");

  const sections = [
    { id: "holographicUniverse", label: "Holographisches Universum", component: HolographicUniverse },
    { id: "quantentheorie", label: "Quantentheorie Advanced", component: QuantentheorieAdvanced },
    { id: "teslatech", label: "Tesla-Technologien", component: TeslaTechnologies },
    { id: "rifemachine", label: "Royal Rife Machine", component: RoyalRifeMachine },
    { id: "lakhovskyMWO", label: "Lakhovsky MWO", component: LakhovskyMultiwave },
    { id: "radiationDetox", label: "Strahlung Detox 5G/6G", component: RadiationDetox },
    { id: "electrometabo", label: "Elektro-Metabolograph", component: ElectroMetaboGraph },
    { id: "commonalities", label: "Gemeinsamkeiten & Konsolidierung", component: TheoriesCommonalities }
  ];

  return (
    <div className="flex h-full w-full space-x-2">
      <Card className="w-64 flex-none">
        <CardHeader>
          <CardTitle>Theorien</CardTitle>
        </CardHeader>
        <ScrollArea className="h-[calc(100vh-8rem)] px-2">
          <div className="flex flex-col space-y-1">
            {sections.map((section) => (
              <button
                key={section.id}
                className={`flex items-center justify-start rounded-md px-2 py-1.5 text-sm font-medium hover:bg-secondary hover:text-secondary-foreground focus:bg-secondary focus:text-secondary-foreground ${
                  activeSection === section.id ? "bg-secondary text-secondary-foreground" : "text-muted-foreground"
                }`}
                onClick={() => setActiveSection(section.id)}
              >
                {section.label}
              </button>
            ))}
          </div>
        </ScrollArea>
      </Card>
      <Separator orientation="vertical" />
      <div className="flex-1 overflow-y-auto">
        {sections.map(
          (section) =>
            activeSection === section.id && (
              <section.component key={section.id} />
            )
        )}
      </div>
    </div>
  );
};

export default AdvancedTheoriesMain;
