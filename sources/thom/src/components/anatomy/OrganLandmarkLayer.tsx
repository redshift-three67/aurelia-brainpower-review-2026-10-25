/**
 * Organ-Landmark 3D-Layer
 * Visualisiert anatomische Landmarks (A-Punkte) und Scan-Punkte (S-Punkte)
 * aus dem BodyParts3D/FMA-basierten Pilot-Datensatz
 */
import { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import type { OrganLandmark } from '@/hooks/useOrganLandmarks';

interface OrganLandmarkLayerProps {
  landmarks: OrganLandmark[];
  activeLandmarkId: string | null;
  onLandmarkClick: (landmark: OrganLandmark) => void;
  selectedOrgan: string | null;
}

const ORGAN_COLORS: Record<string, string> = {
  HEART: '#ef4444',
  BRAIN: '#a855f7',
  LIVER: '#f59e0b',
  KIDNEY_PAIR: '#10b981',
  LUNG_PAIR: '#06b6d4',
  SPINE_PELVIS: '#8b5cf6',
  WHOLEBODY: '#6366f1',
  TCM_SURFACE: '#ec4899',
};

const CLASS_SHAPES: Record<string, 'sphere' | 'octahedron' | 'diamond'> = {
  A: 'diamond',  // Anatomische Landmarks
  S: 'sphere',   // Scan-Punkte
  V: 'octahedron', // Validierungs-Punkte
};

function LandmarkMesh({
  landmark,
  isActive,
  onClick,
}: {
  landmark: OrganLandmark;
  isActive: boolean;
  onClick: () => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const [isHovered, setIsHovered] = useState(false);

  const color = ORGAN_COLORS[landmark.organCode || ''] || '#6366f1';
  const isAnchor = landmark.pointClass === 'A';

  useFrame((state) => {
    if (!meshRef.current) return;
    if (isActive || isHovered) {
      const pulse = Math.sin(state.clock.elapsedTime * 4) * 0.15 + 1;
      meshRef.current.scale.setScalar(pulse * (isActive ? 1.5 : 1.2));
    } else {
      meshRef.current.scale.setScalar(1);
    }
  });

  const size = isAnchor ? 0.006 : 0.004;

  return (
    <group position={[landmark.x, landmark.y, landmark.z]}>
      {/* Glow ring for A-landmarks */}
      {isAnchor && (
        <mesh>
          <ringGeometry args={[0.008, 0.01, 16]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={isActive ? 0.6 : 0.2}
            side={THREE.DoubleSide}
            depthWrite={false}
          />
        </mesh>
      )}

      {/* Main point */}
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
        {isAnchor ? (
          <octahedronGeometry args={[size]} />
        ) : (
          <sphereGeometry args={[size, 8, 8]} />
        )}
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isActive ? 2.0 : isHovered ? 1.2 : 0.6}
          transparent
          opacity={landmark.confidence}
          depthWrite={false}
        />
      </mesh>

      {/* Label on hover/active */}
      {(isHovered || isActive) && (
        <Html center distanceFactor={3} position={[0, 0.015, 0]} style={{ pointerEvents: 'none' }}>
          <div className="bg-background/95 backdrop-blur-sm px-2 py-1 rounded border border-primary/40 shadow-lg whitespace-nowrap">
            <div className="flex items-center gap-1">
              <span className="text-[8px] font-bold text-primary">{landmark.pointId}</span>
              <span className={`text-[7px] px-1 rounded ${isAnchor ? 'bg-primary/20 text-primary' : 'bg-muted text-muted-foreground'}`}>
                {landmark.pointClass}
              </span>
            </div>
            <p className="text-[8px] font-medium text-foreground">{landmark.label}</p>
            <div className="flex items-center gap-1 mt-0.5">
              <span className="text-[7px] text-muted-foreground">{landmark.regionCode}</span>
              {landmark.scanFrequency && (
                <span className="text-[7px] font-mono text-primary">{landmark.scanFrequency} Hz</span>
              )}
            </div>
          </div>
        </Html>
      )}
    </group>
  );
}

export function OrganLandmarkLayer({
  landmarks,
  activeLandmarkId,
  onLandmarkClick,
  selectedOrgan,
}: OrganLandmarkLayerProps) {
  const visible = useMemo(() => {
    if (!selectedOrgan) return landmarks;
    return landmarks.filter(l => l.organCode === selectedOrgan);
  }, [landmarks, selectedOrgan]);

  return (
    <group>
      {visible.map((lm) => (
        <LandmarkMesh
          key={lm.id}
          landmark={lm}
          isActive={activeLandmarkId === lm.id}
          onClick={() => onLandmarkClick(lm)}
        />
      ))}
    </group>
  );
}

export default OrganLandmarkLayer;
