/**
 * 3D Anatomie-Resonanz-Visualisierung
 * Interaktives 3D-Modell mit resonierenden Körperpunkten und TCM-Meridianen
 * Mit Dysregulations-Farbskala für Meridianpunkte
 */
import { useRef, useState, useEffect, useMemo, useCallback, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, Environment, ContactShadows, Float, Line } from '@react-three/drei';
import { GLBModelLoader, type GLBModelInfo } from '@/components/anatomy/GLBModelLoader';
import { AVAILABLE_MODELS } from '@/components/anatomy/glb-model-utils';
import { ChakraVisualization } from '@/components/anatomy/ChakraVisualization';
import type { ChakraData } from '@/components/anatomy/chakra-data';
import { ModelSelector } from '@/components/anatomy/ModelSelector';
import { ModelUpload } from '@/components/anatomy/ModelUpload';
import { useAnatomyModels, type AnatomyModel } from '@/hooks/useAnatomyModels';
import { projectMeridianPoints, projectMeridianPath, collectMeshes, isMeshSufficientForProjection, type ProjectedPoint } from '@/utils/surfaceProjection';
import { OrganScanLayer } from '@/components/anatomy/OrganScanLayer';
import { OrganLandmarkLayer } from '@/components/anatomy/OrganLandmarkLayer';
import { useOrganScanPoints, type OrganScanPoint, getOrganColor, getTissueIcon } from '@/hooks/useOrganScanPoints';
import { useOrganLandmarks, type OrganLandmark } from '@/hooks/useOrganLandmarks';
import { NLSScanConfigPanel, type NLSScanConfig } from '@/components/NLSScanConfigPanel';
import { useNLSAutoScan } from '@/hooks/useNLSAutoScan';
import { NLSAutoScanOverlay } from '@/components/NLSAutoScanOverlay';
import * as THREE from 'three';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, 
  Heart, 
  Brain, 
  Zap, 
  Volume2,
  Eye,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Info,
  GitBranch,
  AlertTriangle,
  Settings2,
  Crosshair
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useResonanceDatabase, type AnatomyResonancePoint } from '@/hooks/useResonanceDatabase';
import { DysregulationLegend } from '@/components/anatomy/DysregulationLegend';
import { getDysregulationColor, getDysregulationLevel } from '@/components/anatomy/dysregulation-utils';
import type { VectorAnalysis } from '@/services/feldengine';

import type { NLSDysregulationData } from '@/components/MeridianDiagnosisPanel';

interface AnatomyResonanceViewerProps {
  vectorAnalysis?: VectorAnalysis | null;
  onFrequencySelect?: (frequency: number) => void;
  onScanConfigChange?: (config: NLSScanConfig | null) => void;
  onNLSDysregulationData?: (data: NLSDysregulationData) => void;
}

// Anatomie-Modell Typen
type AnatomyModelType = 'full_body' | 'heart' | 'brain' | 'meridians';

interface ModelConfig {
  id: AnatomyModelType;
  name: string;
  icon: typeof Heart;
  description: string;
  cameraPosition: [number, number, number];
  scale: number;
}

const MODEL_CONFIGS: ModelConfig[] = [
  {
    id: 'full_body',
    name: 'Ganzkörper',
    icon: Activity,
    description: 'Vollständige Körperansicht mit allen Resonanzpunkten',
    cameraPosition: [0, 0, 3],
    scale: 1,
  },
  {
    id: 'meridians',
    name: 'Meridiane',
    icon: GitBranch,
    description: 'Die 12 TCM-Hauptmeridiane mit Akupunkturpunkten',
    cameraPosition: [0, 0.4, 2.5],
    scale: 1,
  },
  {
    id: 'heart',
    name: 'Herz',
    icon: Heart,
    description: 'Detaillierte Herzansicht mit kardialen Resonanzen',
    cameraPosition: [0, 0, 2],
    scale: 1.5,
  },
  {
    id: 'brain',
    name: 'Gehirn',
    icon: Brain,
    description: 'Neurologische Zentren und Gehirnwellen-Resonanzen',
    cameraPosition: [0, 0.2, 2],
    scale: 1.5,
  },
];

// ============= TCM MERIDIAN SYSTEM =============

interface MeridianPath {
  id: string;
  name: string;
  nameChinese: string;
  element: 'wood' | 'fire' | 'earth' | 'metal' | 'water' | 'fire_ministerial';
  yinYang: 'yin' | 'yang';
  organ: string;
  color: string;
  points: THREE.Vector3[];
  acupoints: AcupuncturePoint[];
}

interface AcupuncturePoint {
  id: string;
  name: string;
  nameChinese: string;
  position: THREE.Vector3;
  frequency: number;
  indication: string;
}

// Die 12 Hauptmeridiane der TCM mit vereinfachten Pfaden
const TCM_MERIDIANS: MeridianPath[] = [
  // LUNGEN-MERIDIAN (LU) - Yin, Metall
  {
    id: 'LU',
    name: 'Lungen-Meridian',
    nameChinese: '手太陰肺經',
    element: 'metal',
    yinYang: 'yin',
    organ: 'lung',
    color: '#94a3b8',
    points: [
      new THREE.Vector3(-0.12, 0.55, 0.05),
      new THREE.Vector3(-0.16, 0.52, 0.04),
      new THREE.Vector3(-0.20, 0.48, 0.03),
      new THREE.Vector3(-0.24, 0.40, 0.02),
      new THREE.Vector3(-0.28, 0.30, 0.01),
      new THREE.Vector3(-0.30, 0.20, 0),
    ],
    acupoints: [
      { id: 'LU1', name: 'Zhongfu', nameChinese: '中府', position: new THREE.Vector3(-0.12, 0.55, 0.05), frequency: 146.0, indication: 'Husten, Atemnot' },
      { id: 'LU7', name: 'Lieque', nameChinese: '列缺', position: new THREE.Vector3(-0.28, 0.30, 0.01), frequency: 194.7, indication: 'Kopfschmerzen, Nackensteife' },
      { id: 'LU9', name: 'Taiyuan', nameChinese: '太淵', position: new THREE.Vector3(-0.30, 0.20, 0), frequency: 256.0, indication: 'Puls-Diagnostik' },
    ],
  },
  // DICKDARM-MERIDIAN (LI) - Yang, Metall
  {
    id: 'LI',
    name: 'Dickdarm-Meridian',
    nameChinese: '手陽明大腸經',
    element: 'metal',
    yinYang: 'yang',
    organ: 'large_intestine',
    color: '#cbd5e1',
    points: [
      new THREE.Vector3(-0.32, 0.18, 0),
      new THREE.Vector3(-0.30, 0.28, 0.01),
      new THREE.Vector3(-0.26, 0.40, 0.02),
      new THREE.Vector3(-0.20, 0.55, 0.03),
      new THREE.Vector3(-0.14, 0.70, 0.04),
      new THREE.Vector3(-0.06, 0.80, 0.06),
    ],
    acupoints: [
      { id: 'LI4', name: 'Hegu', nameChinese: '合谷', position: new THREE.Vector3(-0.30, 0.28, 0.01), frequency: 136.1, indication: 'Schmerzen, Immunsystem' },
      { id: 'LI11', name: 'Quchi', nameChinese: '曲池', position: new THREE.Vector3(-0.22, 0.50, 0.025), frequency: 174.6, indication: 'Fieber, Hautprobleme' },
      { id: 'LI20', name: 'Yingxiang', nameChinese: '迎香', position: new THREE.Vector3(-0.06, 0.80, 0.06), frequency: 221.2, indication: 'Nasenbeschwerden' },
    ],
  },
  // MAGEN-MERIDIAN (ST) - Yang, Erde
  {
    id: 'ST',
    name: 'Magen-Meridian',
    nameChinese: '足陽明胃經',
    element: 'earth',
    yinYang: 'yang',
    organ: 'stomach',
    color: '#fbbf24',
    points: [
      new THREE.Vector3(-0.04, 0.82, 0.08),
      new THREE.Vector3(-0.06, 0.72, 0.06),
      new THREE.Vector3(-0.08, 0.60, 0.04),
      new THREE.Vector3(-0.08, 0.48, 0.03),
      new THREE.Vector3(-0.08, 0.35, 0.02),
      new THREE.Vector3(-0.08, 0.20, 0.01),
      new THREE.Vector3(-0.08, 0.05, 0),
      new THREE.Vector3(-0.08, -0.10, 0),
    ],
    acupoints: [
      { id: 'ST36', name: 'Zusanli', nameChinese: '足三里', position: new THREE.Vector3(-0.08, 0.05, 0), frequency: 126.2, indication: 'Verdauung, Energie' },
      { id: 'ST25', name: 'Tianshu', nameChinese: '天樞', position: new THREE.Vector3(-0.08, 0.48, 0.03), frequency: 141.3, indication: 'Darmregulation' },
    ],
  },
  // MILZ-MERIDIAN (SP) - Yin, Erde
  {
    id: 'SP',
    name: 'Milz-Meridian',
    nameChinese: '足太陰脾經',
    element: 'earth',
    yinYang: 'yin',
    organ: 'spleen',
    color: '#f59e0b',
    points: [
      new THREE.Vector3(-0.10, -0.12, 0.01),
      new THREE.Vector3(-0.10, 0.00, 0.02),
      new THREE.Vector3(-0.10, 0.15, 0.03),
      new THREE.Vector3(-0.10, 0.30, 0.04),
      new THREE.Vector3(-0.12, 0.45, 0.05),
      new THREE.Vector3(-0.14, 0.55, 0.06),
    ],
    acupoints: [
      { id: 'SP6', name: 'Sanyinjiao', nameChinese: '三陰交', position: new THREE.Vector3(-0.10, 0.00, 0.02), frequency: 117.3, indication: 'Gynäkologie, Schlaf' },
      { id: 'SP9', name: 'Yinlingquan', nameChinese: '陰陵泉', position: new THREE.Vector3(-0.10, 0.15, 0.03), frequency: 131.8, indication: 'Feuchtigkeit, Ödeme' },
    ],
  },
  // HERZ-MERIDIAN (HT) - Yin, Feuer
  {
    id: 'HT',
    name: 'Herz-Meridian',
    nameChinese: '手少陰心經',
    element: 'fire',
    yinYang: 'yin',
    organ: 'heart',
    color: '#ef4444',
    points: [
      new THREE.Vector3(-0.10, 0.58, 0.02),
      new THREE.Vector3(-0.14, 0.52, 0.01),
      new THREE.Vector3(-0.18, 0.44, 0),
      new THREE.Vector3(-0.22, 0.34, -0.01),
      new THREE.Vector3(-0.26, 0.24, -0.02),
      new THREE.Vector3(-0.28, 0.16, -0.02),
    ],
    acupoints: [
      { id: 'HT7', name: 'Shenmen', nameChinese: '神門', position: new THREE.Vector3(-0.28, 0.16, -0.02), frequency: 250.6, indication: 'Angst, Schlafstörungen' },
      { id: 'HT3', name: 'Shaohai', nameChinese: '少海', position: new THREE.Vector3(-0.20, 0.40, -0.005), frequency: 211.4, indication: 'Herzruhe' },
    ],
  },
  // DÜNNDARM-MERIDIAN (SI) - Yang, Feuer
  {
    id: 'SI',
    name: 'Dünndarm-Meridian',
    nameChinese: '手太陽小腸經',
    element: 'fire',
    yinYang: 'yang',
    organ: 'small_intestine',
    color: '#f87171',
    points: [
      new THREE.Vector3(-0.30, 0.14, -0.02),
      new THREE.Vector3(-0.26, 0.28, -0.03),
      new THREE.Vector3(-0.22, 0.44, -0.04),
      new THREE.Vector3(-0.16, 0.60, -0.04),
      new THREE.Vector3(-0.10, 0.72, -0.03),
      new THREE.Vector3(-0.04, 0.80, -0.02),
    ],
    acupoints: [
      { id: 'SI3', name: 'Houxi', nameChinese: '後溪', position: new THREE.Vector3(-0.30, 0.14, -0.02), frequency: 185.0, indication: 'Nacken, Wirbelsäule' },
      { id: 'SI19', name: 'Tinggong', nameChinese: '聽宮', position: new THREE.Vector3(-0.04, 0.80, -0.02), frequency: 234.2, indication: 'Ohrenprobleme' },
    ],
  },
  // BLASEN-MERIDIAN (BL) - Yang, Wasser
  {
    id: 'BL',
    name: 'Blasen-Meridian',
    nameChinese: '足太陽膀胱經',
    element: 'water',
    yinYang: 'yang',
    organ: 'bladder',
    color: '#3b82f6',
    points: [
      new THREE.Vector3(-0.02, 0.88, -0.02),
      new THREE.Vector3(-0.04, 0.78, -0.06),
      new THREE.Vector3(-0.04, 0.65, -0.08),
      new THREE.Vector3(-0.04, 0.50, -0.08),
      new THREE.Vector3(-0.04, 0.35, -0.07),
      new THREE.Vector3(-0.06, 0.20, -0.06),
      new THREE.Vector3(-0.06, 0.05, -0.05),
      new THREE.Vector3(-0.06, -0.10, -0.04),
    ],
    acupoints: [
      { id: 'BL23', name: 'Shenshu', nameChinese: '腎俞', position: new THREE.Vector3(-0.04, 0.40, -0.08), frequency: 172.1, indication: 'Nieren, Rücken' },
      { id: 'BL40', name: 'Weizhong', nameChinese: '委中', position: new THREE.Vector3(-0.06, 0.10, -0.055), frequency: 194.2, indication: 'Rückenschmerzen' },
    ],
  },
  // NIEREN-MERIDIAN (KI) - Yin, Wasser
  {
    id: 'KI',
    name: 'Nieren-Meridian',
    nameChinese: '足少陰腎經',
    element: 'water',
    yinYang: 'yin',
    organ: 'kidney',
    color: '#1d4ed8',
    points: [
      new THREE.Vector3(-0.08, -0.14, 0.04),
      new THREE.Vector3(-0.08, -0.02, 0.05),
      new THREE.Vector3(-0.08, 0.12, 0.05),
      new THREE.Vector3(-0.08, 0.26, 0.05),
      new THREE.Vector3(-0.06, 0.42, 0.05),
      new THREE.Vector3(-0.04, 0.56, 0.04),
    ],
    acupoints: [
      { id: 'KI1', name: 'Yongquan', nameChinese: '湧泉', position: new THREE.Vector3(-0.08, -0.14, 0.04), frequency: 136.1, indication: 'Notfall, Bewusstsein' },
      { id: 'KI3', name: 'Taixi', nameChinese: '太溪', position: new THREE.Vector3(-0.08, -0.02, 0.05), frequency: 160.0, indication: 'Nierenessenz' },
    ],
  },
  // PERIKARD-MERIDIAN (PC) - Yin, Minister-Feuer
  {
    id: 'PC',
    name: 'Perikard-Meridian',
    nameChinese: '手厥陰心包經',
    element: 'fire_ministerial',
    yinYang: 'yin',
    organ: 'pericardium',
    color: '#dc2626',
    points: [
      new THREE.Vector3(-0.11, 0.57, 0.03),
      new THREE.Vector3(-0.15, 0.50, 0.02),
      new THREE.Vector3(-0.19, 0.42, 0.01),
      new THREE.Vector3(-0.23, 0.32, 0),
      new THREE.Vector3(-0.27, 0.22, 0),
      new THREE.Vector3(-0.29, 0.14, 0),
    ],
    acupoints: [
      { id: 'PC6', name: 'Neiguan', nameChinese: '內關', position: new THREE.Vector3(-0.25, 0.27, 0), frequency: 183.6, indication: 'Übelkeit, Herzprobleme' },
      { id: 'PC8', name: 'Laogong', nameChinese: '勞宮', position: new THREE.Vector3(-0.29, 0.14, 0), frequency: 210.4, indication: 'Hitze klären' },
    ],
  },
  // DREIFACHER ERWÄRMER (TE) - Yang, Minister-Feuer
  {
    id: 'TE',
    name: 'Dreifacher Erwärmer',
    nameChinese: '手少陽三焦經',
    element: 'fire_ministerial',
    yinYang: 'yang',
    organ: 'triple_warmer',
    color: '#fb923c',
    points: [
      new THREE.Vector3(-0.31, 0.12, 0),
      new THREE.Vector3(-0.27, 0.26, -0.01),
      new THREE.Vector3(-0.23, 0.42, -0.02),
      new THREE.Vector3(-0.17, 0.58, -0.03),
      new THREE.Vector3(-0.10, 0.72, -0.03),
      new THREE.Vector3(-0.04, 0.82, -0.02),
    ],
    acupoints: [
      { id: 'TE5', name: 'Waiguan', nameChinese: '外關', position: new THREE.Vector3(-0.25, 0.34, -0.015), frequency: 176.0, indication: 'Fieber, Erkältung' },
      { id: 'TE17', name: 'Yifeng', nameChinese: '翳風', position: new THREE.Vector3(-0.04, 0.82, -0.02), frequency: 220.0, indication: 'Ohren, Gesicht' },
    ],
  },
  // GALLENBLASEN-MERIDIAN (GB) - Yang, Holz
  {
    id: 'GB',
    name: 'Gallenblasen-Meridian',
    nameChinese: '足少陽膽經',
    element: 'wood',
    yinYang: 'yang',
    organ: 'gallbladder',
    color: '#22c55e',
    points: [
      new THREE.Vector3(-0.06, 0.88, 0.02),
      new THREE.Vector3(-0.10, 0.78, 0.01),
      new THREE.Vector3(-0.12, 0.65, -0.01),
      new THREE.Vector3(-0.12, 0.50, -0.03),
      new THREE.Vector3(-0.10, 0.35, -0.04),
      new THREE.Vector3(-0.10, 0.18, -0.04),
      new THREE.Vector3(-0.10, 0.00, -0.03),
      new THREE.Vector3(-0.10, -0.12, -0.02),
    ],
    acupoints: [
      { id: 'GB20', name: 'Fengchi', nameChinese: '風池', position: new THREE.Vector3(-0.08, 0.75, -0.04), frequency: 164.8, indication: 'Kopfschmerzen, Wind' },
      { id: 'GB34', name: 'Yanglingquan', nameChinese: '陽陵泉', position: new THREE.Vector3(-0.10, 0.10, -0.035), frequency: 147.9, indication: 'Sehnen, Muskeln' },
    ],
  },
  // LEBER-MERIDIAN (LR) - Yin, Holz
  {
    id: 'LR',
    name: 'Leber-Meridian',
    nameChinese: '足厥陰肝經',
    element: 'wood',
    yinYang: 'yin',
    organ: 'liver',
    color: '#15803d',
    points: [
      new THREE.Vector3(-0.12, -0.14, 0.03),
      new THREE.Vector3(-0.12, -0.02, 0.04),
      new THREE.Vector3(-0.12, 0.12, 0.05),
      new THREE.Vector3(-0.12, 0.28, 0.05),
      new THREE.Vector3(-0.10, 0.44, 0.05),
      new THREE.Vector3(-0.08, 0.55, 0.04),
    ],
    acupoints: [
      { id: 'LR3', name: 'Taichong', nameChinese: '太衝', position: new THREE.Vector3(-0.12, -0.08, 0.035), frequency: 183.6, indication: 'Stress, Leber-Qi' },
      { id: 'LR14', name: 'Qimen', nameChinese: '期門', position: new THREE.Vector3(-0.08, 0.55, 0.04), frequency: 197.7, indication: 'Leber-Erkrankungen' },
    ],
  },
];

// Resonanz-Punkt Visualisierung
function ResonancePoint({
  point,
  isActive,
  resonanceScore,
  onClick,
}: {
  point: AnatomyResonancePoint;
  isActive: boolean;
  resonanceScore: number;
  onClick: () => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current && glowRef.current) {
      const pulse = Math.sin(state.clock.elapsedTime * (2 + resonanceScore * 3)) * 0.1 + 1;
      meshRef.current.scale.setScalar(pulse);
      glowRef.current.scale.setScalar(pulse);
      if (isActive) {
        meshRef.current.rotation.y += 0.02;
      }
    }
  });

  // Farbe basierend auf Frequenz
  const getFrequencyColor = (freq: number) => {
    if (freq < 100) return '#22c55e'; // Niedrig - Grün
    if (freq < 300) return '#3b82f6'; // Mittel - Blau
    if (freq < 600) return '#a855f7'; // Hoch - Lila
    return '#f59e0b'; // Sehr hoch - Orange
  };

  const color = getFrequencyColor(point.primaryFrequency);
  const position: [number, number, number] = [
    point.position.x,
    point.position.y,
    point.position.z
  ];

  return (
    <group position={position}>
      {/* Glow-Effekt */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[0.014, 12, 12]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.1 + resonanceScore * 0.15}
          depthWrite={false}
        />
      </mesh>

      {/* Haupt-Punkt */}
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          document.body.style.cursor = 'pointer';
        }}
        onPointerOut={() => {
          document.body.style.cursor = 'default';
        }}
      >
        <sphereGeometry args={[0.007, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isActive ? 1 : 0.5 + resonanceScore * 0.5}
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>

      {/* Label */}
      {isActive && (
        <Html center distanceFactor={3} position={[0, 0.03, 0]} style={{ pointerEvents: 'none' }}>
          <div className="bg-background/90 backdrop-blur-sm px-1.5 py-0.5 rounded border border-primary/30 shadow-sm whitespace-nowrap">
            <span className="text-[8px] font-medium text-foreground">{point.name}</span>
            <span className="text-[7px] text-primary font-mono ml-1">{point.primaryFrequency.toFixed(1)}Hz</span>
          </div>
        </Html>
      )}
    </group>
  );
}
// Error Boundary für 3D-Modelle
import React from 'react';

class ErrorBoundary3D extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; fallback: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error: Error) {
    console.warn('3D Model load error (falling back to procedural):', error.message);
  }
  render() {
    if (this.state.hasError) return this.props.fallback;
    return this.props.children;
  }
}

// Stilisiertes Körper-Modell (Prozedural)
function HumanBodyModel({ opacity = 0.3 }: { opacity?: number }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.05;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Kopf */}
      <mesh position={[0, 0.85, 0]}>
        <sphereGeometry args={[0.1, 32, 32]} />
        <meshStandardMaterial 
          color="#8b5cf6" 
          transparent 
          opacity={opacity}
          metalness={0.2}
          roughness={0.8}
        />
      </mesh>

      {/* Hals */}
      <mesh position={[0, 0.75, 0]}>
        <cylinderGeometry args={[0.03, 0.04, 0.08, 16]} />
        <meshStandardMaterial color="#a78bfa" transparent opacity={opacity} />
      </mesh>

      {/* Torso */}
      <mesh position={[0, 0.55, 0]}>
        <capsuleGeometry args={[0.12, 0.25, 8, 16]} />
        <meshStandardMaterial 
          color="#6366f1" 
          transparent 
          opacity={opacity}
          metalness={0.1}
          roughness={0.9}
        />
      </mesh>

      {/* Becken */}
      <mesh position={[0, 0.32, 0]}>
        <sphereGeometry args={[0.1, 32, 32]} />
        <meshStandardMaterial color="#818cf8" transparent opacity={opacity} />
      </mesh>

      {/* Arme */}
      {[-1, 1].map((side) => (
        <group key={`arm-${side}`}>
          {/* Oberarm */}
          <mesh position={[side * 0.18, 0.6, 0]} rotation={[0, 0, side * 0.3]}>
            <capsuleGeometry args={[0.025, 0.12, 8, 16]} />
            <meshStandardMaterial color="#a5b4fc" transparent opacity={opacity} />
          </mesh>
          {/* Unterarm */}
          <mesh position={[side * 0.25, 0.45, 0]} rotation={[0, 0, side * 0.2]}>
            <capsuleGeometry args={[0.02, 0.1, 8, 16]} />
            <meshStandardMaterial color="#c7d2fe" transparent opacity={opacity} />
          </mesh>
        </group>
      ))}

      {/* Beine */}
      {[-1, 1].map((side) => (
        <group key={`leg-${side}`}>
          {/* Oberschenkel */}
          <mesh position={[side * 0.06, 0.18, 0]}>
            <capsuleGeometry args={[0.04, 0.15, 8, 16]} />
            <meshStandardMaterial color="#a5b4fc" transparent opacity={opacity} />
          </mesh>
          {/* Unterschenkel */}
          <mesh position={[side * 0.06, -0.02, 0]}>
            <capsuleGeometry args={[0.03, 0.15, 8, 16]} />
            <meshStandardMaterial color="#c7d2fe" transparent opacity={opacity} />
          </mesh>
        </group>
      ))}
    </group>
  );
}

// Stilisiertes Herz-Modell
function HeartModel({ opacity = 0.5 }: { opacity?: number }) {
  const heartRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (heartRef.current) {
      // Herzschlag-Animation
      const beat = Math.sin(state.clock.elapsedTime * 4) * 0.03 + 1;
      heartRef.current.scale.setScalar(beat * 0.3);
      heartRef.current.rotation.y = state.clock.elapsedTime * 0.2;
    }
  });

  // Herz-Form mit Kugeln approximieren
  return (
    <Float speed={1} rotationIntensity={0.2} floatIntensity={0.3}>
      <group ref={heartRef} position={[0, 0.5, 0]}>
        {/* Hauptkörper */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[1, 32, 32]} />
          <meshStandardMaterial
            color="#dc2626"
            transparent
            opacity={opacity}
            metalness={0.3}
            roughness={0.5}
          />
        </mesh>

        {/* Obere Wölbungen */}
        <mesh position={[-0.4, 0.5, 0]}>
          <sphereGeometry args={[0.6, 32, 32]} />
          <meshStandardMaterial color="#b91c1c" transparent opacity={opacity} />
        </mesh>
        <mesh position={[0.4, 0.5, 0]}>
          <sphereGeometry args={[0.6, 32, 32]} />
          <meshStandardMaterial color="#b91c1c" transparent opacity={opacity} />
        </mesh>

        {/* Arterien/Venen-Andeutungen */}
        <mesh position={[0, 0.8, 0]} rotation={[0.3, 0, 0.2]}>
          <cylinderGeometry args={[0.1, 0.15, 0.4, 16]} />
          <meshStandardMaterial color="#7f1d1d" transparent opacity={opacity * 0.8} />
        </mesh>
      </group>
    </Float>
  );
}

// Stilisiertes Gehirn-Modell
function BrainModel({ opacity = 0.5 }: { opacity?: number }) {
  const brainRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (brainRef.current) {
      // Sanfte Gehirnwellen-Animation
      const wave = Math.sin(state.clock.elapsedTime * 0.5) * 0.02;
      brainRef.current.rotation.y = state.clock.elapsedTime * 0.1;
      brainRef.current.position.y = 0.5 + wave;
    }
  });

  return (
    <Float speed={0.5} rotationIntensity={0.1} floatIntensity={0.2}>
      <group ref={brainRef} position={[0, 0.5, 0]} scale={0.4}>
        {/* Linke Hemisphäre */}
        <mesh position={[-0.3, 0, 0]}>
          <sphereGeometry args={[0.8, 32, 32]} />
          <meshStandardMaterial
            color="#f472b6"
            transparent
            opacity={opacity}
            metalness={0.2}
            roughness={0.7}
          />
        </mesh>

        {/* Rechte Hemisphäre */}
        <mesh position={[0.3, 0, 0]}>
          <sphereGeometry args={[0.8, 32, 32]} />
          <meshStandardMaterial
            color="#e879f9"
            transparent
            opacity={opacity}
            metalness={0.2}
            roughness={0.7}
          />
        </mesh>

        {/* Kleinhirn */}
        <mesh position={[0, -0.5, -0.2]}>
          <sphereGeometry args={[0.4, 32, 32]} />
          <meshStandardMaterial color="#c084fc" transparent opacity={opacity} />
        </mesh>

        {/* Hirnstamm */}
        <mesh position={[0, -0.8, 0]} rotation={[0.3, 0, 0]}>
          <cylinderGeometry args={[0.1, 0.15, 0.4, 16]} />
          <meshStandardMaterial color="#a855f7" transparent opacity={opacity * 0.8} />
        </mesh>

        {/* Windungen-Andeutung */}
        {Array.from({ length: 8 }).map((_, i) => (
          <mesh
            key={i}
            position={[
              Math.cos(i * Math.PI / 4) * 0.5 + (i % 2 === 0 ? -0.2 : 0.2),
              Math.sin(i * Math.PI / 3) * 0.3,
              Math.sin(i * Math.PI / 4) * 0.3
            ]}
          >
            <sphereGeometry args={[0.15, 16, 16]} />
            <meshStandardMaterial
              color={i % 2 === 0 ? '#f0abfc' : '#d8b4fe'}
              transparent
              opacity={opacity * 0.6}
            />
          </mesh>
        ))}
      </group>
    </Float>
  );
}

// ============= MERIDIAN 3D COMPONENTS =============

// Einzelner Meridian-Pfad mit optionaler Surface-Projection
const MeridianLine = React.memo(function MeridianLine({
  meridian,
  isActive,
  showLabels,
  onAcupointClick,
  activeAcupointId,
  dysregulationScores,
  projectedPoints,
  projectedPath,
}: {
  meridian: MeridianPath;
  isActive: boolean;
  showLabels: boolean;
  onAcupointClick: (point: AcupuncturePoint, meridian: MeridianPath) => void;
  activeAcupointId: string | null;
  dysregulationScores: Map<string, number>;
  projectedPoints?: Map<string, ProjectedPoint>;
  projectedPath?: THREE.Vector3[];
}) {
  const opacity = isActive ? 0.9 : 0.5;

  // Projizierte oder Original-Pfade verwenden
  const leftPath = projectedPath || meridian.points;
  const rightPath = leftPath.map(p => new THREE.Vector3(-p.x, p.y, p.z));

  return (
    <group>
      {/* Meridian-Linie */}
      <Line
        points={leftPath}
        color={meridian.color}
        lineWidth={isActive ? 4 : 2}
        transparent
        opacity={opacity}
      />

      {/* Gespiegelte Linie (rechte Körperseite) */}
      <Line
        points={rightPath}
        color={meridian.color}
        lineWidth={isActive ? 4 : 2}
        transparent
        opacity={isActive ? 0.9 : 0.5}
      />

      {/* Akupunkturpunkte */}
      {meridian.acupoints.map((point) => {
        // Projizierte Position verwenden falls vorhanden
        const projected = projectedPoints?.get(point.id);
        const effectivePoint = projected?.wasProjected
          ? { ...point, position: projected.projectedPosition }
          : point;

        return (
          <AcupuncturePointMesh
            key={point.id}
            point={effectivePoint}
            meridian={meridian}
            isActive={activeAcupointId === point.id}
            showLabel={showLabels || activeAcupointId === point.id}
            onClick={() => onAcupointClick(point, meridian)}
            dysregulationScore={dysregulationScores.get(point.id) || 0}
          />
        );
      })}
    </group>
  );
});

// Akupunkturpunkt-Mesh mit Dysregulations-Farbe (memoized for performance)
const AcupuncturePointMesh = React.memo(function AcupuncturePointMesh({
  point,
  meridian,
  isActive,
  showLabel,
  onClick,
  dysregulationScore = 0,
}: {
  point: AcupuncturePoint;
  meridian: MeridianPath;
  isActive: boolean;
  showLabel: boolean;
  onClick: () => void;
  dysregulationScore?: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [isHovered, setIsHovered] = useState(false);
  
  // Farbe basierend auf Dysregulation oder Standard-Meridian-Farbe
  const pointColor = dysregulationScore > 0 
    ? getDysregulationColor(dysregulationScore)
    : meridian.color;

  // Only run useFrame for active/hovered points to reduce overhead
  const needsAnimation = isActive || isHovered;
  useFrame((state) => {
    if (!needsAnimation || !meshRef.current) return;
    const pulseSpeed = 4 + dysregulationScore * 4;
    const pulse = Math.sin(state.clock.elapsedTime * pulseSpeed) * 0.15 + 1;
    const scaleFactor = isActive ? 1.4 : 1.2;
    meshRef.current.scale.setScalar(pulse * scaleFactor);
  });

  // Shared geometry args - minimal segments for performance
  const geoArgs: [number, number, number] = [0.005, 4, 4];

  return (
    <>
      {/* Linke Seite */}
      <group position={[point.position.x, point.position.y, point.position.z]}>
        <mesh
          ref={meshRef}
          onClick={(e) => { e.stopPropagation(); onClick(); }}
          onPointerOver={(e) => { 
            e.stopPropagation(); 
            document.body.style.cursor = 'pointer';
            setIsHovered(true);
          }}
          onPointerOut={() => { 
            document.body.style.cursor = 'default';
            setIsHovered(false);
          }}
        >
          <sphereGeometry args={geoArgs} />
          <meshBasicMaterial
            color={pointColor}
            depthWrite={false}
          />
        </mesh>

        {/* Label nur bei Hover oder aktiv */}
        {(isHovered || isActive) && (
          <Html center distanceFactor={3} position={[0, 0.025, 0]} style={{ pointerEvents: 'none' }}>
            <div className="bg-background/95 backdrop-blur-sm px-1.5 py-0.5 rounded border border-primary/40 shadow-sm whitespace-nowrap">
              <span className="text-[8px] font-bold text-foreground">{point.id}</span>
              <span className="text-[7px] text-muted-foreground ml-1">{point.name}</span>
              <span className="text-[7px] text-primary font-mono ml-1">{point.frequency}Hz</span>
            </div>
          </Html>
        )}
      </group>

      {/* Rechte Seite (gespiegelt) - simplified, no interaction */}
      <mesh position={[-point.position.x, point.position.y, point.position.z]}>
        <sphereGeometry args={geoArgs} />
        <meshBasicMaterial color={pointColor} depthWrite={false} />
      </mesh>
    </>
  );
});

// Meridian-System-Modell mit Surface-Projection
function MeridianSystemModel({
  activeMeridianId,
  showLabels,
  onAcupointClick,
  activeAcupointId,
  dysregulationScores,
  showBodySilhouette = true,
  surfaceMeshes,
  meridianXScale = 1,
}: {
  activeMeridianId: string | null;
  showLabels: boolean;
  onAcupointClick: (point: AcupuncturePoint, meridian: MeridianPath) => void;
  activeAcupointId: string | null;
  dysregulationScores: Map<string, number>;
  showBodySilhouette?: boolean;
  surfaceMeshes?: THREE.Mesh[];
  meridianXScale?: number;
}) {
  // Surface-Projection für alle Meridiane berechnen
  const projections = useMemo(() => {
    if (!surfaceMeshes || surfaceMeshes.length === 0) return null;
    if (!isMeshSufficientForProjection(surfaceMeshes)) return null;

    const result = new Map<string, { points: Map<string, ProjectedPoint>; path: THREE.Vector3[] }>();

    for (const meridian of TCM_MERIDIANS) {
      const projectedPoints = projectMeridianPoints(
        meridian.acupoints,
        surfaceMeshes,
        meridianXScale,
        0.01
      );
      const projectedPath = projectMeridianPath(
        meridian.points,
        surfaceMeshes,
        meridianXScale,
        0.008
      );
      result.set(meridian.id, { points: projectedPoints, path: projectedPath });
    }

    console.log(`Surface-Projection: ${result.size} Meridiane projiziert`);
    return result;
  }, [surfaceMeshes, meridianXScale]);

  return (
    <group>
      {/* Körper-Silhouette nur wenn standalone (nicht full_body) */}
      {showBodySilhouette && <HumanBodyModel opacity={0.35} />}

      {/* Alle Meridiane */}
      {TCM_MERIDIANS.map((meridian) => {
        const proj = projections?.get(meridian.id);
        return (
          <MeridianLine
            key={meridian.id}
            meridian={meridian}
            isActive={activeMeridianId === meridian.id || !activeMeridianId}
            showLabels={showLabels && (activeMeridianId === meridian.id || !activeMeridianId)}
            onAcupointClick={onAcupointClick}
            activeAcupointId={activeAcupointId}
            dysregulationScores={dysregulationScores}
            projectedPoints={proj?.points}
            projectedPath={proj?.path}
          />
        );
      })}
    </group>
  );
}

// Szene mit Modell und Punkten
function AnatomyScene({
  modelType,
  anatomyPoints,
  activePointId,
  resonanceScores,
  onPointClick,
  showMeridians,
  activeMeridianId,
  showMeridianLabels,
  onAcupointClick,
  activeAcupointId,
  dysregulationScores,
  useGLBModel,
  showChakras,
  activeChakraId,
  onChakraClick,
  meridianXScale,
  onGLBLoaded,
  bodyHalfWidth,
  showResonancePoints,
  selectedModelUrl,
  showOrganScan,
  organScanPoints,
  activeOrganScanPointId,
  onOrganScanPointClick,
  selectedOrganFilter,
  showLandmarks,
  landmarkPoints,
  activeLandmarkId,
  onLandmarkClick,
  selectedLandmarkOrgan,
}: {
  modelType: AnatomyModelType;
  anatomyPoints: AnatomyResonancePoint[];
  activePointId: string | null;
  resonanceScores: Map<string, number>;
  onPointClick: (point: AnatomyResonancePoint) => void;
  showMeridians: boolean;
  activeMeridianId: string | null;
  showMeridianLabels: boolean;
  onAcupointClick: (point: AcupuncturePoint, meridian: MeridianPath) => void;
  activeAcupointId: string | null;
  dysregulationScores: Map<string, number>;
  useGLBModel: boolean;
  showChakras: boolean;
  activeChakraId: string | null;
  onChakraClick: (chakra: ChakraData) => void;
  meridianXScale: number;
  onGLBLoaded: (info: GLBModelInfo) => void;
  bodyHalfWidth: number;
  showResonancePoints: boolean;
  selectedModelUrl: string;
  showOrganScan: boolean;
  organScanPoints: OrganScanPoint[];
  activeOrganScanPointId: string | null;
  onOrganScanPointClick: (point: OrganScanPoint) => void;
  selectedOrganFilter: string | null;
  showLandmarks: boolean;
  landmarkPoints: OrganLandmark[];
  activeLandmarkId: string | null;
  onLandmarkClick: (landmark: OrganLandmark) => void;
  selectedLandmarkOrgan: string | null;
}) {
  const [surfaceMeshes, setSurfaceMeshes] = useState<THREE.Mesh[]>([]);

  // Filter Punkte basierend auf Modell-Typ
  const visiblePoints = useMemo(() => {
    switch (modelType) {
      case 'heart':
        return anatomyPoints.filter(p => 
          p.organAssociations.some(o => ['heart', 'pericardium'].includes(o)) ||
          p.bodyRegion === 'thorax'
        );
      case 'brain':
        return anatomyPoints.filter(p => 
          p.organAssociations.some(o => ['brain', 'pineal', 'pituitary'].includes(o)) ||
          p.bodyRegion === 'head'
        );
      case 'meridians':
        return [];
      default:
        return anatomyPoints;
    }
  }, [modelType, anatomyPoints]);

  // Callback für Meshes vom GLB-Modell
  const handleMeshesReady = useCallback((meshes: THREE.Mesh[]) => {
    setSurfaceMeshes(meshes);
    console.log(`Surface-Projection: ${meshes.length} Meshes bereit`);
  }, []);

  return (
    <>
      {/* Beleuchtung */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} intensity={0.8} castShadow />
      <pointLight position={[-5, 5, -5]} intensity={0.4} color="#60a5fa" />
      
      {/* Umgebung */}
      <Environment preset="city" />
      <ContactShadows 
        position={[0, -0.15, 0]} 
        opacity={0.3} 
        scale={3} 
        blur={2.5} 
      />

       {/* Anatomie-Modell oder Meridian-System */}
       <group>
        {(modelType === 'full_body' || modelType === 'heart' || modelType === 'brain') && (
          <>
            {useGLBModel ? (
              <ErrorBoundary3D fallback={<HumanBodyModel opacity={showMeridians ? 0.25 : 0.3} />}>
                <GLBModelLoader
                  key={selectedModelUrl}
                  modelPath={selectedModelUrl}
                  opacity={showMeridians || showChakras ? 0.2 : 0.35}
                  onLoaded={onGLBLoaded}
                  onMeshesReady={handleMeshesReady}
                />
              </ErrorBoundary3D>
            ) : (
              <HumanBodyModel opacity={showMeridians ? 0.25 : 0.3} />
            )}
            {showMeridians && (
              <group scale={useGLBModel && surfaceMeshes.length > 0 ? [1, 1, 1] : [meridianXScale, 1, 1]}>
                <MeridianSystemModel
                  activeMeridianId={activeMeridianId}
                  showLabels={showMeridianLabels}
                  onAcupointClick={onAcupointClick}
                  activeAcupointId={activeAcupointId}
                  dysregulationScores={dysregulationScores}
                  showBodySilhouette={false}
                  surfaceMeshes={useGLBModel ? surfaceMeshes : undefined}
                  meridianXScale={meridianXScale}
                />
              </group>
            )}
            {showChakras && (
              <ChakraVisualization
                activeChakraId={activeChakraId}
                onChakraClick={onChakraClick}
                bodyHalfWidth={bodyHalfWidth}
                surfaceMeshes={useGLBModel ? surfaceMeshes : undefined}
              />
            )}
          </>
        )}
        {modelType === 'meridians' && (
          <MeridianSystemModel
            activeMeridianId={activeMeridianId}
            showLabels={showMeridianLabels}
            onAcupointClick={onAcupointClick}
            activeAcupointId={activeAcupointId}
            dysregulationScores={dysregulationScores}
          />
        )}
      </group>

      {/* Resonanz-Punkte */}
      {showResonancePoints && visiblePoints.map((point) => (
        <ResonancePoint
          key={point.id}
          point={point}
          isActive={activePointId === point.id}
          resonanceScore={resonanceScores.get(point.id) || 0.5}
          onClick={() => onPointClick(point)}
        />
      ))}

      {/* NLS Organ-Scan-Punkte */}
      {showOrganScan && (
        <OrganScanLayer
          points={organScanPoints}
          activePointId={activeOrganScanPointId}
          onPointClick={onOrganScanPointClick}
          selectedOrgan={selectedOrganFilter}
          surfaceMeshes={useGLBModel ? surfaceMeshes : undefined}
        />
      )}

      {/* Organ Landmark Punkte (BodyParts3D Pilot) */}
      {showLandmarks && (
        <OrganLandmarkLayer
          landmarks={landmarkPoints}
          activeLandmarkId={activeLandmarkId}
          onLandmarkClick={onLandmarkClick}
          selectedOrgan={selectedLandmarkOrgan}
        />
      )}

      {/* Controls */}
      <OrbitControls
        enablePan={false}
        enableZoom={true}
        minDistance={1}
        maxDistance={6}
        target={[0, 0.4, 0]}
        autoRotate={!activePointId && !activeAcupointId && !activeLandmarkId}
        autoRotateSpeed={0.3}
        minPolarAngle={Math.PI * 0.15}
        maxPolarAngle={Math.PI * 0.85}
      />
    </>
  );
}

// Haupt-Komponente
const AnatomyResonanceViewer = ({
  vectorAnalysis,
  onFrequencySelect,
  onScanConfigChange,
  onNLSDysregulationData,
}: AnatomyResonanceViewerProps) => {
  const [activeModel, setActiveModel] = useState<AnatomyModelType>('full_body');
  const [activePoint, setActivePoint] = useState<AnatomyResonancePoint | null>(null);
  const [showInfo, setShowInfo] = useState(false);

   // Meridian-spezifische States
  const [showMeridians, setShowMeridians] = useState(false);
  const [activeMeridianId, setActiveMeridianId] = useState<string | null>(null);
  const [activeAcupoint, setActiveAcupoint] = useState<{ point: AcupuncturePoint; meridian: MeridianPath } | null>(null);
  const [showMeridianLabels, setShowMeridianLabels] = useState(true);
  const [useGLBModel, setUseGLBModel] = useState(true);
  const [showChakras, setShowChakras] = useState(false);
  const [showResonancePoints, setShowResonancePoints] = useState(false);
  const [showOrganScan, setShowOrganScan] = useState(false);
  const [showLandmarks, setShowLandmarks] = useState(false);
  const [activeChakra, setActiveChakra] = useState<ChakraData | null>(null);
  const [glbModelInfo, setGlbModelInfo] = useState<GLBModelInfo | null>(null);
  const [showScanConfig, setShowScanConfig] = useState(false);
  const [activeScanConfig, setActiveScanConfig] = useState<NLSScanConfig | null>(null);

  // Auto-scan hook
  const { scanState, startScan, pauseScan, resumeScan, stopScan, updateScores } = useNLSAutoScan();

  const {
    points: organScanPoints,
    filteredPoints: filteredOrganScanPoints,
    organGroups,
    organSystems,
    isLoading: organScanLoading,
    selectedOrgan: selectedOrganFilter,
    setSelectedOrgan: setSelectedOrganFilter,
    activePoint: activeOrganScanPoint,
    setActivePoint: setActiveOrganScanPoint,
    loadPoints: loadOrganScanPoints,
  } = useOrganScanPoints();

  const { 
    anatomyPoints, 
    loadAnatomyPoints, 
    isLoading,
  } = useResonanceDatabase();

  const {
    models: anatomyModels,
    selectedModel: selectedAnatomyModel,
    setSelectedModel: setSelectedAnatomyModel,
    isLoading: modelsLoading,
    categories: modelCategories,
    loadModels: reloadAnatomyModels,
  } = useAnatomyModels();

  // Organ Landmarks (BodyParts3D Pilot)
  const {
    landmarks: organLandmarks,
    filteredLandmarks: filteredOrganLandmarks,
    organCodes: landmarkOrganCodes,
    isLoading: landmarksLoading,
    selectedOrgan: selectedLandmarkOrgan,
    setSelectedOrgan: setSelectedLandmarkOrgan,
    activeLandmark,
    setActiveLandmark,
    loadLandmarks,
    toScanPoints: landmarkScanPoints,
  } = useOrganLandmarks();

  // Punkte laden
  useEffect(() => {
    loadAnatomyPoints();
    loadOrganScanPoints();
    loadLandmarks();
  }, [loadAnatomyPoints, loadOrganScanPoints, loadLandmarks]);

  // Model-aware layer visibility
  const visibleLayers = useMemo(() => {
    if (selectedAnatomyModel?.visibleLayers) {
      return new Set(selectedAnatomyModel.visibleLayers);
    }
    return new Set(['meridians', 'chakras', 'resonance_points', 'nls_scan']);
  }, [selectedAnatomyModel]);

  const canShowMeridians = visibleLayers.has('meridians');
  const canShowChakras = visibleLayers.has('chakras');
  const canShowResonancePoints = visibleLayers.has('resonance_points');
  const canShowNLS = visibleLayers.has('nls_scan');

  // Auto-disable layers when model doesn't support them
  useEffect(() => {
    setShowMeridians(prev => (canShowMeridians ? prev : false));
    setShowChakras(prev => (canShowChakras ? prev : false));
    setShowResonancePoints(prev => (canShowResonancePoints ? prev : false));
    setShowOrganScan(prev => (canShowNLS ? prev : false));
  }, [canShowMeridians, canShowChakras, canShowResonancePoints, canShowNLS]);

  // Filter NLS points by model's applicable organ systems
  const modelFilteredOrganScanPoints = useMemo(() => {
    if (activeScanConfig) {
      return organScanPoints.filter(p => activeScanConfig.selectedPointIds.includes(p.id));
    }
    if (selectedAnatomyModel?.applicableOrganSystems?.length) {
      return organScanPoints.filter(p => selectedAnatomyModel.applicableOrganSystems!.includes(p.organSystem));
    }
    return organScanPoints;
  }, [organScanPoints, selectedAnatomyModel, activeScanConfig]);

  // Wenn Meridian-Ansicht aktiviert wird
  useEffect(() => {
    if (activeModel === 'meridians') {
      setShowMeridians(true);
    }
  }, [activeModel]);

  // Scan config handler
  const handleScanConfigConfirm = useCallback((config: NLSScanConfig) => {
    setActiveScanConfig(config);
    setShowScanConfig(false);
    setShowOrganScan(true);
    // Apply organ filter from config
    if (config.selectedOrgans.length === 1) {
      setSelectedOrganFilter(config.selectedOrgans[0]);
    } else {
      setSelectedOrganFilter(null);
    }
    // Auto-start the scan sequence (scores will be updated live via updateScores)
    const scanPoints = organScanPoints.filter(p => config.selectedPointIds.includes(p.id));
    if (scanPoints.length > 0) {
      startScan(scanPoints, config, new Map(), (point) => {
        setActiveOrganScanPoint(point);
      });
    }
  }, [setSelectedOrganFilter, organScanPoints, startScan, setActiveOrganScanPoint]);

  // Akupunktur-Punkt auswählen
  const handleAcupointClick = (point: AcupuncturePoint, meridian: MeridianPath) => {
    setActiveAcupoint({ point, meridian });
    setActiveMeridianId(meridian.id);
    setActivePoint(null);
  };

  // Resonanz-Scores berechnen
  const resonanceScores = useMemo(() => {
    const scores = new Map<string, number>();
    
    if (vectorAnalysis) {
      anatomyPoints.forEach(point => {
        const physicalMatch = 1 - Math.abs(vectorAnalysis.clientVector.dimensions[0] || 0);
        const energyMatch = 1 - Math.abs(vectorAnalysis.clientVector.dimensions[3] || 0);
        
        let score = (physicalMatch + energyMatch) / 2;
        
        if (point.organAssociations.includes('heart') && vectorAnalysis.attractorState.phase === 'stable') {
          score += 0.2;
        }
        
        scores.set(point.id, Math.min(1, score));
      });
    } else {
      anatomyPoints.forEach(point => {
        scores.set(point.id, 0.5);
      });
    }
    
    return scores;
  }, [vectorAnalysis, anatomyPoints]);

  // Dysregulations-Scores für Meridianpunkte berechnen
  const dysregulationScores = useMemo(() => {
    const scores = new Map<string, number>();
    
    if (vectorAnalysis) {
      // Berechne Dysregulation basierend auf Vektor-Dimensionen
      const dimensions = vectorAnalysis.clientVector.dimensions;
      const physical = dimensions[0] || 0;
      const emotional = dimensions[1] || 0;
      const mental = dimensions[2] || 0;
      const energy = dimensions[3] || 0;
      const stress = dimensions[4] || 0;

      // Iteriere durch alle TCM-Meridiane und ihre Punkte
      TCM_MERIDIANS.forEach(meridian => {
        meridian.acupoints.forEach(point => {
          let dysScore = 0;
          
          // Element-basierte Dysregulations-Berechnung
          switch (meridian.element) {
            case 'wood':
              // Holz wird durch emotionalen Stress und Stagnation beeinflusst
              dysScore = Math.abs(emotional) * 0.4 + Math.abs(stress) * 0.4 + Math.abs(mental) * 0.2;
              break;
            case 'fire':
            case 'fire_ministerial':
              // Feuer reagiert auf emotionale und energetische Zustände
              dysScore = Math.abs(emotional) * 0.5 + Math.abs(energy) * 0.3 + Math.abs(stress) * 0.2;
              break;
            case 'earth':
              // Erde ist mit Verdauung und mentalem Überfokus verbunden
              dysScore = Math.abs(physical) * 0.4 + Math.abs(mental) * 0.4 + Math.abs(stress) * 0.2;
              break;
            case 'metal':
              // Metall reagiert auf physische und emotionale (Trauer) Zustände
              dysScore = Math.abs(physical) * 0.5 + Math.abs(emotional) * 0.3 + Math.abs(energy) * 0.2;
              break;
            case 'water':
              // Wasser ist mit Energie/Essenz und Angst verbunden
              dysScore = Math.abs(energy) * 0.5 + Math.abs(stress) * 0.3 + Math.abs(physical) * 0.2;
              break;
          }
          
          // Yin/Yang Modifikator
          if (meridian.yinYang === 'yin') {
            // Yin-Meridiane reagieren stärker auf Mangel
            dysScore *= energy < 0 ? 1.2 : 0.9;
          } else {
            // Yang-Meridiane reagieren stärker auf Überschuss
            dysScore *= stress > 0 ? 1.2 : 0.9;
          }
          
          // Attraktor-Stabilität beeinflusst alle Punkte
          dysScore *= (1 - vectorAnalysis.attractorState.stability) + 0.3;
          
          scores.set(point.id, Math.min(1, Math.max(0, dysScore)));
        });
      });
    }
    
    return scores;
  }, [vectorAnalysis]);

  // NLS organ scan dysregulation scores (0-6 scale matching Metatron)
  const nlsDysregulationScores = useMemo(() => {
    const scores = new Map<string, number>();
    if (!vectorAnalysis) return scores;

    const dimensions = vectorAnalysis.clientVector.dimensions;
    const physical = dimensions[0] || 0;
    const emotional = dimensions[1] || 0;
    const mental = dimensions[2] || 0;
    const energy = dimensions[3] || 0;
    const stress = dimensions[4] || 0;

    // Organ-specific dysregulation mapping
    const organWeights: Record<string, { physical: number; emotional: number; mental: number; energy: number; stress: number }> = {
      heart: { physical: 0.3, emotional: 0.4, mental: 0.05, energy: 0.2, stress: 0.05 },
      liver: { physical: 0.2, emotional: 0.4, mental: 0.1, energy: 0.2, stress: 0.1 },
      kidney: { physical: 0.3, emotional: 0.1, mental: 0.05, energy: 0.4, stress: 0.15 },
      lung: { physical: 0.4, emotional: 0.2, mental: 0.05, energy: 0.2, stress: 0.15 },
      spleen: { physical: 0.3, emotional: 0.2, mental: 0.1, energy: 0.3, stress: 0.1 },
      stomach: { physical: 0.4, emotional: 0.2, mental: 0.1, energy: 0.2, stress: 0.1 },
      pancreas: { physical: 0.3, emotional: 0.1, mental: 0.1, energy: 0.3, stress: 0.2 },
      brain: { physical: 0.1, emotional: 0.3, mental: 0.3, energy: 0.1, stress: 0.2 },
      thyroid: { physical: 0.2, emotional: 0.2, mental: 0.1, energy: 0.4, stress: 0.1 },
      intestine: { physical: 0.4, emotional: 0.2, mental: 0.05, energy: 0.2, stress: 0.15 },
      spine: { physical: 0.5, emotional: 0.1, mental: 0.05, energy: 0.2, stress: 0.15 },
      lymph: { physical: 0.3, emotional: 0.1, mental: 0.05, energy: 0.3, stress: 0.25 },
      urogenital: { physical: 0.35, emotional: 0.2, mental: 0.05, energy: 0.25, stress: 0.15 },
      adrenal: { physical: 0.2, emotional: 0.2, mental: 0.1, energy: 0.1, stress: 0.4 },
      sensory: { physical: 0.25, emotional: 0.25, mental: 0.15, energy: 0.2, stress: 0.15 },
    };

    // Deterministic per-point variation using scan frequency as seed
    const hashVariation = (freq: number, index: number): number => {
      const x = Math.sin(freq * 12.9898 + index * 78.233) * 43758.5453;
      return (x - Math.floor(x)) * 0.4 + 0.8; // range 0.8 - 1.2
    };

    modelFilteredOrganScanPoints.forEach((point, idx) => {
      const w = organWeights[point.organSystem] || { physical: 0.25, emotional: 0.25, mental: 0.15, energy: 0.2, stress: 0.15 };
      
      // Use all 5 dimensions for richer scoring
      let rawScore = Math.abs(physical) * w.physical 
        + Math.abs(emotional) * w.emotional 
        + Math.abs(mental) * w.mental
        + Math.abs(energy) * w.energy 
        + Math.abs(stress) * w.stress;
      
      // Non-linear amplification: moderate deviations produce meaningful scores
      // power < 1 amplifies small-to-moderate values (e.g. 0.3 → 0.3^0.55 ≈ 0.52)
      rawScore = Math.pow(Math.min(1, rawScore), 0.55);

      // Per-point variation for realistic diversity
      rawScore *= hashVariation(point.scanFrequency, idx);
      
      // Focus boost: higher dysregulation visibility for focused organs
      if (activeScanConfig?.focusList.some(f => f.relatedOrgans?.includes(point.organSystem))) {
        rawScore *= 1.3;
      }

      // Stability modifier (lower stability → higher dysregulation)
      rawScore *= (1 - vectorAnalysis.attractorState.stability) + 0.5;
      
      // Scale to 0-6 range (Metatron-style 6-level scale)
      const scaledScore = Math.min(6, Math.max(0, rawScore * 6));
      scores.set(point.id, scaledScore);
    });

    return scores;
  }, [vectorAnalysis, modelFilteredOrganScanPoints, activeScanConfig]);

  // Keep auto-scan scores updated with live dysregulation data
  useEffect(() => {
    if (scanState.isScanning) {
      updateScores(nlsDysregulationScores);
    }
  }, [nlsDysregulationScores, scanState.isScanning, updateScores]);

  useEffect(() => {
    if (nlsDysregulationScores.size > 0 && modelFilteredOrganScanPoints.length > 0) {
      onNLSDysregulationData?.({
        scores: nlsDysregulationScores,
        points: modelFilteredOrganScanPoints,
        focusLabels: activeScanConfig?.focusList?.map(f => f.label),
      });
    }
  }, [nlsDysregulationScores, modelFilteredOrganScanPoints, onNLSDysregulationData, activeScanConfig]);

  // Notify parent about scan config changes
  useEffect(() => {
    onScanConfigChange?.(activeScanConfig);
  }, [activeScanConfig, onScanConfigChange]);
  // Modell wechseln
  const currentModelIndex = MODEL_CONFIGS.findIndex(m => m.id === activeModel);
  const prevModel = () => {
    const newIndex = (currentModelIndex - 1 + MODEL_CONFIGS.length) % MODEL_CONFIGS.length;
    setActiveModel(MODEL_CONFIGS[newIndex].id);
    setActivePoint(null);
    setActiveAcupoint(null);
  };
  const nextModel = () => {
    const newIndex = (currentModelIndex + 1) % MODEL_CONFIGS.length;
    setActiveModel(MODEL_CONFIGS[newIndex].id);
    setActivePoint(null);
    setActiveAcupoint(null);
  };

  // Element-Farbe holen
  const getElementColor = (element: string) => {
    switch (element) {
      case 'wood': return 'text-green-500';
      case 'fire': return 'text-red-500';
      case 'fire_ministerial': return 'text-orange-500';
      case 'earth': return 'text-yellow-500';
      case 'metal': return 'text-gray-400';
      case 'water': return 'text-blue-500';
      default: return 'text-foreground';
    }
  };

  const currentConfig = MODEL_CONFIGS[currentModelIndex];
  const Icon = currentConfig.icon;

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <h2 className="font-display text-3xl md:text-4xl text-foreground mb-4">
            3D <span className="text-gradient-primary">Anatomie</span>-Resonanz
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Interaktive Visualisierung der Resonanzpunkte mit Frequenz-Zuordnungen
          </p>
        </motion.div>

        {/* NLS Scan Configuration – Top right below header */}
        {canShowNLS && (
          <div className="flex justify-end mb-4">
            <div className="w-full max-w-md">
              {showScanConfig ? (
                <NLSScanConfigPanel
                  organGroups={organGroups}
                  organSystems={organSystems}
                  allPoints={organScanPoints}
                  models={anatomyModels}
                  selectedModel={selectedAnatomyModel}
                  onConfigConfirm={handleScanConfigConfirm}
                  onCancel={() => setShowScanConfig(false)}
                  isOpen={showScanConfig}
                />
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowScanConfig(true)}
                  className="w-full gap-2"
                >
                  <Settings2 className="w-4 h-4" />
                  NLS-Scan konfigurieren
                  {activeScanConfig && (
                    <Badge variant="secondary" className="ml-auto text-[10px]">
                      {activeScanConfig.selectedPointIds.length} Punkte
                      {activeScanConfig.focusList.length > 0 && ` • ${activeScanConfig.focusList.length} Fokus`}
                    </Badge>
                  )}
                </Button>
              )}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_440px] gap-6">
          {/* 3D Viewer */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="h-[900px] bg-card rounded-lg border border-border overflow-hidden relative"
          >
            {/* Model Selector */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-3 bg-background/80 backdrop-blur-sm px-4 py-2 rounded-full border border-border">
              <Button variant="ghost" size="icon" onClick={prevModel}>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              
              <div className="flex items-center gap-2 min-w-[120px] justify-center">
                <Icon className="w-5 h-5 text-primary" />
                <span className="font-medium text-foreground">{currentConfig.name}</span>
              </div>
              
              <Button variant="ghost" size="icon" onClick={nextModel}>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>

            {/* Canvas */}
            <Suspense fallback={
              <div className="w-full h-full flex items-center justify-center">
                <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
              </div>
            }>
              <Canvas
                camera={{ 
                  position: currentConfig.cameraPosition, 
                  fov: 50 
                }}
                gl={{ antialias: true, alpha: true }}
              >
                <AnatomyScene
                  modelType={activeModel}
                  anatomyPoints={anatomyPoints}
                  activePointId={activePoint?.id || null}
                  resonanceScores={resonanceScores}
                  onPointClick={(p) => { setActivePoint(p); setActiveAcupoint(null); setActiveChakra(null); }}
                  showMeridians={showMeridians}
                  activeMeridianId={activeMeridianId}
                  showMeridianLabels={showMeridianLabels}
                  onAcupointClick={handleAcupointClick}
                  activeAcupointId={activeAcupoint?.point.id || null}
                  dysregulationScores={dysregulationScores}
                  useGLBModel={useGLBModel}
                  showChakras={showChakras}
                  activeChakraId={activeChakra?.id || null}
                  onChakraClick={(c) => { setActiveChakra(c); setActivePoint(null); setActiveAcupoint(null); }}
                  meridianXScale={0.45}
                  onGLBLoaded={(info) => setGlbModelInfo(info)}
                  bodyHalfWidth={glbModelInfo ? Math.min(glbModelInfo.halfWidth, 0.15) : 0.12}
                  showResonancePoints={showResonancePoints}
                  selectedModelUrl={selectedAnatomyModel?.resolvedUrl || AVAILABLE_MODELS.fullBody}
                  showOrganScan={showOrganScan}
                  organScanPoints={modelFilteredOrganScanPoints}
                  activeOrganScanPointId={activeOrganScanPoint?.id || null}
                  onOrganScanPointClick={(p) => { setActiveOrganScanPoint(p); setActivePoint(null); setActiveAcupoint(null); setActiveChakra(null); setActiveLandmark(null); }}
                  selectedOrganFilter={selectedOrganFilter}
                  showLandmarks={showLandmarks}
                  landmarkPoints={organLandmarks}
                  activeLandmarkId={activeLandmark?.id || null}
                  onLandmarkClick={(lm) => { setActiveLandmark(lm); setActivePoint(null); setActiveAcupoint(null); setActiveChakra(null); setActiveOrganScanPoint(null); }}
                  selectedLandmarkOrgan={selectedLandmarkOrgan}
                />
              </Canvas>
            </Suspense>

            {/* Dysregulations-Legende */}
            {(showMeridians || activeModel === 'meridians') && vectorAnalysis && (
              <DysregulationLegend className="absolute top-16 left-4" />
            )}

            {/* NLS Auto-Scan Overlay */}
            <NLSAutoScanOverlay
              scanState={scanState}
              onPause={pauseScan}
              onResume={resumeScan}
              onStop={stopScan}
            />

            <div className="absolute bottom-4 left-4 flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => { setActivePoint(null); setActiveAcupoint(null); setActiveMeridianId(null); }}
                className="bg-background/80 backdrop-blur-sm"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowInfo(!showInfo)}
                className="bg-background/80 backdrop-blur-sm"
              >
                <Info className="w-4 h-4" />
              </Button>
            </div>

            {/* Toggles */}
            {(activeModel === 'full_body' || activeModel === 'heart' || activeModel === 'brain') && (
              <div className="absolute bottom-4 right-4 flex items-center gap-4 bg-background/80 backdrop-blur-sm px-3 py-2 rounded-lg border border-border">
                <div className="flex items-center gap-1.5">
                  <Switch
                    id="use-glb"
                    checked={useGLBModel}
                    onCheckedChange={setUseGLBModel}
                    className="scale-75"
                  />
                  <Label htmlFor="use-glb" className="text-xs text-foreground">
                    3D-Modell
                  </Label>
                </div>
                {canShowMeridians && (
                  <div className="flex items-center gap-1.5">
                    <Switch
                      id="show-meridians"
                      checked={showMeridians}
                      onCheckedChange={setShowMeridians}
                      className="scale-75"
                    />
                    <Label htmlFor="show-meridians" className="text-xs text-foreground">
                      Meridiane
                    </Label>
                  </div>
                )}
                {canShowChakras && (
                  <div className="flex items-center gap-1.5">
                    <Switch
                      id="show-chakras"
                      checked={showChakras}
                      onCheckedChange={setShowChakras}
                      className="scale-75"
                    />
                    <Label htmlFor="show-chakras" className="text-xs text-foreground">
                      Chakren
                    </Label>
                  </div>
                )}
                {canShowResonancePoints && (
                  <div className="flex items-center gap-1.5">
                    <Switch
                      id="show-resonance"
                      checked={showResonancePoints}
                      onCheckedChange={setShowResonancePoints}
                      className="scale-75"
                    />
                    <Label htmlFor="show-resonance" className="text-xs text-foreground">
                      Organe
                    </Label>
                  </div>
                )}
                {canShowNLS && (
                  <div className="flex items-center gap-1.5">
                    <Switch
                      id="show-nls"
                      checked={showOrganScan}
                      onCheckedChange={setShowOrganScan}
                      className="scale-75"
                    />
                    <Label htmlFor="show-nls" className="text-xs text-foreground">
                      NLS-Scan
                    </Label>
                  </div>
                )}
                <div className="flex items-center gap-1.5">
                  <Switch
                    id="show-landmarks"
                    checked={showLandmarks}
                    onCheckedChange={setShowLandmarks}
                    className="scale-75"
                  />
                  <Label htmlFor="show-landmarks" className="text-xs text-foreground">
                    <Crosshair className="w-3 h-3 inline mr-0.5" />
                    Landmarks
                  </Label>
                </div>
              </div>
            )}

            {/* Info Overlay */}
            <AnimatePresence>
              {showInfo && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  className="absolute bottom-16 left-4 right-4 bg-background/90 backdrop-blur-sm p-4 rounded-lg border border-border"
                >
                  <p className="text-sm text-muted-foreground">
                    {currentConfig.description}
                  </p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Klicken Sie auf die leuchtenden Punkte, um Details und Frequenzen zu sehen.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Side Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-4 max-h-[900px] overflow-y-auto"
          >
            {/* Aktiver Punkt / Akupunkturpunkt Details */}
            <div className="bg-card rounded-lg border border-border p-4">
              <div className="flex items-center gap-2 mb-3">
                <Eye className="w-5 h-5 text-primary" />
                <h3 className="font-medium text-foreground">Ausgewählter Punkt</h3>
              </div>

              {activeAcupoint ? (
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-foreground">{activeAcupoint.point.id}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${getElementColor(activeAcupoint.meridian.element)} bg-current/10`}>
                        {activeAcupoint.meridian.yinYang === 'yin' ? 'Yin' : 'Yang'}
                      </span>
                    </div>
                    <p className="text-md font-medium text-foreground">{activeAcupoint.point.name}</p>
                    <p className="text-sm text-muted-foreground">{activeAcupoint.point.nameChinese}</p>
                  </div>

                  <div className="p-3 bg-primary/10 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Frequenz</span>
                      <span className="font-mono text-primary text-lg">
                        {activeAcupoint.point.frequency.toFixed(1)} Hz
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Meridian</p>
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: activeAcupoint.meridian.color }}
                      />
                      <span className="text-sm text-foreground">{activeAcupoint.meridian.name}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{activeAcupoint.meridian.nameChinese}</p>
                  </div>

                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Indikation</p>
                    <p className="text-sm text-foreground">{activeAcupoint.point.indication}</p>
                  </div>

                  <Button
                    onClick={() => onFrequencySelect?.(activeAcupoint.point.frequency)}
                    className="w-full gap-2"
                  >
                    <Volume2 className="w-4 h-4" />
                    Frequenz anwenden
                  </Button>
                </div>
              ) : activePoint ? (
                <div className="space-y-3">
                  <div>
                    <p className="text-lg font-medium text-foreground">{activePoint.name}</p>
                    {activePoint.nameLatin && (
                      <p className="text-sm text-muted-foreground italic">{activePoint.nameLatin}</p>
                    )}
                  </div>

                  <div className="p-3 bg-primary/10 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Primärfrequenz</span>
                      <span className="font-mono text-primary text-lg">
                        {activePoint.primaryFrequency.toFixed(2)} Hz
                      </span>
                    </div>
                  </div>

                  {activePoint.harmonicFrequencies.length > 0 && (
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Harmonische</p>
                      <div className="flex flex-wrap gap-1">
                        {activePoint.harmonicFrequencies.slice(0, 4).map((freq, i) => (
                          <span 
                            key={i}
                            className="text-xs px-2 py-0.5 bg-muted rounded-full text-muted-foreground"
                          >
                            {freq.toFixed(0)} Hz
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Organ-Zuordnung</p>
                    <div className="flex flex-wrap gap-1">
                      {activePoint.organAssociations.map((organ, i) => (
                        <span 
                          key={i}
                          className="text-xs px-2 py-0.5 bg-primary/20 rounded-full text-primary capitalize"
                        >
                          {organ}
                        </span>
                      ))}
                    </div>
                  </div>

                  <Button
                    onClick={() => onFrequencySelect?.(activePoint.primaryFrequency)}
                    className="w-full gap-2"
                  >
                    <Volume2 className="w-4 h-4" />
                    Frequenz anwenden
                  </Button>
                </div>
              ) : activeChakra ? (
                <div className="space-y-3">
                  <div>
                    <p className="text-lg font-bold" style={{ color: activeChakra.color }}>{activeChakra.nameSanskrit}</p>
                    <p className="text-md font-medium text-foreground">{activeChakra.name}</p>
                  </div>

                  <div className="p-3 bg-primary/10 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Solfeggio-Frequenz</span>
                      <span className="font-mono text-primary text-lg">
                        {activeChakra.frequency} Hz
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Element</p>
                    <p className="text-sm text-foreground">{activeChakra.element}</p>
                  </div>

                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Wirkung</p>
                    <p className="text-sm text-foreground">{activeChakra.description}</p>
                  </div>

                  <Button
                    onClick={() => onFrequencySelect?.(activeChakra.frequency)}
                    className="w-full gap-2"
                  >
                    <Volume2 className="w-4 h-4" />
                    Frequenz anwenden
                  </Button>
                </div>
              ) : activeOrganScanPoint ? (
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getTissueIcon(activeOrganScanPoint.tissueType)}</span>
                      <span className="text-lg font-bold text-foreground">{activeOrganScanPoint.pointName}</span>
                    </div>
                    <p className="text-sm text-muted-foreground italic">{activeOrganScanPoint.description}</p>
                  </div>

                  <div className="p-3 bg-primary/10 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Scan-Frequenz</span>
                      <span className="font-mono text-primary text-lg">
                        {activeOrganScanPoint.scanFrequency.toFixed(2)} Hz
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Organ</p>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: getOrganColor(activeOrganScanPoint.organSystem) }} />
                      <span className="text-sm text-foreground">{activeOrganScanPoint.organNameDe}</span>
                    </div>
                    {activeOrganScanPoint.organNameLatin && (
                      <p className="text-xs text-muted-foreground mt-0.5 italic">{activeOrganScanPoint.organNameLatin}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-xs text-muted-foreground">Gewebe</p>
                      <p className="text-sm text-foreground capitalize">{activeOrganScanPoint.tissueType || '–'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Tiefe</p>
                      <p className="text-sm text-foreground capitalize">{activeOrganScanPoint.layerDepth}</p>
                    </div>
                  </div>

                  {activeOrganScanPoint.harmonicFrequencies.length > 0 && (
                    <div>
                      <p className="text-xs text-muted-foreground mb-1">Harmonische</p>
                      <div className="flex flex-wrap gap-1">
                        {activeOrganScanPoint.harmonicFrequencies.map((freq, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 bg-muted rounded-full text-muted-foreground">
                            {freq.toFixed(1)} Hz
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    onClick={() => onFrequencySelect?.(activeOrganScanPoint.scanFrequency)}
                    className="w-full gap-2"
                  >
                    <Volume2 className="w-4 h-4" />
                    Frequenz anwenden
                  </Button>
                </div>
              ) : activeLandmark ? (
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <Crosshair className="w-4 h-4 text-primary" />
                      <span className="text-lg font-bold text-foreground">{activeLandmark.pointId}</span>
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${activeLandmark.pointClass === 'A' ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground'}`}>
                        {activeLandmark.pointClass === 'A' ? 'Anatomisch' : 'Scan'}
                      </span>
                    </div>
                    <p className="text-md font-medium text-foreground">{activeLandmark.label}</p>
                    {activeLandmark.structureConceptId && (
                      <p className="text-xs text-muted-foreground font-mono">{activeLandmark.structureConceptId}</p>
                    )}
                  </div>

                  {activeLandmark.scanFrequency && (
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Scan-Frequenz</span>
                        <span className="font-mono text-primary text-lg">
                          {activeLandmark.scanFrequency} Hz
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-xs text-muted-foreground">Region</p>
                      <p className="text-sm text-foreground">{activeLandmark.regionCode}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Organ</p>
                      <p className="text-sm text-foreground">{activeLandmark.organCode || '–'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Konfidenz</p>
                      <p className="text-sm text-foreground">{(activeLandmark.confidence * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Methode</p>
                      <p className="text-sm text-foreground capitalize">{activeLandmark.placementMethod}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-muted-foreground mb-1">Koordinaten (RAS)</p>
                    <div className="flex gap-2 font-mono text-xs text-foreground">
                      <span>X: {activeLandmark.x.toFixed(3)}</span>
                      <span>Y: {activeLandmark.y.toFixed(3)}</span>
                      <span>Z: {activeLandmark.z.toFixed(3)}</span>
                    </div>
                  </div>

                  {activeLandmark.notes && (
                    <p className="text-xs text-muted-foreground italic">{activeLandmark.notes}</p>
                  )}

                  {activeLandmark.scanFrequency && (
                    <Button
                      onClick={() => onFrequencySelect?.(activeLandmark.scanFrequency!)}
                      className="w-full gap-2"
                    >
                      <Volume2 className="w-4 h-4" />
                      Frequenz anwenden
                    </Button>
                  )}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-6">
                  Klicken Sie auf einen Punkt im 3D-Modell
                </p>
              )}
            </div>

            {/* Modell-Bibliothek */}
            <div className="bg-card rounded-lg border border-border p-4 max-h-[350px] overflow-y-auto">
              <ModelSelector
                models={anatomyModels}
                selectedModel={selectedAnatomyModel}
                onSelect={(model) => {
                  if (!model.isAvailable) return;
                  setSelectedAnatomyModel(model);
                }}
                onDelete={() => reloadAnatomyModels()}
                categories={modelCategories}
                isLoading={modelsLoading}
              />
              <div className="mt-3 pt-3 border-t border-border">
                <ModelUpload onUploadComplete={() => reloadAnatomyModels()} />
              </div>
            </div>

            {/* Meridian-Liste (bei Meridian-Ansicht) */}
            {(activeModel === 'meridians' || showMeridians) && (
              <div className="bg-card rounded-lg border border-border p-4 max-h-[280px] overflow-y-auto">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <GitBranch className="w-5 h-5 text-primary" />
                    <h3 className="font-medium text-foreground">12 Meridiane</h3>
                  </div>
                  <div className="flex items-center gap-1">
                    <Switch
                      id="show-labels"
                      checked={showMeridianLabels}
                      onCheckedChange={setShowMeridianLabels}
                      className="scale-75"
                    />
                    <Label htmlFor="show-labels" className="text-xs text-muted-foreground">Labels</Label>
                  </div>
                </div>

                <div className="space-y-1">
                  {TCM_MERIDIANS.map((meridian) => (
                    <button
                      key={meridian.id}
                      onClick={() => setActiveMeridianId(activeMeridianId === meridian.id ? null : meridian.id)}
                      className={`w-full p-2 rounded-lg text-left transition-colors flex items-center gap-2 ${
                        activeMeridianId === meridian.id
                          ? 'bg-primary/20 border border-primary/30'
                          : 'bg-muted/30 hover:bg-muted/50 border border-transparent'
                      }`}
                    >
                      <div 
                        className="w-3 h-3 rounded-full flex-shrink-0" 
                        style={{ backgroundColor: meridian.color }}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-foreground truncate">{meridian.id}</span>
                          <span className={`text-xs ${meridian.yinYang === 'yin' ? 'text-blue-400' : 'text-orange-400'}`}>
                            {meridian.yinYang === 'yin' ? '陰' : '陽'}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground truncate">{meridian.name}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* NLS Scan Configuration – moved to bottom of panel */}

            {/* NLS Organ-Scan-Punkte (bei aktivem NLS-Scan) */}
            {showOrganScan && (
              <div className="bg-card rounded-lg border border-border p-4 max-h-[320px] overflow-y-auto">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-5 h-5 text-primary" />
                  <h3 className="font-medium text-foreground">NLS Organ-Scan</h3>
                  <span className="text-xs text-muted-foreground ml-auto">{modelFilteredOrganScanPoints.length} Punkte</span>
                  {activeScanConfig?.focusList.length ? (
                    <div className="flex gap-1">
                      {activeScanConfig.focusList.map(f => (
                        <Badge key={f.id} variant="outline" className="text-[9px] py-0">
                          {f.label}
                        </Badge>
                      ))}
                    </div>
                  ) : null}
                </div>

                {/* Organ-Filter */}
                <div className="flex flex-wrap gap-1 mb-3">
                  <button
                    onClick={() => setSelectedOrganFilter(null)}
                    className={`text-xs px-2 py-0.5 rounded-full transition-colors ${
                      !selectedOrganFilter
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground hover:bg-muted/80'
                    }`}
                  >
                    Alle
                  </button>
                  {organGroups.map((group) => (
                    <button
                      key={group.organSystem}
                      onClick={() => setSelectedOrganFilter(
                        selectedOrganFilter === group.organSystem ? null : group.organSystem
                      )}
                      className={`text-xs px-2 py-0.5 rounded-full transition-colors flex items-center gap-1 ${
                        selectedOrganFilter === group.organSystem
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground hover:bg-muted/80'
                      }`}
                    >
                      <div className="w-2 h-2 rounded-full" style={{ backgroundColor: getOrganColor(group.organSystem) }} />
                      {group.organNameDe}
                    </button>
                  ))}
                </div>

                {/* Punkte-Liste */}
                <div className="space-y-1">
                  {(selectedOrganFilter ? modelFilteredOrganScanPoints.filter(p => p.organSystem === selectedOrganFilter) : modelFilteredOrganScanPoints).map((point) => (
                    <button
                      key={point.id}
                      onClick={() => setActiveOrganScanPoint(point)}
                      className={`w-full p-2 rounded-lg text-left transition-colors flex items-center gap-2 ${
                        activeOrganScanPoint?.id === point.id
                          ? 'bg-primary/20 border border-primary/30'
                          : 'bg-muted/30 hover:bg-muted/50 border border-transparent'
                      }`}
                    >
                      <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: getOrganColor(point.organSystem) }} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-foreground truncate">{point.pointName}</span>
                          <span className="text-xs font-mono text-muted-foreground">{point.scanFrequency.toFixed(1)} Hz</span>
                        </div>
                        <p className="text-[10px] text-muted-foreground truncate">{point.organNameDe} • {point.layerDepth}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Organ Landmarks (BodyParts3D Pilot) */}
            {showLandmarks && (
              <div className="bg-card rounded-lg border border-border p-4 max-h-[320px] overflow-y-auto">
                <div className="flex items-center gap-2 mb-3">
                  <Crosshair className="w-5 h-5 text-primary" />
                  <h3 className="font-medium text-foreground">Organ-Landmarks</h3>
                  <span className="text-xs text-muted-foreground ml-auto">{organLandmarks.length} Punkte</span>
                </div>

                {/* Organ-Filter */}
                <div className="flex flex-wrap gap-1 mb-3">
                  <button
                    onClick={() => setSelectedLandmarkOrgan(null)}
                    className={`text-xs px-2 py-0.5 rounded-full transition-colors ${
                      !selectedLandmarkOrgan
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-muted-foreground hover:bg-muted/80'
                    }`}
                  >
                    Alle
                  </button>
                  {landmarkOrganCodes.map((code) => (
                    <button
                      key={code}
                      onClick={() => setSelectedLandmarkOrgan(selectedLandmarkOrgan === code ? null : code)}
                      className={`text-xs px-2 py-0.5 rounded-full transition-colors ${
                        selectedLandmarkOrgan === code
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground hover:bg-muted/80'
                      }`}
                    >
                      {code}
                    </button>
                  ))}
                </div>

                {/* Punkte-Liste */}
                <div className="space-y-1">
                  {filteredOrganLandmarks.map((lm) => (
                    <button
                      key={lm.id}
                      onClick={() => setActiveLandmark(lm)}
                      className={`w-full p-2 rounded-lg text-left transition-colors flex items-center gap-2 ${
                        activeLandmark?.id === lm.id
                          ? 'bg-primary/20 border border-primary/30'
                          : 'bg-muted/30 hover:bg-muted/50 border border-transparent'
                      }`}
                    >
                      <div className={`w-2.5 h-2.5 flex-shrink-0 ${lm.pointClass === 'A' ? 'rotate-45 bg-primary' : 'rounded-full bg-muted-foreground'}`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-foreground truncate">{lm.pointId}</span>
                          <span className="text-[10px] text-muted-foreground">{lm.regionCode}</span>
                        </div>
                        <p className="text-[10px] text-muted-foreground truncate">{lm.label}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-card rounded-lg border border-border p-4 max-h-[300px] overflow-y-auto">
              <div className="flex items-center gap-2 mb-3">
                <Activity className="w-5 h-5 text-primary" />
                <h3 className="font-medium text-foreground">Alle Punkte</h3>
              </div>

              {isLoading ? (
                <div className="flex justify-center py-4">
                  <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full" />
                </div>
              ) : (
                <div className="space-y-2">
                  {anatomyPoints.map((point) => (
                    <button
                      key={point.id}
                      onClick={() => setActivePoint(point)}
                      className={`w-full p-2 rounded-lg text-left transition-colors ${
                        activePoint?.id === point.id
                          ? 'bg-primary/20 border border-primary/30'
                          : 'bg-muted/30 hover:bg-muted/50 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-foreground">{point.name}</span>
                        <span className="text-xs font-mono text-muted-foreground">
                          {point.primaryFrequency.toFixed(0)} Hz
                        </span>
                      </div>
                      <div className="mt-1 h-1 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-primary to-primary/50"
                          style={{ width: `${(resonanceScores.get(point.id) || 0.5) * 100}%` }}
                        />
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default AnatomyResonanceViewer;
