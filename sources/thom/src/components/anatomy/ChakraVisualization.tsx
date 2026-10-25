/**
 * 7-Chakra Visualisierung
 * Pulsierende Energiekugeln an den traditionellen Chakra-Positionen
 * Mit Surface-Projection auf das GLB-Modell
 */
import { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { projectPointToSurface, isMeshSufficientForProjection } from '@/utils/surfaceProjection';
import { CHAKRAS, type ChakraData } from './chakra-data';

function ChakraSphere({
  chakra,
  isActive,
  onClick,
  sizeFactor = 1,
  projectedPosition,
}: {
  chakra: ChakraData;
  isActive: boolean;
  onClick: () => void;
  sizeFactor?: number;
  projectedPosition?: THREE.Vector3;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const [isHovered, setIsHovered] = useState(false);

  // Use projected position or default center-body position
  const pos = projectedPosition || new THREE.Vector3(0, chakra.yPosition, 0.04);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    if (meshRef.current) {
      const offset = CHAKRAS.indexOf(chakra) * 0.9;
      const pulse = Math.sin(t * 2 + offset) * 0.08 + 1;
      const scale = isActive ? 1.4 : isHovered ? 1.2 : 1;
      meshRef.current.scale.setScalar(pulse * scale);
    }
    if (glowRef.current) {
      const glowPulse = Math.sin(t * 1.5 + CHAKRAS.indexOf(chakra)) * 0.15 + 1;
      glowRef.current.scale.setScalar(glowPulse * (isActive ? 1.6 : 1));
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity =
        0.06 + Math.sin(t * 2) * 0.03 + (isActive ? 0.08 : 0);
    }
  });

  const innerRadius = 0.006 * sizeFactor;
  const glowRadius = 0.016 * sizeFactor;

  return (
    <group position={[pos.x, pos.y, pos.z]}>
      {/* Äußerer Glow */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[glowRadius, 12, 12]} />
        <meshBasicMaterial color={chakra.color} transparent opacity={0.06} depthWrite={false} />
      </mesh>

      {/* Innere Energiekugel */}
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
        <sphereGeometry args={[innerRadius, 16, 16]} />
        <meshStandardMaterial
          color={chakra.color}
          emissive={chakra.color}
          emissiveIntensity={isActive ? 1.5 : isHovered ? 0.8 : 0.4}
          transparent
          opacity={0.85}
          depthWrite={false}
        />
      </mesh>

      {/* Hover-Label */}
      {(isHovered || isActive) && (
        <Html center distanceFactor={3} position={[0, 0.02, 0]} style={{ pointerEvents: 'none' }}>
          <div className="bg-background/95 backdrop-blur-sm px-1.5 py-0.5 rounded border border-primary/40 shadow-sm whitespace-nowrap">
            <span className="text-[8px] font-bold" style={{ color: chakra.color }}>{chakra.nameSanskrit}</span>
            <span className="text-[7px] text-foreground ml-1">{chakra.name}</span>
            <span className="text-[7px] text-primary font-mono ml-1">{chakra.frequency}Hz</span>
          </div>
        </Html>
      )}
    </group>
  );
}

interface ChakraVisualizationProps {
  onChakraClick?: (chakra: ChakraData) => void;
  activeChakraId?: string | null;
  bodyHalfWidth?: number;
  surfaceMeshes?: THREE.Mesh[];
}

export function ChakraVisualization({
  onChakraClick,
  activeChakraId,
  bodyHalfWidth = 0.12,
  surfaceMeshes,
}: ChakraVisualizationProps) {
  const sizeFactor = Math.min(1.2, Math.max(0.6, bodyHalfWidth / 0.12));

  // Project chakra positions onto mesh surface
  const projectedPositions = useMemo(() => {
    if (!surfaceMeshes || surfaceMeshes.length === 0) return null;
    if (!isMeshSufficientForProjection(surfaceMeshes)) return null;

    const map = new Map<string, THREE.Vector3>();
    for (const chakra of CHAKRAS) {
      // Chakras sit on the front midline of the body
      const pos = new THREE.Vector3(0, chakra.yPosition, 0.04);
      const result = projectPointToSurface(pos, surfaceMeshes, 0.006);
      if (result.wasProjected) {
        map.set(chakra.id, result.projectedPosition);
      }
    }
    console.log(`Chakra Surface-Projection: ${map.size}/${CHAKRAS.length} projiziert`);
    return map;
  }, [surfaceMeshes]);

  return (
    <group>
      {CHAKRAS.map((chakra) => (
        <ChakraSphere
          key={chakra.id}
          chakra={chakra}
          isActive={activeChakraId === chakra.id}
          onClick={() => onChakraClick?.(chakra)}
          sizeFactor={sizeFactor}
          projectedPosition={projectedPositions?.get(chakra.id)}
        />
      ))}
    </group>
  );
}

export default ChakraVisualization;
