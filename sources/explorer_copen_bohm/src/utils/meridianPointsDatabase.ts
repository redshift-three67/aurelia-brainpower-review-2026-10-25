/**
 * Vollständige WHO-Standard Meridianpunkt-Datenbank
 * 361 klassische Akupunkturpunkte nach WHO-Nomenklatur
 * Quelle: WHO Standard Acupuncture Nomenclature (1991/2014)
 * Zusätzlich mit Extrapunkten erweitert
 */

export interface MeridianPoint {
  id: string;          // z.B. "LU-1" nach WHO-Standard
  nameChinese: string; // Pinyin-Transliteration
  nameGerman: string;  // Deutsche Übersetzung
  frequencyHz: number; // Resonanzfrequenz in Hz
  activeTime: string;  // z.B. "03-05h"
  mainEffect: string;  // Hauptwirkung
  element?: string;    // TCM Element
  chineseCharacter?: string; // Chinesische Schriftzeichen
}

export interface Meridian {
  id: string;
  name: string;
  nameGerman: string;
  element: string;
  activeTime: string;
  color: string;
  totalPoints: number;
  points: MeridianPoint[];
}

// Frequenz-Berechnungsfunktion basierend auf Punkt-Position
const calculateFrequency = (meridianBaseHz: number, pointNumber: number, totalPoints: number): number => {
  const position = pointNumber / totalPoints;
  const variation = meridianBaseHz * 0.5 * position;
  return Math.round((meridianBaseHz + variation) * 10) / 10;
};

export const MERIDIANS: Meridian[] = [
  // ===== LUNGEN-MERIDIAN (LU) - 11 Punkte =====
  {
    id: 'LU',
    name: 'Lung Meridian',
    nameGerman: 'Lungen-Meridian',
    element: 'Metall',
    activeTime: '03-05h',
    color: 'bg-red-100',
    totalPoints: 11,
    points: [
      { id: 'LU-1', nameChinese: 'Zhongfu', nameGerman: 'Mittlerer Palast', chineseCharacter: '中府', frequencyHz: 23.2, activeTime: '03-05h', mainEffect: 'Atemwege, Husten, Asthma' },
      { id: 'LU-2', nameChinese: 'Yunmen', nameGerman: 'Wolkentor', chineseCharacter: '雲門', frequencyHz: 24.4, activeTime: '03-05h', mainEffect: 'Bronchitis, Schulterschmerzen' },
      { id: 'LU-3', nameChinese: 'Tianfu', nameGerman: 'Himmlischer Palast', chineseCharacter: '天府', frequencyHz: 25.6, activeTime: '03-05h', mainEffect: 'Asthma, Nasenbluten' },
      { id: 'LU-4', nameChinese: 'Xiabai', nameGerman: 'Seitliches Weiß', chineseCharacter: '俠白', frequencyHz: 26.8, activeTime: '03-05h', mainEffect: 'Herzschmerzen, Husten' },
      { id: 'LU-5', nameChinese: 'Chize', nameGerman: 'Elle-Sumpf', chineseCharacter: '尺澤', frequencyHz: 28.0, activeTime: '03-05h', mainEffect: 'He-Punkt, Fieber, Ellenbogenschmerz', element: 'Wasser' },
      { id: 'LU-6', nameChinese: 'Kongzui', nameGerman: 'Tiefste Öffnung', chineseCharacter: '孔最', frequencyHz: 29.2, activeTime: '03-05h', mainEffect: 'Xi-Punkt, Akute Atemwegserkrankungen', element: 'Metall' },
      { id: 'LU-7', nameChinese: 'Lieque', nameGerman: 'Unterbrochene Reihe', chineseCharacter: '列缺', frequencyHz: 30.4, activeTime: '03-05h', mainEffect: 'Luo-Punkt, Erkältung, Kopfschmerzen' },
      { id: 'LU-8', nameChinese: 'Jingqu', nameGerman: 'Kanal-Rinne', chineseCharacter: '經渠', frequencyHz: 31.6, activeTime: '03-05h', mainEffect: 'Jing-Punkt, Husten, Fieber', element: 'Metall' },
      { id: 'LU-9', nameChinese: 'Taiyuan', nameGerman: 'Große Tiefe', chineseCharacter: '太淵', frequencyHz: 32.8, activeTime: '03-05h', mainEffect: 'Yuan-Punkt, Puls-Regulation', element: 'Erde' },
      { id: 'LU-10', nameChinese: 'Yuji', nameGerman: 'Fischbauch-Grenze', chineseCharacter: '魚際', frequencyHz: 34.0, activeTime: '03-05h', mainEffect: 'Ying-Punkt, Halsschmerzen', element: 'Feuer' },
      { id: 'LU-11', nameChinese: 'Shaoshang', nameGerman: 'Kleiner Kaufmann', chineseCharacter: '少商', frequencyHz: 35.2, activeTime: '03-05h', mainEffect: 'Jing-Well-Punkt, Notfall, Halsschmerzen', element: 'Holz' },
    ]
  },
  
  // ===== DICKDARM-MERIDIAN (LI) - 20 Punkte =====
  {
    id: 'LI',
    name: 'Large Intestine Meridian',
    nameGerman: 'Dickdarm-Meridian',
    element: 'Metall',
    activeTime: '05-07h',
    color: 'bg-purple-100',
    totalPoints: 20,
    points: [
      { id: 'LI-1', nameChinese: 'Shangyang', nameGerman: 'Kaufmann Yang', chineseCharacter: '商陽', frequencyHz: 25.0, activeTime: '05-07h', mainEffect: 'Jing-Well-Punkt, Zahnschmerzen, Bewusstsein', element: 'Metall' },
      { id: 'LI-2', nameChinese: 'Erjian', nameGerman: 'Zweites Intervall', chineseCharacter: '二間', frequencyHz: 26.3, activeTime: '05-07h', mainEffect: 'Ying-Punkt, Nasenbluten, Zahnschmerzen', element: 'Wasser' },
      { id: 'LI-3', nameChinese: 'Sanjian', nameGerman: 'Drittes Intervall', chineseCharacter: '三間', frequencyHz: 27.6, activeTime: '05-07h', mainEffect: 'Shu-Punkt, Augenschmerzen', element: 'Holz' },
      { id: 'LI-4', nameChinese: 'Hegu', nameGerman: 'Vereinte Täler', chineseCharacter: '合谷', frequencyHz: 42.0, activeTime: '05-07h', mainEffect: 'Yuan-Punkt, Universeller Schmerz-Punkt', element: 'Metall' },
      { id: 'LI-5', nameChinese: 'Yangxi', nameGerman: 'Yang-Bach', chineseCharacter: '陽谿', frequencyHz: 30.2, activeTime: '05-07h', mainEffect: 'Jing-Punkt, Handgelenksschmerzen', element: 'Feuer' },
      { id: 'LI-6', nameChinese: 'Pianli', nameGerman: 'Abweichende Passage', chineseCharacter: '偏歴', frequencyHz: 31.5, activeTime: '05-07h', mainEffect: 'Luo-Punkt, Ödeme, Tinnitus' },
      { id: 'LI-7', nameChinese: 'Wenliu', nameGerman: 'Warmer Fluss', chineseCharacter: '溫溜', frequencyHz: 32.8, activeTime: '05-07h', mainEffect: 'Xi-Punkt, Bauchschmerzen' },
      { id: 'LI-8', nameChinese: 'Xialian', nameGerman: 'Untere Grenze', chineseCharacter: '下廉', frequencyHz: 34.1, activeTime: '05-07h', mainEffect: 'Ellenbogenschmerzen, Kopfschmerzen' },
      { id: 'LI-9', nameChinese: 'Shanglian', nameGerman: 'Obere Grenze', chineseCharacter: '上廉', frequencyHz: 35.4, activeTime: '05-07h', mainEffect: 'Armschmerzen, Lähmungen' },
      { id: 'LI-10', nameChinese: 'Shousanli', nameGerman: 'Drei Meilen am Arm', chineseCharacter: '手三里', frequencyHz: 48.6, activeTime: '05-07h', mainEffect: 'Armschmerzen, Verdauung' },
      { id: 'LI-11', nameChinese: 'Quchi', nameGerman: 'Gekrümmter Teich', chineseCharacter: '曲池', frequencyHz: 50.4, activeTime: '05-07h', mainEffect: 'He-Punkt, Fieber, Hypertonie', element: 'Erde' },
      { id: 'LI-12', nameChinese: 'Zhouliao', nameGerman: 'Ellenbogen-Spalt', chineseCharacter: '肘髎', frequencyHz: 40.1, activeTime: '05-07h', mainEffect: 'Ellenbogenschmerzen' },
      { id: 'LI-13', nameChinese: 'Shouwuli', nameGerman: 'Fünf Meilen am Arm', chineseCharacter: '手五里', frequencyHz: 41.4, activeTime: '05-07h', mainEffect: 'Armlähmungen' },
      { id: 'LI-14', nameChinese: 'Binao', nameGerman: 'Oberarm', chineseCharacter: '臂臑', frequencyHz: 42.7, activeTime: '05-07h', mainEffect: 'Schulter-Arm-Syndrom' },
      { id: 'LI-15', nameChinese: 'Jianyu', nameGerman: 'Schulter-Ecke', chineseCharacter: '肩髃', frequencyHz: 55.0, activeTime: '05-07h', mainEffect: 'Schulterschmerzen, Hypertonie' },
      { id: 'LI-16', nameChinese: 'Jugu', nameGerman: 'Großer Knochen', chineseCharacter: '巨骨', frequencyHz: 45.3, activeTime: '05-07h', mainEffect: 'Schulterschmerzen' },
      { id: 'LI-17', nameChinese: 'Tianding', nameGerman: 'Himmlischer Dreifuß', chineseCharacter: '天鼎', frequencyHz: 46.6, activeTime: '05-07h', mainEffect: 'Halsschmerzen, Schluckstörungen' },
      { id: 'LI-18', nameChinese: 'Futu', nameGerman: 'Stützender Vorsprung', chineseCharacter: '扶突', frequencyHz: 47.9, activeTime: '05-07h', mainEffect: 'Husten, Heiserkeit' },
      { id: 'LI-19', nameChinese: 'Kouheliao', nameGerman: 'Mund-Getreide-Spalt', chineseCharacter: '口禾髎', frequencyHz: 49.2, activeTime: '05-07h', mainEffect: 'Nasenpolypen, Schnupfen' },
      { id: 'LI-20', nameChinese: 'Yingxiang', nameGerman: 'Duftender Empfang', chineseCharacter: '迎香', frequencyHz: 63.0, activeTime: '05-07h', mainEffect: 'Nasenverstopfung, Sinusitis, Geruchsverlust' },
    ]
  },
  
  // ===== MAGEN-MERIDIAN (ST) - 45 Punkte =====
  {
    id: 'ST',
    name: 'Stomach Meridian',
    nameGerman: 'Magen-Meridian',
    element: 'Erde',
    activeTime: '07-09h',
    color: 'bg-green-100',
    totalPoints: 45,
    points: [
      { id: 'ST-1', nameChinese: 'Chengqi', nameGerman: 'Tränen-Behälter', chineseCharacter: '承泣', frequencyHz: 19.8, activeTime: '07-09h', mainEffect: 'Augenleiden, Tränenfluss' },
      { id: 'ST-2', nameChinese: 'Sibai', nameGerman: 'Vier Weiße', chineseCharacter: '四白', frequencyHz: 20.6, activeTime: '07-09h', mainEffect: 'Augenkrankheiten, Gesichtslähmung' },
      { id: 'ST-3', nameChinese: 'Juliao', nameGerman: 'Großer Spalt', chineseCharacter: '巨髎', frequencyHz: 21.4, activeTime: '07-09h', mainEffect: 'Zahnschmerzen, Nasenleiden' },
      { id: 'ST-4', nameChinese: 'Dicang', nameGerman: 'Erd-Speicher', chineseCharacter: '地倉', frequencyHz: 22.2, activeTime: '07-09h', mainEffect: 'Mundwinkellähmung, Speichelfluss' },
      { id: 'ST-5', nameChinese: 'Daying', nameGerman: 'Großer Empfang', chineseCharacter: '大迎', frequencyHz: 23.0, activeTime: '07-09h', mainEffect: 'Kieferschmerzen, Gesichtslähmung' },
      { id: 'ST-6', nameChinese: 'Jiache', nameGerman: 'Wagen-Knochen', chineseCharacter: '頰車', frequencyHz: 39.6, activeTime: '07-09h', mainEffect: 'Kiefergelenk, Bruxismus, Zahnschmerzen' },
      { id: 'ST-7', nameChinese: 'Xiaguan', nameGerman: 'Unteres Tor', chineseCharacter: '下關', frequencyHz: 24.6, activeTime: '07-09h', mainEffect: 'Kiefergelenksprobleme, Taubheit' },
      { id: 'ST-8', nameChinese: 'Touwei', nameGerman: 'Kopf-Ecke', chineseCharacter: '頭維', frequencyHz: 43.2, activeTime: '07-09h', mainEffect: 'Kopfschmerzen, Migräne, Augenprobleme' },
      { id: 'ST-9', nameChinese: 'Renying', nameGerman: 'Menschen-Empfang', chineseCharacter: '人迎', frequencyHz: 26.2, activeTime: '07-09h', mainEffect: 'Halsschmerzen, Hypertonie' },
      { id: 'ST-10', nameChinese: 'Shuitu', nameGerman: 'Wasser-Vorsprung', chineseCharacter: '水突', frequencyHz: 27.0, activeTime: '07-09h', mainEffect: 'Halsschmerzen, Husten' },
      { id: 'ST-11', nameChinese: 'Qishe', nameGerman: 'Qi-Residenz', chineseCharacter: '氣舍', frequencyHz: 27.8, activeTime: '07-09h', mainEffect: 'Schluckauf, Asthma' },
      { id: 'ST-12', nameChinese: 'Quepen', nameGerman: 'Leere Schale', chineseCharacter: '缺盆', frequencyHz: 28.6, activeTime: '07-09h', mainEffect: 'Schulterschmerzen, Husten' },
      { id: 'ST-13', nameChinese: 'Qihu', nameGerman: 'Qi-Tür', chineseCharacter: '氣戶', frequencyHz: 29.4, activeTime: '07-09h', mainEffect: 'Asthma, Brustschmerzen' },
      { id: 'ST-14', nameChinese: 'Kufang', nameGerman: 'Lager-Raum', chineseCharacter: '庫房', frequencyHz: 30.2, activeTime: '07-09h', mainEffect: 'Husten, Brustschmerzen' },
      { id: 'ST-15', nameChinese: 'Wuyi', nameGerman: 'Dach-Schirm', chineseCharacter: '屋翳', frequencyHz: 31.0, activeTime: '07-09h', mainEffect: 'Brustschmerzen, Mastitis' },
      { id: 'ST-16', nameChinese: 'Yingchuang', nameGerman: 'Brust-Fenster', chineseCharacter: '膺窗', frequencyHz: 31.8, activeTime: '07-09h', mainEffect: 'Husten, Brustschmerzen' },
      { id: 'ST-17', nameChinese: 'Ruzhong', nameGerman: 'Brust-Mitte', chineseCharacter: '乳中', frequencyHz: 32.6, activeTime: '07-09h', mainEffect: 'Orientierungspunkt (keine Nadel!)' },
      { id: 'ST-18', nameChinese: 'Rugen', nameGerman: 'Brust-Wurzel', chineseCharacter: '乳根', frequencyHz: 33.4, activeTime: '07-09h', mainEffect: 'Mastitis, Laktationsstörungen' },
      { id: 'ST-19', nameChinese: 'Burong', nameGerman: 'Nicht-Enthalten', chineseCharacter: '不容', frequencyHz: 34.2, activeTime: '07-09h', mainEffect: 'Erbrechen, Magenschmerzen' },
      { id: 'ST-20', nameChinese: 'Chengman', nameGerman: 'Fülle-Empfang', chineseCharacter: '承滿', frequencyHz: 35.0, activeTime: '07-09h', mainEffect: 'Völlegefühl, Erbrechen' },
      { id: 'ST-21', nameChinese: 'Liangmen', nameGerman: 'Balken-Tor', chineseCharacter: '梁門', frequencyHz: 35.8, activeTime: '07-09h', mainEffect: 'Magenschmerzen, Appetitlosigkeit' },
      { id: 'ST-22', nameChinese: 'Guanmen', nameGerman: 'Schließ-Tor', chineseCharacter: '關門', frequencyHz: 36.6, activeTime: '07-09h', mainEffect: 'Bauchschmerzen, Durchfall' },
      { id: 'ST-23', nameChinese: 'Taiyi', nameGerman: 'Große Einheit', chineseCharacter: '太乙', frequencyHz: 37.4, activeTime: '07-09h', mainEffect: 'Magenkrämpfe, psychische Unruhe' },
      { id: 'ST-24', nameChinese: 'Huaroumen', nameGerman: 'Gleitendes Fleisch-Tor', chineseCharacter: '滑肉門', frequencyHz: 38.2, activeTime: '07-09h', mainEffect: 'Erbrechen, Epilepsie' },
      { id: 'ST-25', nameChinese: 'Tianshu', nameGerman: 'Himmelsdrehpunkt', chineseCharacter: '天樞', frequencyHz: 69.3, activeTime: '07-09h', mainEffect: 'Mu-Punkt des Dickdarms, Durchfall, Verstopfung' },
      { id: 'ST-26', nameChinese: 'Wailing', nameGerman: 'Äußerer Hügel', chineseCharacter: '外陵', frequencyHz: 40.0, activeTime: '07-09h', mainEffect: 'Bauchschmerzen, Hernie' },
      { id: 'ST-27', nameChinese: 'Daju', nameGerman: 'Große Riesen', chineseCharacter: '大巨', frequencyHz: 40.8, activeTime: '07-09h', mainEffect: 'Unterbauchschmerzen, Blasenprobleme' },
      { id: 'ST-28', nameChinese: 'Shuidao', nameGerman: 'Wasserweg', chineseCharacter: '水道', frequencyHz: 41.6, activeTime: '07-09h', mainEffect: 'Ödeme, Menstruationsstörungen' },
      { id: 'ST-29', nameChinese: 'Guilai', nameGerman: 'Rückkehr', chineseCharacter: '歸來', frequencyHz: 42.4, activeTime: '07-09h', mainEffect: 'Genitalerkrankungen, Hernie' },
      { id: 'ST-30', nameChinese: 'Qichong', nameGerman: 'Qi-Ansturm', chineseCharacter: '氣沖', frequencyHz: 43.2, activeTime: '07-09h', mainEffect: 'Genitalschmerzen, Hernie' },
      { id: 'ST-31', nameChinese: 'Biguan', nameGerman: 'Oberschenkel-Tor', chineseCharacter: '髀關', frequencyHz: 44.0, activeTime: '07-09h', mainEffect: 'Oberschenkelschmerzen, Lähmungen' },
      { id: 'ST-32', nameChinese: 'Futu', nameGerman: 'Hockender Hase', chineseCharacter: '伏兔', frequencyHz: 44.8, activeTime: '07-09h', mainEffect: 'Oberschenkellähmung, Knieprobleme' },
      { id: 'ST-33', nameChinese: 'Yinshi', nameGerman: 'Yin-Markt', chineseCharacter: '陰市', frequencyHz: 45.6, activeTime: '07-09h', mainEffect: 'Knieschmerzen, Unterbauchschmerzen' },
      { id: 'ST-34', nameChinese: 'Liangqiu', nameGerman: 'Hügel-Kamm', chineseCharacter: '梁丘', frequencyHz: 46.4, activeTime: '07-09h', mainEffect: 'Xi-Punkt, Akute Magenschmerzen, Knieprobleme' },
      { id: 'ST-35', nameChinese: 'Dubi', nameGerman: 'Kalbsnase', chineseCharacter: '犢鼻', frequencyHz: 47.2, activeTime: '07-09h', mainEffect: 'Kniegelenkschmerzen' },
      { id: 'ST-36', nameChinese: 'Zusanli', nameGerman: 'Drei Li vom Knie', chineseCharacter: '足三里', frequencyHz: 99.0, activeTime: '07-09h', mainEffect: 'He-Punkt, Universelles Tonikum, Immunstärkung', element: 'Erde' },
      { id: 'ST-37', nameChinese: 'Shangjuxu', nameGerman: 'Obere große Leere', chineseCharacter: '上巨虛', frequencyHz: 49.6, activeTime: '07-09h', mainEffect: 'Unterer He-Punkt des Dickdarms, Durchfall' },
      { id: 'ST-38', nameChinese: 'Tiaokou', nameGerman: 'Streifen-Öffnung', chineseCharacter: '條口', frequencyHz: 50.4, activeTime: '07-09h', mainEffect: 'Schulterschmerzen, Wadenkrämpfe' },
      { id: 'ST-39', nameChinese: 'Xiajuxu', nameGerman: 'Untere große Leere', chineseCharacter: '下巨虛', frequencyHz: 51.2, activeTime: '07-09h', mainEffect: 'Unterer He-Punkt des Dünndarms' },
      { id: 'ST-40', nameChinese: 'Fenglong', nameGerman: 'Üppiger Hügel', chineseCharacter: '豐隆', frequencyHz: 108.5, activeTime: '07-09h', mainEffect: 'Luo-Punkt, Schleimlösung, Beruhigung' },
      { id: 'ST-41', nameChinese: 'Jiexi', nameGerman: 'Lösen der Meerenge', chineseCharacter: '解谿', frequencyHz: 53.6, activeTime: '07-09h', mainEffect: 'Jing-Punkt, Knöchelschmerzen', element: 'Feuer' },
      { id: 'ST-42', nameChinese: 'Chongyang', nameGerman: 'Ansturm-Yang', chineseCharacter: '沖陽', frequencyHz: 54.4, activeTime: '07-09h', mainEffect: 'Yuan-Punkt, Magenschmerzen' },
      { id: 'ST-43', nameChinese: 'Xiangu', nameGerman: 'Versunkenes Tal', chineseCharacter: '陷谷', frequencyHz: 55.2, activeTime: '07-09h', mainEffect: 'Shu-Punkt, Fußschwellung', element: 'Holz' },
      { id: 'ST-44', nameChinese: 'Neiting', nameGerman: 'Innerer Hof', chineseCharacter: '内庭', frequencyHz: 115.2, activeTime: '07-09h', mainEffect: 'Ying-Punkt, Zahnschmerzen, Fieber', element: 'Wasser' },
      { id: 'ST-45', nameChinese: 'Lidui', nameGerman: 'Strenger Austausch', chineseCharacter: '厲兌', frequencyHz: 57.6, activeTime: '07-09h', mainEffect: 'Jing-Well-Punkt, Alpträume, Gesichtsschwellung', element: 'Metall' },
    ]
  },
  
  // ===== MILZ-PANKREAS-MERIDIAN (SP) - 21 Punkte =====
  {
    id: 'SP',
    name: 'Spleen Meridian',
    nameGerman: 'Milz-Pankreas-Meridian',
    element: 'Erde',
    activeTime: '09-11h',
    color: 'bg-yellow-100',
    totalPoints: 21,
    points: [
      { id: 'SP-1', nameChinese: 'Yinbai', nameGerman: 'Verstecktes Weiß', chineseCharacter: '隱白', frequencyHz: 16.2, activeTime: '09-11h', mainEffect: 'Jing-Well-Punkt, Menstruationsstörungen, Blutungen', element: 'Holz' },
      { id: 'SP-2', nameChinese: 'Dadu', nameGerman: 'Große Stadt', chineseCharacter: '大都', frequencyHz: 18.1, activeTime: '09-11h', mainEffect: 'Ying-Punkt, Magenschmerzen', element: 'Feuer' },
      { id: 'SP-3', nameChinese: 'Taibai', nameGerman: 'Großes Weiß', chineseCharacter: '太白', frequencyHz: 24.3, activeTime: '09-11h', mainEffect: 'Shu-Punkt, Yuan-Punkt, Verdauung', element: 'Erde' },
      { id: 'SP-4', nameChinese: 'Gongsun', nameGerman: 'Großvaters Enkel', chineseCharacter: '公孫', frequencyHz: 28.4, activeTime: '09-11h', mainEffect: 'Luo-Punkt, Magen-Darm-Beschwerden' },
      { id: 'SP-5', nameChinese: 'Shangqiu', nameGerman: 'Metall-Hügel', chineseCharacter: '商丘', frequencyHz: 30.5, activeTime: '09-11h', mainEffect: 'Jing-Punkt, Verdauungsstörungen', element: 'Metall' },
      { id: 'SP-6', nameChinese: 'Sanyinjiao', nameGerman: 'Drei Yin-Kreuzung', chineseCharacter: '三陰交', frequencyHz: 72.9, activeTime: '09-11h', mainEffect: 'Gynäkologie, Fertilität, Schlafstörungen' },
      { id: 'SP-7', nameChinese: 'Lougu', nameGerman: 'Leckendes Tal', chineseCharacter: '漏谷', frequencyHz: 34.7, activeTime: '09-11h', mainEffect: 'Blasenentzündung, Ödeme' },
      { id: 'SP-8', nameChinese: 'Diji', nameGerman: 'Erd-Maschine', chineseCharacter: '地機', frequencyHz: 78.3, activeTime: '09-11h', mainEffect: 'Xi-Punkt, Menstruationsschmerzen', element: 'Erde' },
      { id: 'SP-9', nameChinese: 'Yinlingquan', nameGerman: 'Yin-Hügel-Quelle', chineseCharacter: '陰陵泉', frequencyHz: 81.0, activeTime: '09-11h', mainEffect: 'He-Punkt, Ödeme, Blasenprobleme', element: 'Wasser' },
      { id: 'SP-10', nameChinese: 'Xuehai', nameGerman: 'Blut-Meer', chineseCharacter: '血海', frequencyHz: 43.1, activeTime: '09-11h', mainEffect: 'Blut regulierend, Hauterkrankungen' },
      { id: 'SP-11', nameChinese: 'Jimen', nameGerman: 'Sieb-Tor', chineseCharacter: '箕門', frequencyHz: 45.2, activeTime: '09-11h', mainEffect: 'Blasenstörungen, Leistenschmerzen' },
      { id: 'SP-12', nameChinese: 'Chongmen', nameGerman: 'Ansturm-Tor', chineseCharacter: '衝門', frequencyHz: 47.3, activeTime: '09-11h', mainEffect: 'Hernie, Menstruationsschmerzen' },
      { id: 'SP-13', nameChinese: 'Fushe', nameGerman: 'Eingeweide-Residenz', chineseCharacter: '府舍', frequencyHz: 49.4, activeTime: '09-11h', mainEffect: 'Hernie, Bauchschmerzen' },
      { id: 'SP-14', nameChinese: 'Fujie', nameGerman: 'Bauch-Knoten', chineseCharacter: '腹結', frequencyHz: 51.5, activeTime: '09-11h', mainEffect: 'Verstopfung, Durchfall' },
      { id: 'SP-15', nameChinese: 'Daheng', nameGerman: 'Große Horizontale', chineseCharacter: '大横', frequencyHz: 53.6, activeTime: '09-11h', mainEffect: 'Verstopfung, Darmparasiten' },
      { id: 'SP-16', nameChinese: 'Fuai', nameGerman: 'Bauch-Klage', chineseCharacter: '腹哀', frequencyHz: 55.7, activeTime: '09-11h', mainEffect: 'Bauchschmerzen, Verdauungsstörungen' },
      { id: 'SP-17', nameChinese: 'Shidou', nameGerman: 'Nahrungshöhle', chineseCharacter: '食竇', frequencyHz: 57.8, activeTime: '09-11h', mainEffect: 'Brustschmerzen, Schluckauf' },
      { id: 'SP-18', nameChinese: 'Tianxi', nameGerman: 'Himmlische Schlucht', chineseCharacter: '天谿', frequencyHz: 59.9, activeTime: '09-11h', mainEffect: 'Husten, Brustschmerzen, Mastitis' },
      { id: 'SP-19', nameChinese: 'Xiongxiang', nameGerman: 'Brust-Dorf', chineseCharacter: '胸鄉', frequencyHz: 62.0, activeTime: '09-11h', mainEffect: 'Brustschmerzen, Schluckauf' },
      { id: 'SP-20', nameChinese: 'Zhourong', nameGerman: 'Umfassende Blüte', chineseCharacter: '周榮', frequencyHz: 64.1, activeTime: '09-11h', mainEffect: 'Husten, Brustschmerzen' },
      { id: 'SP-21', nameChinese: 'Dabao', nameGerman: 'Großer Umhang', chineseCharacter: '大包', frequencyHz: 89.1, activeTime: '09-11h', mainEffect: 'Große Luo-Punkt, Thoraxschmerzen, Asthma' },
    ]
  },
  
  // ===== HERZ-MERIDIAN (HT) - 9 Punkte =====
  {
    id: 'HT',
    name: 'Heart Meridian',
    nameGerman: 'Herz-Meridian',
    element: 'Feuer',
    activeTime: '11-13h',
    color: 'bg-orange-100',
    totalPoints: 9,
    points: [
      { id: 'HT-1', nameChinese: 'Jiquan', nameGerman: 'Höchste Quelle', chineseCharacter: '極泉', frequencyHz: 13.8, activeTime: '11-13h', mainEffect: 'Herzrhythmus, Angina, Armschmerzen' },
      { id: 'HT-2', nameChinese: 'Qingling', nameGerman: 'Grüner Geist', chineseCharacter: '青靈', frequencyHz: 18.9, activeTime: '11-13h', mainEffect: 'Armschmerzen, Kopfschmerzen' },
      { id: 'HT-3', nameChinese: 'Shaohai', nameGerman: 'Kleines Meer', chineseCharacter: '少海', frequencyHz: 20.7, activeTime: '11-13h', mainEffect: 'He-Punkt, Ellenbogenschmerzen, Angst', element: 'Wasser' },
      { id: 'HT-4', nameChinese: 'Lingdao', nameGerman: 'Geist-Pfad', chineseCharacter: '靈道', frequencyHz: 27.6, activeTime: '11-13h', mainEffect: 'Jing-Punkt, Herzschmerzen, Stimmungsschwankungen', element: 'Metall' },
      { id: 'HT-5', nameChinese: 'Tongli', nameGerman: 'Geist-Verbindung', chineseCharacter: '通里', frequencyHz: 34.5, activeTime: '11-13h', mainEffect: 'Luo-Punkt, Sprachstörungen, Stottern' },
      { id: 'HT-6', nameChinese: 'Yinxi', nameGerman: 'Yin-Spalt', chineseCharacter: '陰郄', frequencyHz: 41.4, activeTime: '11-13h', mainEffect: 'Xi-Punkt, Nachtschweiß, Herzklopfen', element: 'Feuer' },
      { id: 'HT-7', nameChinese: 'Shenmen', nameGerman: 'Geist-Tor', chineseCharacter: '神門', frequencyHz: 48.3, activeTime: '11-13h', mainEffect: 'Shu-Punkt, Yuan-Punkt, Angst, Schlaflosigkeit', element: 'Erde' },
      { id: 'HT-8', nameChinese: 'Shaofu', nameGerman: 'Kleine Residenz', chineseCharacter: '少府', frequencyHz: 52.1, activeTime: '11-13h', mainEffect: 'Ying-Punkt, Herzhitze, Juckreiz', element: 'Feuer' },
      { id: 'HT-9', nameChinese: 'Shaochong', nameGerman: 'Kleiner Ansturm', chineseCharacter: '少沖', frequencyHz: 55.2, activeTime: '11-13h', mainEffect: 'Jing-Well-Punkt, Bewusstlosigkeit, Schock', element: 'Holz' },
    ]
  },
  
  // ===== DÜNNDARM-MERIDIAN (SI) - 19 Punkte =====
  {
    id: 'SI',
    name: 'Small Intestine Meridian',
    nameGerman: 'Dünndarm-Meridian',
    element: 'Feuer',
    activeTime: '13-15h',
    color: 'bg-blue-100',
    totalPoints: 19,
    points: [
      { id: 'SI-1', nameChinese: 'Shaoze', nameGerman: 'Kleine Meerenge', chineseCharacter: '少澤', frequencyHz: 27.6, activeTime: '13-15h', mainEffect: 'Jing-Well-Punkt, Laktationsstörungen', element: 'Metall' },
      { id: 'SI-2', nameChinese: 'Qiangu', nameGerman: 'Vorderes Tal', chineseCharacter: '前谷', frequencyHz: 30.9, activeTime: '13-15h', mainEffect: 'Ying-Punkt, Fieber, Kopfschmerzen', element: 'Wasser' },
      { id: 'SI-3', nameChinese: 'Houxi', nameGerman: 'Hinterer Bach', chineseCharacter: '後谿', frequencyHz: 41.4, activeTime: '13-15h', mainEffect: 'Shu-Punkt, Nackenverspannungen', element: 'Holz' },
      { id: 'SI-4', nameChinese: 'Wangu', nameGerman: 'Handgelenk-Knochen', chineseCharacter: '腕骨', frequencyHz: 48.6, activeTime: '13-15h', mainEffect: 'Yuan-Punkt, Handgelenksschmerzen' },
      { id: 'SI-5', nameChinese: 'Yanggu', nameGerman: 'Yang-Tal', chineseCharacter: '陽谷', frequencyHz: 44.2, activeTime: '13-15h', mainEffect: 'Jing-Punkt, Handgelenksschmerzen', element: 'Feuer' },
      { id: 'SI-6', nameChinese: 'Yanglao', nameGerman: 'Pflege des Alters', chineseCharacter: '養老', frequencyHz: 62.1, activeTime: '13-15h', mainEffect: 'Xi-Punkt, Augen, Schultern' },
      { id: 'SI-7', nameChinese: 'Zhizheng', nameGerman: 'Zweig zum Aufrechten', chineseCharacter: '支正', frequencyHz: 50.7, activeTime: '13-15h', mainEffect: 'Luo-Punkt, Ellenbogenschmerzen, Angst' },
      { id: 'SI-8', nameChinese: 'Xiaohai', nameGerman: 'Kleines Meer', chineseCharacter: '小海', frequencyHz: 57.2, activeTime: '13-15h', mainEffect: 'He-Punkt, Ellenbogenschmerzen', element: 'Erde' },
      { id: 'SI-9', nameChinese: 'Jianzhen', nameGerman: 'Wahre Schulter', chineseCharacter: '肩貞', frequencyHz: 63.7, activeTime: '13-15h', mainEffect: 'Schulterschmerzen' },
      { id: 'SI-10', nameChinese: 'Naoshu', nameGerman: 'Oberarm-Shu', chineseCharacter: '臑俞', frequencyHz: 70.2, activeTime: '13-15h', mainEffect: 'Schulterschmerzen, Taubheit im Arm' },
      { id: 'SI-11', nameChinese: 'Tianzong', nameGerman: 'Himmlische Versammlung', chineseCharacter: '天宗', frequencyHz: 96.6, activeTime: '13-15h', mainEffect: 'Schulterschmerzen, Laktationsstörungen' },
      { id: 'SI-12', nameChinese: 'Bingfeng', nameGerman: 'Ergreifen des Windes', chineseCharacter: '秉風', frequencyHz: 83.2, activeTime: '13-15h', mainEffect: 'Schulterschmerzen, Taubheit' },
      { id: 'SI-13', nameChinese: 'Quyuan', nameGerman: 'Gekrümmte Mauer', chineseCharacter: '曲垣', frequencyHz: 89.7, activeTime: '13-15h', mainEffect: 'Schulterschmerzen' },
      { id: 'SI-14', nameChinese: 'Jianwaishu', nameGerman: 'Äußerer Schulter-Shu', chineseCharacter: '肩外俞', frequencyHz: 96.2, activeTime: '13-15h', mainEffect: 'Schulterschmerzen, Nackensteifheit' },
      { id: 'SI-15', nameChinese: 'Jianzhongshu', nameGerman: 'Mittlerer Schulter-Shu', chineseCharacter: '肩中俞', frequencyHz: 102.7, activeTime: '13-15h', mainEffect: 'Schulterschmerzen, Husten' },
      { id: 'SI-16', nameChinese: 'Tianchuang', nameGerman: 'Himmelsfenster', chineseCharacter: '天窗', frequencyHz: 109.2, activeTime: '13-15h', mainEffect: 'Halsschmerzen, Taubheit' },
      { id: 'SI-17', nameChinese: 'Tianrong', nameGerman: 'Himmlische Erscheinung', chineseCharacter: '天容', frequencyHz: 115.7, activeTime: '13-15h', mainEffect: 'Halsschmerzen, Schwerhörigkeit' },
      { id: 'SI-18', nameChinese: 'Quanliao', nameGerman: 'Jochbein-Spalt', chineseCharacter: '顴髎', frequencyHz: 118.5, activeTime: '13-15h', mainEffect: 'Gesichtslähmung, Zahnschmerzen' },
      { id: 'SI-19', nameChinese: 'Tinggong', nameGerman: 'Palast des Hörens', chineseCharacter: '聽宮', frequencyHz: 124.2, activeTime: '13-15h', mainEffect: 'Tinnitus, Schwerhörigkeit' },
    ]
  },
  
  // ===== BLASEN-MERIDIAN (BL) - 67 Punkte =====
  {
    id: 'BL',
    name: 'Bladder Meridian',
    nameGerman: 'Blasen-Meridian',
    element: 'Wasser',
    activeTime: '15-17h',
    color: 'bg-indigo-100',
    totalPoints: 67,
    points: [
      { id: 'BL-1', nameChinese: 'Jingming', nameGerman: 'Helles Licht', chineseCharacter: '睛明', frequencyHz: 7.0, activeTime: '15-17h', mainEffect: 'Augenerkrankungen aller Art' },
      { id: 'BL-2', nameChinese: 'Zanzhu', nameGerman: 'Bambus-Versammlung', chineseCharacter: '攢竹', frequencyHz: 10.5, activeTime: '15-17h', mainEffect: 'Kopfschmerzen, Migräne, Sehstörungen' },
      { id: 'BL-3', nameChinese: 'Meichong', nameGerman: 'Augenbrauen-Aufstieg', chineseCharacter: '眉衝', frequencyHz: 8.2, activeTime: '15-17h', mainEffect: 'Kopfschmerzen, Nasenverstopfung' },
      { id: 'BL-4', nameChinese: 'Quchai', nameGerman: 'Abweichende Kurve', chineseCharacter: '曲差', frequencyHz: 8.9, activeTime: '15-17h', mainEffect: 'Kopfschmerzen, Nasenbluten' },
      { id: 'BL-5', nameChinese: 'Wuchu', nameGerman: 'Fünfte Position', chineseCharacter: '五處', frequencyHz: 9.6, activeTime: '15-17h', mainEffect: 'Kopfschmerzen, Epilepsie' },
      { id: 'BL-6', nameChinese: 'Chengguang', nameGerman: 'Licht empfangen', chineseCharacter: '承光', frequencyHz: 10.3, activeTime: '15-17h', mainEffect: 'Kopfschmerzen, verschwommenes Sehen' },
      { id: 'BL-7', nameChinese: 'Tongtian', nameGerman: 'Himmel erreichen', chineseCharacter: '通天', frequencyHz: 11.0, activeTime: '15-17h', mainEffect: 'Kopfschmerzen, Nasenverstopfung' },
      { id: 'BL-8', nameChinese: 'Luoque', nameGerman: 'Absteigende Verbindung', chineseCharacter: '絡卻', frequencyHz: 11.7, activeTime: '15-17h', mainEffect: 'Schwindel, Sehstörungen' },
      { id: 'BL-9', nameChinese: 'Yuzhen', nameGerman: 'Jadekissen', chineseCharacter: '玉枕', frequencyHz: 12.4, activeTime: '15-17h', mainEffect: 'Kopfschmerzen, Sehstörungen' },
      { id: 'BL-10', nameChinese: 'Tianzhu', nameGerman: 'Himmelspfeiler', chineseCharacter: '天柱', frequencyHz: 21.0, activeTime: '15-17h', mainEffect: 'Nackenschmerzen, Stress, Schlafstörungen' },
      { id: 'BL-11', nameChinese: 'Dazhu', nameGerman: 'Großer Shuttle', chineseCharacter: '大杼', frequencyHz: 24.5, activeTime: '15-17h', mainEffect: 'Hui-Punkt der Knochen, Knochenerkrankungen' },
      { id: 'BL-12', nameChinese: 'Fengmen', nameGerman: 'Windtor', chineseCharacter: '風門', frequencyHz: 14.5, activeTime: '15-17h', mainEffect: 'Erkältung, Husten, Fieber' },
      { id: 'BL-13', nameChinese: 'Feishu', nameGerman: 'Lungen-Shu', chineseCharacter: '肺俞', frequencyHz: 28.0, activeTime: '15-17h', mainEffect: 'Back-Shu der Lunge, Lungenerkrankungen' },
      { id: 'BL-14', nameChinese: 'Jueyinshu', nameGerman: 'Perikard-Shu', chineseCharacter: '厥陰俞', frequencyHz: 16.1, activeTime: '15-17h', mainEffect: 'Back-Shu des Perikards, Herzschmerzen' },
      { id: 'BL-15', nameChinese: 'Xinshu', nameGerman: 'Herz-Shu', chineseCharacter: '心俞', frequencyHz: 31.5, activeTime: '15-17h', mainEffect: 'Back-Shu des Herzens, Herzerkrankungen' },
      { id: 'BL-16', nameChinese: 'Dushu', nameGerman: 'Du-Mai-Shu', chineseCharacter: '督俞', frequencyHz: 17.5, activeTime: '15-17h', mainEffect: 'Herzschmerzen, Bauchschmerzen' },
      { id: 'BL-17', nameChinese: 'Geshu', nameGerman: 'Zwerchfell-Shu', chineseCharacter: '膈俞', frequencyHz: 18.2, activeTime: '15-17h', mainEffect: 'Hui-Punkt des Blutes, Schluckauf, Erbrechen' },
      { id: 'BL-18', nameChinese: 'Ganshu', nameGerman: 'Leber-Shu', chineseCharacter: '肝俞', frequencyHz: 38.5, activeTime: '15-17h', mainEffect: 'Back-Shu der Leber, Lebererkrankungen, Augenprobleme' },
      { id: 'BL-19', nameChinese: 'Danshu', nameGerman: 'Gallenblase-Shu', chineseCharacter: '膽俞', frequencyHz: 19.6, activeTime: '15-17h', mainEffect: 'Back-Shu der Gallenblase' },
      { id: 'BL-20', nameChinese: 'Pishu', nameGerman: 'Milz-Shu', chineseCharacter: '脾俞', frequencyHz: 42.0, activeTime: '15-17h', mainEffect: 'Back-Shu der Milz, Milzerkrankungen, Verdauung' },
      { id: 'BL-21', nameChinese: 'Weishu', nameGerman: 'Magen-Shu', chineseCharacter: '胃俞', frequencyHz: 21.0, activeTime: '15-17h', mainEffect: 'Back-Shu des Magens, Magenschmerzen' },
      { id: 'BL-22', nameChinese: 'Sanjiaoshu', nameGerman: 'Dreifach-Erwärmer-Shu', chineseCharacter: '三焦俞', frequencyHz: 21.7, activeTime: '15-17h', mainEffect: 'Back-Shu des Dreifach-Erwärmers' },
      { id: 'BL-23', nameChinese: 'Shenshu', nameGerman: 'Nieren-Shu', chineseCharacter: '腎俞', frequencyHz: 28.0, activeTime: '15-17h', mainEffect: 'Back-Shu der Nieren, Rückenschmerzen, Nieren' },
      { id: 'BL-24', nameChinese: 'Qihaishu', nameGerman: 'Qi-Meer-Shu', chineseCharacter: '氣海俞', frequencyHz: 23.1, activeTime: '15-17h', mainEffect: 'Rückenschmerzen, Menstruationsstörungen' },
      { id: 'BL-25', nameChinese: 'Dachangshu', nameGerman: 'Dickdarm-Shu', chineseCharacter: '大腸俞', frequencyHz: 23.8, activeTime: '15-17h', mainEffect: 'Back-Shu des Dickdarms, Durchfall, Verstopfung' },
      { id: 'BL-26', nameChinese: 'Guanyuanshu', nameGerman: 'Ursprungs-Tor-Shu', chineseCharacter: '關元俞', frequencyHz: 24.5, activeTime: '15-17h', mainEffect: 'Rückenschmerzen, Blasenprobleme' },
      { id: 'BL-27', nameChinese: 'Xiaochangshu', nameGerman: 'Dünndarm-Shu', chineseCharacter: '小腸俞', frequencyHz: 25.2, activeTime: '15-17h', mainEffect: 'Back-Shu des Dünndarms' },
      { id: 'BL-28', nameChinese: 'Pangguangshu', nameGerman: 'Blasen-Shu', chineseCharacter: '膀胱俞', frequencyHz: 25.9, activeTime: '15-17h', mainEffect: 'Back-Shu der Blase, Blasenentzündung' },
      { id: 'BL-29', nameChinese: 'Zhonglushu', nameGerman: 'Mittel-Wirbel-Shu', chineseCharacter: '中膂俞', frequencyHz: 26.6, activeTime: '15-17h', mainEffect: 'Rückenschmerzen, Durchfall' },
      { id: 'BL-30', nameChinese: 'Baihuanshu', nameGerman: 'Weißer Ring-Shu', chineseCharacter: '白環俞', frequencyHz: 27.3, activeTime: '15-17h', mainEffect: 'Gynäkologische Probleme, Rückenschmerzen' },
      { id: 'BL-31', nameChinese: 'Shangliao', nameGerman: 'Oberer Spalt', chineseCharacter: '上髎', frequencyHz: 28.0, activeTime: '15-17h', mainEffect: 'Menstruationsstörungen, Rückenschmerzen' },
      { id: 'BL-32', nameChinese: 'Ciliao', nameGerman: 'Zweiter Spalt', chineseCharacter: '次髎', frequencyHz: 28.7, activeTime: '15-17h', mainEffect: 'Menstruationsstörungen, Ischias' },
      { id: 'BL-33', nameChinese: 'Zhongliao', nameGerman: 'Mittlerer Spalt', chineseCharacter: '中髎', frequencyHz: 29.4, activeTime: '15-17h', mainEffect: 'Blasenprobleme, Verstopfung' },
      { id: 'BL-34', nameChinese: 'Xialiao', nameGerman: 'Unterer Spalt', chineseCharacter: '下髎', frequencyHz: 30.1, activeTime: '15-17h', mainEffect: 'Rückenschmerzen, Blasenprobleme' },
      { id: 'BL-35', nameChinese: 'Huiyang', nameGerman: 'Yang-Treffen', chineseCharacter: '會陽', frequencyHz: 30.8, activeTime: '15-17h', mainEffect: 'Hämorrhoiden, Impotenz' },
      { id: 'BL-36', nameChinese: 'Chengfu', nameGerman: 'Stütze empfangen', chineseCharacter: '承扶', frequencyHz: 31.5, activeTime: '15-17h', mainEffect: 'Ischias, Hämorrhoiden' },
      { id: 'BL-37', nameChinese: 'Yinmen', nameGerman: 'Tor der Fülle', chineseCharacter: '殷門', frequencyHz: 32.2, activeTime: '15-17h', mainEffect: 'Oberschenkelschmerzen, Rückenschmerzen' },
      { id: 'BL-38', nameChinese: 'Fuxi', nameGerman: 'Oberflächlicher Spalt', chineseCharacter: '浮郄', frequencyHz: 32.9, activeTime: '15-17h', mainEffect: 'Knieschmerzen, Taubheit' },
      { id: 'BL-39', nameChinese: 'Weiyang', nameGerman: 'Seitliches Yang', chineseCharacter: '委陽', frequencyHz: 33.6, activeTime: '15-17h', mainEffect: 'Unterer He-Punkt des Dreifach-Erwärmers' },
      { id: 'BL-40', nameChinese: 'Weizhong', nameGerman: 'Mittelstütze', chineseCharacter: '委中', frequencyHz: 56.0, activeTime: '15-17h', mainEffect: 'He-Punkt, Rücken, Knie, Haut', element: 'Erde' },
      { id: 'BL-41', nameChinese: 'Fufen', nameGerman: 'Anhängender Teil', chineseCharacter: '附分', frequencyHz: 35.0, activeTime: '15-17h', mainEffect: 'Nackenschmerzen, Schulterschmerzen' },
      { id: 'BL-42', nameChinese: 'Pohu', nameGerman: 'Tor der körperlichen Seele', chineseCharacter: '魄戶', frequencyHz: 35.7, activeTime: '15-17h', mainEffect: 'Husten, Schulterschmerzen' },
      { id: 'BL-43', nameChinese: 'Gaohuangshu', nameGerman: 'Vitale Region Shu', chineseCharacter: '膏肓俞', frequencyHz: 36.4, activeTime: '15-17h', mainEffect: 'Erschöpfung, chronische Krankheiten' },
      { id: 'BL-44', nameChinese: 'Shentang', nameGerman: 'Geist-Halle', chineseCharacter: '神堂', frequencyHz: 37.1, activeTime: '15-17h', mainEffect: 'Herzschmerzen, Husten' },
      { id: 'BL-45', nameChinese: 'Yixi', nameGerman: 'Das tut weh', chineseCharacter: '譩譆', frequencyHz: 37.8, activeTime: '15-17h', mainEffect: 'Husten, Schulterschmerzen' },
      { id: 'BL-46', nameChinese: 'Geguan', nameGerman: 'Zwerchfell-Tor', chineseCharacter: '膈關', frequencyHz: 38.5, activeTime: '15-17h', mainEffect: 'Schluckauf, Erbrechen' },
      { id: 'BL-47', nameChinese: 'Hunmen', nameGerman: 'Tor der ätherischen Seele', chineseCharacter: '魂門', frequencyHz: 39.2, activeTime: '15-17h', mainEffect: 'Flankenschmerzen, Erbrechen' },
      { id: 'BL-48', nameChinese: 'Yanggang', nameGerman: 'Yang-Netz', chineseCharacter: '陽綱', frequencyHz: 39.9, activeTime: '15-17h', mainEffect: 'Gelbsucht, Durchfall' },
      { id: 'BL-49', nameChinese: 'Yishe', nameGerman: 'Wohnsitz des Intellekts', chineseCharacter: '意舍', frequencyHz: 40.6, activeTime: '15-17h', mainEffect: 'Bauchschmerzen, Erbrechen' },
      { id: 'BL-50', nameChinese: 'Weicang', nameGerman: 'Magen-Speicher', chineseCharacter: '胃倉', frequencyHz: 41.3, activeTime: '15-17h', mainEffect: 'Bauchschmerzen, Rückenschmerzen' },
      { id: 'BL-51', nameChinese: 'Huangmen', nameGerman: 'Vital-Tor', chineseCharacter: '肓門', frequencyHz: 42.0, activeTime: '15-17h', mainEffect: 'Mastitis, Verstopfung' },
      { id: 'BL-52', nameChinese: 'Zhishi', nameGerman: 'Willenskraft-Raum', chineseCharacter: '志室', frequencyHz: 42.7, activeTime: '15-17h', mainEffect: 'Impotenz, Rückenschmerzen' },
      { id: 'BL-53', nameChinese: 'Baohuang', nameGerman: 'Blasen-Vital', chineseCharacter: '胞肓', frequencyHz: 43.4, activeTime: '15-17h', mainEffect: 'Rückenschmerzen, Blasenprobleme' },
      { id: 'BL-54', nameChinese: 'Zhibian', nameGerman: 'Geordneter Rand', chineseCharacter: '秩邊', frequencyHz: 44.1, activeTime: '15-17h', mainEffect: 'Ischias, Hämorrhoiden' },
      { id: 'BL-55', nameChinese: 'Heyang', nameGerman: 'Yang-Zusammenfluss', chineseCharacter: '合陽', frequencyHz: 44.8, activeTime: '15-17h', mainEffect: 'Rückenschmerzen, Uterusblutung' },
      { id: 'BL-56', nameChinese: 'Chengjin', nameGerman: 'Sehnen-Stütze', chineseCharacter: '承筋', frequencyHz: 45.5, activeTime: '15-17h', mainEffect: 'Wadenkrämpfe, Hämorrhoiden' },
      { id: 'BL-57', nameChinese: 'Chengshan', nameGerman: 'Berg-Stütze', chineseCharacter: '承山', frequencyHz: 46.2, activeTime: '15-17h', mainEffect: 'Wadenkrämpfe, Hämorrhoiden, Verstopfung' },
      { id: 'BL-58', nameChinese: 'Feiyang', nameGerman: 'Aufsteigend', chineseCharacter: '飛陽', frequencyHz: 46.9, activeTime: '15-17h', mainEffect: 'Luo-Punkt, Kopfschmerzen, Rückenschmerzen' },
      { id: 'BL-59', nameChinese: 'Fuyang', nameGerman: 'Fußrist-Yang', chineseCharacter: '跗陽', frequencyHz: 47.6, activeTime: '15-17h', mainEffect: 'Xi-Punkt des Yang-Qiao-Mai, Kopfschmerzen' },
      { id: 'BL-60', nameChinese: 'Kunlun', nameGerman: 'Kunlun-Berge', chineseCharacter: '昆侖', frequencyHz: 84.0, activeTime: '15-17h', mainEffect: 'Jing-Punkt, Kopfschmerzen, Nacken, Geburtshilfe', element: 'Feuer' },
      { id: 'BL-61', nameChinese: 'Pucan', nameGerman: 'Diener-Besucher', chineseCharacter: '僕參', frequencyHz: 49.0, activeTime: '15-17h', mainEffect: 'Fersenschmerzen, Epilepsie' },
      { id: 'BL-62', nameChinese: 'Shenmai', nameGerman: 'Ausdehnende Gefäß', chineseCharacter: '申脈', frequencyHz: 49.7, activeTime: '15-17h', mainEffect: 'Öffnungspunkt Yang-Qiao-Mai, Kopfschmerzen' },
      { id: 'BL-63', nameChinese: 'Jinmen', nameGerman: 'Goldenes Tor', chineseCharacter: '金門', frequencyHz: 50.4, activeTime: '15-17h', mainEffect: 'Xi-Punkt, Epilepsie, Rückenschmerzen' },
      { id: 'BL-64', nameChinese: 'Jinggu', nameGerman: 'Hauptknochen', chineseCharacter: '京骨', frequencyHz: 51.1, activeTime: '15-17h', mainEffect: 'Yuan-Punkt, Kopfschmerzen, Nackensteifheit' },
      { id: 'BL-65', nameChinese: 'Shugu', nameGerman: 'Gebundener Knochen', chineseCharacter: '束骨', frequencyHz: 51.8, activeTime: '15-17h', mainEffect: 'Shu-Punkt, Kopfschmerzen', element: 'Holz' },
      { id: 'BL-66', nameChinese: 'Zutonggu', nameGerman: 'Fuß-Tal-Passage', chineseCharacter: '足通谷', frequencyHz: 52.5, activeTime: '15-17h', mainEffect: 'Ying-Punkt, Kopfschmerzen, Nasenbluten', element: 'Wasser' },
      { id: 'BL-67', nameChinese: 'Zhiyin', nameGerman: 'Extremes Yin', chineseCharacter: '至陰', frequencyHz: 45.5, activeTime: '15-17h', mainEffect: 'Jing-Well-Punkt, Beckenendlage, Geburt', element: 'Metall' },
    ]
  },
  
  // ===== NIEREN-MERIDIAN (KI) - 27 Punkte =====
  {
    id: 'KI',
    name: 'Kidney Meridian',
    nameGerman: 'Nieren-Meridian',
    element: 'Wasser',
    activeTime: '17-19h',
    color: 'bg-teal-100',
    totalPoints: 27,
    points: [
      { id: 'KI-1', nameChinese: 'Yongquan', nameGerman: 'Sprudelnde Quelle', chineseCharacter: '湧泉', frequencyHz: 19.5, activeTime: '17-19h', mainEffect: 'Jing-Well-Punkt, Erdung, Bluthochdruck, Notfall', element: 'Holz' },
      { id: 'KI-2', nameChinese: 'Rangu', nameGerman: 'Brennendes Tal', chineseCharacter: '然谷', frequencyHz: 22.1, activeTime: '17-19h', mainEffect: 'Ying-Punkt, Nachtschweiß, Diabetes', element: 'Feuer' },
      { id: 'KI-3', nameChinese: 'Taixi', nameGerman: 'Große Meerenge', chineseCharacter: '太谿', frequencyHz: 26.0, activeTime: '17-19h', mainEffect: 'Shu-Punkt, Yuan-Punkt, Nieren-Stärkung', element: 'Erde' },
      { id: 'KI-4', nameChinese: 'Dazhong', nameGerman: 'Große Glocke', chineseCharacter: '大鐘', frequencyHz: 27.3, activeTime: '17-19h', mainEffect: 'Luo-Punkt, Willenskraft, Fersenschmerzen' },
      { id: 'KI-5', nameChinese: 'Shuiquan', nameGerman: 'Wasser-Quelle', chineseCharacter: '水泉', frequencyHz: 32.5, activeTime: '17-19h', mainEffect: 'Xi-Punkt, Menstruation, Blasenprobleme', element: 'Wasser' },
      { id: 'KI-6', nameChinese: 'Zhaohai', nameGerman: 'Leuchtender See', chineseCharacter: '照海', frequencyHz: 39.0, activeTime: '17-19h', mainEffect: 'Öffnungspunkt Yin-Qiao-Mai, Schlaflosigkeit, Hals' },
      { id: 'KI-7', nameChinese: 'Fuliu', nameGerman: 'Rückkehr des Stroms', chineseCharacter: '復溜', frequencyHz: 45.5, activeTime: '17-19h', mainEffect: 'Jing-Punkt, Schwitzen, Ödeme', element: 'Metall' },
      { id: 'KI-8', nameChinese: 'Jiaoxin', nameGerman: 'Kreuzungs-Vertrauen', chineseCharacter: '交信', frequencyHz: 35.1, activeTime: '17-19h', mainEffect: 'Xi-Punkt des Yin-Qiao-Mai, Menstruationsstörungen' },
      { id: 'KI-9', nameChinese: 'Zhubin', nameGerman: 'Gasthaus-Bau', chineseCharacter: '築賓', frequencyHz: 37.7, activeTime: '17-19h', mainEffect: 'Xi-Punkt des Yin-Wei-Mai, psychische Störungen' },
      { id: 'KI-10', nameChinese: 'Yingu', nameGerman: 'Yin-Tal', chineseCharacter: '陰谷', frequencyHz: 40.3, activeTime: '17-19h', mainEffect: 'He-Punkt, Knieprobleme, Impotenz', element: 'Wasser' },
      { id: 'KI-11', nameChinese: 'Henggu', nameGerman: 'Schambein', chineseCharacter: '橫骨', frequencyHz: 42.9, activeTime: '17-19h', mainEffect: 'Genitalprobleme, Harnverhalt' },
      { id: 'KI-12', nameChinese: 'Dahe', nameGerman: 'Große Herrlichkeit', chineseCharacter: '大赫', frequencyHz: 45.5, activeTime: '17-19h', mainEffect: 'Impotenz, vaginale Probleme' },
      { id: 'KI-13', nameChinese: 'Qixue', nameGerman: 'Qi-Höhle', chineseCharacter: '氣穴', frequencyHz: 48.1, activeTime: '17-19h', mainEffect: 'Menstruationsstörungen, Durchfall' },
      { id: 'KI-14', nameChinese: 'Siman', nameGerman: 'Vierfache Fülle', chineseCharacter: '四滿', frequencyHz: 50.7, activeTime: '17-19h', mainEffect: 'Bauchschmerzen, Durchfall' },
      { id: 'KI-15', nameChinese: 'Zhongzhu', nameGerman: 'Mitte eingießen', chineseCharacter: '中注', frequencyHz: 53.3, activeTime: '17-19h', mainEffect: 'Verstopfung, Menstruationsstörungen' },
      { id: 'KI-16', nameChinese: 'Huangshu', nameGerman: 'Vital-Shu', chineseCharacter: '肓俞', frequencyHz: 55.9, activeTime: '17-19h', mainEffect: 'Bauchschmerzen, Verstopfung' },
      { id: 'KI-17', nameChinese: 'Shangqu', nameGerman: 'Metall-Biegung', chineseCharacter: '商曲', frequencyHz: 58.5, activeTime: '17-19h', mainEffect: 'Bauchschmerzen, Verstopfung' },
      { id: 'KI-18', nameChinese: 'Shiguan', nameGerman: 'Stein-Tor', chineseCharacter: '石關', frequencyHz: 61.1, activeTime: '17-19h', mainEffect: 'Erbrechen, Unfruchtbarkeit' },
      { id: 'KI-19', nameChinese: 'Yindu', nameGerman: 'Yin-Metropole', chineseCharacter: '陰都', frequencyHz: 63.7, activeTime: '17-19h', mainEffect: 'Bauchschmerzen, Asthma' },
      { id: 'KI-20', nameChinese: 'Futonggu', nameGerman: 'Bauch-Tal-Passage', chineseCharacter: '腹通谷', frequencyHz: 66.3, activeTime: '17-19h', mainEffect: 'Bauchschmerzen, Erbrechen' },
      { id: 'KI-21', nameChinese: 'Youmen', nameGerman: 'Verstecktes Tor', chineseCharacter: '幽門', frequencyHz: 68.9, activeTime: '17-19h', mainEffect: 'Erbrechen, Durchfall, Magenschmerzen' },
      { id: 'KI-22', nameChinese: 'Bulang', nameGerman: 'Schreitende Galerie', chineseCharacter: '步廊', frequencyHz: 71.5, activeTime: '17-19h', mainEffect: 'Husten, Brustschmerzen' },
      { id: 'KI-23', nameChinese: 'Shenfeng', nameGerman: 'Geist-Siegel', chineseCharacter: '神封', frequencyHz: 74.1, activeTime: '17-19h', mainEffect: 'Husten, Brustschmerzen, Laktationsstörungen' },
      { id: 'KI-24', nameChinese: 'Lingxu', nameGerman: 'Geist-Ruine', chineseCharacter: '靈墟', frequencyHz: 76.7, activeTime: '17-19h', mainEffect: 'Husten, Brustschmerzen' },
      { id: 'KI-25', nameChinese: 'Shencang', nameGerman: 'Geist-Speicher', chineseCharacter: '神藏', frequencyHz: 79.3, activeTime: '17-19h', mainEffect: 'Husten, Asthma, Brustschmerzen' },
      { id: 'KI-26', nameChinese: 'Yuzhong', nameGerman: 'Anmutige Mitte', chineseCharacter: '彧中', frequencyHz: 81.9, activeTime: '17-19h', mainEffect: 'Husten, Brustschmerzen' },
      { id: 'KI-27', nameChinese: 'Shufu', nameGerman: 'Elegantes Haus', chineseCharacter: '俞府', frequencyHz: 91.0, activeTime: '17-19h', mainEffect: 'Asthma, Husten, Brustschmerzen' },
    ]
  },
  
  // ===== PERIKARD-MERIDIAN (PC) - 9 Punkte =====
  {
    id: 'PC',
    name: 'Pericardium Meridian',
    nameGerman: 'Perikard-Meridian',
    element: 'Feuer',
    activeTime: '19-21h',
    color: 'bg-pink-100',
    totalPoints: 9,
    points: [
      { id: 'PC-1', nameChinese: 'Tianchi', nameGerman: 'Himmlischer Teich', chineseCharacter: '天池', frequencyHz: 14.4, activeTime: '19-21h', mainEffect: 'Brustschmerzen, Mastitis' },
      { id: 'PC-2', nameChinese: 'Tianquan', nameGerman: 'Himmlische Quelle', chineseCharacter: '天泉', frequencyHz: 18.0, activeTime: '19-21h', mainEffect: 'Herzschmerzen, Husten' },
      { id: 'PC-3', nameChinese: 'Quze', nameGerman: 'Gekrümmte Meerenge', chineseCharacter: '曲澤', frequencyHz: 21.6, activeTime: '19-21h', mainEffect: 'He-Punkt, Herzrhythmusstörungen', element: 'Wasser' },
      { id: 'PC-4', nameChinese: 'Ximen', nameGerman: 'Spalt-Tor', chineseCharacter: '郄門', frequencyHz: 28.8, activeTime: '19-21h', mainEffect: 'Xi-Punkt, Herzschmerzen, Angst' },
      { id: 'PC-5', nameChinese: 'Jianshi', nameGerman: 'Vermittler', chineseCharacter: '間使', frequencyHz: 36.0, activeTime: '19-21h', mainEffect: 'Jing-Punkt, Herzklopfen, Erbrechen', element: 'Metall' },
      { id: 'PC-6', nameChinese: 'Neiguan', nameGerman: 'Innere Barriere', chineseCharacter: '內關', frequencyHz: 43.2, activeTime: '19-21h', mainEffect: 'Luo-Punkt, Übelkeit, Motion Sickness, Öffnungspunkt Yin-Wei-Mai' },
      { id: 'PC-7', nameChinese: 'Daling', nameGerman: 'Große Mauer', chineseCharacter: '大陵', frequencyHz: 50.4, activeTime: '19-21h', mainEffect: 'Shu-Punkt, Yuan-Punkt, Sedierung, Angst', element: 'Erde' },
      { id: 'PC-8', nameChinese: 'Laogong', nameGerman: 'Arbeitspalast', chineseCharacter: '勞宮', frequencyHz: 54.0, activeTime: '19-21h', mainEffect: 'Ying-Punkt, Herzhitze, Stress, Mundgeschwüre', element: 'Feuer' },
      { id: 'PC-9', nameChinese: 'Zhongchong', nameGerman: 'Mittlerer Ansturm', chineseCharacter: '中衝', frequencyHz: 57.6, activeTime: '19-21h', mainEffect: 'Jing-Well-Punkt, Bewusstlosigkeit, Schock, Notfall', element: 'Holz' },
    ]
  },
  
  // ===== DREI-ERWÄRMER-MERIDIAN (TE) - 23 Punkte =====
  {
    id: 'TE',
    name: 'Triple Energizer Meridian',
    nameGerman: 'Drei-Erwärmer-Meridian',
    element: 'Feuer',
    activeTime: '21-23h',
    color: 'bg-cyan-100',
    totalPoints: 23,
    points: [
      { id: 'TE-1', nameChinese: 'Guanchong', nameGerman: 'Tor-Ansturm', chineseCharacter: '關衝', frequencyHz: 28.8, activeTime: '21-23h', mainEffect: 'Jing-Well-Punkt, Kopfschmerzen, Fieber', element: 'Metall' },
      { id: 'TE-2', nameChinese: 'Yemen', nameGerman: 'Flüssigkeits-Tor', chineseCharacter: '液門', frequencyHz: 32.4, activeTime: '21-23h', mainEffect: 'Ying-Punkt, Kopfschmerzen, Tinnitus', element: 'Wasser' },
      { id: 'TE-3', nameChinese: 'Zhongzhu', nameGerman: 'Mittlere Insel', chineseCharacter: '中渚', frequencyHz: 43.2, activeTime: '21-23h', mainEffect: 'Shu-Punkt, Handschmerzen, Kopfschmerzen', element: 'Holz' },
      { id: 'TE-4', nameChinese: 'Yangchi', nameGerman: 'Yang-Teich', chineseCharacter: '陽池', frequencyHz: 50.4, activeTime: '21-23h', mainEffect: 'Yuan-Punkt, Handgelenk, Diabetes' },
      { id: 'TE-5', nameChinese: 'Waiguan', nameGerman: 'Äußere Barriere', chineseCharacter: '外關', frequencyHz: 72.0, activeTime: '21-23h', mainEffect: 'Luo-Punkt, Öffnungspunkt Yang-Wei-Mai, Erkältung, Immunsystem' },
      { id: 'TE-6', nameChinese: 'Zhigou', nameGerman: 'Zweig-Graben', chineseCharacter: '支溝', frequencyHz: 54.0, activeTime: '21-23h', mainEffect: 'Jing-Punkt, Verstopfung, Flankenschmerzen', element: 'Feuer' },
      { id: 'TE-7', nameChinese: 'Huizong', nameGerman: 'Versammlungs-Vorfahre', chineseCharacter: '會宗', frequencyHz: 57.6, activeTime: '21-23h', mainEffect: 'Xi-Punkt, Taubheit, Epilepsie' },
      { id: 'TE-8', nameChinese: 'Sanyangluo', nameGerman: 'Drei-Yang-Verbindung', chineseCharacter: '三陽絡', frequencyHz: 61.2, activeTime: '21-23h', mainEffect: 'Taubheit, Zahnschmerzen' },
      { id: 'TE-9', nameChinese: 'Sidu', nameGerman: 'Vier Flüsse', chineseCharacter: '四瀆', frequencyHz: 64.8, activeTime: '21-23h', mainEffect: 'Taubheit, Zahnschmerzen' },
      { id: 'TE-10', nameChinese: 'Tianjing', nameGerman: 'Himmlischer Brunnen', chineseCharacter: '天井', frequencyHz: 68.4, activeTime: '21-23h', mainEffect: 'He-Punkt, Ellenbogenschmerzen, Lymphknoten', element: 'Erde' },
      { id: 'TE-11', nameChinese: 'Qinglengyuan', nameGerman: 'Kühle Tiefe', chineseCharacter: '清冷淵', frequencyHz: 72.0, activeTime: '21-23h', mainEffect: 'Schulterschmerzen, Kopfschmerzen' },
      { id: 'TE-12', nameChinese: 'Xiaoluo', nameGerman: 'Abfließender Luo', chineseCharacter: '消濼', frequencyHz: 75.6, activeTime: '21-23h', mainEffect: 'Kopfschmerzen, Nackensteifheit' },
      { id: 'TE-13', nameChinese: 'Naohui', nameGerman: 'Oberarm-Treffen', chineseCharacter: '臑會', frequencyHz: 79.2, activeTime: '21-23h', mainEffect: 'Schulterschmerzen, Kropf' },
      { id: 'TE-14', nameChinese: 'Jianliao', nameGerman: 'Schulter-Spalt', chineseCharacter: '肩髎', frequencyHz: 100.8, activeTime: '21-23h', mainEffect: 'Schulterschmerzen, Armlähmung' },
      { id: 'TE-15', nameChinese: 'Tianliao', nameGerman: 'Himmlischer Spalt', chineseCharacter: '天髎', frequencyHz: 86.4, activeTime: '21-23h', mainEffect: 'Schulter-Nacken-Schmerzen' },
      { id: 'TE-16', nameChinese: 'Tianyou', nameGerman: 'Himmelsfenster', chineseCharacter: '天牖', frequencyHz: 90.0, activeTime: '21-23h', mainEffect: 'Kopfschmerzen, Nackensteifheit, Taubheit' },
      { id: 'TE-17', nameChinese: 'Yifeng', nameGerman: 'Windschirm', chineseCharacter: '翳風', frequencyHz: 115.2, activeTime: '21-23h', mainEffect: 'Tinnitus, Schwerhörigkeit, Gesichtslähmung' },
      { id: 'TE-18', nameChinese: 'Qimai', nameGerman: 'Spasmus-Gefäß', chineseCharacter: '契脈', frequencyHz: 97.2, activeTime: '21-23h', mainEffect: 'Kopfschmerzen, Tinnitus' },
      { id: 'TE-19', nameChinese: 'Luxi', nameGerman: 'Schädel-Ruhe', chineseCharacter: '顱息', frequencyHz: 100.8, activeTime: '21-23h', mainEffect: 'Kopfschmerzen, Tinnitus, Epilepsie' },
      { id: 'TE-20', nameChinese: 'Jiaosun', nameGerman: 'Winkel-Nachfolger', chineseCharacter: '角孫', frequencyHz: 104.4, activeTime: '21-23h', mainEffect: 'Zahnschmerzen, Ohrenschmerzen' },
      { id: 'TE-21', nameChinese: 'Ermen', nameGerman: 'Ohr-Tor', chineseCharacter: '耳門', frequencyHz: 108.0, activeTime: '21-23h', mainEffect: 'Tinnitus, Schwerhörigkeit, Zahnschmerzen' },
      { id: 'TE-22', nameChinese: 'Erheliao', nameGerman: 'Ohr-Harmonie-Spalt', chineseCharacter: '耳和髎', frequencyHz: 111.6, activeTime: '21-23h', mainEffect: 'Kopfschmerzen, Tinnitus' },
      { id: 'TE-23', nameChinese: 'Sizhukong', nameGerman: 'Seide-Bambus-Loch', chineseCharacter: '絲竹空', frequencyHz: 129.6, activeTime: '21-23h', mainEffect: 'Migräne, Augenschmerzen, Gesichtslähmung' },
    ]
  },
  
  // ===== GALLENBLASEN-MERIDIAN (GB) - 44 Punkte =====
  {
    id: 'GB',
    name: 'Gallbladder Meridian',
    nameGerman: 'Gallenblasen-Meridian',
    element: 'Holz',
    activeTime: '23-01h',
    color: 'bg-lime-100',
    totalPoints: 44,
    points: [
      { id: 'GB-1', nameChinese: 'Tongziliao', nameGerman: 'Pupillen-Spalt', chineseCharacter: '瞳子髎', frequencyHz: 22.4, activeTime: '23-01h', mainEffect: 'Augenleiden, Kopfschmerz, Sehstörungen' },
      { id: 'GB-2', nameChinese: 'Tinghui', nameGerman: 'Hör-Treffen', chineseCharacter: '聽會', frequencyHz: 24.2, activeTime: '23-01h', mainEffect: 'Tinnitus, Schwerhörigkeit, Zahnschmerzen' },
      { id: 'GB-3', nameChinese: 'Shangguan', nameGerman: 'Oberes Tor', chineseCharacter: '上關', frequencyHz: 26.0, activeTime: '23-01h', mainEffect: 'Kiefergelenk, Tinnitus, Gesichtslähmung' },
      { id: 'GB-4', nameChinese: 'Hanyan', nameGerman: 'Kiefer-Ruhe', chineseCharacter: '頷厭', frequencyHz: 27.8, activeTime: '23-01h', mainEffect: 'Migräne, Schwindel, Tinnitus' },
      { id: 'GB-5', nameChinese: 'Xuanlu', nameGerman: 'Hängender Schädel', chineseCharacter: '懸顱', frequencyHz: 29.6, activeTime: '23-01h', mainEffect: 'Migräne, Zahnschmerzen' },
      { id: 'GB-6', nameChinese: 'Xuanli', nameGerman: 'Hängende Haarsträhne', chineseCharacter: '懸厘', frequencyHz: 31.4, activeTime: '23-01h', mainEffect: 'Migräne, Augenschmerzen' },
      { id: 'GB-7', nameChinese: 'Qubin', nameGerman: 'Gebogene Schläfe', chineseCharacter: '曲鬢', frequencyHz: 33.2, activeTime: '23-01h', mainEffect: 'Kiefergelenk, Kopfschmerzen' },
      { id: 'GB-8', nameChinese: 'Shuaigu', nameGerman: 'Führendes Tal', chineseCharacter: '率谷', frequencyHz: 44.8, activeTime: '23-01h', mainEffect: 'Migräne, Übelkeit, Alkohol-Kater' },
      { id: 'GB-9', nameChinese: 'Tianchong', nameGerman: 'Himmlischer Ansturm', chineseCharacter: '天沖', frequencyHz: 36.8, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Epilepsie, Zahnfleischschwellung' },
      { id: 'GB-10', nameChinese: 'Fubai', nameGerman: 'Schwebendes Weiß', chineseCharacter: '浮白', frequencyHz: 38.6, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Tinnitus, Zahnschmerzen' },
      { id: 'GB-11', nameChinese: 'Touqiaoyin', nameGerman: 'Kopf-Yin-Öffnung', chineseCharacter: '頭竅陰', frequencyHz: 40.4, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Tinnitus, Schwerhörigkeit' },
      { id: 'GB-12', nameChinese: 'Wangu', nameGerman: 'Vollendeter Knochen', chineseCharacter: '完骨', frequencyHz: 42.2, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Schlaflosigkeit, Gesichtslähmung' },
      { id: 'GB-13', nameChinese: 'Benshen', nameGerman: 'Geist-Wurzel', chineseCharacter: '本神', frequencyHz: 44.0, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Epilepsie, Angst' },
      { id: 'GB-14', nameChinese: 'Yangbai', nameGerman: 'Yang-Weiß', chineseCharacter: '陽白', frequencyHz: 56.0, activeTime: '23-01h', mainEffect: 'Stirnkopfschmerz, Augenprobleme, Gesichtslähmung' },
      { id: 'GB-15', nameChinese: 'Toulinqi', nameGerman: 'Kopf-Tränen', chineseCharacter: '頭臨泣', frequencyHz: 47.6, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Sehstörungen' },
      { id: 'GB-16', nameChinese: 'Muchuang', nameGerman: 'Augen-Fenster', chineseCharacter: '目窗', frequencyHz: 49.4, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Sehstörungen, Gesichtsschwellung' },
      { id: 'GB-17', nameChinese: 'Zhengying', nameGerman: 'Aufrechte Nahrung', chineseCharacter: '正營', frequencyHz: 51.2, activeTime: '23-01h', mainEffect: 'Migräne, Schwindel' },
      { id: 'GB-18', nameChinese: 'Chengling', nameGerman: 'Geist-Stütze', chineseCharacter: '承靈', frequencyHz: 53.0, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Nasenbluten' },
      { id: 'GB-19', nameChinese: 'Naokong', nameGerman: 'Gehirn-Höhle', chineseCharacter: '腦空', frequencyHz: 54.8, activeTime: '23-01h', mainEffect: 'Kopfschmerzen, Nackensteifheit, Epilepsie' },
      { id: 'GB-20', nameChinese: 'Fengchi', nameGerman: 'Windpool', chineseCharacter: '風池', frequencyHz: 67.2, activeTime: '23-01h', mainEffect: 'Nackenverspannungen, Erkältung, Kopfschmerzen' },
      { id: 'GB-21', nameChinese: 'Jianjing', nameGerman: 'Schulter-Brunnen', chineseCharacter: '肩井', frequencyHz: 72.8, activeTime: '23-01h', mainEffect: 'Schulterspannung, Kopfschmerz, Laktationsstörungen' },
      { id: 'GB-22', nameChinese: 'Yuanye', nameGerman: 'Achselhöhlen-Abgrund', chineseCharacter: '淵腋', frequencyHz: 60.2, activeTime: '23-01h', mainEffect: 'Flankenschmerzen, Achselschmerzen' },
      { id: 'GB-23', nameChinese: 'Zhejin', nameGerman: 'Flanken-Sehne', chineseCharacter: '輒筋', frequencyHz: 62.0, activeTime: '23-01h', mainEffect: 'Flankenschmerzen, Asthma' },
      { id: 'GB-24', nameChinese: 'Riyue', nameGerman: 'Sonne und Mond', chineseCharacter: '日月', frequencyHz: 63.8, activeTime: '23-01h', mainEffect: 'Mu-Punkt der Gallenblase, Gallenblasenerkrankungen' },
      { id: 'GB-25', nameChinese: 'Jingmen', nameGerman: 'Hauptstadt-Tor', chineseCharacter: '京門', frequencyHz: 65.6, activeTime: '23-01h', mainEffect: 'Mu-Punkt der Nieren, Flankenschmerzen' },
      { id: 'GB-26', nameChinese: 'Daimai', nameGerman: 'Gürtelgefäß', chineseCharacter: '帶脈', frequencyHz: 67.4, activeTime: '23-01h', mainEffect: 'Menstruationsstörungen, Leukorrhoe' },
      { id: 'GB-27', nameChinese: 'Wushu', nameGerman: 'Fünf Drehpunkte', chineseCharacter: '五樞', frequencyHz: 69.2, activeTime: '23-01h', mainEffect: 'Leistenschmerzen, Verstopfung' },
      { id: 'GB-28', nameChinese: 'Weidao', nameGerman: 'Verbindungspfad', chineseCharacter: '維道', frequencyHz: 71.0, activeTime: '23-01h', mainEffect: 'Leistenschmerzen, vaginaler Ausfluss' },
      { id: 'GB-29', nameChinese: 'Juliao', nameGerman: 'Hockender Spalt', chineseCharacter: '居髎', frequencyHz: 72.8, activeTime: '23-01h', mainEffect: 'Hüftschmerzen, Beinlähmung' },
      { id: 'GB-30', nameChinese: 'Huantiao', nameGerman: 'Springender Kreis', chineseCharacter: '環跳', frequencyHz: 84.0, activeTime: '23-01h', mainEffect: 'Ischiasschmerzen, Hüftschmerzen, Beinlähmung' },
      { id: 'GB-31', nameChinese: 'Fengshi', nameGerman: 'Wind-Markt', chineseCharacter: '風市', frequencyHz: 76.4, activeTime: '23-01h', mainEffect: 'Beinlähmung, Juckreiz, Urtikaria' },
      { id: 'GB-32', nameChinese: 'Zhongdu', nameGerman: 'Mittlerer Graben', chineseCharacter: '中瀆', frequencyHz: 78.2, activeTime: '23-01h', mainEffect: 'Beinschmerzen, Taubheit' },
      { id: 'GB-33', nameChinese: 'Xiyangguan', nameGerman: 'Knie-Yang-Tor', chineseCharacter: '膝陽關', frequencyHz: 80.0, activeTime: '23-01h', mainEffect: 'Knieschmerzen, Beinlähmung' },
      { id: 'GB-34', nameChinese: 'Yanglingquan', nameGerman: 'Yang-Hügel-Quelle', chineseCharacter: '陽陵泉', frequencyHz: 89.6, activeTime: '23-01h', mainEffect: 'He-Punkt, Hui-Punkt der Sehnen, Muskel-Sehnen-Probleme', element: 'Erde' },
      { id: 'GB-35', nameChinese: 'Yangjiao', nameGerman: 'Yang-Kreuzung', chineseCharacter: '陽交', frequencyHz: 83.6, activeTime: '23-01h', mainEffect: 'Xi-Punkt Yang-Wei-Mai, Beinschmerzen' },
      { id: 'GB-36', nameChinese: 'Waiqiu', nameGerman: 'Äußerer Hügel', chineseCharacter: '外丘', frequencyHz: 85.4, activeTime: '23-01h', mainEffect: 'Xi-Punkt, Nackensteifheit, Beinkrämpfe' },
      { id: 'GB-37', nameChinese: 'Guangming', nameGerman: 'Helles Licht', chineseCharacter: '光明', frequencyHz: 87.2, activeTime: '23-01h', mainEffect: 'Luo-Punkt, Sehstörungen, Brustschmerzen' },
      { id: 'GB-38', nameChinese: 'Yangfu', nameGerman: 'Yang-Hilfe', chineseCharacter: '陽輔', frequencyHz: 89.0, activeTime: '23-01h', mainEffect: 'Jing-Punkt, Migräne, Knöchelschmerzen', element: 'Feuer' },
      { id: 'GB-39', nameChinese: 'Xuanzhong', nameGerman: 'Hängende Glocke', chineseCharacter: '懸鐘', frequencyHz: 90.8, activeTime: '23-01h', mainEffect: 'Hui-Punkt des Marks, Nackensteifheit, Hemiplegie' },
      { id: 'GB-40', nameChinese: 'Qiuxu', nameGerman: 'Hügel-Ruine', chineseCharacter: '丘墟', frequencyHz: 92.6, activeTime: '23-01h', mainEffect: 'Yuan-Punkt, Knöchelschmerzen, Flankenschmerzen' },
      { id: 'GB-41', nameChinese: 'Zulinqi', nameGerman: 'Fuß-Tränen', chineseCharacter: '足臨泣', frequencyHz: 96.8, activeTime: '23-01h', mainEffect: 'Shu-Punkt, Öffnungspunkt Dai-Mai, Kopfschmerzen, Menstruation', element: 'Holz' },
      { id: 'GB-42', nameChinese: 'Diwuhui', nameGerman: 'Erd-Fünf-Treffen', chineseCharacter: '地五會', frequencyHz: 96.2, activeTime: '23-01h', mainEffect: 'Fußschmerzen, Brustschmerzen' },
      { id: 'GB-43', nameChinese: 'Xiaxi', nameGerman: 'Geklemmter Bach', chineseCharacter: '俠谿', frequencyHz: 98.0, activeTime: '23-01h', mainEffect: 'Ying-Punkt, Kopfschmerzen, Tinnitus', element: 'Wasser' },
      { id: 'GB-44', nameChinese: 'Zuqiaoyin', nameGerman: 'Fuß-Yin-Öffnung', chineseCharacter: '足竅陰', frequencyHz: 100.8, activeTime: '23-01h', mainEffect: 'Jing-Well-Punkt, Migräne, Schlaflosigkeit', element: 'Metall' },
    ]
  },
  
  // ===== LEBER-MERIDIAN (LV/LR) - 14 Punkte =====
  {
    id: 'LV',
    name: 'Liver Meridian',
    nameGerman: 'Leber-Meridian',
    element: 'Holz',
    activeTime: '01-03h',
    color: 'bg-emerald-100',
    totalPoints: 14,
    points: [
      { id: 'LV-1', nameChinese: 'Dadun', nameGerman: 'Großer Dicker', chineseCharacter: '大敦', frequencyHz: 32.4, activeTime: '01-03h', mainEffect: 'Jing-Well-Punkt, Menstruationsstörungen, Hernie', element: 'Holz' },
      { id: 'LV-2', nameChinese: 'Xingjian', nameGerman: 'Wandelndes Intervall', chineseCharacter: '行間', frequencyHz: 40.5, activeTime: '01-03h', mainEffect: 'Ying-Punkt, Kopfschmerzen, Augenprobleme, Leber-Feuer', element: 'Feuer' },
      { id: 'LV-3', nameChinese: 'Taichong', nameGerman: 'Große Übersteigung', chineseCharacter: '太沖', frequencyHz: 48.6, activeTime: '01-03h', mainEffect: 'Shu-Punkt, Yuan-Punkt, Stress, Hypertonie, Kopfschmerzen', element: 'Erde' },
      { id: 'LV-4', nameChinese: 'Zhongfeng', nameGerman: 'Mittleres Siegel', chineseCharacter: '中封', frequencyHz: 56.7, activeTime: '01-03h', mainEffect: 'Jing-Punkt, Urogenitalprobleme, Hernie', element: 'Metall' },
      { id: 'LV-5', nameChinese: 'Ligou', nameGerman: 'Holzwurm-Graben', chineseCharacter: '蠡溝', frequencyHz: 64.8, activeTime: '01-03h', mainEffect: 'Luo-Punkt, Genitalprobleme, Depression' },
      { id: 'LV-6', nameChinese: 'Zhongdu', nameGerman: 'Zentrale Hauptstadt', chineseCharacter: '中都', frequencyHz: 72.9, activeTime: '01-03h', mainEffect: 'Xi-Punkt, Akute Blutungen, Hernie' },
      { id: 'LV-7', nameChinese: 'Xiguan', nameGerman: 'Knie-Tor', chineseCharacter: '膝關', frequencyHz: 81.0, activeTime: '01-03h', mainEffect: 'Knieschmerzen, Beinlähmung' },
      { id: 'LV-8', nameChinese: 'Ququan', nameGerman: 'Gekrümmte Quelle', chineseCharacter: '曲泉', frequencyHz: 97.2, activeTime: '01-03h', mainEffect: 'He-Punkt, Urogenitale Probleme, Knieschmerzen', element: 'Wasser' },
      { id: 'LV-9', nameChinese: 'Yinbao', nameGerman: 'Yin-Umhüllung', chineseCharacter: '陰包', frequencyHz: 89.1, activeTime: '01-03h', mainEffect: 'Menstruationsstörungen, Harnprobleme' },
      { id: 'LV-10', nameChinese: 'Zuwuli', nameGerman: 'Fuß-Fünf-Li', chineseCharacter: '足五里', frequencyHz: 97.2, activeTime: '01-03h', mainEffect: 'Leistenschmerzen, Harnretention' },
      { id: 'LV-11', nameChinese: 'Yinlian', nameGerman: 'Yin-Rand', chineseCharacter: '陰廉', frequencyHz: 105.3, activeTime: '01-03h', mainEffect: 'Menstruationsstörungen, Oberschenkelschmerzen' },
      { id: 'LV-12', nameChinese: 'Jimai', nameGerman: 'Schnelles Gefäß', chineseCharacter: '急脈', frequencyHz: 113.4, activeTime: '01-03h', mainEffect: 'Hernie, Genitalschmerzen' },
      { id: 'LV-13', nameChinese: 'Zhangmen', nameGerman: 'Kapitel-Tor', chineseCharacter: '章門', frequencyHz: 121.5, activeTime: '01-03h', mainEffect: 'Mu-Punkt der Milz, Hui-Punkt der Zang-Organe, Milz-Leber-Disharmonie' },
      { id: 'LV-14', nameChinese: 'Qimen', nameGerman: 'Periode-Tor', chineseCharacter: '期門', frequencyHz: 113.4, activeTime: '01-03h', mainEffect: 'Mu-Punkt der Leber, Leber-Qi-Stagnation, Flankenschmerzen' },
    ]
  },
  
  // ===== LENKERGEFÄSS / DU MAI (GV) - 28 Punkte =====
  {
    id: 'GV',
    name: 'Governing Vessel',
    nameGerman: 'Lenkergefäß (Du Mai)',
    element: 'Yang',
    activeTime: 'ganztags',
    color: 'bg-amber-100',
    totalPoints: 28,
    points: [
      { id: 'GV-1', nameChinese: 'Changqiang', nameGerman: 'Lange Stärke', chineseCharacter: '長強', frequencyHz: 15.0, activeTime: 'ganztags', mainEffect: 'Luo-Punkt, Hämorrhoiden, Steißbeinschmerzen' },
      { id: 'GV-2', nameChinese: 'Yaoshu', nameGerman: 'Lenden-Shu', chineseCharacter: '腰俞', frequencyHz: 17.1, activeTime: 'ganztags', mainEffect: 'Rückenschmerzen, Menstruationsstörungen' },
      { id: 'GV-3', nameChinese: 'Yaoyangguan', nameGerman: 'Lenden-Yang-Tor', chineseCharacter: '腰陽關', frequencyHz: 19.2, activeTime: 'ganztags', mainEffect: 'Rückenschmerzen, Impotenz' },
      { id: 'GV-4', nameChinese: 'Mingmen', nameGerman: 'Lebenstor', chineseCharacter: '命門', frequencyHz: 30.0, activeTime: 'ganztags', mainEffect: 'Nierenessenz, Rückenstärkung, Impotenz' },
      { id: 'GV-5', nameChinese: 'Xuanshu', nameGerman: 'Hängender Drehpunkt', chineseCharacter: '懸樞', frequencyHz: 23.4, activeTime: 'ganztags', mainEffect: 'Rückenschmerzen, Durchfall' },
      { id: 'GV-6', nameChinese: 'Jizhong', nameGerman: 'Wirbelsäulen-Mitte', chineseCharacter: '脊中', frequencyHz: 25.5, activeTime: 'ganztags', mainEffect: 'Rückenschmerzen, Durchfall' },
      { id: 'GV-7', nameChinese: 'Zhongshu', nameGerman: 'Zentraler Drehpunkt', chineseCharacter: '中樞', frequencyHz: 27.6, activeTime: 'ganztags', mainEffect: 'Rückenschmerzen, Gelbsucht' },
      { id: 'GV-8', nameChinese: 'Jinsuo', nameGerman: 'Sehnen-Kontraktion', chineseCharacter: '筋縮', frequencyHz: 29.7, activeTime: 'ganztags', mainEffect: 'Epilepsie, Rückenschmerzen' },
      { id: 'GV-9', nameChinese: 'Zhiyang', nameGerman: 'Extremes Yang', chineseCharacter: '至陽', frequencyHz: 31.8, activeTime: 'ganztags', mainEffect: 'Husten, Asthma, Gelbsucht' },
      { id: 'GV-10', nameChinese: 'Lingtai', nameGerman: 'Geist-Plattform', chineseCharacter: '靈台', frequencyHz: 33.9, activeTime: 'ganztags', mainEffect: 'Husten, Nackensteifheit' },
      { id: 'GV-11', nameChinese: 'Shendao', nameGerman: 'Geist-Pfad', chineseCharacter: '神道', frequencyHz: 36.0, activeTime: 'ganztags', mainEffect: 'Herzschmerzen, Gedächtnisstörungen' },
      { id: 'GV-12', nameChinese: 'Shenzhu', nameGerman: 'Körper-Pfeiler', chineseCharacter: '身柱', frequencyHz: 38.1, activeTime: 'ganztags', mainEffect: 'Husten, Epilepsie bei Kindern' },
      { id: 'GV-13', nameChinese: 'Taodao', nameGerman: 'Töpfer-Weg', chineseCharacter: '陶道', frequencyHz: 40.2, activeTime: 'ganztags', mainEffect: 'Fieber, Malaria, Steifheit' },
      { id: 'GV-14', nameChinese: 'Dazhui', nameGerman: 'Großer Wirbel', chineseCharacter: '大椎', frequencyHz: 52.5, activeTime: 'ganztags', mainEffect: 'Treffpunkt aller Yang-Meridiane, Fieber, Immunsystem' },
      { id: 'GV-15', nameChinese: 'Yamen', nameGerman: 'Stummes Tor', chineseCharacter: '瘂門', frequencyHz: 44.4, activeTime: 'ganztags', mainEffect: 'Sprachstörungen, Epilepsie' },
      { id: 'GV-16', nameChinese: 'Fengfu', nameGerman: 'Wind-Palast', chineseCharacter: '風府', frequencyHz: 46.5, activeTime: 'ganztags', mainEffect: 'Kopfschmerzen, Nackensteifheit, Wind-Ausleitung' },
      { id: 'GV-17', nameChinese: 'Naohu', nameGerman: 'Gehirn-Tür', chineseCharacter: '腦戶', frequencyHz: 48.6, activeTime: 'ganztags', mainEffect: 'Kopfschmerzen, Epilepsie' },
      { id: 'GV-18', nameChinese: 'Qiangjian', nameGerman: 'Steifes Intervall', chineseCharacter: '強間', frequencyHz: 50.7, activeTime: 'ganztags', mainEffect: 'Kopfschmerzen, Schwindel' },
      { id: 'GV-19', nameChinese: 'Houding', nameGerman: 'Hinterer Scheitel', chineseCharacter: '後頂', frequencyHz: 52.8, activeTime: 'ganztags', mainEffect: 'Kopfschmerzen, Schwindel' },
      { id: 'GV-20', nameChinese: 'Baihui', nameGerman: 'Hundert Begegnungen', chineseCharacter: '百會', frequencyHz: 40.0, activeTime: 'ganztags', mainEffect: 'Bewusstsein, Kopfschmerzen, alle Yang-Meridiane, Aufstiegspunkt' },
      { id: 'GV-21', nameChinese: 'Qianding', nameGerman: 'Vorderer Scheitel', chineseCharacter: '前頂', frequencyHz: 57.0, activeTime: 'ganztags', mainEffect: 'Kopfschmerzen, Schwindel, Epilepsie' },
      { id: 'GV-22', nameChinese: 'Xinhui', nameGerman: 'Fontanelle-Treffen', chineseCharacter: '囟會', frequencyHz: 59.1, activeTime: 'ganztags', mainEffect: 'Kopfschmerzen, Schwindel' },
      { id: 'GV-23', nameChinese: 'Shangxing', nameGerman: 'Oberer Stern', chineseCharacter: '上星', frequencyHz: 61.2, activeTime: 'ganztags', mainEffect: 'Nasenbluten, Kopfschmerzen, Augenprobleme' },
      { id: 'GV-24', nameChinese: 'Shenting', nameGerman: 'Geist-Hof', chineseCharacter: '神庭', frequencyHz: 45.0, activeTime: 'ganztags', mainEffect: 'Beruhigung, Klarheit, Epilepsie, Angst' },
      { id: 'GV-25', nameChinese: 'Suliao', nameGerman: 'Nasenspitzen-Spalt', chineseCharacter: '素髎', frequencyHz: 65.4, activeTime: 'ganztags', mainEffect: 'Nasenverstopfung, Bewusstlosigkeit' },
      { id: 'GV-26', nameChinese: 'Renzhong', nameGerman: 'Mitte des Menschen', chineseCharacter: '人中', frequencyHz: 48.0, activeTime: 'ganztags', mainEffect: 'Notfall, Bewusstlosigkeit, Schock, Wiederbelebung' },
      { id: 'GV-27', nameChinese: 'Duiduan', nameGerman: 'Austausch-Ende', chineseCharacter: '兌端', frequencyHz: 69.6, activeTime: 'ganztags', mainEffect: 'Zahnfleischprobleme, Nasenverstopfung' },
      { id: 'GV-28', nameChinese: 'Yinjiao', nameGerman: 'Zahnfleisch-Kreuzung', chineseCharacter: '齦交', frequencyHz: 71.7, activeTime: 'ganztags', mainEffect: 'Zahnfleischentzündung, Nasenverstopfung' },
    ]
  },
  
  // ===== KONZEPTIONSGEFÄSS / REN MAI (CV) - 24 Punkte =====
  {
    id: 'CV',
    name: 'Conception Vessel',
    nameGerman: 'Konzeptionsgefäß (Ren Mai)',
    element: 'Yin',
    activeTime: 'ganztags',
    color: 'bg-rose-100',
    totalPoints: 24,
    points: [
      { id: 'CV-1', nameChinese: 'Huiyin', nameGerman: 'Yin-Treffen', chineseCharacter: '會陰', frequencyHz: 12.0, activeTime: 'ganztags', mainEffect: 'Bewusstlosigkeit, Harnprobleme, Prolaps' },
      { id: 'CV-2', nameChinese: 'Qugu', nameGerman: 'Gekrümmter Knochen', chineseCharacter: '曲骨', frequencyHz: 14.4, activeTime: 'ganztags', mainEffect: 'Blasenprobleme, Impotenz' },
      { id: 'CV-3', nameChinese: 'Zhongji', nameGerman: 'Mittlerer Pol', chineseCharacter: '中極', frequencyHz: 18.0, activeTime: 'ganztags', mainEffect: 'Mu-Punkt der Blase, Blase, Menstruation' },
      { id: 'CV-4', nameChinese: 'Guanyuan', nameGerman: 'Tor des Ursprungs', chineseCharacter: '關元', frequencyHz: 21.6, activeTime: 'ganztags', mainEffect: 'Mu-Punkt des Dünndarms, Tonisierung, Erschöpfung' },
      { id: 'CV-5', nameChinese: 'Shimen', nameGerman: 'Stein-Tor', chineseCharacter: '石門', frequencyHz: 25.2, activeTime: 'ganztags', mainEffect: 'Mu-Punkt des Dreifach-Erwärmers, Bauchschmerzen' },
      { id: 'CV-6', nameChinese: 'Qihai', nameGerman: 'Qi-Meer', chineseCharacter: '氣海', frequencyHz: 28.8, activeTime: 'ganztags', mainEffect: 'Tonisierung, Erschöpfung, Bauchschmerzen' },
      { id: 'CV-7', nameChinese: 'Yinjiao', nameGerman: 'Yin-Kreuzung', chineseCharacter: '陰交', frequencyHz: 32.4, activeTime: 'ganztags', mainEffect: 'Menstruationsstörungen, Hernie' },
      { id: 'CV-8', nameChinese: 'Shenque', nameGerman: 'Geist-Tor', chineseCharacter: '神闕', frequencyHz: 36.0, activeTime: 'ganztags', mainEffect: 'Nabel, Durchfall, Moxibustion (keine Nadel!)' },
      { id: 'CV-9', nameChinese: 'Shuifen', nameGerman: 'Wasser-Teilung', chineseCharacter: '水分', frequencyHz: 39.6, activeTime: 'ganztags', mainEffect: 'Ödeme, Durchfall, Aszites' },
      { id: 'CV-10', nameChinese: 'Xiawan', nameGerman: 'Unterer Magenmund', chineseCharacter: '下脘', frequencyHz: 43.2, activeTime: 'ganztags', mainEffect: 'Magenschmerzen, Erbrechen' },
      { id: 'CV-11', nameChinese: 'Jianli', nameGerman: 'Innerer Aufbau', chineseCharacter: '建里', frequencyHz: 46.8, activeTime: 'ganztags', mainEffect: 'Magenschmerzen, Ödeme' },
      { id: 'CV-12', nameChinese: 'Zhongwan', nameGerman: 'Mittlerer Magenmund', chineseCharacter: '中脘', frequencyHz: 50.4, activeTime: 'ganztags', mainEffect: 'Mu-Punkt des Magens, Hui-Punkt der Fu-Organe, Verdauung' },
      { id: 'CV-13', nameChinese: 'Shangwan', nameGerman: 'Oberer Magenmund', chineseCharacter: '上脘', frequencyHz: 54.0, activeTime: 'ganztags', mainEffect: 'Magenschmerzen, Erbrechen' },
      { id: 'CV-14', nameChinese: 'Juque', nameGerman: 'Großes Tor', chineseCharacter: '巨闕', frequencyHz: 57.6, activeTime: 'ganztags', mainEffect: 'Mu-Punkt des Herzens, Herzschmerzen, Angst' },
      { id: 'CV-15', nameChinese: 'Jiuwei', nameGerman: 'Taubenschwanz', chineseCharacter: '鳩尾', frequencyHz: 61.2, activeTime: 'ganztags', mainEffect: 'Luo-Punkt, Epilepsie, Brustschmerzen' },
      { id: 'CV-16', nameChinese: 'Zhongting', nameGerman: 'Zentraler Hof', chineseCharacter: '中庭', frequencyHz: 64.8, activeTime: 'ganztags', mainEffect: 'Brustschmerzen, Schluckauf' },
      { id: 'CV-17', nameChinese: 'Shanzhong', nameGerman: 'Brust-Mitte', chineseCharacter: '膻中', frequencyHz: 68.4, activeTime: 'ganztags', mainEffect: 'Mu-Punkt des Perikards, Hui-Punkt des Qi, Brustschmerzen, Asthma' },
      { id: 'CV-18', nameChinese: 'Yutang', nameGerman: 'Jade-Halle', chineseCharacter: '玉堂', frequencyHz: 72.0, activeTime: 'ganztags', mainEffect: 'Brustschmerzen, Husten' },
      { id: 'CV-19', nameChinese: 'Zigong', nameGerman: 'Purpur-Palast', chineseCharacter: '紫宮', frequencyHz: 75.6, activeTime: 'ganztags', mainEffect: 'Husten, Brustschmerzen' },
      { id: 'CV-20', nameChinese: 'Huagai', nameGerman: 'Prächtiger Baldachin', chineseCharacter: '華蓋', frequencyHz: 79.2, activeTime: 'ganztags', mainEffect: 'Husten, Asthma' },
      { id: 'CV-21', nameChinese: 'Xuanji', nameGerman: 'Jade-Drehstern', chineseCharacter: '璇璣', frequencyHz: 82.8, activeTime: 'ganztags', mainEffect: 'Husten, Brustschmerzen' },
      { id: 'CV-22', nameChinese: 'Tiantu', nameGerman: 'Himmels-Vorsprung', chineseCharacter: '天突', frequencyHz: 86.4, activeTime: 'ganztags', mainEffect: 'Asthma, Husten, Halsschmerzen, Aphonie' },
      { id: 'CV-23', nameChinese: 'Lianquan', nameGerman: 'Rand-Quelle', chineseCharacter: '廉泉', frequencyHz: 90.0, activeTime: 'ganztags', mainEffect: 'Sprachstörungen, Schluckstörungen' },
      { id: 'CV-24', nameChinese: 'Chengjiang', nameGerman: 'Speichel-Empfang', chineseCharacter: '承漿', frequencyHz: 93.6, activeTime: 'ganztags', mainEffect: 'Gesichtslähmung, Zahnschmerzen, Speichelfluss' },
    ]
  },
  
  // ===== EXTRAPUNKTE (EX) =====
  {
    id: 'EX',
    name: 'Extra Points',
    nameGerman: 'Extrapunkte',
    element: 'Gemischt',
    activeTime: 'variabel',
    color: 'bg-gray-100',
    totalPoints: 48,
    points: [
      // Kopf- und Nackenextrapunkte
      { id: 'EX-HN1', nameChinese: 'Sishencong', nameGerman: 'Vier Geister-Hören', frequencyHz: 42.0, activeTime: 'variabel', mainEffect: 'Kopfschmerzen, Schwindel, Schlaflosigkeit' },
      { id: 'EX-HN2', nameChinese: 'Dangyang', nameGerman: 'Stirn-Yang', frequencyHz: 44.5, activeTime: 'variabel', mainEffect: 'Kopfschmerzen, Schwindel' },
      { id: 'EX-HN3', nameChinese: 'Yintang', nameGerman: 'Halle des Siegels', frequencyHz: 38.4, activeTime: 'variabel', mainEffect: 'Drittes Auge, Beruhigung, Kopfschmerzen, Schlaflosigkeit' },
      { id: 'EX-HN4', nameChinese: 'Yuyao', nameGerman: 'Fisch-Taille', frequencyHz: 46.2, activeTime: 'variabel', mainEffect: 'Augenprobleme, Gesichtslähmung' },
      { id: 'EX-HN5', nameChinese: 'Taiyang', nameGerman: 'Große Sonne', frequencyHz: 52.8, activeTime: 'variabel', mainEffect: 'Schläfenkopfschmerz, Migräne, Augenschmerzen' },
      { id: 'EX-HN6', nameChinese: 'Erjian', nameGerman: 'Ohrspitze', frequencyHz: 48.3, activeTime: 'variabel', mainEffect: 'Augenrötung, Fieber' },
      { id: 'EX-HN7', nameChinese: 'Qiuhou', nameGerman: 'Hinter dem Augapfel', frequencyHz: 50.4, activeTime: 'variabel', mainEffect: 'Augenerkrankungen' },
      { id: 'EX-HN8', nameChinese: 'Shangyingxiang', nameGerman: 'Oberer Duftempfang', frequencyHz: 52.5, activeTime: 'variabel', mainEffect: 'Nasenverstopfung, Rhinitis' },
      { id: 'EX-HN9', nameChinese: 'Neiying', nameGerman: 'Innerer Empfang', frequencyHz: 54.6, activeTime: 'variabel', mainEffect: 'Augenkrankheiten' },
      { id: 'EX-HN10', nameChinese: 'Juquan', nameGerman: 'Erhöhte Quelle', frequencyHz: 56.7, activeTime: 'variabel', mainEffect: 'Sprachstörungen, Diabetes' },
      { id: 'EX-HN11', nameChinese: 'Haiquan', nameGerman: 'Meeres-Quelle', frequencyHz: 58.8, activeTime: 'variabel', mainEffect: 'Sprachstörungen, Erbrechen' },
      { id: 'EX-HN12', nameChinese: 'Jinjin', nameGerman: 'Gold-Flüssigkeit', frequencyHz: 60.9, activeTime: 'variabel', mainEffect: 'Zungensteifheit, Erbrechen' },
      { id: 'EX-HN13', nameChinese: 'Yuye', nameGerman: 'Jade-Flüssigkeit', frequencyHz: 63.0, activeTime: 'variabel', mainEffect: 'Zungensteifheit, Diabetes' },
      { id: 'EX-HN14', nameChinese: 'Yiming', nameGerman: 'Leuchtende Höhle', frequencyHz: 65.1, activeTime: 'variabel', mainEffect: 'Sehstörungen, Tinnitus' },
      { id: 'EX-HN15', nameChinese: 'Anmian', nameGerman: 'Friedlicher Schlaf', frequencyHz: 34.2, activeTime: 'variabel', mainEffect: 'Schlaflosigkeit, Beruhigung' },
      
      // Brust- und Bauchextrapunkte
      { id: 'EX-CA1', nameChinese: 'Zigongxue', nameGerman: 'Uterus-Punkt', frequencyHz: 67.2, activeTime: 'variabel', mainEffect: 'Gynäkologische Probleme, Unfruchtbarkeit' },
      
      // Rückenextrapunkte
      { id: 'EX-B1', nameChinese: 'Dingchuan', nameGerman: 'Asthma-Stopp', frequencyHz: 69.3, activeTime: 'variabel', mainEffect: 'Asthma, Husten' },
      { id: 'EX-B2', nameChinese: 'Jiaji', nameGerman: 'Huatuojiaji', frequencyHz: 71.4, activeTime: 'variabel', mainEffect: '17 Paare paravertebral, Rückenschmerzen, Organfunktionen' },
      { id: 'EX-B3', nameChinese: 'Weiguanxiashu', nameGerman: 'Unterer Magen-Shu', frequencyHz: 73.5, activeTime: 'variabel', mainEffect: 'Magenschmerzen, Diabetes' },
      { id: 'EX-B4', nameChinese: 'Pigen', nameGerman: 'Milz-Wurzel', frequencyHz: 75.6, activeTime: 'variabel', mainEffect: 'Leber-Milz-Vergrößerung, Bauchschmerzen' },
      { id: 'EX-B5', nameChinese: 'Xiajishu', nameGerman: 'Unterer Wirbel-Shu', frequencyHz: 77.7, activeTime: 'variabel', mainEffect: 'Rückenschmerzen, Beinschmerzen' },
      { id: 'EX-B6', nameChinese: 'Yaoyan', nameGerman: 'Lenden-Auge', frequencyHz: 79.8, activeTime: 'variabel', mainEffect: 'Rückenschmerzen, Menstruationsstörungen' },
      { id: 'EX-B7', nameChinese: 'Yaoqi', nameGerman: 'Lenden-Wunder', frequencyHz: 81.9, activeTime: 'variabel', mainEffect: 'Epilepsie, Kopfschmerzen' },
      { id: 'EX-B8', nameChinese: 'Shiqizhui', nameGerman: '17. Wirbel', frequencyHz: 84.0, activeTime: 'variabel', mainEffect: 'Rückenschmerzen, Beinlähmung' },
      
      // Arm- und Handextrapunkte
      { id: 'EX-UE1', nameChinese: 'Zhoujian', nameGerman: 'Ellenbogen-Spitze', frequencyHz: 86.1, activeTime: 'variabel', mainEffect: 'Lymphadenitis, Furunkel' },
      { id: 'EX-UE2', nameChinese: 'Erbai', nameGerman: 'Zwei Weiße', frequencyHz: 88.2, activeTime: 'variabel', mainEffect: 'Hämorrhoiden, Prolaps' },
      { id: 'EX-UE3', nameChinese: 'Zhongquan', nameGerman: 'Mittlere Quelle', frequencyHz: 90.3, activeTime: 'variabel', mainEffect: 'Brustschmerzen, Erbrechen' },
      { id: 'EX-UE4', nameChinese: 'Zhongkui', nameGerman: 'Mittlerer Schenkel', frequencyHz: 92.4, activeTime: 'variabel', mainEffect: 'Schluckauf, Erbrechen' },
      { id: 'EX-UE5', nameChinese: 'Dagukong', nameGerman: 'Große Knochen-Höhle', frequencyHz: 94.5, activeTime: 'variabel', mainEffect: 'Augenprobleme, Magenschmerzen' },
      { id: 'EX-UE6', nameChinese: 'Xiaogukong', nameGerman: 'Kleine Knochen-Höhle', frequencyHz: 96.6, activeTime: 'variabel', mainEffect: 'Augenprobleme, Halsschmerzen' },
      { id: 'EX-UE7', nameChinese: 'Yaotongdian', nameGerman: 'Rückenschmerz-Punkt', frequencyHz: 98.7, activeTime: 'variabel', mainEffect: 'Akute Rückenschmerzen' },
      { id: 'EX-UE8', nameChinese: 'Wailaogong', nameGerman: 'Äußerer Arbeitspalast', frequencyHz: 100.8, activeTime: 'variabel', mainEffect: 'Hand-Taubheit, Nackensteifheit' },
      { id: 'EX-UE9', nameChinese: 'Baxie', nameGerman: 'Acht Übel', frequencyHz: 102.9, activeTime: 'variabel', mainEffect: '8 Punkte zwischen den Fingern, Hand-Probleme' },
      { id: 'EX-UE10', nameChinese: 'Sifeng', nameGerman: 'Vier Nähte', frequencyHz: 105.0, activeTime: 'variabel', mainEffect: 'Verdauungsstörungen bei Kindern' },
      { id: 'EX-UE11', nameChinese: 'Shixuan', nameGerman: 'Zehn Drainagen', frequencyHz: 107.1, activeTime: 'variabel', mainEffect: '10 Fingerspitzen, Notfall, Fieber, Bewusstlosigkeit' },
      
      // Bein- und Fußextrapunkte
      { id: 'EX-LE1', nameChinese: 'Kuangu', nameGerman: 'Hüft-Knochen', frequencyHz: 109.2, activeTime: 'variabel', mainEffect: 'Hüftschmerzen, Beinlähmung' },
      { id: 'EX-LE2', nameChinese: 'Heding', nameGerman: 'Knie-Gipfel', frequencyHz: 111.3, activeTime: 'variabel', mainEffect: 'Knieschmerzen, Beinlähmung' },
      { id: 'EX-LE3', nameChinese: 'Baichongwo', nameGerman: 'Hundert-Insekten-Nest', frequencyHz: 113.4, activeTime: 'variabel', mainEffect: 'Hautjucken, Urtikaria' },
      { id: 'EX-LE4', nameChinese: 'Neixiyan', nameGerman: 'Inneres Knie-Auge', frequencyHz: 115.5, activeTime: 'variabel', mainEffect: 'Knieschmerzen' },
      { id: 'EX-LE5', nameChinese: 'Xiyan', nameGerman: 'Knie-Augen', frequencyHz: 117.6, activeTime: 'variabel', mainEffect: 'Knieschmerzen (2 Punkte)' },
      { id: 'EX-LE6', nameChinese: 'Dannangxue', nameGerman: 'Gallenblase-Punkt', frequencyHz: 119.7, activeTime: 'variabel', mainEffect: 'Gallenblasenentzündung, Gallensteine' },
      { id: 'EX-LE7', nameChinese: 'Lanweixue', nameGerman: 'Appendix-Punkt', frequencyHz: 121.8, activeTime: 'variabel', mainEffect: 'Appendizitis' },
      { id: 'EX-LE8', nameChinese: 'Neihuaijian', nameGerman: 'Innerer Knöchel-Spitze', frequencyHz: 123.9, activeTime: 'variabel', mainEffect: 'Zahnschmerzen' },
      { id: 'EX-LE9', nameChinese: 'Waihuaijian', nameGerman: 'Äußerer Knöchel-Spitze', frequencyHz: 126.0, activeTime: 'variabel', mainEffect: 'Zahnschmerzen' },
      { id: 'EX-LE10', nameChinese: 'Bafeng', nameGerman: 'Acht Winde', frequencyHz: 128.1, activeTime: 'variabel', mainEffect: '8 Punkte zwischen den Zehen, Fußprobleme' },
      { id: 'EX-LE11', nameChinese: 'Duyin', nameGerman: 'Alleiniges Yin', frequencyHz: 130.2, activeTime: 'variabel', mainEffect: 'Unterleibsschmerzen, Menstruationsstörungen' },
      { id: 'EX-LE12', nameChinese: 'Qiduan', nameGerman: 'Qi-Ende', frequencyHz: 132.3, activeTime: 'variabel', mainEffect: '10 Zehenspitzen, Fußprobleme' },
    ]
  },
];

// ============= HILFSFUNKTIONEN =============

/**
 * Gibt alle Meridianpunkte als formatierte Liste für die Testung zurück
 */
export function getAllMeridianPointsForTesting(): string[] {
  const allPoints: string[] = [];
  
  for (const meridian of MERIDIANS) {
    allPoints.push(`\n=== ${meridian.nameGerman} (${meridian.id}) - ${meridian.element} - ${meridian.activeTime} ===`);
    for (const point of meridian.points) {
      allPoints.push(`${point.id} ${point.nameChinese} (${point.nameGerman}) - ${point.frequencyHz}Hz - ${point.mainEffect}`);
    }
  }
  
  return allPoints;
}

/**
 * Gibt alle Meridianpunkte als flache Liste zurück
 */
export function getAllMeridianPointsFlat(): string[] {
  const allPoints: string[] = [];
  
  for (const meridian of MERIDIANS) {
    for (const point of meridian.points) {
      allPoints.push(`${point.id} ${point.nameChinese} (${point.nameGerman})`);
    }
  }
  
  return allPoints;
}

/**
 * Gibt alle Punkte eines bestimmten Meridians zurück
 */
export function getMeridianPoints(meridianId: string): MeridianPoint[] {
  const meridian = MERIDIANS.find(m => m.id === meridianId);
  return meridian ? meridian.points : [];
}

/**
 * Findet einen Punkt nach seiner ID
 */
export function findPointById(pointId: string): MeridianPoint | undefined {
  for (const meridian of MERIDIANS) {
    const point = meridian.points.find(p => p.id === pointId);
    if (point) return point;
  }
  return undefined;
}

/**
 * Gibt die Gesamtzahl aller Punkte zurück
 */
export function getTotalPointCount(): number {
  return MERIDIANS.reduce((sum, meridian) => sum + meridian.points.length, 0);
}

/**
 * Gibt Statistiken über die Datenbank zurück
 */
export function getMeridianStats(): { 
  totalMeridians: number; 
  totalPoints: number; 
  byElement: Record<string, number>;
  byMeridian: Record<string, number>;
} {
  const byElement: Record<string, number> = {};
  const byMeridian: Record<string, number> = {};
  
  for (const meridian of MERIDIANS) {
    byElement[meridian.element] = (byElement[meridian.element] || 0) + meridian.points.length;
    byMeridian[meridian.nameGerman] = meridian.points.length;
  }
  
  return {
    totalMeridians: MERIDIANS.length,
    totalPoints: getTotalPointCount(),
    byElement,
    byMeridian
  };
}

/**
 * Sucht Punkte nach Schlüsselwort in der Wirkung
 */
export function searchPointsByEffect(keyword: string): MeridianPoint[] {
  const results: MeridianPoint[] = [];
  const lowerKeyword = keyword.toLowerCase();
  
  for (const meridian of MERIDIANS) {
    for (const point of meridian.points) {
      if (point.mainEffect.toLowerCase().includes(lowerKeyword)) {
        results.push(point);
      }
    }
  }
  
  return results;
}

/**
 * Gibt Punkte nach Element zurück
 */
export function getPointsByElement(element: string): MeridianPoint[] {
  const results: MeridianPoint[] = [];
  
  for (const meridian of MERIDIANS) {
    for (const point of meridian.points) {
      if (point.element === element) {
        results.push(point);
      }
    }
  }
  
  return results;
}

/**
 * Gibt Punkte nach aktiver Zeit zurück
 */
export function getPointsByActiveTime(time: string): MeridianPoint[] {
  const results: MeridianPoint[] = [];
  
  for (const meridian of MERIDIANS) {
    if (meridian.activeTime === time) {
      results.push(...meridian.points);
    }
  }
  
  return results;
}
