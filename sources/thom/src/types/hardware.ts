// Hardware-Typen für das NLS-Feldengine-System

export interface ServerHardware {
  cpu: CPUInfo;
  gpu: GPUInfo;
  memory: MemoryInfo;
  storage: StorageInfo;
  network: NetworkInfo;
}

export interface CPUInfo {
  name: string;
  cores: number;
  threads: number;
  baseFrequency: number;
  turboFrequency: number;
  usage: number;
  temperature?: number;
}

export interface GPUInfo {
  name: string;
  vram: number;
  cudaCores?: number;
  tensorCores?: number;
  usage: number;
  temperature?: number;
  driver?: string;
}

export interface MemoryInfo {
  total: number;
  used: number;
  available: number;
  type: string;
  speed?: number;
  jitter?: number; // Für Präzisionsmessungen
}

export interface StorageInfo {
  devices: StorageDevice[];
  totalCapacity: number;
  usedCapacity: number;
}

export interface StorageDevice {
  name: string;
  type: 'nvme' | 'ssd' | 'hdd';
  capacity: number;
  used: number;
  readSpeed?: number;
  writeSpeed?: number;
}

export interface NetworkInfo {
  interfaces: NetworkInterface[];
  latency?: number;
  bandwidth?: number;
}

export interface NetworkInterface {
  name: string;
  speed: number;
  ipAddress?: string;
  isConnected: boolean;
}

// Externe Hardware-Geräte
export interface ExternalDevice {
  id: string;
  type: DeviceType;
  name: string;
  manufacturer?: string;
  vendorId?: number;
  productId?: number;
  status: DeviceStatus;
  capabilities: DeviceCapability[];
  lastSeen: Date;
}

export type DeviceType = 
  | 'usb-dac'
  | 'frequency-generator'
  | 'microcontroller'
  | 'biosensor'
  | 'unknown';

export type DeviceStatus = 
  | 'connected'
  | 'disconnected'
  | 'initializing'
  | 'error'
  | 'ready';

export interface DeviceCapability {
  name: string;
  type: 'audio' | 'serial' | 'gpio' | 'sensor';
  parameters?: Record<string, unknown>;
}

// Bekannte Geräte-Profile
export interface DeviceProfile {
  vendorId: number;
  productId: number;
  name: string;
  type: DeviceType;
  capabilities: DeviceCapability[];
  driver?: string;
}

// WebUSB/WebSerial Konfiguration
export interface USBDeviceFilter {
  vendorId?: number;
  productId?: number;
  classCode?: number;
  subclassCode?: number;
  protocolCode?: number;
}

export interface SerialPortFilter {
  usbVendorId?: number;
  usbProductId?: number;
}

// Hardware-Events
export interface HardwareEvent {
  type: 'connect' | 'disconnect' | 'error' | 'data';
  device: ExternalDevice;
  timestamp: Date;
  data?: unknown;
}

// System-Metriken
export interface SystemMetrics {
  timestamp: Date;
  cpu: {
    usage: number;
    frequency: number;
    temperature?: number;
  };
  gpu: {
    usage: number;
    vramUsed: number;
    temperature?: number;
  };
  memory: {
    used: number;
    available: number;
    jitter?: number;
  };
  latency: {
    websocket?: number;
    hardware?: number;
  };
}

// Frequenz-Output Konfiguration
export interface FrequencyOutput {
  type: 'audio' | 'electromagnetic' | 'dual';
  frequency: number;
  amplitude: number;
  waveform: 'sine' | 'square' | 'triangle' | 'sawtooth';
  duration?: number;
  modulation?: ModulationConfig;
}

export interface ModulationConfig {
  type: 'am' | 'fm' | 'pwm';
  frequency: number;
  depth: number;
}

// Klienten-Vektor für NLS
export interface ClientVector {
  id: string;
  timestamp: Date;
  dimensions: number[];
  metadata: ClientMetadata;
  trajectory?: VectorTrajectory;
}

export interface ClientMetadata {
  sessionId: string;
  therapistId?: string;
  clientId: string;
  inputMethod: 'manual' | 'sensor' | 'hybrid';
  sensorData?: SensorReading[];
}

export interface SensorReading {
  type: 'hrv' | 'gsr' | 'eeg' | 'custom';
  value: number;
  unit: string;
  timestamp: Date;
  quality: number; // 0-1
}

export interface VectorTrajectory {
  points: TrajectoryPoint[];
  attractorDistance: number;
  phase: 'approach' | 'transition' | 'stable';
}

export interface TrajectoryPoint {
  position: number[];
  timestamp: Date;
  velocity?: number[];
}
