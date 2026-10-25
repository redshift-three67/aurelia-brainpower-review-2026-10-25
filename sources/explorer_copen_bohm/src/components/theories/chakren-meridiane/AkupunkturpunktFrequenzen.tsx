
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const AkupunkturpunktFrequenzen = () => {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl text-center text-blue-800">
            Punkt-spezifische Frequenzen der Hauptakupunkturpunkte
          </CardTitle>
        </CardHeader>
        <CardContent className="prose prose-lg max-w-none">
          
          <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">Berechnungsgrundlagen für Punkt-Frequenzen</h3>

          <div className="bg-slate-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold text-gray-800 mb-2">Punkt-spezifische Parameter:</h4>
            <div className="bg-white p-3 rounded border-l-4 border-slate-400 my-3">
              <strong>Punkt-spezifische Parameter:</strong><br/>
              Z_punkt = R_punkt + j(ωL_punkt - 1/(ωC_punkt))<br/>
              R_punkt = Gewebewiderstand am Punkt (50-500 Ω)<br/>
              L_punkt = Induktivität durch Gewebestruktur (0,1-2 μH)<br/>
              C_punkt = Kapazität der Punktumgebung (1-10 nF)<br/><br/>
              <strong>Resonanzfrequenz-Formel:</strong><br/>
              f_punkt = 1/(2π√(L_punkt × C_punkt))<br/><br/>
              <strong>Harmonische Beziehung zum Meridian:</strong><br/>
              f_punkt = f_meridian × n ± Δf_spezifisch<br/>
              n = ganzzahlige Harmonische (1-50)<br/>
              Δf_spezifisch = funktionsspezifische Abweichung
            </div>
          </div>

          <Separator className="my-6" />

          <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">Vollständige Punkt-Frequenz-Tabelle aller Hauptmeridiane</h3>

          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold text-gray-800 mb-4">Hauptakupunkturpunkte mit berechneten Frequenzen:</h4>
            <div className="bg-white p-3 rounded border-l-4 border-gray-400 my-3">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-20">Punkt</TableHead>
                    <TableHead className="w-32">Name (Deutsch)</TableHead>
                    <TableHead className="w-32">Name (Chinesisch)</TableHead>
                    <TableHead className="w-24">Frequenz (Hz)</TableHead>
                    <TableHead className="w-20">Harmonische</TableHead>
                    <TableHead className="w-24">Aktive Zeit</TableHead>
                    <TableHead>Hauptwirkung</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {/* Lungen-Meridian (LU) */}
                  <TableRow className="bg-red-50">
                    <TableCell className="font-semibold">LU-1</TableCell>
                    <TableCell>Mittlerer Palast</TableCell>
                    <TableCell>Zhongfu</TableCell>
                    <TableCell>23,2</TableCell>
                    <TableCell>4×5,8</TableCell>
                    <TableCell>03-05h</TableCell>
                    <TableCell>Atemwege, Husten</TableCell>
                  </TableRow>
                  <TableRow className="bg-red-50">
                    <TableCell className="font-semibold">LU-5</TableCell>
                    <TableCell>Handlungsort</TableCell>
                    <TableCell>Chize</TableCell>
                    <TableCell>29,0</TableCell>
                    <TableCell>5×5,8</TableCell>
                    <TableCell>03-05h</TableCell>
                    <TableCell>Fieber, Ellenbogenschmerz</TableCell>
                  </TableRow>
                  <TableRow className="bg-red-50">
                    <TableCell className="font-semibold">LU-9</TableCell>
                    <TableCell>Große Tiefe</TableCell>
                    <TableCell>Taiyuan</TableCell>
                    <TableCell>34,8</TableCell>
                    <TableCell>6×5,8</TableCell>
                    <TableCell>03-05h</TableCell>
                    <TableCell>Puls-Regulation, Yuan-Punkt</TableCell>
                  </TableRow>
                  <TableRow className="bg-red-50">
                    <TableCell className="font-semibold">LU-11</TableCell>
                    <TableCell>Kleiner Kaufmann</TableCell>
                    <TableCell>Shaoshang</TableCell>
                    <TableCell>46,4</TableCell>
                    <TableCell>8×5,8</TableCell>
                    <TableCell>03-05h</TableCell>
                    <TableCell>Halsschmerzen, Notfall</TableCell>
                  </TableRow>

                  {/* Dickdarm-Meridian (DI) */}
                  <TableRow className="bg-purple-50">
                    <TableCell className="font-semibold">DI-1</TableCell>
                    <TableCell>Kaufmann Yang</TableCell>
                    <TableCell>Shangyang</TableCell>
                    <TableCell>25,2</TableCell>
                    <TableCell>6×4,2</TableCell>
                    <TableCell>05-07h</TableCell>
                    <TableCell>Zahnschmerzen, Bewusstsein</TableCell>
                  </TableRow>
                  <TableRow className="bg-purple-50">
                    <TableCell className="font-semibold">DI-4</TableCell>
                    <TableCell>Vereinte Täler</TableCell>
                    <TableCell>Hegu</TableCell>
                    <TableCell>42,0</TableCell>
                    <TableCell>10×4,2</TableCell>
                    <TableCell>05-07h</TableCell>
                    <TableCell>Universeller Schmerz-Punkt</TableCell>
                  </TableRow>
                  <TableRow className="bg-purple-50">
                    <TableCell className="font-semibold">DI-11</TableCell>
                    <TableCell>Gekrümmter Teich</TableCell>
                    <TableCell>Quchi</TableCell>
                    <TableCell>50,4</TableCell>
                    <TableCell>12×4,2</TableCell>
                    <TableCell>05-07h</TableCell>
                    <TableCell>Fieber, Hypertonie</TableCell>
                  </TableRow>
                  <TableRow className="bg-purple-50">
                    <TableCell className="font-semibold">DI-20</TableCell>
                    <TableCell>Duftender Empfang</TableCell>
                    <TableCell>Yingxiang</TableCell>
                    <TableCell>63,0</TableCell>
                    <TableCell>15×4,2</TableCell>
                    <TableCell>05-07h</TableCell>
                    <TableCell>Nasenverstopfung, Sinusitis</TableCell>
                  </TableRow>

                  {/* Magen-Meridian (ST) */}
                  <TableRow className="bg-green-50">
                    <TableCell className="font-semibold">ST-1</TableCell>
                    <TableCell>Tränen-Behälter</TableCell>
                    <TableCell>Chengqi</TableCell>
                    <TableCell>19,8</TableCell>
                    <TableCell>2×9,9</TableCell>
                    <TableCell>07-09h</TableCell>
                    <TableCell>Augenleiden, Tränenfluss</TableCell>
                  </TableRow>
                  <TableRow className="bg-green-50">
                    <TableCell className="font-semibold">ST-6</TableCell>
                    <TableCell>Wagen-Knochen</TableCell>
                    <TableCell>Jiache</TableCell>
                    <TableCell>39,6</TableCell>
                    <TableCell>4×9,9</TableCell>
                    <TableCell>07-09h</TableCell>
                    <TableCell>Kiefergelenk, Bruxismus</TableCell>
                  </TableRow>
                  <TableRow className="bg-green-50">
                    <TableCell className="font-semibold">ST-25</TableCell>
                    <TableCell>Himmelsdrehpunkt</TableCell>
                    <TableCell>Tianshu</TableCell>
                    <TableCell>69,3</TableCell>
                    <TableCell>7×9,9</TableCell>
                    <TableCell>07-09h</TableCell>
                    <TableCell>Durchfall, Verstopfung</TableCell>
                  </TableRow>
                  <TableRow className="bg-green-50">
                    <TableCell className="font-semibold">ST-36</TableCell>
                    <TableCell>Drei Li vom Knie</TableCell>
                    <TableCell>Zusanli</TableCell>
                    <TableCell>99,0</TableCell>
                    <TableCell>10×9,9</TableCell>
                    <TableCell>07-09h</TableCell>
                    <TableCell>Universelles Tonikum</TableCell>
                  </TableRow>

                  {/* Milz-Pankreas-Meridian (MP) */}
                  <TableRow className="bg-yellow-50">
                    <TableCell className="font-semibold">MP-1</TableCell>
                    <TableCell>Verstecktes Weiß</TableCell>
                    <TableCell>Yinbai</TableCell>
                    <TableCell>16,2</TableCell>
                    <TableCell>2×8,1</TableCell>
                    <TableCell>09-11h</TableCell>
                    <TableCell>Menstruationsstörungen</TableCell>
                  </TableRow>
                  <TableRow className="bg-yellow-50">
                    <TableCell className="font-semibold">MP-3</TableCell>
                    <TableCell>Großer Weiß</TableCell>
                    <TableCell>Taibai</TableCell>
                    <TableCell>24,3</TableCell>
                    <TableCell>3×8,1</TableCell>
                    <TableCell>09-11h</TableCell>
                    <TableCell>Verdauung, Yuan-Punkt</TableCell>
                  </TableRow>
                  <TableRow className="bg-yellow-50">
                    <TableCell className="font-semibold">MP-6</TableCell>
                    <TableCell>Drei Yin-Kreuzung</TableCell>
                    <TableCell>Sanyinjiao</TableCell>
                    <TableCell>72,9</TableCell>
                    <TableCell>9×8,1</TableCell>
                    <TableCell>09-11h</TableCell>
                    <TableCell>Gynäkologie, Fertilität</TableCell>
                  </TableRow>
                  <TableRow className="bg-yellow-50">
                    <TableCell className="font-semibold">MP-21</TableCell>
                    <TableCell>Großer Umhang</TableCell>
                    <TableCell>Dabao</TableCell>
                    <TableCell>89,1</TableCell>
                    <TableCell>11×8,1</TableCell>
                    <TableCell>09-11h</TableCell>
                    <TableCell>Thoraxschmerzen, Asthma</TableCell>
                  </TableRow>

                  {/* Herz-Meridian (HE) */}
                  <TableRow className="bg-orange-50">
                    <TableCell className="font-semibold">HE-1</TableCell>
                    <TableCell>Höchste Quelle</TableCell>
                    <TableCell>Jiquan</TableCell>
                    <TableCell>13,8</TableCell>
                    <TableCell>2×6,9</TableCell>
                    <TableCell>11-13h</TableCell>
                    <TableCell>Herzrhythmus, Angina</TableCell>
                  </TableRow>
                  <TableRow className="bg-orange-50">
                    <TableCell className="font-semibold">HE-5</TableCell>
                    <TableCell>Geist-Verbindung</TableCell>
                    <TableCell>Tongli</TableCell>
                    <TableCell>34,5</TableCell>
                    <TableCell>5×6,9</TableCell>
                    <TableCell>11-13h</TableCell>
                    <TableCell>Sprachstörungen, Stottern</TableCell>
                  </TableRow>
                  <TableRow className="bg-orange-50">
                    <TableCell className="font-semibold">HE-7</TableCell>
                    <TableCell>Geist-Tor</TableCell>
                    <TableCell>Shenmen</TableCell>
                    <TableCell>48,3</TableCell>
                    <TableCell>7×6,9</TableCell>
                    <TableCell>11-13h</TableCell>
                    <TableCell>Angst, Schlaflosigkeit</TableCell>
                  </TableRow>
                  <TableRow className="bg-orange-50">
                    <TableCell className="font-semibold">HE-9</TableCell>
                    <TableCell>Kleiner Ansturm</TableCell>
                    <TableCell>Shaochong</TableCell>
                    <TableCell>55,2</TableCell>
                    <TableCell>8×6,9</TableCell>
                    <TableCell>11-13h</TableCell>
                    <TableCell>Bewusstlosigkeit, Schock</TableCell>
                  </TableRow>

                  {/* Dünndarm-Meridian (SI) */}
                  <TableRow className="bg-blue-50">
                    <TableCell className="font-semibold">SI-1</TableCell>
                    <TableCell>Kleine Meerenge</TableCell>
                    <TableCell>Shaoze</TableCell>
                    <TableCell>27,6</TableCell>
                    <TableCell>2×13,8</TableCell>
                    <TableCell>13-15h</TableCell>
                    <TableCell>Laktationsstörungen</TableCell>
                  </TableRow>
                  <TableRow className="bg-blue-50">
                    <TableCell className="font-semibold">SI-3</TableCell>
                    <TableCell>Hinterer Bach</TableCell>
                    <TableCell>Houxi</TableCell>
                    <TableCell>41,4</TableCell>
                    <TableCell>3×13,8</TableCell>
                    <TableCell>13-15h</TableCell>
                    <TableCell>Nackenverspannungen</TableCell>
                  </TableRow>
                  <TableRow className="bg-blue-50">
                    <TableCell className="font-semibold">SI-11</TableCell>
                    <TableCell>Himmlische Versammlung</TableCell>
                    <TableCell>Tianzong</TableCell>
                    <TableCell>96,6</TableCell>
                    <TableCell>7×13,8</TableCell>
                    <TableCell>13-15h</TableCell>
                    <TableCell>Schulterschmerzen</TableCell>
                  </TableRow>
                  <TableRow className="bg-blue-50">
                    <TableCell className="font-semibold">SI-19</TableCell>
                    <TableCell>Palast des Hörens</TableCell>
                    <TableCell>Tinggong</TableCell>
                    <TableCell>124,2</TableCell>
                    <TableCell>9×13,8</TableCell>
                    <TableCell>13-15h</TableCell>
                    <TableCell>Tinnitus, Schwerhörigkeit</TableCell>
                  </TableRow>

                  {/* Blasen-Meridian (BL) */}
                  <TableRow className="bg-indigo-50">
                    <TableCell className="font-semibold">BL-1</TableCell>
                    <TableCell>Helles Licht</TableCell>
                    <TableCell>Jingming</TableCell>
                    <TableCell>7,0</TableCell>
                    <TableCell>2×3,5</TableCell>
                    <TableCell>15-17h</TableCell>
                    <TableCell>Augenerkrankungen</TableCell>
                  </TableRow>
                  <TableRow className="bg-indigo-50">
                    <TableCell className="font-semibold">BL-2</TableCell>
                    <TableCell>Bambus-Versammlung</TableCell>
                    <TableCell>Zanzhu</TableCell>
                    <TableCell>10,5</TableCell>
                    <TableCell>3×3,5</TableCell>
                    <TableCell>15-17h</TableCell>
                    <TableCell>Kopfschmerzen, Migräne</TableCell>
                  </TableRow>
                  <TableRow className="bg-indigo-50">
                    <TableCell className="font-semibold">BL-23</TableCell>
                    <TableCell>Nieren-Shu</TableCell>
                    <TableCell>Shenshu</TableCell>
                    <TableCell>28,0</TableCell>
                    <TableCell>8×3,5</TableCell>
                    <TableCell>15-17h</TableCell>
                    <TableCell>Rückenschmerzen, Nieren</TableCell>
                  </TableRow>
                  <TableRow className="bg-indigo-50">
                    <TableCell className="font-semibold">BL-67</TableCell>
                    <TableCell>Extremes Yin</TableCell>
                    <TableCell>Zhiyin</TableCell>
                    <TableCell>45,5</TableCell>
                    <TableCell>13×3,5</TableCell>
                    <TableCell>15-17h</TableCell>
                    <TableCell>Beckenendlage, Geburt</TableCell>
                  </TableRow>

                  {/* Nieren-Meridian (KI) */}
                  <TableRow className="bg-teal-50">
                    <TableCell className="font-semibold">KI-1</TableCell>
                    <TableCell>Sprudelnde Quelle</TableCell>
                    <TableCell>Yongquan</TableCell>
                    <TableCell>19,5</TableCell>
                    <TableCell>3×6,5</TableCell>
                    <TableCell>17-19h</TableCell>
                    <TableCell>Erdung, Bluthochdruck</TableCell>
                  </TableRow>
                  <TableRow className="bg-teal-50">
                    <TableCell className="font-semibold">KI-3</TableCell>
                    <TableCell>Große Meerenge</TableCell>
                    <TableCell>Taixi</TableCell>
                    <TableCell>26,0</TableCell>
                    <TableCell>4×6,5</TableCell>
                    <TableCell>17-19h</TableCell>
                    <TableCell>Nieren-Stärkung, Yuan-Punkt</TableCell>
                  </TableRow>
                  <TableRow className="bg-teal-50">
                    <TableCell className="font-semibold">KI-7</TableCell>
                    <TableCell>Rückkehr des Stroms</TableCell>
                    <TableCell>Fuliu</TableCell>
                    <TableCell>45,5</TableCell>
                    <TableCell>7×6,5</TableCell>
                    <TableCell>17-19h</TableCell>
                    <TableCell>Schwitzen, Ödeme</TableCell>
                  </TableRow>
                  <TableRow className="bg-teal-50">
                    <TableCell className="font-semibold">KI-27</TableCell>
                    <TableCell>Elegantes Haus</TableCell>
                    <TableCell>Shufu</TableCell>
                    <TableCell>91,0</TableCell>
                    <TableCell>14×6,5</TableCell>
                    <TableCell>17-19h</TableCell>
                    <TableCell>Asthma, Husten</TableCell>
                  </TableRow>

                  {/* Perikard-Meridian (PE) */}
                  <TableRow className="bg-pink-50">
                    <TableCell className="font-semibold">PE-3</TableCell>
                    <TableCell>Gekrümmte Meerenge</TableCell>
                    <TableCell>Quze</TableCell>
                    <TableCell>21,6</TableCell>
                    <TableCell>3×7,2</TableCell>
                    <TableCell>19-21h</TableCell>
                    <TableCell>Herzrhythmusstörungen</TableCell>
                  </TableRow>
                  <TableRow className="bg-pink-50">
                    <TableCell className="font-semibold">PE-6</TableCell>
                    <TableCell>Innere Barriere</TableCell>
                    <TableCell>Neiguan</TableCell>
                    <TableCell>43,2</TableCell>
                    <TableCell>6×7,2</TableCell>
                    <TableCell>19-21h</TableCell>
                    <TableCell>Übelkeit, Motion Sickness</TableCell>
                  </TableRow>
                  <TableRow className="bg-pink-50">
                    <TableCell className="font-semibold">PE-7</TableCell>
                    <TableCell>Große Mauer</TableCell>
                    <TableCell>Daling</TableCell>
                    <TableCell>50,4</TableCell>
                    <TableCell>7×7,2</TableCell>
                    <TableCell>19-21h</TableCell>
                    <TableCell>Sedierung, Yuan-Punkt</TableCell>
                  </TableRow>
                  <TableRow className="bg-pink-50">
                    <TableCell className="font-semibold">PE-9</TableCell>
                    <TableCell>Mittlerer Ansturm</TableCell>
                    <TableCell>Zhongchong</TableCell>
                    <TableCell>57,6</TableCell>
                    <TableCell>8×7,2</TableCell>
                    <TableCell>19-21h</TableCell>
                    <TableCell>Bewusstlosigkeit, Schock</TableCell>
                  </TableRow>

                  {/* Drei-Erwärmer-Meridian (TE) */}
                  <TableRow className="bg-cyan-50">
                    <TableCell className="font-semibold">TE-1</TableCell>
                    <TableCell>Beziehung zum Ansturm</TableCell>
                    <TableCell>Guanchong</TableCell>
                    <TableCell>28,8</TableCell>
                    <TableCell>2×14,4</TableCell>
                    <TableCell>21-23h</TableCell>
                    <TableCell>Kopfschmerzen, Fieber</TableCell>
                  </TableRow>
                  <TableRow className="bg-cyan-50">
                    <TableCell className="font-semibold">TE-5</TableCell>
                    <TableCell>Äußere Barriere</TableCell>
                    <TableCell>Waiguan</TableCell>
                    <TableCell>72,0</TableCell>
                    <TableCell>5×14,4</TableCell>
                    <TableCell>21-23h</TableCell>
                    <TableCell>Erkältung, Immunsystem</TableCell>
                  </TableRow>
                  <TableRow className="bg-cyan-50">
                    <TableCell className="font-semibold">TE-17</TableCell>
                    <TableCell>Windschirm</TableCell>
                    <TableCell>Yifeng</TableCell>
                    <TableCell>115,2</TableCell>
                    <TableCell>8×14,4</TableCell>
                    <TableCell>21-23h</TableCell>
                    <TableCell>Tinnitus, Schwerhörigkeit</TableCell>
                  </TableRow>
                  <TableRow className="bg-cyan-50">
                    <TableCell className="font-semibold">TE-23</TableCell>
                    <TableCell>Seide-Bambus-Loch</TableCell>
                    <TableCell>Sizhukong</TableCell>
                    <TableCell>129,6</TableCell>
                    <TableCell>9×14,4</TableCell>
                    <TableCell>21-23h</TableCell>
                    <TableCell>Migräne, Augenschmerzen</TableCell>
                  </TableRow>

                  {/* Gallenblasen-Meridian (GB) */}
                  <TableRow className="bg-lime-50">
                    <TableCell className="font-semibold">GB-1</TableCell>
                    <TableCell>Augen-Pupille-Loch</TableCell>
                    <TableCell>Tongziliao</TableCell>
                    <TableCell>22,4</TableCell>
                    <TableCell>2×11,2</TableCell>
                    <TableCell>23-01h</TableCell>
                    <TableCell>Augenleiden, Kopfschmerz</TableCell>
                  </TableRow>
                  <TableRow className="bg-lime-50">
                    <TableCell className="font-semibold">GB-20</TableCell>
                    <TableCell>Windpool</TableCell>
                    <TableCell>Fengchi</TableCell>
                    <TableCell>67,2</TableCell>
                    <TableCell>6×11,2</TableCell>
                    <TableCell>23-01h</TableCell>
                    <TableCell>Nackenverspannungen</TableCell>
                  </TableRow>
                  <TableRow className="bg-lime-50">
                    <TableCell className="font-semibold">GB-34</TableCell>
                    <TableCell>Yang-Hügel-Quelle</TableCell>
                    <TableCell>Yanglingquan</TableCell>
                    <TableCell>89,6</TableCell>
                    <TableCell>8×11,2</TableCell>
                    <TableCell>23-01h</TableCell>
                    <TableCell>Muskel-Sehnen-Probleme</TableCell>
                  </TableRow>
                  <TableRow className="bg-lime-50">
                    <TableCell className="font-semibold">GB-44</TableCell>
                    <TableCell>Fuß-Qiao-Yin</TableCell>
                    <TableCell>Zuqiaoyin</TableCell>
                    <TableCell>100,8</TableCell>
                    <TableCell>9×11,2</TableCell>
                    <TableCell>23-01h</TableCell>
                    <TableCell>Migräne, Schlaflosigkeit</TableCell>
                  </TableRow>

                  {/* Leber-Meridian (LV) */}
                  <TableRow className="bg-emerald-50">
                    <TableCell className="font-semibold">LV-1</TableCell>
                    <TableCell>Großer Dicker</TableCell>
                    <TableCell>Dadun</TableCell>
                    <TableCell>32,4</TableCell>
                    <TableCell>2×16,2</TableCell>
                    <TableCell>01-03h</TableCell>
                    <TableCell>Menstruationsstörungen</TableCell>
                  </TableRow>
                  <TableRow className="bg-emerald-50">
                    <TableCell className="font-semibold">LV-3</TableCell>
                    <TableCell>Große Übersteigung</TableCell>
                    <TableCell>Taichong</TableCell>
                    <TableCell>48,6</TableCell>
                    <TableCell>3×16,2</TableCell>
                    <TableCell>01-03h</TableCell>
                    <TableCell>Stress, Hypertonie</TableCell>
                  </TableRow>
                  <TableRow className="bg-emerald-50">
                    <TableCell className="font-semibold">LV-8</TableCell>
                    <TableCell>Gekrümmte Quelle</TableCell>
                    <TableCell>Ququan</TableCell>
                    <TableCell>97,2</TableCell>
                    <TableCell>6×16,2</TableCell>
                    <TableCell>01-03h</TableCell>
                    <TableCell>Urogenitale Probleme</TableCell>
                  </TableRow>
                  <TableRow className="bg-emerald-50">
                    <TableCell className="font-semibold">LV-14</TableCell>
                    <TableCell>Periode-Tor</TableCell>
                    <TableCell>Qimen</TableCell>
                    <TableCell>113,4</TableCell>
                    <TableCell>7×16,2</TableCell>
                    <TableCell>01-03h</TableCell>
                    <TableCell>Leber-Qi-Stagnation</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </div>

          <Separator className="my-6" />

          <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">Besondere Punktkategorien</h3>

          <div className="bg-amber-50 p-4 rounded-lg mb-4">
            <h4 className="font-semibold text-gray-800 mb-2">Extra-Meridian-Punkte mit spezifischen Frequenzen:</h4>
            <div className="bg-white p-3 rounded border-l-4 border-amber-400 my-3">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Punkt</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Frequenz (Hz)</TableHead>
                    <TableHead>Berechnung</TableHead>
                    <TableHead>Hauptwirkung</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell className="font-semibold">DU-20</TableCell>
                    <TableCell>Baihui (Hundert Begegnungen)</TableCell>
                    <TableCell>40,0</TableCell>
                    <TableCell>Gamma-Wellen-Synchronisation</TableCell>
                    <TableCell>Bewusstsein, alle Yang-Meridiane</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-semibold">REN-17</TableCell>
                    <TableCell>Danzhong (Zentrum der Brust)</TableCell>
                    <TableCell>27,5</TableCell>
                    <TableCell>Yin-Meridian-Mittelwert</TableCell>
                    <TableCell>Emotionen, Atemwege</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-semibold">EX-HN5</TableCell>
                    <TableCell>Yintang (Siegelhalle)</TableCell>
                    <TableCell>35,8</TableCell>
                    <TableCell>3. Auge, Theta-Resonanz</TableCell>
                    <TableCell>Beruhigung, Klarheit</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-semibold">EX-LE10</TableCell>
                    <TableCell>Baxie (Acht Übel)</TableCell>
                    <TableCell>52,3</TableCell>
                    <TableCell>Hand-Gamma-Frequenz</TableCell>
                    <TableCell>Finger-Arthritis, Rheuma</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </div>

          <div className="bg-gray-100 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">Anwendungshinweise:</h4>
            <ul className="list-disc pl-6 space-y-1 text-sm">
              <li><strong>Frequenz-Toleranz:</strong> ±5% individueller Spielraum</li>
              <li><strong>Harmonische Wirkung:</strong> Ganzzahlige Vielfache verstärken die Wirkung</li>
              <li><strong>Zirkadiane Variation:</strong> Maximal-Wirkung zur angegebenen Organ-Zeit</li>
              <li><strong>Kombinationstherapie:</strong> Multiple Punkte können frequenz-moduliert werden</li>
              <li><strong>Messtechnik:</strong> EAV, Prognos oder Bioimpedanz-Geräte zur Validierung</li>
            </ul>
          </div>

        </CardContent>
      </Card>
    </div>
  );
};

export default AkupunkturpunktFrequenzen;
