/**
 * 3D-Trajektorien-Visualisierung im Kuspen-Raum
 * Zeigt den aktuellen Klienten-Vektor und die Bewegung zum Attraktor in Echtzeit
 */
import { useRef, useMemo, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Line, Sphere, Html } from '@react-three/drei';
import * as THREE from 'three';
import { motion } from 'framer-motion';
import { Activity, Target, Zap, TrendingUp, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { VectorAnalysis } from '@/services/feldengine';

interface ClientVectorTrajectory3DProps {
  vectorAnalysis: VectorAnalysis | null;
  isAnimating?: boolean;
}

const DEFAULT_ATTRACTOR_POSITION: [number, number, number] = [0, 0, 0];

// Cusp-Oberfläche berechnen
function CuspSurface() {
  const meshRef = useRef<THREE.Points>(null);

  const { geometry, colors } = useMemo(() => {
    const positions: number[] = [];
    const cols: number[] = [];
    const resolution = 60;

    for (let i = 0; i < resolution; i++) {
      for (let j = 0; j < resolution; j++) {
        const a = (i / resolution - 0.5) * 4;
        const b = (j / resolution - 0.5) * 4;

        // Cusp: V(x) = x⁴ + ax² + bx, dV/dx = 4x³ + 2ax + b = 0
        // Approximation der stabilen Lösungen
        for (let k = -1; k <= 1; k += 0.5) {
          const x = k * 1.5;
          const derivative = 4 * Math.pow(x, 3) + 2 * a * x + b;
          const secondDerivative = 12 * x * x + 2 * a;

          if (Math.abs(derivative) < 1.5) {
            positions.push(a, x, b);

            // Farbe basierend auf Stabilität
            const isStable = secondDerivative > 0;
            if (isStable) {
              cols.push(0.2, 0.6, 0.9); // Blau für stabil
            } else {
              cols.push(0.9, 0.3, 0.3); // Rot für instabil
            }
          }
        }
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));

    return { geometry: geo, colors: cols };
  }, []);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.05;
    }
  });

  return (
    <points ref={meshRef} geometry={geometry}>
      <pointsMaterial
        size={0.03}
        vertexColors
        transparent
        opacity={0.4}
        sizeAttenuation
      />
    </points>
  );
}

// Attraktor-Punkt (Ziel)
function AttractorPoint({ position, stability }: { position: number[]; stability: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current && glowRef.current) {
      const pulse = Math.sin(state.clock.elapsedTime * 2) * 0.1 + 1;
      meshRef.current.scale.setScalar(pulse * 0.15);
      glowRef.current.scale.setScalar(pulse * 0.4);
    }
  });

  const attractorPos: [number, number, number] = [0, 0, 0]; // Optimaler Attraktor im Zentrum

  return (
    <group position={attractorPos}>
      {/* Glow */}
      <Sphere ref={glowRef} args={[1, 16, 16]}>
        <meshBasicMaterial color="#22c55e" transparent opacity={0.15} />
      </Sphere>
      {/* Core */}
      <Sphere ref={meshRef} args={[1, 32, 32]}>
        <meshStandardMaterial
          color="#22c55e"
          emissive="#22c55e"
          emissiveIntensity={0.5}
        />
      </Sphere>
      <Html center distanceFactor={10}>
        <div className="bg-green-500/20 backdrop-blur-sm px-2 py-1 rounded text-xs text-green-400 whitespace-nowrap">
          Attraktor ({(stability * 100).toFixed(0)}%)
        </div>
      </Html>
    </group>
  );
}

// Aktueller Klienten-Vektor-Punkt
function ClientPoint({
  position,
  phase,
  bifurcationRisk
}: {
  position: number[];
  phase: string;
  bifurcationRisk: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const trailRef = useRef<THREE.Line>(null);
  const [trail, setTrail] = useState<THREE.Vector3[]>([]);

  // 3D-Position aus 5D-Vektor (verwende erste 3 Dimensionen)
  const pos3D: [number, number, number] = [
    position[0] * 1.5 || 0,
    position[1] * 1.5 || 0,
    position[2] * 1.5 || 0
  ];

  useFrame((state) => {
    if (meshRef.current) {
      // Pulsieren
      const pulse = Math.sin(state.clock.elapsedTime * 3) * 0.1 + 1;
      meshRef.current.scale.setScalar(pulse * 0.12);

      // Trail aktualisieren
      const currentPos = new THREE.Vector3(...pos3D);
      setTrail(prev => {
        const newTrail = [...prev, currentPos].slice(-50);
        return newTrail;
      });
    }
  });

  // Farbe basierend auf Phase
  const phaseColor = phase === 'stable' ? '#22c55e' :
                     phase === 'transition' ? '#eab308' : '#ef4444';

  return (
    <group>
      {/* Trail */}
      {trail.length > 2 && (
        <Line
          points={trail}
          color={phaseColor}
          lineWidth={2}
          transparent
          opacity={0.5}
        />
      )}

      {/* Klienten-Punkt */}
      <Sphere ref={meshRef} args={[1, 32, 32]} position={pos3D}>
        <meshStandardMaterial
          color={phaseColor}
          emissive={phaseColor}
          emissiveIntensity={0.8}
        />
      </Sphere>

      {/* Label */}
      <Html center position={[pos3D[0], pos3D[1] + 0.3, pos3D[2]]} distanceFactor={8}>
        <div className="bg-background/80 backdrop-blur-sm px-2 py-1 rounded text-xs text-foreground whitespace-nowrap border border-border">
          Klient ({phase})
          {bifurcationRisk > 0.5 && (
            <span className="ml-1 text-red-400">⚠</span>
          )}
        </div>
      </Html>
    </group>
  );
}

// Verbindungslinie zum Attraktor
function ConnectionLine({
  clientPosition,
  attractorPosition = DEFAULT_ATTRACTOR_POSITION
}: {
  clientPosition: number[];
  attractorPosition?: number[];
}) {
  const points = useMemo(() => {
    const pos3D: [number, number, number] = [
      clientPosition[0] * 1.5 || 0,
      clientPosition[1] * 1.5 || 0,
      clientPosition[2] * 1.5 || 0
    ];
    const start = new THREE.Vector3(...pos3D);
    const end = new THREE.Vector3(...(attractorPosition as [number, number, number]));
    const curve = new THREE.QuadraticBezierCurve3(
      start,
      new THREE.Vector3(
        (start.x + end.x) / 2,
        (start.y + end.y) / 2 + 0.3,
        (start.z + end.z) / 2
      ),
      end
    );
    return curve.getPoints(30);
  }, [clientPosition, attractorPosition]);

  return (
    <Line
      points={points}
      color="#60a5fa"
      lineWidth={1}
      dashed
      dashScale={5}
      dashSize={0.1}
      gapSize={0.05}
      transparent
      opacity={0.6}
    />
  );
}

// Achsen und Labels
function Axes() {
  return (
    <group>
      {/* X-Achse (Physical) */}
      <Line points={[[-2, 0, 0], [2, 0, 0]]} color="#ef4444" lineWidth={1} />
      <Text position={[2.2, 0, 0]} fontSize={0.15} color="#ef4444">
        Körperlich
      </Text>

      {/* Y-Achse (Emotional) */}
      <Line points={[[0, -2, 0], [0, 2, 0]]} color="#a855f7" lineWidth={1} />
      <Text position={[0, 2.2, 0]} fontSize={0.15} color="#a855f7">
        Emotional
      </Text>

      {/* Z-Achse (Mental) */}
      <Line points={[[0, 0, -2], [0, 0, 2]]} color="#3b82f6" lineWidth={1} />
      <Text position={[0, 0, 2.2]} fontSize={0.15} color="#3b82f6">
        Mental
      </Text>
    </group>
  );
}

// Energie-Ring Visualisierung
function EnergyRings({ energy, stress }: { energy: number; stress: number }) {
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (ringRef.current) {
      ringRef.current.rotation.x = state.clock.elapsedTime * 0.2;
      ringRef.current.rotation.z = state.clock.elapsedTime * 0.1;
    }
  });

  const energyRadius = 0.8 + energy * 0.4;
  const stressColor = stress > 0 ? `hsl(${30 - stress * 30}, 80%, 50%)` : '#22c55e';

  return (
    <mesh ref={ringRef} position={[0, 0, 0]}>
      <torusGeometry args={[energyRadius, 0.02, 8, 64]} />
      <meshBasicMaterial color={stressColor} transparent opacity={0.4} />
    </mesh>
  );
}

const ClientVectorTrajectory3D = ({
  vectorAnalysis,
  isAnimating = false
}: ClientVectorTrajectory3DProps) => {
  const [autoRotate, setAutoRotate] = useState(true);
  const [showCusp, setShowCusp] = useState(true);

  // Default-Werte wenn keine Analyse vorhanden
  const dimensions = vectorAnalysis?.clientVector.dimensions || [0, 0, 0, 0, 0];
  const attractorState = vectorAnalysis?.attractorState || {
    position: dimensions,
    stability: 0.5,
    bifurcationRisk: 0.3,
    phase: 'approach' as const,
    chreodeAlignment: 0.5
  };

  // Dimensionswerte für Anzeige
  const displayDimensions = [
    { name: 'Körperlich', value: dimensions[0], color: 'text-red-400' },
    { name: 'Emotional', value: dimensions[1], color: 'text-purple-400' },
    { name: 'Mental', value: dimensions[2], color: 'text-blue-400' },
    { name: 'Energie', value: dimensions[3], color: 'text-yellow-400' },
    { name: 'Stress', value: dimensions[4], color: 'text-orange-400' },
  ];

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-muted/20 to-background">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-8"
        >
          <h2 className="font-display text-3xl md:text-4xl text-foreground mb-4">
            3D <span className="text-gradient-primary">Trajektorien</span>-Visualisierung
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Echtzeit-Darstellung des Klienten-Vektors im topologischen Kuspen-Raum
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 3D Visualization */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="lg:col-span-3 h-[500px] bg-card rounded-lg border border-border overflow-hidden relative"
          >
            <Canvas
              camera={{ position: [3, 2, 3], fov: 50 }}
              gl={{ antialias: true, alpha: true }}
            >
              <ambientLight intensity={0.4} />
              <pointLight position={[10, 10, 10]} intensity={0.8} />
              <pointLight position={[-10, -10, -10]} intensity={0.3} color="#60a5fa" />

              {/* Cusp-Oberfläche */}
              {showCusp && <CuspSurface />}

              {/* Achsen */}
              <Axes />

              {/* Energie-Ringe */}
              <EnergyRings
                energy={dimensions[3] || 0}
                stress={dimensions[4] || 0}
              />

              {/* Attraktor */}
              <AttractorPoint
                position={[0, 0, 0]}
                stability={attractorState.stability}
              />

              {/* Klienten-Vektor */}
              {vectorAnalysis && (
                <>
                  <ClientPoint
                    position={dimensions}
                    phase={attractorState.phase}
                    bifurcationRisk={attractorState.bifurcationRisk}
                  />
                  <ConnectionLine clientPosition={dimensions} />
                </>
              )}

              <OrbitControls
                enablePan={true}
                enableZoom={true}
                enableRotate={true}
                autoRotate={autoRotate}
                autoRotateSpeed={0.5}
              />
            </Canvas>

            {/* Controls Overlay */}
            <div className="absolute bottom-4 left-4 flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setAutoRotate(!autoRotate)}
                className="bg-background/80 backdrop-blur-sm"
              >
                <RotateCcw className={`w-4 h-4 ${autoRotate ? 'animate-spin' : ''}`} />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowCusp(!showCusp)}
                className="bg-background/80 backdrop-blur-sm"
              >
                {showCusp ? 'Cusp ✓' : 'Cusp'}
              </Button>
            </div>

            {/* Legende */}
            <div className="absolute top-4 right-4 bg-background/80 backdrop-blur-sm p-3 rounded-lg border border-border text-xs space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-muted-foreground">Attraktor (Ziel)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span className="text-muted-foreground">Klient (aktuell)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-400 opacity-50" />
                <span className="text-muted-foreground">Cusp-Oberfläche</span>
              </div>
            </div>
          </motion.div>

          {/* Status Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-4"
          >
            {/* Attraktor-Status */}
            <div className="bg-card rounded-lg border border-border p-4">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-5 h-5 text-primary" />
                <h3 className="font-medium text-foreground">Attraktor-Status</h3>
              </div>

              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Stabilität</span>
                    <span className="text-foreground">{(attractorState.stability * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-400 transition-all duration-500"
                      style={{ width: `${attractorState.stability * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Bifurkationsrisiko</span>
                    <span className="text-foreground">{(attractorState.bifurcationRisk * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-yellow-500 to-red-500 transition-all duration-500"
                      style={{ width: `${attractorState.bifurcationRisk * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Chreode-Alignment</span>
                    <span className="text-foreground">{(attractorState.chreodeAlignment * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                      style={{ width: `${attractorState.chreodeAlignment * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="mt-4 p-2 bg-muted/30 rounded text-center">
                <span className={`text-sm font-medium ${
                  attractorState.phase === 'stable' ? 'text-green-400' :
                  attractorState.phase === 'transition' ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  Phase: {attractorState.phase === 'stable' ? 'Stabil' :
                          attractorState.phase === 'transition' ? 'Übergang' : 'Annäherung'}
                </span>
              </div>
            </div>

            {/* Dimensionen */}
            <div className="bg-card rounded-lg border border-border p-4">
              <div className="flex items-center gap-2 mb-3">
                <Activity className="w-5 h-5 text-primary" />
                <h3 className="font-medium text-foreground">Dimensionen</h3>
              </div>

              <div className="space-y-2">
                {displayDimensions.map((dim, i) => (
                  <div key={dim.name} className="flex items-center justify-between">
                    <span className={`text-xs ${dim.color}`}>{dim.name}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-300 ${
                            dim.value >= 0 ? 'bg-green-500' : 'bg-red-500'
                          }`}
                          style={{
                            width: `${Math.abs(dim.value) * 50 + 50}%`,
                            marginLeft: dim.value < 0 ? `${50 - Math.abs(dim.value) * 50}%` : '50%'
                          }}
                        />
                      </div>
                      <span className="text-xs font-mono text-muted-foreground w-10 text-right">
                        {dim.value.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            {vectorAnalysis && (
              <div className="bg-card rounded-lg border border-border p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Zap className="w-5 h-5 text-primary" />
                  <h3 className="font-medium text-foreground">Empfehlung</h3>
                </div>

                {vectorAnalysis.recommendedFrequencies.slice(0, 2).map((freq, i) => (
                  <div
                    key={i}
                    className="p-2 bg-muted/30 rounded-lg mb-2 last:mb-0"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-foreground">{freq.name}</span>
                      <span className="text-xs text-primary font-mono">{freq.frequency} Hz</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{freq.description}</p>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default ClientVectorTrajectory3D;
