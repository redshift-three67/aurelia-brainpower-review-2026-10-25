// System Monitor Service für Server-Hardware Metriken
import type { ServerHardware, SystemMetrics } from '@/types/hardware';

// Umgebungsmodus
export type EnvironmentMode = 'development' | 'production';

// Development Hardware: ASUS Vivobook S 16 (Ryzen 9 8945HS)
const DEVELOPMENT_CONFIG: ServerHardware = {
  cpu: {
    name: 'AMD Ryzen 9 8945HS',
    cores: 8,
    threads: 16,
    baseFrequency: 4000,
    turboFrequency: 5200,
    usage: 0,
    temperature: undefined,
  },
  gpu: {
    name: 'AMD Radeon 780M',
    vram: 370, // Shared Memory
    cudaCores: undefined,
    tensorCores: undefined,
    usage: 0,
    temperature: undefined,
    driver: 'RDNA3 iGPU',
  },
  memory: {
    total: 16384, // 16 GB in MB
    used: 0,
    available: 16384,
    type: 'DDR5',
    speed: 7500,
    jitter: undefined,
  },
  storage: {
    devices: [
      { name: 'Micron SSD', type: 'nvme', capacity: 954000, used: 680000 },
    ],
    totalCapacity: 954000,
    usedCapacity: 680000,
  },
  network: {
    interfaces: [
      { name: 'WiFi 6E', speed: 1000, isConnected: true },
    ],
    latency: undefined,
    bandwidth: 1000,
  },
};

// Production Hardware: GPU Server M G1 (Ryzen 5 9600X + RTX 4000)
const PRODUCTION_CONFIG: ServerHardware = {
  cpu: {
    name: 'AMD Ryzen 5 9600X',
    cores: 6,
    threads: 12,
    baseFrequency: 3900,
    turboFrequency: 5400,
    usage: 0,
    temperature: undefined,
  },
  gpu: {
    name: 'NVIDIA RTX 4000 SFF Ada',
    vram: 20480, // 20 GB in MB
    cudaCores: 6144,
    tensorCores: 192,
    usage: 0,
    temperature: undefined,
    driver: 'CUDA 12.x',
  },
  memory: {
    total: 131072, // 128 GB in MB
    used: 0,
    available: 131072,
    type: 'DDR5',
    speed: 5600,
    jitter: undefined,
  },
  storage: {
    devices: [
      { name: 'NVMe SSD 1', type: 'nvme', capacity: 1024000, used: 0 },
      { name: 'NVMe SSD 2', type: 'nvme', capacity: 1024000, used: 0 },
    ],
    totalCapacity: 2048000,
    usedCapacity: 0,
  },
  network: {
    interfaces: [
      { name: 'eth0', speed: 1000, isConnected: true },
      { name: 'eth1', speed: 1000, isConnected: true },
    ],
    latency: undefined,
    bandwidth: 2000,
  },
};

type MetricsCallback = (metrics: SystemMetrics) => void;

class SystemMonitorService {
  private listeners: Set<MetricsCallback> = new Set();
  private currentMetrics: SystemMetrics | null = null;
  private updateInterval: ReturnType<typeof setInterval> | null = null;
  private isRunning = false;
  private mode: EnvironmentMode = 'development';

  // Umgebungsmodus setzen
  setMode(mode: EnvironmentMode): void {
    this.mode = mode;
    console.log('[SystemMonitor] Mode set to:', mode);
  }

  getMode(): EnvironmentMode {
    return this.mode;
  }

  // Aktive Konfiguration basierend auf Modus
  private getActiveConfig(): ServerHardware {
    return this.mode === 'production' ? PRODUCTION_CONFIG : DEVELOPMENT_CONFIG;
  }

  // Server-Konfiguration abrufen
  getServerConfig(): ServerHardware {
    return { ...this.getActiveConfig() };
  }
  getCurrentMetrics(): SystemMetrics | null {
    return this.currentMetrics;
  }

  // Listener registrieren
  addMetricsListener(callback: MetricsCallback): void {
    this.listeners.add(callback);
  }

  removeMetricsListener(callback: MetricsCallback): void {
    this.listeners.delete(callback);
  }

  private emitMetrics(metrics: SystemMetrics): void {
    this.listeners.forEach((callback) => callback(metrics));
  }

  // Monitoring starten
  start(intervalMs: number = 1000): void {
    if (this.isRunning) {
      return;
    }

    this.isRunning = true;
    console.log('[SystemMonitor] Starting with interval:', intervalMs, 'ms');

    // Initiale Messung
    this.collectMetrics();

    // Regelmäßige Updates
    this.updateInterval = setInterval(() => {
      this.collectMetrics();
    }, intervalMs);
  }

  // Monitoring stoppen
  stop(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
    this.isRunning = false;
    console.log('[SystemMonitor] Stopped');
  }

  // Metriken sammeln
  private async collectMetrics(): Promise<void> {
    const timestamp = new Date();

    // Browser Performance API für verfügbare Metriken
    const performanceMemory = (performance as Performance & { memory?: { usedJSHeapSize: number; jsHeapSizeLimit: number } }).memory;
    
    // Simulierte Metriken mit realistischen Schwankungen
    // In der Produktion würden diese vom Server über WebSocket kommen
    const metrics: SystemMetrics = {
      timestamp,
      cpu: {
        usage: this.simulateUsage(15, 45),
        frequency: this.simulateFrequency(3900, 5400),
        temperature: this.simulateTemperature(35, 65),
      },
      gpu: {
        usage: this.simulateUsage(5, 30),
        vramUsed: this.simulateVRAMUsage(2000, 8000),
        temperature: this.simulateTemperature(30, 55),
      },
      memory: {
        used: performanceMemory 
          ? Math.round(performanceMemory.usedJSHeapSize / 1024 / 1024)
          : this.simulateMemoryUsage(16000, 32000),
        available: this.getActiveConfig().memory.total - (performanceMemory 
          ? Math.round(performanceMemory.usedJSHeapSize / 1024 / 1024)
          : this.simulateMemoryUsage(16000, 32000)),
        jitter: this.simulateJitter(0.1, 2.0),
      },
      latency: {
        websocket: this.simulateLatency(1, 5),
        hardware: this.simulateLatency(0.1, 1),
      },
    };

    this.currentMetrics = metrics;
    this.emitMetrics(metrics);
  }

  // WebSocket-Latenz messen (echte Messung)
  async measureWebSocketLatency(wsUrl: string): Promise<number> {
    return new Promise((resolve) => {
      const start = performance.now();
      
      try {
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          const latency = performance.now() - start;
          ws.close();
          resolve(latency);
        };
        
        ws.onerror = () => {
          resolve(-1);
        };
        
        // Timeout nach 5 Sekunden
        setTimeout(() => {
          ws.close();
          resolve(-1);
        }, 5000);
      } catch {
        resolve(-1);
      }
    });
  }

  // Netzwerk-Latenz messen
  async measureNetworkLatency(endpoint: string): Promise<number> {
    const start = performance.now();
    
    try {
      await fetch(endpoint, { method: 'HEAD', mode: 'no-cors' });
      return performance.now() - start;
    } catch {
      return -1;
    }
  }

  // Simulationsfunktionen für Demo-Modus
  private simulateUsage(min: number, max: number): number {
    const base = (min + max) / 2;
    const variation = (max - min) / 4;
    return Math.round(base + (Math.random() - 0.5) * variation * 2);
  }

  private simulateFrequency(base: number, turbo: number): number {
    const load = Math.random();
    return Math.round(base + (turbo - base) * load);
  }

  private simulateTemperature(idle: number, load: number): number {
    const usage = Math.random() * 0.5 + 0.2;
    return Math.round(idle + (load - idle) * usage);
  }

  private simulateVRAMUsage(min: number, max: number): number {
    return Math.round(min + Math.random() * (max - min));
  }

  private simulateMemoryUsage(min: number, max: number): number {
    return Math.round(min + Math.random() * (max - min));
  }

  private simulateLatency(min: number, max: number): number {
    return Math.round((min + Math.random() * (max - min)) * 100) / 100;
  }

  private simulateJitter(min: number, max: number): number {
    return Math.round((min + Math.random() * (max - min)) * 100) / 100;
  }

  // Service beenden
  destroy(): void {
    this.stop();
    this.listeners.clear();
  }
}

// Singleton-Instanz
export const systemMonitor = new SystemMonitorService();
