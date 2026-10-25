/**
 * GLB Model Loader Komponente
 * Lädt GLB/GLTF 3D-Modelle und normalisiert sie automatisch
 * auf die Koordinaten des prozeduralen Modells (y: -0.15 bis 0.95)
 * Exportiert die berechnete x-Skalierung für Meridian-Alignment
 */
import { useRef, useEffect, useMemo, useCallback } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF, Float } from '@react-three/drei';
import * as THREE from 'three';

interface GLBModelLoaderProps {
  modelPath: string;
  opacity?: number;
  pulseIntensity?: number;
  wireframe?: boolean;
  highlightColor?: string;
  onLoaded?: (info: GLBModelInfo) => void;
  onMeshesReady?: (meshes: THREE.Mesh[]) => void;
}

export interface GLBModelInfo {
  /** Verhältnis Breite/Höhe des Modells */
  aspectRatio: number;
  /** Normalisierte halbe Breite in Szenen-Koordinaten */
  halfWidth: number;
  /** Normalisierte halbe Tiefe */
  halfDepth: number;
  /** Normalisierungs-Skalierungsfaktor */
  normalizeScale: number;
}

// Zielkoordinaten passend zu den Meridianpunkten
const TARGET_BOUNDS = {
  minY: -0.15,
  maxY: 0.95,
  centerX: 0,
  centerZ: 0,
};

export function GLBModelLoader({
  modelPath,
  opacity = 0.4,
  pulseIntensity = 0.01,
  wireframe = false,
  highlightColor,
  onLoaded,
  onMeshesReady,
}: GLBModelLoaderProps) {
  const groupRef = useRef<THREE.Group>(null);
  const { scene } = useGLTF(modelPath);

  const { clonedScene, modelInfo } = useMemo(() => {
    const clone = scene.clone(true);

    // Filter out text labels, planes, and annotation objects from Z-Anatomy exports
    const toRemove: THREE.Object3D[] = [];
    clone.traverse((child) => {
      const name = child.name.toLowerCase();
      // Z-Anatomy text labels, reference planes, annotations
      const isLabel = name.includes('text') || name.includes('label') || name.includes('annotation')
        || name.includes('title') || name.includes('caption') || name.includes('plane')
        || name.includes('reference') || name.includes('movement') || name.includes('general_t');
      
      if (child instanceof THREE.Mesh) {
        const geo = child.geometry;
        // Detect flat planes: very thin in one axis (text quads)
        if (geo) {
          geo.computeBoundingBox();
          const geoSize = new THREE.Vector3();
          geo.boundingBox?.getSize(geoSize);
          const minDim = Math.min(geoSize.x, geoSize.y, geoSize.z);
          const maxDim = Math.max(geoSize.x, geoSize.y, geoSize.z);
          // Extremely flat objects are likely label planes
          if (minDim > 0 && maxDim / minDim > 50) {
            toRemove.push(child);
            return;
          }
        }
      }
      
      if (isLabel) {
        toRemove.push(child);
      }
    });
    toRemove.forEach(obj => obj.removeFromParent());

    // Bounding Box berechnen
    const box = new THREE.Box3().setFromObject(clone);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    // Skalierung auf Zielhöhe
    const targetHeight = TARGET_BOUNDS.maxY - TARGET_BOUNDS.minY;
    const normalizeScale = targetHeight / size.y;

    // Normalisierte Breite/Tiefe
    const halfWidth = (size.x * normalizeScale) / 2;
    const halfDepth = (size.z * normalizeScale) / 2;

    // Transform anwenden
    clone.scale.setScalar(normalizeScale);
    clone.position.set(
      -center.x * normalizeScale + TARGET_BOUNDS.centerX,
      -box.min.y * normalizeScale + TARGET_BOUNDS.minY,
      -center.z * normalizeScale + TARGET_BOUNDS.centerZ,
    );

    // Material anwenden
    clone.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.material = new THREE.MeshStandardMaterial({
          color: highlightColor || '#a78bfa',
          transparent: true,
          opacity,
          metalness: 0.15,
          roughness: 0.75,
          wireframe,
          side: THREE.DoubleSide,
          depthWrite: true,
        });
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });

    const info: GLBModelInfo = {
      aspectRatio: size.x / size.y,
      halfWidth,
      halfDepth,
      normalizeScale,
    };

    return { clonedScene: clone, modelInfo: info };
  }, [scene, opacity, wireframe, highlightColor]);

  useEffect(() => {
    onLoaded?.(modelInfo);
  }, [modelInfo, onLoaded]);

  // Meshes für Surface-Projection exportieren
  useEffect(() => {
    if (clonedScene && onMeshesReady) {
      const meshes: THREE.Mesh[] = [];
      clonedScene.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          meshes.push(child);
        }
      });
      if (meshes.length > 0) {
        onMeshesReady(meshes);
      }
    }
  }, [clonedScene, onMeshesReady]);

  // Atem-Animation
  useFrame((state) => {
    if (groupRef.current) {
      const breath = Math.sin(state.clock.elapsedTime * 0.8) * pulseIntensity;
      groupRef.current.scale.set(1, 1 + breath, 1);
      // Gentle Y-axis sway only - no X/Z rotation to prevent model tilting
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.15) * 0.03;
    }
  });

  return (
    <Float speed={0.3} rotationIntensity={0} floatIntensity={0.05}>
      <group ref={groupRef}>
        <primitive object={clonedScene} />
      </group>
    </Float>
  );
}

export default GLBModelLoader;
