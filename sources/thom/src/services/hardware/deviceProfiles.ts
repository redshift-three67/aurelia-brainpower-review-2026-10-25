// Bekannte Geräte-Profile für Auto-Detection
import type { DeviceProfile, DeviceType } from '@/types/hardware';

// USB Vendor IDs bekannter Hersteller
export const KNOWN_VENDORS = {
  FOCUSRITE: 0x1235,
  BEHRINGER: 0x1397,
  STEINBERG: 0x0763,
  NATIVE_INSTRUMENTS: 0x17cc,
  PRESONUS: 0x0194,
  MOTU: 0x07fd,
  RME: 0x0424,
  ESPRESSIF: 0x303a, // ESP32
  ARDUINO: 0x2341,
  RASPBERRY_PI: 0x2e8a,
  FTDI: 0x0403,
  SILICON_LABS: 0x10c4,
  // Spooky2 und ähnliche Frequenzgeneratoren
  SPOOKY2: 0x04d8,
  RIFE: 0x04d8,
} as const;

// Bekannte Geräte-Profile
export const DEVICE_PROFILES: DeviceProfile[] = [
  // USB Audio DACs
  {
    vendorId: KNOWN_VENDORS.FOCUSRITE,
    productId: 0x8212,
    name: 'Focusrite Scarlett 2i2',
    type: 'usb-dac',
    capabilities: [
      { name: 'Audio Output', type: 'audio', parameters: { channels: 2, sampleRate: 192000, bitDepth: 24 } },
      { name: 'Audio Input', type: 'audio', parameters: { channels: 2, sampleRate: 192000, bitDepth: 24 } },
    ],
  },
  {
    vendorId: KNOWN_VENDORS.BEHRINGER,
    productId: 0x0002,
    name: 'Behringer UMC202HD',
    type: 'usb-dac',
    capabilities: [
      { name: 'Audio Output', type: 'audio', parameters: { channels: 2, sampleRate: 96000, bitDepth: 24 } },
    ],
  },
  {
    vendorId: KNOWN_VENDORS.STEINBERG,
    productId: 0x2020,
    name: 'Steinberg UR22',
    type: 'usb-dac',
    capabilities: [
      { name: 'Audio Output', type: 'audio', parameters: { channels: 2, sampleRate: 192000, bitDepth: 24 } },
    ],
  },
  
  // Frequenzgeneratoren
  {
    vendorId: KNOWN_VENDORS.SPOOKY2,
    productId: 0xea60,
    name: 'Spooky2 XM Generator',
    type: 'frequency-generator',
    capabilities: [
      { name: 'Frequency Output', type: 'serial', parameters: { maxFreq: 25000000, channels: 2 } },
      { name: 'Modulation', type: 'serial', parameters: { types: ['am', 'fm', 'pwm'] } },
    ],
  },
  {
    vendorId: KNOWN_VENDORS.SPOOKY2,
    productId: 0x00dd,
    name: 'Spooky2 GeneratorX',
    type: 'frequency-generator',
    capabilities: [
      { name: 'Frequency Output', type: 'serial', parameters: { maxFreq: 40000000, channels: 2 } },
      { name: 'Biofeedback', type: 'sensor', parameters: { types: ['angle', 'current'] } },
    ],
  },
  
  // Mikrocontroller
  {
    vendorId: KNOWN_VENDORS.ESPRESSIF,
    productId: 0x1001,
    name: 'ESP32-S3',
    type: 'microcontroller',
    capabilities: [
      { name: 'GPIO Control', type: 'gpio', parameters: { pins: 45, pwmChannels: 16 } },
      { name: 'Serial Communication', type: 'serial', parameters: { baudRate: 115200 } },
      { name: 'WiFi', type: 'serial', parameters: { protocols: ['websocket', 'mqtt'] } },
    ],
  },
  {
    vendorId: KNOWN_VENDORS.ARDUINO,
    productId: 0x0043,
    name: 'Arduino Uno',
    type: 'microcontroller',
    capabilities: [
      { name: 'GPIO Control', type: 'gpio', parameters: { pins: 14, pwmChannels: 6 } },
      { name: 'Serial Communication', type: 'serial', parameters: { baudRate: 115200 } },
    ],
  },
  {
    vendorId: KNOWN_VENDORS.ARDUINO,
    productId: 0x8037,
    name: 'Arduino Leonardo',
    type: 'microcontroller',
    capabilities: [
      { name: 'GPIO Control', type: 'gpio', parameters: { pins: 20, pwmChannels: 7 } },
      { name: 'Serial Communication', type: 'serial', parameters: { baudRate: 115200 } },
    ],
  },
  {
    vendorId: KNOWN_VENDORS.RASPBERRY_PI,
    productId: 0x000a,
    name: 'Raspberry Pi Pico',
    type: 'microcontroller',
    capabilities: [
      { name: 'GPIO Control', type: 'gpio', parameters: { pins: 26, pwmChannels: 16 } },
      { name: 'Serial Communication', type: 'serial', parameters: { baudRate: 115200 } },
      { name: 'I2C', type: 'serial', parameters: { busses: 2 } },
    ],
  },
  
  // FTDI/Serial Adapter (für Biosensoren etc.)
  {
    vendorId: KNOWN_VENDORS.FTDI,
    productId: 0x6001,
    name: 'FTDI Serial Adapter',
    type: 'biosensor',
    capabilities: [
      { name: 'Serial Communication', type: 'serial', parameters: { baudRate: 921600 } },
    ],
  },
  {
    vendorId: KNOWN_VENDORS.SILICON_LABS,
    productId: 0xea60,
    name: 'CP2102 Serial Adapter',
    type: 'biosensor',
    capabilities: [
      { name: 'Serial Communication', type: 'serial', parameters: { baudRate: 921600 } },
    ],
  },
];

// Funktion zum Identifizieren eines Geräts
export function identifyDevice(vendorId: number, productId: number): DeviceProfile | null {
  return DEVICE_PROFILES.find(
    (profile) => profile.vendorId === vendorId && profile.productId === productId
  ) || null;
}

// Funktion zum Erkennen des Gerätetyps anhand der Vendor ID
export function guessDeviceType(vendorId: number): DeviceType {
  switch (vendorId) {
    case KNOWN_VENDORS.FOCUSRITE:
    case KNOWN_VENDORS.BEHRINGER:
    case KNOWN_VENDORS.STEINBERG:
    case KNOWN_VENDORS.NATIVE_INSTRUMENTS:
    case KNOWN_VENDORS.PRESONUS:
    case KNOWN_VENDORS.MOTU:
    case KNOWN_VENDORS.RME:
      return 'usb-dac';
    
    case KNOWN_VENDORS.SPOOKY2:
    case KNOWN_VENDORS.RIFE:
      return 'frequency-generator';
    
    case KNOWN_VENDORS.ESPRESSIF:
    case KNOWN_VENDORS.ARDUINO:
    case KNOWN_VENDORS.RASPBERRY_PI:
      return 'microcontroller';
    
    case KNOWN_VENDORS.FTDI:
    case KNOWN_VENDORS.SILICON_LABS:
      return 'biosensor';
    
    default:
      return 'unknown';
  }
}

// Audio DAC Filter für WebUSB
export const USB_DAC_FILTERS = [
  { vendorId: KNOWN_VENDORS.FOCUSRITE },
  { vendorId: KNOWN_VENDORS.BEHRINGER },
  { vendorId: KNOWN_VENDORS.STEINBERG },
  { vendorId: KNOWN_VENDORS.NATIVE_INSTRUMENTS },
  { vendorId: KNOWN_VENDORS.PRESONUS },
  { vendorId: KNOWN_VENDORS.MOTU },
  { vendorId: KNOWN_VENDORS.RME },
];

// Frequenzgenerator Filter
export const FREQUENCY_GENERATOR_FILTERS = [
  { vendorId: KNOWN_VENDORS.SPOOKY2 },
  { vendorId: KNOWN_VENDORS.RIFE },
];

// Mikrocontroller Filter für WebSerial
export const MICROCONTROLLER_FILTERS = [
  { usbVendorId: KNOWN_VENDORS.ESPRESSIF },
  { usbVendorId: KNOWN_VENDORS.ARDUINO },
  { usbVendorId: KNOWN_VENDORS.RASPBERRY_PI },
  { usbVendorId: KNOWN_VENDORS.FTDI },
  { usbVendorId: KNOWN_VENDORS.SILICON_LABS },
];
