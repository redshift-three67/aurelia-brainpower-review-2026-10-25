// React Hook für Hardware-Discovery
import { useState, useEffect, useCallback } from 'react';
import type { ExternalDevice, HardwareEvent, DeviceType } from '@/types/hardware';
import { hardwareDiscovery } from '@/services/hardware/HardwareDiscoveryService';

interface UseHardwareDiscoveryReturn {
  devices: ExternalDevice[];
  isInitialized: boolean;
  isWebUSBSupported: boolean;
  isWebSerialSupported: boolean;
  getDevicesByType: (type: DeviceType) => ExternalDevice[];
  requestUSBDAC: () => Promise<ExternalDevice | null>;
  requestFrequencyGenerator: () => Promise<ExternalDevice | null>;
  requestMicrocontroller: () => Promise<ExternalDevice | null>;
  requestAnyUSBDevice: () => Promise<ExternalDevice | null>;
  requestAnySerialPort: () => Promise<ExternalDevice | null>;
  lastEvent: HardwareEvent | null;
}

export function useHardwareDiscovery(): UseHardwareDiscoveryReturn {
  const [devices, setDevices] = useState<ExternalDevice[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [lastEvent, setLastEvent] = useState<HardwareEvent | null>(null);

  // Event-Handler
  const handleHardwareEvent = useCallback((event: HardwareEvent) => {
    setLastEvent(event);
    setDevices(hardwareDiscovery.getDevices());
    
    console.log('[useHardwareDiscovery] Event:', event.type, event.device.name);
  }, []);

  // Initialisierung
  useEffect(() => {
    const init = async () => {
      hardwareDiscovery.addEventListener(handleHardwareEvent);
      await hardwareDiscovery.initialize();
      setDevices(hardwareDiscovery.getDevices());
      setIsInitialized(true);
    };

    init();

    return () => {
      hardwareDiscovery.removeEventListener(handleHardwareEvent);
    };
  }, [handleHardwareEvent]);

  // Geräte nach Typ filtern
  const getDevicesByType = useCallback((type: DeviceType): ExternalDevice[] => {
    return devices.filter((device) => device.type === type);
  }, [devices]);

  // USB DAC anfordern
  const requestUSBDAC = useCallback(async (): Promise<ExternalDevice | null> => {
    const device = await hardwareDiscovery.requestUSBDAC();
    if (device) {
      setDevices(hardwareDiscovery.getDevices());
    }
    return device;
  }, []);

  // Frequenzgenerator anfordern
  const requestFrequencyGenerator = useCallback(async (): Promise<ExternalDevice | null> => {
    const device = await hardwareDiscovery.requestFrequencyGenerator();
    if (device) {
      setDevices(hardwareDiscovery.getDevices());
    }
    return device;
  }, []);

  // Mikrocontroller anfordern
  const requestMicrocontroller = useCallback(async (): Promise<ExternalDevice | null> => {
    const device = await hardwareDiscovery.requestMicrocontroller();
    if (device) {
      setDevices(hardwareDiscovery.getDevices());
    }
    return device;
  }, []);

  // Beliebiges USB-Gerät anfordern
  const requestAnyUSBDevice = useCallback(async (): Promise<ExternalDevice | null> => {
    const device = await hardwareDiscovery.requestAnyUSBDevice();
    if (device) {
      setDevices(hardwareDiscovery.getDevices());
    }
    return device;
  }, []);

  // Beliebigen Serial-Port anfordern
  const requestAnySerialPort = useCallback(async (): Promise<ExternalDevice | null> => {
    const device = await hardwareDiscovery.requestAnySerialPort();
    if (device) {
      setDevices(hardwareDiscovery.getDevices());
    }
    return device;
  }, []);

  return {
    devices,
    isInitialized,
    isWebUSBSupported: hardwareDiscovery.isWebUSBSupported,
    isWebSerialSupported: hardwareDiscovery.isWebSerialSupported,
    getDevicesByType,
    requestUSBDAC,
    requestFrequencyGenerator,
    requestMicrocontroller,
    requestAnyUSBDevice,
    requestAnySerialPort,
    lastEvent,
  };
}
