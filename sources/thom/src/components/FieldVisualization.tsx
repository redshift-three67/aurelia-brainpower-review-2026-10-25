import { useEffect, useRef } from "react";

const FieldVisualization = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth * 2;
      canvas.height = canvas.offsetHeight * 2;
      ctx.scale(2, 2);
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    let animationId: number;
    let time = 0;

    // Attractor points
    const attractors = [
      { x: 0.3, y: 0.4, strength: 1, color: "192, 82%, 45%" },
      { x: 0.7, y: 0.6, strength: 0.8, color: "38, 92%, 50%" },
      { x: 0.5, y: 0.3, strength: 0.6, color: "270, 60%, 55%" },
    ];

    // Particles for field visualization
    const particles: { x: number; y: number; vx: number; vy: number; life: number }[] = [];
    const maxParticles = 150;

    const createParticle = () => {
      return {
        x: Math.random() * canvas.offsetWidth,
        y: Math.random() * canvas.offsetHeight,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        life: Math.random() * 100 + 50,
      };
    };

    // Initialize particles
    for (let i = 0; i < maxParticles; i++) {
      particles.push(createParticle());
    }

    const animate = () => {
      time += 0.01;
      const width = canvas.offsetWidth;
      const height = canvas.offsetHeight;

      // Clear with fade effect
      ctx.fillStyle = "hsla(222, 47%, 4%, 0.1)";
      ctx.fillRect(0, 0, width, height);

      // Draw field lines
      ctx.strokeStyle = "hsla(192, 82%, 45%, 0.05)";
      ctx.lineWidth = 1;
      
      for (let i = 0; i < 20; i++) {
        ctx.beginPath();
        const y = (i / 20) * height + Math.sin(time + i * 0.3) * 10;
        ctx.moveTo(0, y);
        
        for (let x = 0; x < width; x += 10) {
          const waveY = y + Math.sin((x / 50) + time + i * 0.2) * 15;
          ctx.lineTo(x, waveY);
        }
        ctx.stroke();
      }

      // Update and draw particles
      particles.forEach((particle, index) => {
        // Apply attractor forces
        attractors.forEach((attractor) => {
          const ax = attractor.x * width;
          const ay = attractor.y * height;
          const dx = ax - particle.x;
          const dy = ay - particle.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist > 5) {
            const force = (attractor.strength * 0.5) / dist;
            particle.vx += (dx / dist) * force;
            particle.vy += (dy / dist) * force;
          }
        });

        // Add some turbulence
        particle.vx += (Math.random() - 0.5) * 0.1;
        particle.vy += (Math.random() - 0.5) * 0.1;

        // Damping
        particle.vx *= 0.98;
        particle.vy *= 0.98;

        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life -= 0.5;

        // Reset particle if dead or out of bounds
        if (particle.life <= 0 || particle.x < 0 || particle.x > width || particle.y < 0 || particle.y > height) {
          particles[index] = createParticle();
        }

        // Draw particle
        const alpha = Math.min(particle.life / 100, 0.6);
        ctx.beginPath();
        ctx.fillStyle = `hsla(192, 82%, 55%, ${alpha})`;
        ctx.arc(particle.x, particle.y, 2, 0, Math.PI * 2);
        ctx.fill();
      });

      // Draw attractors with pulsing effect
      attractors.forEach((attractor, i) => {
        const x = attractor.x * width;
        const y = attractor.y * height;
        const pulse = 1 + Math.sin(time * 2 + i) * 0.2;

        // Outer glow
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 60 * pulse);
        gradient.addColorStop(0, `hsla(${attractor.color}, 0.3)`);
        gradient.addColorStop(0.5, `hsla(${attractor.color}, 0.1)`);
        gradient.addColorStop(1, `hsla(${attractor.color}, 0)`);

        ctx.beginPath();
        ctx.fillStyle = gradient;
        ctx.arc(x, y, 60 * pulse, 0, Math.PI * 2);
        ctx.fill();

        // Core
        ctx.beginPath();
        ctx.fillStyle = `hsla(${attractor.color}, 0.8)`;
        ctx.arc(x, y, 6 * pulse, 0, Math.PI * 2);
        ctx.fill();
      });

      // Draw chreode paths (curved lines connecting attractors)
      ctx.strokeStyle = "hsla(38, 92%, 50%, 0.2)";
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 10]);
      
      for (let i = 0; i < attractors.length; i++) {
        for (let j = i + 1; j < attractors.length; j++) {
          const a1 = attractors[i];
          const a2 = attractors[j];
          
          ctx.beginPath();
          ctx.moveTo(a1.x * width, a1.y * height);
          
          const cpx = ((a1.x + a2.x) / 2) * width + Math.sin(time) * 30;
          const cpy = ((a1.y + a2.y) / 2) * height + Math.cos(time) * 20;
          
          ctx.quadraticCurveTo(cpx, cpy, a2.x * width, a2.y * height);
          ctx.stroke();
        }
      }
      ctx.setLineDash([]);

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full opacity-60"
      style={{ background: "transparent" }}
    />
  );
};

export default FieldVisualization;
