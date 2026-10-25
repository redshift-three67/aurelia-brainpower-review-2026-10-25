export interface ChakraData {
  id: string;
  name: string;
  nameSanskrit: string;
  color: string;
  yPosition: number;
  frequency: number;
  element: string;
  description: string;
}

export const CHAKRAS: ChakraData[] = [
  { id: 'muladhara', name: 'Wurzel-Chakra', nameSanskrit: 'Mūlādhāra', color: '#ef4444', yPosition: 0.27, frequency: 396, element: 'Erde', description: 'Erdung, Stabilität, Überlebensinstinkt' },
  { id: 'svadhisthana', name: 'Sakral-Chakra', nameSanskrit: 'Svādhiṣṭhāna', color: '#f97316', yPosition: 0.33, frequency: 417, element: 'Wasser', description: 'Kreativität, Sexualität, Emotionen' },
  { id: 'manipura', name: 'Solarplexus-Chakra', nameSanskrit: 'Maṇipūra', color: '#eab308', yPosition: 0.42, frequency: 528, element: 'Feuer', description: 'Willenskraft, Selbstbewusstsein, Transformation' },
  { id: 'anahata', name: 'Herz-Chakra', nameSanskrit: 'Anāhata', color: '#22c55e', yPosition: 0.52, frequency: 639, element: 'Luft', description: 'Liebe, Mitgefühl, Verbundenheit' },
  { id: 'vishuddha', name: 'Hals-Chakra', nameSanskrit: 'Viśuddha', color: '#06b6d4', yPosition: 0.65, frequency: 741, element: 'Äther', description: 'Kommunikation, Ausdruck, Wahrheit' },
  { id: 'ajna', name: 'Stirn-Chakra', nameSanskrit: 'Ājñā', color: '#6366f1', yPosition: 0.78, frequency: 852, element: 'Licht', description: 'Intuition, Weisheit, innere Schau' },
  { id: 'sahasrara', name: 'Kronen-Chakra', nameSanskrit: 'Sahasrāra', color: '#a855f7', yPosition: 0.88, frequency: 963, element: 'Kosmische Energie', description: 'Spiritualität, Erleuchtung, Einheit' },
];
