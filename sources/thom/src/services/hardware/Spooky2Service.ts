/**
 * Spooky2 Hardware Integration Service
 * WebSerial-Protokoll für Spooky2 XM Generator und Generator X Pro
 * 
 * Kommunikation über USB-Serial (CH340/FT232) mit ASCII-Befehlen
 * Baud: 115200, 8N1
 */

export type Spooky2Model = 'xm' | 'gx_pro';

export interface Spooky2DeviceInfo {
  model: Spooky2Model;
  name: string;
  port: SerialPort;
  firmwareVersion: string | null;
  connected: boolean;
  maxFrequency: number;
  maxAmplitude: number;
  channels: number;
  supportsWobble: boolean;
}

export interface Spooky2Command {
  type: 'set_frequency' | 'set_amplitude' | 'set_waveform' | 'start' | 'stop' | 'status' | 'set_channel';
  frequency?: number;
  amplitude?: number;
  waveform?: Spooky2Waveform;
  channel?: number;
}

export type Spooky2Waveform = 'sine' | 'square' | 'sawtooth' | 'inverse_sawtooth' | 'h_bomb' | 'damped';

export interface Spooky2Status {
  running: boolean;
  frequency: number;
  amplitude: number;
  waveform: string;
  channel: number;
  temperature?: number;
}

// USB Vendor/Product IDs für bekannte Spooky2-Chips
const KNOWN_FILTERS: SerialPortFilter[] = [
  { usbVendorId: 0x1A86, usbProductId: 0x7523 }, // CH340 (Spooky2 XM)
  { usbVendorId: 0x0403, usbProductId: 0x6001 }, // FT232R (Generator X)
  { usbVendorId: 0x0403, usbProductId: 0x6015 }, // FT231X (Generator X Pro)
  { usbVendorId: 0x10C4, usbProductId: 0xEA60 }, // CP2102 (alternative)
];

const DEVICE_CONFIGS: Record<Spooky2Model, {
  name: string;
  maxFrequency: number;
  maxAmplitude: number;
  channels: number;
  supportsWobble: boolean;
  baudRate: number;
}> = {
  xm: {
    name: 'Spooky2 XM Generator',
    maxFrequency: 5_000_000, // 5 MHz
    maxAmplitude: 20, // 20V p-p
    channels: 2,
    supportsWobble: true,
    baudRate: 115200,
  },
  gx_pro: {
    name: 'Spooky2 Generator X Pro',
    maxFrequency: 40_000_000, // 40 MHz
    maxAmplitude: 40, // 40V p-p
    channels: 2,
    supportsWobble: true,
    baudRate: 115200,
  },
};

class Spooky2Service {
  private port: SerialPort | null = null;
  private reader: ReadableStreamDefaultReader<Uint8Array> | null = null;
  private writer: WritableStreamDefaultWriter<Uint8Array> | null = null;
  private model: Spooky2Model = 'xm';
  private connected = false;
  private responseBuffer = '';
  private responseCallbacks: Map<string, (response: string) => void> = new Map();

  get isConnected(): boolean {
    return this.connected;
  }

  get deviceInfo(): Spooky2DeviceInfo | null {
    if (!this.port || !this.connected) return null;
    const config = DEVICE_CONFIGS[this.model];
    return {
      model: this.model,
      name: config.name,
      port: this.port,
      firmwareVersion: null,
      connected: true,
      maxFrequency: config.maxFrequency,
      maxAmplitude: config.maxAmplitude,
      channels: config.channels,
      supportsWobble: config.supportsWobble,
    };
  }

  /**
   * Verbindung zu Spooky2 Generator herstellen
   */
  async connect(preferredModel?: Spooky2Model): Promise<Spooky2DeviceInfo> {
    if (!('serial' in navigator)) {
      throw new Error('WebSerial API wird nicht unterstützt. Bitte Chrome/Edge verwenden.');
    }

    try {
      // Request port with known USB filters
      this.port = await navigator.serial.requestPort({ filters: KNOWN_FILTERS });
      
      // Detect model from port info
      const portInfo = this.port.getInfo();
      if (portInfo.usbVendorId === 0x0403) {
        this.model = 'gx_pro';
      } else {
        this.model = preferredModel || 'xm';
      }

      const config = DEVICE_CONFIGS[this.model];
      
      await this.port.open({
        baudRate: config.baudRate,
        dataBits: 8,
        stopBits: 1,
        parity: 'none',
        flowControl: 'none',
      });

      this.connected = true;

      // Start reading responses
      this.startReading();

      // Query firmware version
      const fwVersion = await this.sendCommand('VER?');

      const deviceInfo: Spooky2DeviceInfo = {
        model: this.model,
        name: config.name,
        port: this.port,
        firmwareVersion: fwVersion || null,
        connected: true,
        maxFrequency: config.maxFrequency,
        maxAmplitude: config.maxAmplitude,
        channels: config.channels,
        supportsWobble: config.supportsWobble,
      };

      return deviceInfo;
    } catch (error) {
      this.connected = false;
      throw error;
    }
  }

  /**
   * Verbindung trennen
   */
  async disconnect(): Promise<void> {
    try {
      if (this.reader) {
        await this.reader.cancel();
        this.reader = null;
      }
      if (this.writer) {
        await this.writer.close();
        this.writer = null;
      }
      if (this.port) {
        await this.port.close();
        this.port = null;
      }
    } catch {
      // Ignore close errors
    }
    this.connected = false;
  }

  /**
   * Frequenz setzen (Hz)
   */
  async setFrequency(frequency: number, channel = 1): Promise<void> {
    const config = DEVICE_CONFIGS[this.model];
    const clampedFreq = Math.min(Math.max(0.01, frequency), config.maxFrequency);
    await this.sendCommand(`C${channel}:F=${clampedFreq.toFixed(6)}`);
  }

  /**
   * Amplitude setzen (Volt peak-to-peak)
   */
  async setAmplitude(amplitude: number, channel = 1): Promise<void> {
    const config = DEVICE_CONFIGS[this.model];
    const clampedAmp = Math.min(Math.max(0, amplitude), config.maxAmplitude);
    await this.sendCommand(`C${channel}:A=${clampedAmp.toFixed(2)}`);
  }

  /**
   * Wellenform setzen
   */
  async setWaveform(waveform: Spooky2Waveform, channel = 1): Promise<void> {
    const wfMap: Record<Spooky2Waveform, string> = {
      sine: 'SINE',
      square: 'SQUARE',
      sawtooth: 'SAW',
      inverse_sawtooth: 'ISAW',
      h_bomb: 'HBOMB',
      damped: 'DAMPED',
    };
    await this.sendCommand(`C${channel}:W=${wfMap[waveform] || 'SINE'}`);
  }

  /**
   * Generator starten
   */
  async start(channel = 1): Promise<void> {
    await this.sendCommand(`C${channel}:START`);
  }

  /**
   * Generator stoppen
   */
  async stop(channel = 1): Promise<void> {
    await this.sendCommand(`C${channel}:STOP`);
  }

  /**
   * Komplette Frequenzsequenz hochladen
   */
  async uploadSequence(
    frequencies: Array<{ frequency: number; duration: number; amplitude?: number; waveform?: Spooky2Waveform }>,
    channel = 1,
  ): Promise<void> {
    // Stop current output
    await this.stop(channel);
    
    // Upload each frequency as a program step
    for (let i = 0; i < frequencies.length; i++) {
      const step = frequencies[i];
      const cmd = [
        `P${i}:F=${step.frequency.toFixed(6)}`,
        `P${i}:D=${step.duration}`,
      ];
      if (step.amplitude !== undefined) cmd.push(`P${i}:A=${step.amplitude.toFixed(2)}`);
      if (step.waveform) {
        const wfMap: Record<string, string> = { sine: 'SINE', square: 'SQUARE', sawtooth: 'SAW' };
        cmd.push(`P${i}:W=${wfMap[step.waveform] || 'SINE'}`);
      }
      
      for (const c of cmd) {
        await this.sendCommand(`C${channel}:${c}`);
      }
    }
    
    // Set total program length
    await this.sendCommand(`C${channel}:PLEN=${frequencies.length}`);
  }

  /**
   * Status abfragen
   */
  async getStatus(): Promise<Spooky2Status | null> {
    if (!this.connected) return null;
    const response = await this.sendCommand('STATUS?');
    if (!response) return null;

    // Parse status response (format varies by firmware)
    try {
      const parts = response.split(',');
      return {
        running: parts[0] === '1',
        frequency: parseFloat(parts[1]) || 0,
        amplitude: parseFloat(parts[2]) || 0,
        waveform: parts[3] || 'sine',
        channel: parseInt(parts[4]) || 1,
        temperature: parts[5] ? parseFloat(parts[5]) : undefined,
      };
    } catch {
      return null;
    }
  }

  // ---- Private Methods ----

  private async sendCommand(cmd: string): Promise<string | null> {
    if (!this.port || !this.connected) {
      throw new Error('Nicht verbunden');
    }

    const encoder = new TextEncoder();
    
    if (!this.writer) {
      const writable = this.port.writable;
      if (!writable) throw new Error('Port nicht beschreibbar');
      this.writer = writable.getWriter();
    }

    const fullCmd = `${cmd}\r\n`;
    await this.writer.write(encoder.encode(fullCmd));

    // Wait for response with timeout
    return new Promise<string | null>((resolve) => {
      const timeout = setTimeout(() => {
        this.responseCallbacks.delete(cmd);
        resolve(null);
      }, 2000);

      this.responseCallbacks.set(cmd, (response) => {
        clearTimeout(timeout);
        resolve(response);
      });
    });
  }

  private async startReading(): Promise<void> {
    if (!this.port?.readable) return;

    const decoder = new TextDecoder();
    this.reader = this.port.readable.getReader();

    const readLoop = async () => {
      try {
        while (this.connected && this.reader) {
          const { value, done } = await this.reader.read();
          if (done) break;
          if (value) {
            this.responseBuffer += decoder.decode(value, { stream: true });
            this.processBuffer();
          }
        }
      } catch {
        // Port closed or disconnected
        this.connected = false;
      }
    };

    readLoop(); // Fire and forget
  }

  private processBuffer(): void {
    const lines = this.responseBuffer.split('\n');
    this.responseBuffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      // Resolve any waiting callback
      for (const [cmd, callback] of this.responseCallbacks) {
        callback(trimmed);
        this.responseCallbacks.delete(cmd);
        break; // Only resolve the first waiting callback
      }
    }
  }
}

// Singleton instance
export const spooky2Service = new Spooky2Service();
export default Spooky2Service;
