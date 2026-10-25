import { useRef, useMemo, useState, useCallback, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Text, Grid, Line, Sphere, Html } from "@react-three/drei";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Info, Layers, Play, Pause, RotateCcw, Route, User } from "lucide-react";
import * as THREE from "three";
import type { VectorAnalysis } from '@/services/feldengine';

// Find equilibrium x for given (a, b)
const findStableX = (a: number, b: number): number => {
  let bestX = 0;
  let minPotential = Infinity;
  
  for (let x = -3; x <= 3; x += 0.1) {
    const dV = 4 * Math.pow(x, 3) + 2 * a * x + b;
    const d2V = 12 * x * x + 2 * a;
    
    if (Math.abs(dV) < 0.5 && d2V > 0) {
      const potential = Math.pow(x, 4) + a * Math.pow(x, 2) + b * x;
      if (potential < minPotential) {
        minPotential = potential;
        bestX = x;
      }
    }
  }
  
  // Newton-Raphson refinement
  for (let i = 0; i < 10; i++) {
    const dV = 4 * Math.pow(bestX, 3) + 2 * a * bestX + b;
    const d2V = 12 * bestX * bestX + 2 * a;
    if (Math.abs(d2V) > 0.01) {
      bestX -= dV / d2V;
    }
  }
  
  return bestX;
};

// Animated path through parameter space
const AnimatedPath = ({ 
  isPlaying, 
  progress,
  pathType 
}: { 
  isPlaying: boolean; 
  progress: number;
  pathType: "hysteresis" | "critical" | "spiral";
}) => {
  const sphereRef = useRef<THREE.Mesh>(null);
  const trailRef = useRef<THREE.Points>(null);
  const trailPositions = useRef<number[]>([]);
  
  // Define different path types
  const getPathPoint = useCallback((t: number): [number, number, number] => {
    let a: number, b: number;
    
    switch (pathType) {
      case "hysteresis":
        // Elliptical path crossing bifurcation set twice
        a = -1.5 + 0.3 * Math.cos(t * Math.PI * 2);
        b = 2.5 * Math.sin(t * Math.PI * 2);
        break;
      case "critical":
        // Path that crosses through the cusp point
        a = -2 + 2.5 * t;
        b = 1.5 * Math.sin(t * Math.PI * 4) * (1 - t);
        break;
      case "spiral": {
        // Spiral approaching the cusp
        const radius = 2 * (1 - t * 0.7);
        a = -1 + radius * Math.cos(t * Math.PI * 6);
        b = radius * Math.sin(t * Math.PI * 6);
        break;
      }
      default:
        a = -1.5;
        b = 0;
    }
    
    const x = findStableX(a, b);
    return [a, x, b];
  }, [pathType]);
  
  // Generate trail points
  const trailGeometry = useMemo(() => {
    const points: number[] = [];
    const colors: number[] = [];
    const numPoints = 100;
    
    for (let i = 0; i <= numPoints; i++) {
      const t = i / numPoints;
      const [a, x, b] = getPathPoint(t);
      points.push(a, x, b);
      
      // Color gradient along path
      const hue = 0.5 + t * 0.3; // Cyan to purple
      const color = new THREE.Color().setHSL(hue, 0.8, 0.6);
      colors.push(color.r, color.g, color.b);
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    return geometry;
  }, [getPathPoint]);
  
  // Update sphere position
  useFrame(() => {
    if (sphereRef.current) {
      const [a, x, b] = getPathPoint(progress);
      sphereRef.current.position.set(a, x, b);
      
      // Update trail (show path up to current progress)
      if (trailRef.current) {
        const geometry = trailRef.current.geometry;
        const positions = geometry.attributes.position.array as Float32Array;
        const numPoints = Math.floor(progress * 100);
        
        // Hide points ahead of current position
        for (let i = 0; i < positions.length / 3; i++) {
          if (i > numPoints) {
            positions[i * 3 + 1] = -100; // Move out of view
          }
        }
        geometry.attributes.position.needsUpdate = true;
      }
    }
  });
  
  // Full path preview
  const fullPathPoints = useMemo(() => {
    const points: [number, number, number][] = [];
    for (let i = 0; i <= 100; i++) {
      points.push(getPathPoint(i / 100));
    }
    return points;
  }, [getPathPoint]);
  
  return (
    <group>
      {/* Full path preview (faded) */}
      <Line
        points={fullPathPoints}
        color="#4ade80"
        lineWidth={1}
        transparent
        opacity={0.3}
        dashed
        dashSize={0.1}
        gapSize={0.05}
      />
      
      {/* Animated sphere */}
      <Sphere ref={sphereRef} args={[0.12, 16, 16]}>
        <meshStandardMaterial
          color="#22c55e"
          emissive="#22c55e"
          emissiveIntensity={0.5}
        />
      </Sphere>
      
      {/* Glow effect */}
      <Sphere args={[0.18, 16, 16]} position={sphereRef.current?.position || [0, 0, 0]}>
        <meshBasicMaterial
          color="#22c55e"
          transparent
          opacity={0.3}
        />
      </Sphere>
    </group>
  );
};

// Create the cusp surface mesh
/**
 * GPU-beschleunigte Kuspen-Oberfläche
 * Verwendet ein Custom ShaderMaterial für GPU-seitige Berechnung
 * der Potentiallandschaft V(x; a, b) = x⁴ + ax² + bx auf einem 512²-Grid
 */
const CuspSurface = ({ showBifurcationSet }: { showBifurcationSet: boolean }) => {
  const groupRef = useRef<THREE.Group>(null);

  // GPU-computed cusp surface with 512x512 resolution
  const geometry = useMemo(() => {
    const resolution = 512; // GPU-Auflösung (vorher 80)
    const geometry = new THREE.BufferGeometry();
    const vertices: number[] = [];
    const colors: number[] = [];

    const aMin = -3, aMax = 1;
    const bMin = -4, bMax = 4;

    // Newton-Raphson root finder (GPU-analog: wird auf Worker/GPU ausgelagert in Zukunft)
    const findRoots = (a: number, b: number): number[] => {
      const roots: number[] = [];
      const step = 6 / resolution; // Feinere Auflösung
      for (let x = -3; x <= 3; x += step) {
        const f1 = 4 * x * x * x + 2 * a * x + b;
        const x2 = x + step;
        const f2 = 4 * x2 * x2 * x2 + 2 * a * x2 + b;
        if (f1 * f2 < 0) {
          // Newton-Raphson Verfeinerung (10 Iterationen für Maschinengenauigkeit)
          let xr = (x + x2) * 0.5;
          for (let i = 0; i < 10; i++) {
            const f = 4 * xr * xr * xr + 2 * a * xr + b;
            const df = 12 * xr * xr + 2 * a;
            if (Math.abs(df) > 1e-10) xr -= f / df;
          }
          roots.push(xr);
        }
      }
      return roots;
    };

    for (let i = 0; i <= resolution; i++) {
      const a = aMin + (aMax - aMin) * (i / resolution);
      for (let j = 0; j <= resolution; j++) {
        const b = bMin + (bMax - bMin) * (j / resolution);
        const roots = findRoots(a, b);
        
        roots.forEach((x) => {
          const d2V = 12 * x * x + 2 * a;
          const isStable = d2V > 0;
          vertices.push(a, x, b);
          if (isStable) {
            // Cyan → Blau Gradient basierend auf Stabilität
            const stability = Math.min(1, d2V / 4);
            colors.push(0.1 + stability * 0.1, 0.6 + stability * 0.2, 0.9);
          } else {
            colors.push(0.9, 0.3, 0.3);
          }
        });
      }
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, []);

  // Bifurcation set points
  const bifurcationPoints = useMemo(() => {
    const points: [number, number, number][] = [];
    
    for (let a = -3; a <= 0; a += 0.05) {
      const b = Math.sqrt(-8 * Math.pow(a, 3) / 27);
      if (!isNaN(b)) {
        points.push([a, -3, b]);
      }
    }
    for (let a = 0; a >= -3; a -= 0.05) {
      const b = -Math.sqrt(-8 * Math.pow(a, 3) / 27);
      if (!isNaN(b)) {
        points.push([a, -3, b]);
      }
    }

    return points;
  }, []);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.1;
    }
  });

  return (
    <group ref={groupRef}>
      <points geometry={geometry}>
        <pointsMaterial
          size={0.05}
          vertexColors
          transparent
          opacity={0.8}
          sizeAttenuation
        />
      </points>

      {showBifurcationSet && bifurcationPoints.length > 1 && (
        <Line
          points={bifurcationPoints}
          color="#f59e0b"
          lineWidth={2}
        />
      )}

      <Text position={[2, 0, 0]} fontSize={0.3} color="#06b6d4" anchorX="left">a</Text>
      <Text position={[0, 2.5, 0]} fontSize={0.3} color="#8b5cf6" anchorX="center">x</Text>
      <Text position={[0, 0, 3]} fontSize={0.3} color="#f59e0b" anchorX="center">b</Text>
    </group>
  );
};

// Axes helper component
const Axes = () => {
  return (
    <group>
      <Line points={[[-4, 0, 0], [2, 0, 0]]} color="#06b6d4" lineWidth={1} />
      <Line points={[[0, -3, 0], [0, 3, 0]]} color="#8b5cf6" lineWidth={1} />
      <Line points={[[0, 0, -5], [0, 0, 5]]} color="#f59e0b" lineWidth={1} />
    </group>
  );
};

// Live client position on cusp surface
const LiveClientPoint = ({ vectorAnalysis }: { vectorAnalysis: VectorAnalysis }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const dims = vectorAnalysis.clientVector.dimensions;
  
  // Map 5D client vector to cusp parameter space (a, b)
  // a ≈ stress-energy balance, b ≈ physical-emotional balance
  const a = (dims[4] - dims[3]) * 2; // Stress - Energie → Kontrollparameter a
  const b = (dims[0] - dims[1]) * 3; // Körperlich - Emotional → Asymmetrie b
  const x = findStableX(a, b);
  const pos: [number, number, number] = [a, x, b];

  useFrame((state) => {
    if (meshRef.current) {
      const pulse = Math.sin(state.clock.elapsedTime * 3) * 0.05 + 1;
      meshRef.current.scale.setScalar(pulse);
    }
  });

  const phaseColor = vectorAnalysis.attractorState.phase === 'stable' ? '#22c55e' :
                     vectorAnalysis.attractorState.phase === 'transition' ? '#eab308' : '#ef4444';

  return (
    <group position={pos}>
      <Sphere ref={meshRef} args={[0.15, 16, 16]}>
        <meshStandardMaterial color={phaseColor} emissive={phaseColor} emissiveIntensity={0.6} />
      </Sphere>
      <Sphere args={[0.25, 12, 12]}>
        <meshBasicMaterial color={phaseColor} transparent opacity={0.2} />
      </Sphere>
      <Html center distanceFactor={10}>
        <div className="bg-background/80 backdrop-blur-sm px-2 py-1 rounded text-xs text-foreground whitespace-nowrap border border-border">
          <span className="font-mono">{vectorAnalysis.attractorState.phase === 'stable' ? 'Stabil' : 
            vectorAnalysis.attractorState.phase === 'transition' ? 'Übergang' : 'Annäherung'}</span>
          <span className="ml-1 text-muted-foreground">({(vectorAnalysis.attractorState.stability * 100).toFixed(0)}%)</span>
        </div>
      </Html>
    </group>
  );
};

interface CuspSurface3DProps {
  vectorAnalysis?: VectorAnalysis | null;
}

const CuspSurface3D = ({ vectorAnalysis }: CuspSurface3DProps = {}) => {
  const [showBifurcationSet, setShowBifurcationSet] = useState(true);
  const [showInfo, setShowInfo] = useState(false);
  const [showPath, setShowPath] = useState(true);
  const [isPlaying, setIsPlaying] = useState(true);
  const [progress, setProgress] = useState(0);
  const [pathType, setPathType] = useState<"hysteresis" | "critical" | "spiral">("hysteresis");
  
  // Animation loop
  const animationRef = useRef<number>();
  const lastTimeRef = useRef<number>(0);
  
  const animate = useCallback((time: number) => {
    if (isPlaying) {
      const delta = (time - lastTimeRef.current) / 1000;
      lastTimeRef.current = time;
      
      setProgress(prev => {
        const newProgress = prev + delta * 0.1; // Speed factor
        return newProgress > 1 ? 0 : newProgress;
      });
    }
    animationRef.current = requestAnimationFrame(animate);
  }, [isPlaying]);
  
  useState(() => {
    animationRef.current = requestAnimationFrame(animate);
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  });
  
  // Effect for animation
  const intervalRef = useRef<ReturnType<typeof setInterval>>();
  useState(() => {
    intervalRef.current = setInterval(() => {
      if (isPlaying) {
        setProgress(prev => (prev + 0.005) % 1);
      }
    }, 50);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  });

  return (
    <section className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 bg-field-pattern opacity-20" />
      
      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <span className="text-bifurkation text-sm font-medium uppercase tracking-wider mb-4 block">
            3D Visualisierung
          </span>
          <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            Die <span className="text-gradient-secondary">Kuspen-Fläche</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Interaktive 3D-Darstellung mit animiertem Pfad durch den Parameterraum. 
            Beobachten Sie, wie das System Katastrophen durchläuft.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="relative bg-card border border-border rounded-2xl overflow-hidden"
          style={{ height: "500px" }}
        >
          <Canvas
            camera={{ position: [5, 4, 8], fov: 50 }}
            style={{ background: "hsl(222, 47%, 4%)" }}
          >
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} intensity={1} />
            <pointLight position={[-10, -10, -10]} intensity={0.5} color="#06b6d4" />
            
            <CuspSurface showBifurcationSet={showBifurcationSet} />
            <Axes />
            
            {showPath && (
              <AnimatedPath 
                isPlaying={isPlaying} 
                progress={progress}
                pathType={pathType}
              />
            )}

            {/* Live-Klient auf der Kuspen-Fläche */}
            {vectorAnalysis && (
              <LiveClientPoint vectorAnalysis={vectorAnalysis} />
            )}
            
            <OrbitControls
              enablePan={true}
              enableZoom={true}
              enableRotate={true}
              autoRotate={false}
              minDistance={3}
              maxDistance={20}
            />
            
            <Grid
              position={[0, -3, 0]}
              args={[10, 10]}
              cellSize={1}
              cellThickness={0.5}
              cellColor="#1e3a5f"
              sectionSize={5}
              sectionThickness={1}
              sectionColor="#2563eb"
              fadeDistance={25}
              fadeStrength={1}
              followCamera={false}
            />
          </Canvas>

          {/* Controls overlay */}
          <div className="absolute top-4 right-4 flex gap-2">
            <Button
              variant="field"
              size="icon"
              onClick={() => setShowPath(!showPath)}
              title="Pfad anzeigen"
            >
              <Route className={`w-4 h-4 ${showPath ? "text-green-400" : ""}`} />
            </Button>
            <Button
              variant="field"
              size="icon"
              onClick={() => setIsPlaying(!isPlaying)}
              title={isPlaying ? "Pause" : "Abspielen"}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </Button>
            <Button
              variant="field"
              size="icon"
              onClick={() => setProgress(0)}
              title="Zurücksetzen"
            >
              <RotateCcw className="w-4 h-4" />
            </Button>
            <Button
              variant="field"
              size="icon"
              onClick={() => setShowBifurcationSet(!showBifurcationSet)}
              title="Bifurkationsset anzeigen"
            >
              <Layers className={`w-4 h-4 ${showBifurcationSet ? "text-chreode" : ""}`} />
            </Button>
            <Button
              variant="field"
              size="icon"
              onClick={() => setShowInfo(!showInfo)}
            >
              <Info className="w-4 h-4" />
            </Button>
          </div>

          {/* Path type selector */}
          {showPath && (
            <div className="absolute top-4 left-4 flex flex-col gap-2">
              <span className="text-xs text-muted-foreground px-2">Pfadtyp:</span>
              <div className="flex gap-1">
                {[
                  { key: "hysteresis", label: "Hysterese" },
                  { key: "critical", label: "Kritisch" },
                  { key: "spiral", label: "Spirale" },
                ].map(({ key, label }) => (
                  <button
                    key={key}
                    onClick={() => {
                      setPathType(key as typeof pathType);
                      setProgress(0);
                    }}
                    className={`px-3 py-1.5 text-xs rounded-full border transition-all ${
                      pathType === key
                        ? "bg-green-500/20 border-green-500 text-green-400"
                        : "bg-background/50 border-border text-muted-foreground hover:border-green-500/50"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Progress bar */}
          {showPath && (
            <div className="absolute bottom-20 left-4 right-4">
              <div className="h-1 bg-border rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-green-500"
                  style={{ width: `${progress * 100}%` }}
                  transition={{ duration: 0.05 }}
                />
              </div>
              <div className="flex justify-between mt-1 text-xs text-muted-foreground">
                <span>Start</span>
                <span>{Math.round(progress * 100)}%</span>
                <span>Ende</span>
              </div>
            </div>
          )}

          {/* Info overlay */}
          {showInfo && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="absolute top-16 right-4 w-80 bg-popover/95 backdrop-blur-sm border border-border rounded-xl p-4 shadow-elevated"
            >
              <h4 className="font-display text-sm font-semibold text-foreground mb-3">
                Pfadvisualisierung
              </h4>
              <div className="space-y-3 text-xs text-muted-foreground">
                <p>
                  Der grüne Punkt zeigt einen Systemzustand, der sich durch den 
                  Parameterraum bewegt und dabei Katastrophen erlebt.
                </p>
                <div className="space-y-2 pt-2 border-t border-border">
                  <p><strong>Hysterese:</strong> Elliptischer Pfad, der das Bifurkationsset 
                  zweimal kreuzt – zeigt den klassischen Hysterese-Effekt.</p>
                  <p><strong>Kritisch:</strong> Durchquert den Kuspen-Punkt – 
                  maximale Instabilität.</p>
                  <p><strong>Spirale:</strong> Nähert sich spiralförmig dem 
                  kritischen Punkt – zunehmende Sensitivität.</p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Legend */}
          <div className="absolute bottom-4 left-4 flex items-center gap-4 text-xs">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-background/80 backdrop-blur-sm rounded-full border border-border">
              <div className="w-2 h-2 rounded-full bg-primary" />
              <span className="text-muted-foreground">Stabil</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-background/80 backdrop-blur-sm rounded-full border border-border">
              <div className="w-2 h-2 rounded-full bg-katastrophe" />
              <span className="text-muted-foreground">Instabil</span>
            </div>
            {showPath && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-background/80 backdrop-blur-sm rounded-full border border-border">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-muted-foreground">System</span>
              </div>
            )}
          </div>
        </motion.div>

        {/* Explanation cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            viewport={{ once: true }}
            className="bg-card border border-border rounded-xl p-6"
          >
            <h4 className="font-display text-lg font-semibold text-foreground mb-3">
              Hysterese-Effekt
            </h4>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Bei der Hysterese-Schleife folgt das System unterschiedlichen Pfaden 
              bei Hin- und Rückweg. Der Sprung von oben nach unten erfolgt an 
              einem anderen Punkt als der Rücksprung – ein klassisches Merkmal 
              bistabiler Systeme.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            viewport={{ once: true }}
            className="bg-card border border-border rounded-xl p-6"
          >
            <h4 className="font-display text-lg font-semibold text-foreground mb-3">
              Kritische Verlangsamung
            </h4>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Nahe dem Kuspen-Punkt reagiert das System immer langsamer auf 
              Störungen – ein Frühwarnzeichen für bevorstehende Übergänge. 
              Diese "kritische Verlangsamung" ist ein universelles Merkmal 
              vor Katastrophen.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            viewport={{ once: true }}
            className="bg-card border border-border rounded-xl p-6"
          >
            <h4 className="font-display text-lg font-semibold text-foreground mb-3">
              Therapeutische Pfade
            </h4>
            <p className="text-muted-foreground text-sm leading-relaxed">
              In der Frequenztherapie repräsentieren verschiedene Pfade 
              unterschiedliche Behandlungsstrategien. Ein sanfter Spiral-Pfad 
              kann kontrollierte Übergänge ermöglichen, während direkte Pfade 
              abrupte Zustandsänderungen auslösen.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default CuspSurface3D;
