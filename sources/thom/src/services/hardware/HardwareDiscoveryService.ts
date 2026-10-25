// Hardware Discovery Service für WebUSB und WebSerial
import type { 
  ExternalDevice, 
  HardwareEvent,
  DeviceType 
} from '@/types/hardware';
import { 
  identifyDevice, 
  guessDeviceType,
  USB_DAC_FILTERS,
  FREQUENCY_GENERATOR_FILTERS,
  MICROCONTROLLER_FILTERS 
} from './deviceProfiles';

type EventCallback = (event: HardwareEvent) => void;

class HardwareDiscoveryService {
  private devices: Map<string, ExternalDevice> = new Map();
  private eventListeners: Set<EventCallback> = new Set();
  private usbDevices: Map<string, USBDevice> = new Map();
  private serialPorts: Map<string, SerialPort> = new Map();
  private isScanning = false;
  private scanInterval: ReturnType<typeof setInterval> | null = null;

  // WebUSB Unterstützung prüfen
  get isWebUSBSupported(): boolean {
    return 'usb' in navigator;
  }

  // WebSerial Unterstützung prüfen
  get isWebSerialSupported(): boolean {
    return 'serial' in navigator;
  }

  // Event-Listener registrieren
  addEventListener(callback: EventCallback): void {
    this.eventListeners.add(callback);
  }

  removeEventListener(callback: EventCallback): void {
    this.eventListeners.delete(callback);
  }

  private emitEvent(event: HardwareEvent): void {
    this.eventListeners.forEach((callback) => callback(event));
  }

  // Alle verbundenen Geräte abrufen
  getDevices(): ExternalDevice[] {
    return Array.from(this.devices.values());
  }

  getDevicesByType(type: DeviceType): ExternalDevice[] {
    return this.getDevices().filter((device) => device.type === type);
  }

  // Initialisierung des Discovery-Service
  async initialize(): Promise<void> {
    console.log('[HardwareDiscovery] Initializing...');
    
    if (this.isWebUSBSupported) {
      await this.initializeWebUSB();
    } else {
      console.warn('[HardwareDiscovery] WebUSB not supported');
    }

    if (this.isWebSerialSupported) {
      await this.initializeWebSerial();
    } else {
      console.warn('[HardwareDiscovery] WebSerial not supported');
    }

    // Starte automatisches Scanning
    this.startAutoScan();
    
    console.log('[HardwareDiscovery] Initialized with', this.devices.size, 'devices');
  }

  // WebUSB initialisieren
  private async initializeWebUSB(): Promise<void> {
    try {
      // Bereits autorisierte Geräte abrufen
      const devices = await navigator.usb.getDevices();
      
      for (const device of devices) {
        await this.registerUSBDevice(device);
      }

      // Event-Listener für USB-Ereignisse
      navigator.usb.addEventListener('connect', (event) => {
        this.registerUSBDevice(event.device);
      });

      navigator.usb.addEventListener('disconnect', (event) => {
        this.unregisterUSBDevice(event.device);
      });
      
      console.log('[HardwareDiscovery] WebUSB initialized with', devices.length, 'devices');
    } catch (error) {
      console.error('[HardwareDiscovery] WebUSB initialization error:', error);
    }
  }

  // WebSerial initialisieren
  private async initializeWebSerial(): Promise<void> {
    try {
      // Bereits autorisierte Ports abrufen
      const ports = await navigator.serial.getPorts();
      
      for (const port of ports) {
        await this.registerSerialPort(port);
      }

      // Event-Listener für Serial-Ereignisse
      navigator.serial.addEventListener('connect', (event) => {
        const serialEvent = event as { port?: { getInfo: () => { usbVendorId?: number; usbProductId?: number } } };
        if (serialEvent.port) {
          this.registerSerialPort(serialEvent.port as unknown as SerialPort);
        }
      });

      navigator.serial.addEventListener('disconnect', (event) => {
        const serialEvent = event as { port?: { getInfo: () => { usbVendorId?: number; usbProductId?: number } } };
        if (serialEvent.port) {
          this.unregisterSerialPort(serialEvent.port as unknown as SerialPort);
        }
      });
      
      console.log('[HardwareDiscovery] WebSerial initialized with', ports.length, 'ports');
    } catch (error) {
      console.error('[HardwareDiscovery] WebSerial initialization error:', error);
    }
  }

  // USB-Gerät registrieren
  private async registerUSBDevice(usbDevice: USBDevice): Promise<void> {
    const id = this.getUSBDeviceId(usbDevice);
    
    if (this.devices.has(id)) {
      return;
    }

    const profile = identifyDevice(usbDevice.vendorId, usbDevice.productId);
    
    const device: ExternalDevice = {
      id,
      type: profile?.type || guessDeviceType(usbDevice.vendorId),
      name: profile?.name || usbDevice.productName || `USB Device ${usbDevice.vendorId.toString(16)}:${usbDevice.productId.toString(16)}`,
      manufacturer: usbDevice.manufacturerName || undefined,
      vendorId: usbDevice.vendorId,
      productId: usbDevice.productId,
      status: 'connected',
      capabilities: profile?.capabilities || [],
      lastSeen: new Date(),
    };

    this.devices.set(id, device);
    this.usbDevices.set(id, usbDevice);

    this.emitEvent({
      type: 'connect',
      device,
      timestamp: new Date(),
    });

    console.log('[HardwareDiscovery] USB device registered:', device.name);
  }

  // USB-Gerät entfernen
  private unregisterUSBDevice(usbDevice: USBDevice): void {
    const id = this.getUSBDeviceId(usbDevice);
    const device = this.devices.get(id);

    if (device) {
      device.status = 'disconnected';
      
      this.emitEvent({
        type: 'disconnect',
        device,
        timestamp: new Date(),
      });

      this.devices.delete(id);
      this.usbDevices.delete(id);

      console.log('[HardwareDiscovery] USB device unregistered:', device.name);
    }
  }

  // Serial-Port registrieren
  private async registerSerialPort(port: SerialPort): Promise<void> {
    const info = port.getInfo();
    const id = this.getSerialPortId(info);
    
    if (this.devices.has(id)) {
      return;
    }

    const profile = info.usbVendorId && info.usbProductId 
      ? identifyDevice(info.usbVendorId, info.usbProductId)
      : null;

    const device: ExternalDevice = {
      id,
      type: profile?.type || (info.usbVendorId ? guessDeviceType(info.usbVendorId) : 'unknown'),
      name: profile?.name || `Serial Device ${info.usbVendorId?.toString(16) || 'unknown'}`,
      vendorId: info.usbVendorId,
      productId: info.usbProductId,
      status: 'connected',
      capabilities: profile?.capabilities || [
        { name: 'Serial Communication', type: 'serial', parameters: { baudRate: 115200 } }
      ],
      lastSeen: new Date(),
    };

    this.devices.set(id, device);
    this.serialPorts.set(id, port);

    this.emitEvent({
      type: 'connect',
      device,
      timestamp: new Date(),
    });

    console.log('[HardwareDiscovery] Serial port registered:', device.name);
  }

  // Serial-Port entfernen
  private unregisterSerialPort(port: SerialPort): void {
    const info = port.getInfo();
    const id = this.getSerialPortId(info);
    const device = this.devices.get(id);

    if (device) {
      device.status = 'disconnected';
      
      this.emitEvent({
        type: 'disconnect',
        device,
        timestamp: new Date(),
      });

      this.devices.delete(id);
      this.serialPorts.delete(id);

      console.log('[HardwareDiscovery] Serial port unregistered:', device.name);
    }
  }

  // USB Audio DAC anfordern
  async requestUSBDAC(): Promise<ExternalDevice | null> {
    if (!this.isWebUSBSupported) {
      console.error('[HardwareDiscovery] WebUSB not supported');
      return null;
    }

    try {
      const device = await navigator.usb.requestDevice({
        filters: USB_DAC_FILTERS,
      });
      
      await this.registerUSBDevice(device);
      return this.devices.get(this.getUSBDeviceId(device)) || null;
    } catch (error) {
      if ((error as Error).name !== 'NotFoundError') {
        console.error('[HardwareDiscovery] Error requesting USB DAC:', error);
      }
      return null;
    }
  }

  // Frequenzgenerator anfordern
  async requestFrequencyGenerator(): Promise<ExternalDevice | null> {
    if (!this.isWebSerialSupported) {
      console.error('[HardwareDiscovery] WebSerial not supported');
      return null;
    }

    try {
      const port = await navigator.serial.requestPort({
        filters: FREQUENCY_GENERATOR_FILTERS.map(f => ({ usbVendorId: f.vendorId })),
      });
      
      await this.registerSerialPort(port);
      const info = port.getInfo();
      return this.devices.get(this.getSerialPortId(info)) || null;
    } catch (error) {
      if ((error as Error).name !== 'NotFoundError') {
        console.error('[HardwareDiscovery] Error requesting frequency generator:', error);
      }
      return null;
    }
  }

  // Mikrocontroller anfordern
  async requestMicrocontroller(): Promise<ExternalDevice | null> {
    if (!this.isWebSerialSupported) {
      console.error('[HardwareDiscovery] WebSerial not supported');
      return null;
    }

    try {
      const port = await navigator.serial.requestPort({
        filters: MICROCONTROLLER_FILTERS,
      });
      
      await this.registerSerialPort(port);
      const info = port.getInfo();
      return this.devices.get(this.getSerialPortId(info)) || null;
    } catch (error) {
      if ((error as Error).name !== 'NotFoundError') {
        console.error('[HardwareDiscovery] Error requesting microcontroller:', error);
      }
      return null;
    }
  }

  // Beliebiges USB-Gerät anfordern
  async requestAnyUSBDevice(): Promise<ExternalDevice | null> {
    if (!this.isWebUSBSupported) {
      console.error('[HardwareDiscovery] WebUSB not supported');
      return null;
    }

    try {
      const device = await navigator.usb.requestDevice({
        filters: [],
      });
      
      await this.registerUSBDevice(device);
      return this.devices.get(this.getUSBDeviceId(device)) || null;
    } catch (error) {
      if ((error as Error).name !== 'NotFoundError') {
        console.error('[HardwareDiscovery] Error requesting USB device:', error);
      }
      return null;
    }
  }

  // Beliebigen Serial-Port anfordern
  async requestAnySerialPort(): Promise<ExternalDevice | null> {
    if (!this.isWebSerialSupported) {
      console.error('[HardwareDiscovery] WebSerial not supported');
      return null;
    }

    try {
      const port = await navigator.serial.requestPort({
        filters: [],
      });
      
      await this.registerSerialPort(port);
      const info = port.getInfo();
      return this.devices.get(this.getSerialPortId(info)) || null;
    } catch (error) {
      if ((error as Error).name !== 'NotFoundError') {
        console.error('[HardwareDiscovery] Error requesting serial port:', error);
      }
      return null;
    }
  }

  // USB-Gerät öffnen
  async openUSBDevice(deviceId: string): Promise<USBDevice | null> {
    const usbDevice = this.usbDevices.get(deviceId);
    
    if (!usbDevice) {
      console.error('[HardwareDiscovery] USB device not found:', deviceId);
      return null;
    }

    try {
      await usbDevice.open();
      
      const device = this.devices.get(deviceId);
      if (device) {
        device.status = 'ready';
      }
      
      return usbDevice;
    } catch (error) {
      console.error('[HardwareDiscovery] Error opening USB device:', error);
      
      const device = this.devices.get(deviceId);
      if (device) {
        device.status = 'error';
        this.emitEvent({
          type: 'error',
          device,
          timestamp: new Date(),
          data: error,
        });
      }
      
      return null;
    }
  }

  // Serial-Port öffnen
  async openSerialPort(deviceId: string, options?: SerialOptions): Promise<SerialPort | null> {
    const port = this.serialPorts.get(deviceId);
    
    if (!port) {
      console.error('[HardwareDiscovery] Serial port not found:', deviceId);
      return null;
    }

    try {
      await port.open(options || { baudRate: 115200 });
      
      const device = this.devices.get(deviceId);
      if (device) {
        device.status = 'ready';
      }
      
      return port;
    } catch (error) {
      console.error('[HardwareDiscovery] Error opening serial port:', error);
      
      const device = this.devices.get(deviceId);
      if (device) {
        device.status = 'error';
        this.emitEvent({
          type: 'error',
          device,
          timestamp: new Date(),
          data: error,
        });
      }
      
      return null;
    }
  }

  // Automatisches Scanning starten
  private startAutoScan(): void {
    if (this.scanInterval) {
      return;
    }

    this.scanInterval = setInterval(() => {
      this.updateDeviceStatus();
    }, 5000);
  }

  // Automatisches Scanning stoppen
  stopAutoScan(): void {
    if (this.scanInterval) {
      clearInterval(this.scanInterval);
      this.scanInterval = null;
    }
  }

  // Geräte-Status aktualisieren
  private updateDeviceStatus(): void {
    const now = new Date();
    
    this.devices.forEach((device) => {
      if (device.status === 'connected' || device.status === 'ready') {
        device.lastSeen = now;
      }
    });
  }

  // Helper: USB-Geräte-ID generieren
  private getUSBDeviceId(device: USBDevice): string {
    return `usb-${device.vendorId.toString(16)}-${device.productId.toString(16)}-${device.serialNumber || 'unknown'}`;
  }

  // Helper: Serial-Port-ID generieren
  private getSerialPortId(info: SerialPortInfo): string {
    return `serial-${info.usbVendorId?.toString(16) || 'unknown'}-${info.usbProductId?.toString(16) || 'unknown'}`;
  }

  // Service beenden
  destroy(): void {
    this.stopAutoScan();
    this.devices.clear();
    this.usbDevices.clear();
    this.serialPorts.clear();
    this.eventListeners.clear();
  }
}

// Singleton-Instanz
export const hardwareDiscovery = new HardwareDiscoveryService();

// Interface für SerialConnectionEvent (TypeScript)
interface SerialConnectionEvent extends Event {
  target: SerialPort | null;
}
