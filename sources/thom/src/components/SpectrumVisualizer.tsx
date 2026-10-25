/**
 * Echtzeit-FFT-Spektrum-Visualisierung
 * Zeigt Frequenzspektrum und Wellenform via AnalyserNode
 */
import { useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface SpectrumVisualizerProps {
  analyser: AnalyserNode | null;
  isPlaying: boolean;
  mode?: 'spectrum' | 'waveform' | 'both';
  height?: number;
  className?: string;
  primaryColor?: string;
  secondaryColor?: string;
}

export function SpectrumVisualizer({
  analyser,
  isPlaying,
  mode = 'both',
  height = 120,
  className,
  primaryColor,
  secondaryColor,
}: SpectrumVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animFrameRef = useRef<number>(0);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !analyser) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    const showSpectrum = mode === 'spectrum' || mode === 'both';
    const showWaveform = mode === 'waveform' || mode === 'both';

    // Get CSS custom property values for theming
    const computedStyle = getComputedStyle(canvas);
    const pColor = primaryColor || computedStyle.getPropertyValue('--primary').trim();
    const sColor = secondaryColor || computedStyle.getPropertyValue('--accent').trim();

    const hslPrimary = pColor.includes(',') ? `hsl(${pColor})` : 'hsl(168, 60%, 42%)';
    const hslSecondary = sColor.includes(',') ? `hsl(${sColor})` : 'hsl(142, 40%, 55%)';

    // --- Spectrum (bars) ---
    if (showSpectrum) {
      const bufLen = analyser.frequencyBinCount;
      const freqData = new Uint8Array(bufLen);
      analyser.getByteFrequencyData(freqData);

      // Only show first ~40% of bins (most musical content)
      const usableBins = Math.floor(bufLen * 0.4);
      const barW = w / usableBins;
      const spectrumH = showWaveform ? h * 0.55 : h;

      for (let i = 0; i < usableBins; i++) {
        const val = freqData[i] / 255;
        const barH = val * spectrumH;

        // Gradient from primary to secondary based on frequency
        const ratio = i / usableBins;
        const alpha = 0.4 + val * 0.6;

        ctx.fillStyle = ratio < 0.5
          ? hslPrimary.replace(')', ` / ${alpha})`)
          : hslSecondary.replace(')', ` / ${alpha})`);

        ctx.fillRect(i * barW, spectrumH - barH, barW - 0.5, barH);
      }

      // Subtle baseline
      ctx.strokeStyle = hslPrimary.replace(')', ' / 0.15)');
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(0, spectrumH);
      ctx.lineTo(w, spectrumH);
      ctx.stroke();
    }

    // --- Waveform (oscilloscope) ---
    if (showWaveform) {
      const bufLen = analyser.frequencyBinCount;
      const timeData = new Uint8Array(bufLen);
      analyser.getByteTimeDomainData(timeData);

      const waveY = showSpectrum ? h * 0.6 : 0;
      const waveH = showSpectrum ? h * 0.4 : h;
      const centerY = waveY + waveH / 2;

      ctx.strokeStyle = hslSecondary.replace(')', ' / 0.8)');
      ctx.lineWidth = 1.5;
      ctx.beginPath();

      const sliceW = w / bufLen;
      for (let i = 0; i < bufLen; i++) {
        const v = timeData[i] / 128.0 - 1;
        const y = centerY + v * (waveH / 2) * 0.85;
        if (i === 0) ctx.moveTo(0, y);
        else ctx.lineTo(i * sliceW, y);
      }
      ctx.stroke();

      // Center line
      ctx.strokeStyle = hslSecondary.replace(')', ' / 0.1)');
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(0, centerY);
      ctx.lineTo(w, centerY);
      ctx.stroke();
    }

    animFrameRef.current = requestAnimationFrame(draw);
  }, [analyser, mode, primaryColor, secondaryColor]);

  useEffect(() => {
    // Size canvas to container
    const canvas = canvasRef.current;
    if (canvas) {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = height * window.devicePixelRatio;
      const ctx = canvas.getContext('2d');
      if (ctx) ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      canvas.width = rect.width;
      canvas.height = height;
    }
  }, [height]);

  useEffect(() => {
    if (isPlaying && analyser) {
      animFrameRef.current = requestAnimationFrame(draw);
    }
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isPlaying, analyser, draw]);

  // Draw idle state
  useEffect(() => {
    if (!isPlaying) {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Flat line
      const centerY = canvas.height / 2;
      ctx.strokeStyle = 'hsl(168, 60%, 42% / 0.2)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(0, centerY);
      ctx.lineTo(canvas.width, centerY);
      ctx.stroke();
      ctx.setLineDash([]);
    }
  }, [isPlaying]);

  return (
    <canvas
      ref={canvasRef}
      style={{ height }}
      className={cn('w-full rounded-md bg-muted/20', className)}
    />
  );
}

export default SpectrumVisualizer;
