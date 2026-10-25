import { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { RotateCcw, Info, Play, Pause } from "lucide-react";

const CuspVisualization = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [paramA, setParamA] = useState(-2);
  const [paramB, setParamB] = useState(0);
  const [ballPosition, setBallPosition] = useState(0);
  const [isAnimating, setIsAnimating] = useState(true);
  const [showInfo, setShowInfo] = useState(false);
  const animationRef = useRef<number>();

  // Potential function V(x) = x⁴ + ax² + bx
  const potential = useCallback((x: number, a: number, b: number) => {
    return Math.pow(x, 4) + a * Math.pow(x, 2) + b * x;
  }, []);

  // Derivative dV/dx = 4x³ + 2ax + b (force = -dV/dx)
  const derivative = useCallback((x: number, a: number, b: number) => {
    return 4 * Math.pow(x, 3) + 2 * a * x + b;
  }, []);

  // Find equilibrium points (where derivative = 0)
  const findEquilibria = useCallback((a: number, b: number) => {
    const equilibria: number[] = [];
    // Numerical search for roots of 4x³ + 2ax + b = 0
    for (let x = -3; x <= 3; x += 0.01) {
      const d1 = derivative(x, a, b);
      const d2 = derivative(x + 0.01, a, b);
      if (d1 * d2 < 0) {
        // Sign change - root nearby
        equilibria.push(x + 0.005);
      }
    }
    return equilibria;
  }, [derivative]);

  // Ball physics simulation
  useEffect(() => {
    if (!isAnimating) return;

    let velocity = 0;
    const damping = 0.95;
    const dt = 0.016;

    const animate = () => {
      const force = -derivative(ballPosition, paramA, paramB);
      velocity += force * dt * 2;
      velocity *= damping;
      
      const newPosition = ballPosition + velocity * dt * 5;
      setBallPosition(Math.max(-3, Math.min(3, newPosition)));
      
      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [paramA, paramB, ballPosition, isAnimating, derivative]);

  // Draw the potential curve
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const scaleX = width / 6; // x range: -3 to 3
    const scaleY = height / 20; // V range scaling

    // Clear canvas
    ctx.fillStyle = "hsl(222, 47%, 6%)";
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    ctx.strokeStyle = "hsl(220, 20%, 15%)";
    ctx.lineWidth = 1;
    
    for (let i = -3; i <= 3; i++) {
      const x = centerX + i * scaleX;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Draw potential curve
    ctx.beginPath();
    ctx.strokeStyle = "hsl(192, 82%, 45%)";
    ctx.lineWidth = 3;
    ctx.shadowColor = "hsl(192, 82%, 45%)";
    ctx.shadowBlur = 10;

    let minV = Infinity;
    let maxV = -Infinity;
    
    // First pass: find min/max for scaling
    for (let px = 0; px < width; px++) {
      const x = (px - centerX) / scaleX;
      const v = potential(x, paramA, paramB);
      minV = Math.min(minV, v);
      maxV = Math.max(maxV, v);
    }

    const vRange = Math.max(maxV - minV, 10);
    const vCenter = (maxV + minV) / 2;

    // Second pass: draw curve
    for (let px = 0; px < width; px++) {
      const x = (px - centerX) / scaleX;
      const v = potential(x, paramA, paramB);
      const py = centerY - ((v - vCenter) / vRange) * height * 0.8;
      
      if (px === 0) {
        ctx.moveTo(px, py);
      } else {
        ctx.lineTo(px, py);
      }
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Draw equilibrium points
    const equilibria = findEquilibria(paramA, paramB);
    equilibria.forEach((eq, i) => {
      const px = centerX + eq * scaleX;
      const v = potential(eq, paramA, paramB);
      const py = centerY - ((v - vCenter) / vRange) * height * 0.8;
      
      // Check if stable (minimum) or unstable (maximum)
      const secondDeriv = 12 * Math.pow(eq, 2) + 2 * paramA;
      const isStable = secondDeriv > 0;

      ctx.beginPath();
      if (isStable) {
        ctx.fillStyle = "hsl(38, 92%, 50%)";
        ctx.shadowColor = "hsl(38, 92%, 50%)";
      } else {
        ctx.fillStyle = "hsl(350, 80%, 55%)";
        ctx.shadowColor = "hsl(350, 80%, 55%)";
      }
      ctx.shadowBlur = 15;
      ctx.arc(px, py, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      // Label
      ctx.fillStyle = "hsl(210, 40%, 98%)";
      ctx.font = "11px Inter";
      ctx.fillText(isStable ? "Stabil" : "Instabil", px - 18, py + 25);
    });

    // Draw ball
    const ballPx = centerX + ballPosition * scaleX;
    const ballV = potential(ballPosition, paramA, paramB);
    const ballPy = centerY - ((ballV - vCenter) / vRange) * height * 0.8;

    // Ball shadow/trail
    ctx.beginPath();
    const gradient = ctx.createRadialGradient(ballPx, ballPy, 0, ballPx, ballPy, 30);
    gradient.addColorStop(0, "hsla(270, 60%, 55%, 0.5)");
    gradient.addColorStop(1, "hsla(270, 60%, 55%, 0)");
    ctx.fillStyle = gradient;
    ctx.arc(ballPx, ballPy, 30, 0, Math.PI * 2);
    ctx.fill();

    // Ball
    ctx.beginPath();
    ctx.fillStyle = "hsl(270, 60%, 55%)";
    ctx.shadowColor = "hsl(270, 60%, 65%)";
    ctx.shadowBlur = 20;
    ctx.arc(ballPx, ballPy - 12, 12, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Labels
    ctx.fillStyle = "hsl(210, 40%, 80%)";
    ctx.font = "12px Inter";
    ctx.fillText("x", width - 20, centerY + 20);
    ctx.fillText("V(x)", 10, 20);

  }, [paramA, paramB, ballPosition, potential, findEquilibria]);

  const resetBall = () => {
    setBallPosition(2);
  };

  // Check if we're in the bifurcation region (cusp)
  const isInBifurcation = paramA < 0 && Math.abs(paramB) < Math.pow(-paramA, 1.5) * (2/3) * Math.sqrt(2);

  return (
    <section className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 bg-field-pattern opacity-30" />
      
      <div className="container mx-auto px-4 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <span className="text-accent text-sm font-medium uppercase tracking-wider mb-4 block">
            Interaktive Simulation
          </span>
          <h2 className="font-display text-3xl md:text-4xl font-bold text-foreground mb-4">
            <span className="text-gradient-primary">Kuspen-Katastrophe</span> Visualisierung
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Steuern Sie die Parameter a und b, um zu sehen, wie sich die Potenzialfläche 
            und die stabilen Gleichgewichte verändern.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Canvas */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="lg:col-span-2 bg-card border border-border rounded-2xl p-4 relative"
          >
            <canvas
              ref={canvasRef}
              width={800}
              height={400}
              className="w-full h-auto rounded-xl"
            />
            
            {/* Overlay controls */}
            <div className="absolute top-6 right-6 flex gap-2">
              <Button
                variant="field"
                size="icon"
                onClick={() => setIsAnimating(!isAnimating)}
              >
                {isAnimating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </Button>
              <Button
                variant="field"
                size="icon"
                onClick={resetBall}
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
              <Button
                variant="field"
                size="icon"
                onClick={() => setShowInfo(!showInfo)}
              >
                <Info className="w-4 h-4" />
              </Button>
            </div>

            {/* Info overlay */}
            {showInfo && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute top-16 right-6 w-72 bg-popover border border-border rounded-xl p-4 shadow-elevated"
              >
                <h4 className="font-display text-sm font-semibold text-foreground mb-2">
                  Legende
                </h4>
                <div className="space-y-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-primary" />
                    <span>Potenzialfunktion V(x)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-chreode" />
                    <span>Stabile Gleichgewichte (Attraktoren)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-katastrophe" />
                    <span>Instabile Gleichgewichte</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-accent" />
                    <span>Systemzustand (Ball)</span>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Status indicator */}
            <div className="absolute bottom-6 left-6">
              <div className={`
                inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium
                ${isInBifurcation 
                  ? "bg-chreode/20 text-chreode border border-chreode/30" 
                  : "bg-primary/20 text-primary border border-primary/30"
                }
              `}>
                <div className={`w-2 h-2 rounded-full ${isInBifurcation ? "bg-chreode animate-pulse" : "bg-primary"}`} />
                {isInBifurcation ? "Bifurkationszone (2 Attraktoren)" : "Monostabil (1 Attraktor)"}
              </div>
            </div>
          </motion.div>

          {/* Controls */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            {/* Formula */}
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="font-display text-lg font-semibold text-foreground mb-4">
                Potenzialfunktion
              </h3>
              <div className="bg-muted/50 border border-border rounded-lg p-4 font-mono text-center">
                <div className="text-foreground text-lg">
                  V(x) = x<sup>4</sup> + <span className="text-primary">{paramA.toFixed(1)}</span>x<sup>2</sup> + <span className="text-chreode">{paramB.toFixed(1)}</span>x
                </div>
              </div>
            </div>

            {/* Parameter A */}
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-display font-semibold text-foreground">
                  Parameter <span className="text-primary">a</span>
                </h4>
                <span className="text-sm font-mono text-primary bg-primary/10 px-2 py-1 rounded">
                  {paramA.toFixed(2)}
                </span>
              </div>
              <Slider
                value={[paramA]}
                onValueChange={(v) => setParamA(v[0])}
                min={-4}
                max={2}
                step={0.1}
                className="mb-3"
              />
              <p className="text-xs text-muted-foreground">
                Negativer Wert → Doppelmulde (Bistabilität)
              </p>
            </div>

            {/* Parameter B */}
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-display font-semibold text-foreground">
                  Parameter <span className="text-chreode">b</span>
                </h4>
                <span className="text-sm font-mono text-chreode bg-chreode/10 px-2 py-1 rounded">
                  {paramB.toFixed(2)}
                </span>
              </div>
              <Slider
                value={[paramB]}
                onValueChange={(v) => setParamB(v[0])}
                min={-4}
                max={4}
                step={0.1}
                className="mb-3"
              />
              <p className="text-xs text-muted-foreground">
                Asymmetrie → Kippt das System zu einem Attraktor
              </p>
            </div>

            {/* Presets */}
            <div className="bg-card border border-border rounded-xl p-6">
              <h4 className="font-display font-semibold text-foreground mb-4">
                Beispielszenarien
              </h4>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="field"
                  size="sm"
                  onClick={() => { setParamA(-2); setParamB(0); resetBall(); }}
                >
                  Bistabil
                </Button>
                <Button
                  variant="field"
                  size="sm"
                  onClick={() => { setParamA(1); setParamB(0); resetBall(); }}
                >
                  Monostabil
                </Button>
                <Button
                  variant="glow"
                  size="sm"
                  onClick={() => { setParamA(-2); setParamB(1.5); resetBall(); }}
                >
                  Katastrophe →
                </Button>
                <Button
                  variant="glow"
                  size="sm"
                  onClick={() => { setParamA(-2); setParamB(-1.5); resetBall(); }}
                >
                  ← Katastrophe
                </Button>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Explanation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          viewport={{ once: true }}
          className="mt-12 grid md:grid-cols-3 gap-6"
        >
          <div className="bg-card border border-primary/20 rounded-xl p-6">
            <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-4">
              <span className="font-mono font-bold">a</span>
            </div>
            <h4 className="font-display font-semibold text-foreground mb-2">
              Spaltparameter
            </h4>
            <p className="text-sm text-muted-foreground">
              Bei a &lt; 0 spaltet sich die Potenzialfläche in zwei Minima (Attraktoren). 
              Dies entspricht der Entstehung von Bistabilität im System.
            </p>
          </div>

          <div className="bg-card border border-chreode/20 rounded-xl p-6">
            <div className="w-10 h-10 rounded-lg bg-chreode/10 text-chreode flex items-center justify-center mb-4">
              <span className="font-mono font-bold">b</span>
            </div>
            <h4 className="font-display font-semibold text-foreground mb-2">
              Normalfaktor
            </h4>
            <p className="text-sm text-muted-foreground">
              Der Parameter b kippt die Symmetrie und bestimmt, welcher Attraktor 
              bevorzugt wird. Bei kritischen Werten erfolgt der Katastrophen-Sprung.
            </p>
          </div>

          <div className="bg-card border border-accent/20 rounded-xl p-6">
            <div className="w-10 h-10 rounded-lg bg-accent/10 text-accent flex items-center justify-center mb-4">
              <span className="font-mono font-bold">⚡</span>
            </div>
            <h4 className="font-display font-semibold text-foreground mb-2">
              Katastrophen-Sprung
            </h4>
            <p className="text-sm text-muted-foreground">
              Wenn b die kritische Grenze überschreitet, verschwindet ein Attraktor 
              und das System springt abrupt zum verbleibenden – die eigentliche Katastrophe.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CuspVisualization;
