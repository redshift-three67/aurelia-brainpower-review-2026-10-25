/**
 * Spooky2 Hardware Hook
 * React-Integration für die Spooky2 XM und Generator X Pro Steuerung
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { toast } from 'sonner';
import { spooky2Service, type Spooky2DeviceInfo, type Spooky2Waveform, type Spooky2Status } from '@/services/hardware/Spooky2Service';

const getErrorMessage = (error: unknown, fallback: string): string =>
  error instanceof Error && error.message ? error.message : fallback;

export function useSpooky2() {
  const [device, setDevice] = useState<Spooky2DeviceInfo | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [status, setStatus] = useState<Spooky2Status | null>(null);
  const statusIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const connect = useCallback(async () => {
    setIsConnecting(true);
    try {
      const info = await spooky2Service.connect();
      setDevice(info);
      toast.success(`${info.name} verbunden`, {
        description: info.firmwareVersion ? `Firmware: ${info.firmwareVersion}` : 'Bereit',
      });
      return info;
    } catch (error: unknown) {
      const message = getErrorMessage(error, 'Verbindung fehlgeschlagen');
      toast.error('Spooky2 Verbindungsfehler', { description: message });
      return null;
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const disconnect = useCallback(async () => {
    await spooky2Service.disconnect();
    setDevice(null);
    setStatus(null);
    toast.info('Spooky2 Generator getrennt');
  }, []);

  const setFrequency = useCallback(async (frequency: number, channel = 1) => {
    await spooky2Service.setFrequency(frequency, channel);
  }, []);

  const setAmplitude = useCallback(async (amplitude: number, channel = 1) => {
    await spooky2Service.setAmplitude(amplitude, channel);
  }, []);

  const setWaveform = useCallback(async (waveform: Spooky2Waveform, channel = 1) => {
    await spooky2Service.setWaveform(waveform, channel);
  }, []);

  const start = useCallback(async (channel = 1) => {
    await spooky2Service.start(channel);
    toast.success('Generator gestartet');
  }, []);

  const stop = useCallback(async (channel = 1) => {
    await spooky2Service.stop(channel);
    toast.info('Generator gestoppt');
  }, []);

  const uploadSequence = useCallback(async (
    frequencies: Array<{ frequency: number; duration: number; amplitude?: number; waveform?: Spooky2Waveform }>,
    channel = 1,
  ) => {
    try {
      await spooky2Service.uploadSequence(frequencies, channel);
      toast.success(`${frequencies.length} Frequenzen hochgeladen`);
    } catch (error: unknown) {
      toast.error('Upload fehlgeschlagen', { description: getErrorMessage(error, 'Upload fehlgeschlagen') });
    }
  }, []);

  // Status polling when connected
  useEffect(() => {
    if (device?.connected) {
      statusIntervalRef.current = setInterval(async () => {
        const s = await spooky2Service.getStatus();
        if (s) setStatus(s);
      }, 3000);
    }
    return () => {
      if (statusIntervalRef.current) clearInterval(statusIntervalRef.current);
    };
  }, [device?.connected]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (spooky2Service.isConnected) {
        spooky2Service.disconnect();
      }
    };
  }, []);

  return {
    device,
    status,
    isConnecting,
    isConnected: device?.connected || false,
    connect,
    disconnect,
    setFrequency,
    setAmplitude,
    setWaveform,
    start,
    stop,
    uploadSequence,
  };
}
