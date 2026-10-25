/**
 * NLS Organ-Scan-Punkte 3D-Layer
 * Visualisiert die vordefinierten NLS-Scan-Punkte als interaktive 3D-Elemente
 * Mit Surface-Projection auf das GLB-Modell
 */
import { useRef, useState, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { type OrganScanPoint, getOrganColor, getTissueIcon } from '@/hooks/useOrganScanPoints';
import { projectPointToSurface, isMeshSufficientForProjection } from '@/utils/surfaceProjection';

interface OrganScanLayerProps {
  points: OrganScanPoint[];
  activePointId: string | null;
  onPointClick: (point: OrganScanPoint) => void;
  selectedOrgan: string | null;
  surfaceMeshes?: THREE.Mesh[];
}

function ScanPointMesh({
  point,
  isActive,
  onClick,
  projectedPosition,
}: {
  point: OrganScanPoint;
  isActive: boolean;
  onClick: () => void;
  projectedPosition?: THREE.Vector3;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const [isHovered, setIsHovered] = useState(false);

  const color = getOrganColor(point.organSystem);
  const depthOpacity = point.layerDepth === 'deep' ? 0.6 : point.layerDepth === 'middle' ? 0.8 : 1.0;

  // Use projected position or original
  const pos = projectedPosition || new THREE.Vector3(point.x, point.y, point.z);

  useFrame((state) => {
    if (meshRef.current) {
      const pulse = Math.sin(state.clock.elapsedTime * (3 + point.scanFrequency * 0.1)) * 0.15 + 1;
      const scale = isActive ? 1.5 : isHovered ? 1.3 : 1;
      meshRef.current.scale.setScalar(pulse * scale);
    }
    if (ringRef.current && isActive) {
      ringRef.current.rotation.z += 0.02;
      ringRef.current.rotation.x = Math.sin(state.clock.elapsedTime) * 0.3;
    }
  });

  return (
    <group position={[pos.x, pos.y, pos.z]}>
      {/* Scan-Ring bei aktiv */}
      {isActive && (
        <mesh ref={ringRef}>
          <torusGeometry args={[0.012, 0.0015, 8, 24]} />
          <meshBasicMaterial color={color} transparent opacity={0.6} />
        </mesh>
      )}

      {/* Outer Glow */}
      <mesh>
        <sphereGeometry args={[0.012, 6, 6]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.2 * depthOpacity}
          depthWrite={false}
        />
      </mesh>

      {/* Punkt */}
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
        {point.tissueType === 'vessel' ? (
          <octahedronGeometry args={[0.005]} />
        ) : point.tissueType === 'node' || point.tissueType === 'conduction' ? (
          <dodecahedronGeometry args={[0.005]} />
        ) : (
          <sphereGeometry args={[0.005, 6, 6]} />
        )}
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isActive ? 2.0 : isHovered ? 1.4 : 0.9}
          transparent
          opacity={depthOpacity}
          depthWrite={false}
        />
      </mesh>

      {/* Label */}
      {(isHovered || isActive) && (
        <Html center distanceFactor={3} position={[0, 0.02, 0]} style={{ pointerEvents: 'none' }}>
          <div className="bg-background/95 backdrop-blur-sm px-2 py-1 rounded border border-primary/40 shadow-lg whitespace-nowrap">
            <div className="flex items-center gap-1">
              <span className="text-[8px]">{getTissueIcon(point.tissueType)}</span>
              <span className="text-[8px] font-bold text-foreground">{point.pointName}</span>
            </div>
            <div className="flex items-center gap-1 mt-0.5">
              <span className="text-[7px] font-mono text-primary">{point.scanFrequency.toFixed(1)} Hz</span>
              <span className="text-[7px] text-muted-foreground">• {point.layerDepth}</span>
            </div>
          </div>
        </Html>
      )}
    </group>
  );
}

export function OrganScanLayer({
  points,
  activePointId,
  onPointClick,
  selectedOrgan,
  surfaceMeshes,
}: OrganScanLayerProps) {
  const visiblePoints = selectedOrgan
    ? points.filter(p => p.organSystem === selectedOrgan)
    : points;

  // Project all organ points onto the mesh surface
  const projectedPositions = useMemo(() => {
    if (!surfaceMeshes || surfaceMeshes.length === 0) return null;
    if (!isMeshSufficientForProjection(surfaceMeshes)) return null;

    const map = new Map<string, THREE.Vector3>();
    for (const point of visiblePoints) {
      const pos = new THREE.Vector3(point.x, point.y, point.z);
      const result = projectPointToSurface(pos, surfaceMeshes, 0.008);
      if (result.wasProjected) {
        map.set(point.id, result.projectedPosition);
      }
    }
    console.log(`OrganScan Surface-Projection: ${map.size}/${visiblePoints.length} Punkte projiziert`);
    return map;
  }, [surfaceMeshes, visiblePoints]);

  return (
    <group>
      {visiblePoints.map((point) => (
        <ScanPointMesh
          key={point.id}
          point={point}
          isActive={activePointId === point.id}
          onClick={() => onPointClick(point)}
          projectedPosition={projectedPositions?.get(point.id)}
        />
      ))}
    </group>
  );
}

export default OrganScanLayer;
