/**
 * Hochqualitatives 3D-Anatomie-Modell Komponente
 * Verwendet prozedurales Modell mit detaillierter Geometrie
 * Designed für spätere GLB-Integration
 */
import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Float } from '@react-three/drei';

interface DetailedHumanModelProps {
  opacity?: number;
  showMuscles?: boolean;
  showSkeleton?: boolean;
  pulseIntensity?: number;
  highlightedRegions?: string[];
}

// Körperproportionen nach anatomischen Standards
const BODY_PROPORTIONS = {
  headRadius: 0.09,
  neckHeight: 0.06,
  torsoHeight: 0.35,
  torsoWidth: 0.18,
  torsoDepth: 0.12,
  waistWidth: 0.14,
  hipWidth: 0.16,
  upperArmLength: 0.14,
  lowerArmLength: 0.13,
  handLength: 0.06,
  upperLegLength: 0.2,
  lowerLegLength: 0.22,
  footLength: 0.08,
};

export function DetailedHumanModel({
  opacity = 0.4,
  showMuscles = false,
  showSkeleton = false,
  pulseIntensity = 0.02,
  highlightedRegions = [],
}: DetailedHumanModelProps) {
  const groupRef = useRef<THREE.Group>(null);
  
  // Atmungs-Animation
  useFrame((state) => {
    if (groupRef.current) {
      const breath = Math.sin(state.clock.elapsedTime * 0.8) * pulseIntensity;
      
      // Sanfte Bewegung
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.15) * 0.04;
      
      // Atmung auf Torso anwenden
      groupRef.current.children.forEach((child) => {
        if (child.name === 'torso') {
          child.scale.x = 1 + breath * 0.5;
          child.scale.z = 1 + breath * 0.3;
        }
      });
    }
  });
  
  // Materialien
  const skinMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#c9a89d',
    transparent: true,
    opacity,
    metalness: 0.1,
    roughness: 0.8,
  }), [opacity]);
  
  const muscleMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#8b4557',
    transparent: true,
    opacity: opacity * 0.7,
    metalness: 0.2,
    roughness: 0.6,
  }), [opacity]);
  
  const skeletonMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#e8dcc8',
    transparent: true,
    opacity: opacity * 0.9,
    metalness: 0.05,
    roughness: 0.95,
  }), [opacity]);
  
  const highlightMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: '#8b5cf6',
    transparent: true,
    opacity: 0.6,
    emissive: '#8b5cf6',
    emissiveIntensity: 0.5,
  }), []);
  
  const getMaterial = (region: string) => {
    if (highlightedRegions.includes(region)) return highlightMaterial;
    if (showSkeleton) return skeletonMaterial;
    if (showMuscles) return muscleMaterial;
    return skinMaterial;
  };
  
  return (
    <Float speed={0.5} rotationIntensity={0} floatIntensity={0.1}>
      <group ref={groupRef} position={[0, 0.4, 0]}>
        
        {/* ===== KOPF ===== */}
        <group name="head" position={[0, 0.48, 0]}>
          {/* Schädel */}
          <mesh>
            <sphereGeometry args={[BODY_PROPORTIONS.headRadius, 32, 32]} />
            <primitive object={getMaterial('head')} />
          </mesh>
          
          {/* Gesicht (leicht abgeflacht) */}
          <mesh position={[0, -0.01, 0.04]} scale={[0.9, 0.95, 0.8]}>
            <sphereGeometry args={[BODY_PROPORTIONS.headRadius * 0.85, 32, 32]} />
            <primitive object={getMaterial('face')} />
          </mesh>
          
          {/* Kiefer */}
          <mesh position={[0, -0.05, 0.02]}>
            <boxGeometry args={[0.06, 0.04, 0.05]} />
            <primitive object={getMaterial('jaw')} />
          </mesh>
        </group>
        
        {/* ===== HALS ===== */}
        <mesh name="neck" position={[0, 0.38, 0]}>
          <cylinderGeometry args={[0.028, 0.035, BODY_PROPORTIONS.neckHeight, 16]} />
          <primitive object={getMaterial('neck')} />
        </mesh>
        
        {/* ===== OBERKÖRPER ===== */}
        <group name="torso">
          {/* Brustkorb */}
          <mesh position={[0, 0.24, 0]}>
            <capsuleGeometry args={[BODY_PROPORTIONS.torsoWidth * 0.6, 0.18, 16, 32]} />
            <primitive object={getMaterial('chest')} />
          </mesh>
          
          {/* Schultern */}
          {[-1, 1].map((side) => (
            <mesh key={`shoulder-${side}`} position={[side * 0.12, 0.30, 0]}>
              <sphereGeometry args={[0.04, 16, 16]} />
              <primitive object={getMaterial('shoulder')} />
            </mesh>
          ))}
          
          {/* Bauch */}
          <mesh position={[0, 0.08, 0.01]}>
            <capsuleGeometry args={[BODY_PROPORTIONS.waistWidth * 0.5, 0.1, 16, 32]} />
            <primitive object={getMaterial('abdomen')} />
          </mesh>
        </group>
        
        {/* ===== BECKEN ===== */}
        <mesh name="pelvis" position={[0, -0.04, 0]}>
          <capsuleGeometry args={[BODY_PROPORTIONS.hipWidth * 0.4, 0.06, 16, 32]} />
          <primitive object={getMaterial('pelvis')} />
        </mesh>
        
        {/* ===== ARME ===== */}
        {[-1, 1].map((side) => (
          <group key={`arm-${side}`} name={side === -1 ? 'leftArm' : 'rightArm'}>
            {/* Oberarm */}
            <mesh 
              position={[side * 0.18, 0.22, 0]} 
              rotation={[0, 0, side * 0.15]}
            >
              <capsuleGeometry args={[0.028, BODY_PROPORTIONS.upperArmLength, 12, 24]} />
              <primitive object={getMaterial('upperArm')} />
            </mesh>
            
            {/* Ellbogen */}
            <mesh position={[side * 0.22, 0.10, 0]}>
              <sphereGeometry args={[0.025, 12, 12]} />
              <primitive object={getMaterial('elbow')} />
            </mesh>
            
            {/* Unterarm */}
            <mesh 
              position={[side * 0.25, -0.02, 0.01]} 
              rotation={[0.1, 0, side * 0.1]}
            >
              <capsuleGeometry args={[0.022, BODY_PROPORTIONS.lowerArmLength, 12, 24]} />
              <primitive object={getMaterial('forearm')} />
            </mesh>
            
            {/* Handgelenk */}
            <mesh position={[side * 0.27, -0.14, 0.02]}>
              <sphereGeometry args={[0.018, 12, 12]} />
              <primitive object={getMaterial('wrist')} />
            </mesh>
            
            {/* Hand */}
            <mesh position={[side * 0.28, -0.18, 0.02]}>
              <boxGeometry args={[0.035, BODY_PROPORTIONS.handLength, 0.015]} />
              <primitive object={getMaterial('hand')} />
            </mesh>
          </group>
        ))}
        
        {/* ===== BEINE ===== */}
        {[-1, 1].map((side) => (
          <group key={`leg-${side}`} name={side === -1 ? 'leftLeg' : 'rightLeg'}>
            {/* Hüftgelenk */}
            <mesh position={[side * 0.06, -0.08, 0]}>
              <sphereGeometry args={[0.035, 12, 12]} />
              <primitive object={getMaterial('hip')} />
            </mesh>
            
            {/* Oberschenkel */}
            <mesh position={[side * 0.06, -0.20, 0]}>
              <capsuleGeometry args={[0.04, BODY_PROPORTIONS.upperLegLength, 12, 24]} />
              <primitive object={getMaterial('thigh')} />
            </mesh>
            
            {/* Knie */}
            <mesh position={[side * 0.06, -0.34, 0.01]}>
              <sphereGeometry args={[0.032, 12, 12]} />
              <primitive object={getMaterial('knee')} />
            </mesh>
            
            {/* Unterschenkel */}
            <mesh position={[side * 0.06, -0.50, 0]}>
              <capsuleGeometry args={[0.028, BODY_PROPORTIONS.lowerLegLength, 12, 24]} />
              <primitive object={getMaterial('calf')} />
            </mesh>
            
            {/* Knöchel */}
            <mesh position={[side * 0.06, -0.66, 0]}>
              <sphereGeometry args={[0.022, 12, 12]} />
              <primitive object={getMaterial('ankle')} />
            </mesh>
            
            {/* Fuß */}
            <mesh position={[side * 0.06, -0.70, 0.03]} rotation={[0.3, 0, 0]}>
              <boxGeometry args={[0.04, 0.02, BODY_PROPORTIONS.footLength]} />
              <primitive object={getMaterial('foot')} />
            </mesh>
          </group>
        ))}
        
        {/* ===== WIRBELSÄULE (wenn Skelett sichtbar) ===== */}
        {showSkeleton && (
          <group name="spine">
            {Array.from({ length: 24 }).map((_, i) => (
              <mesh 
                key={`vertebra-${i}`} 
                position={[0, 0.35 - i * 0.025, -0.04]}
              >
                <boxGeometry args={[0.025, 0.018, 0.02]} />
                <primitive object={skeletonMaterial} />
              </mesh>
            ))}
          </group>
        )}
        
        {/* ===== ORGANE (wenn Muskeln sichtbar) ===== */}
        {showMuscles && (
          <group name="organs">
            {/* Herz */}
            <mesh position={[0.03, 0.26, 0.02]}>
              <sphereGeometry args={[0.035, 16, 16]} />
              <meshStandardMaterial 
                color="#dc2626" 
                transparent 
                opacity={0.7}
                emissive="#dc2626"
                emissiveIntensity={0.3}
              />
            </mesh>
            
            {/* Lungen */}
            {[-1, 1].map((side) => (
              <mesh 
                key={`lung-${side}`} 
                position={[side * 0.06, 0.25, 0]}
              >
                <capsuleGeometry args={[0.04, 0.08, 8, 16]} />
                <meshStandardMaterial 
                  color="#ec4899" 
                  transparent 
                  opacity={0.5}
                />
              </mesh>
            ))}
            
            {/* Leber */}
            <mesh position={[0.05, 0.14, 0.02]}>
              <sphereGeometry args={[0.045, 16, 16]} />
              <meshStandardMaterial 
                color="#7c2d12" 
                transparent 
                opacity={0.6}
              />
            </mesh>
            
            {/* Magen */}
            <mesh position={[-0.03, 0.12, 0.03]}>
              <sphereGeometry args={[0.03, 16, 16]} />
              <meshStandardMaterial 
                color="#be185d" 
                transparent 
                opacity={0.5}
              />
            </mesh>
          </group>
        )}
      </group>
    </Float>
  );
}

export default DetailedHumanModel;
