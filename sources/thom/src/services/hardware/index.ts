// Barrel Export für Hardware Services
export { hardwareDiscovery } from './HardwareDiscoveryService';
export { systemMonitor } from './SystemMonitorService';
export { 
  KNOWN_VENDORS, 
  DEVICE_PROFILES, 
  identifyDevice, 
  guessDeviceType,
  USB_DAC_FILTERS,
  FREQUENCY_GENERATOR_FILTERS,
  MICROCONTROLLER_FILTERS 
} from './deviceProfiles';
