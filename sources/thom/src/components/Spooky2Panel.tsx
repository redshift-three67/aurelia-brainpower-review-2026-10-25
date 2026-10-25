/**
 * Spooky2 Generator Panel
 * UI-Komponente zur Steuerung von Spooky2 XM und Generator X Pro
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Radio, Plug, PlugZap, Play, Square, Upload, Zap, Settings2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { useSpooky2 } from '@/hooks/useSpooky2';
import type { Spooky2Waveform } from '@/services/hardware/Spooky2Service';
import type { TreatmentPoint } from '@/hooks/useTreatmentSequence';

interface Spooky2PanelProps {
  treatmentPoints?: TreatmentPoint[];
  currentFrequency?: number;
  isSequenceRunning?: boolean;
}

const WAVEFORM_OPTIONS: { value: Spooky2Waveform; label: string }[] = [
  { value: 'sine', label: 'Sinus' },
  { value: 'square', label: 'Rechteck' },
  { value: 'sawtooth', label: 'Sägezahn' },
  { value: 'inverse_sawtooth', label: 'Inv. Sägezahn' },
  { value: 'damped', label: 'Gedämpft' },
];

const Spooky2Panel = ({ treatmentPoints, currentFrequency, isSequenceRunning }: Spooky2PanelProps) => {
  const {
    device,
    status,
    isConnecting,
    isConnected,
    connect,
    disconnect,
    setFrequency,
    setAmplitude,
    setWaveform,
    start,
    stop,
    uploadSequence,
  } = useSpooky2();

  const [selectedWaveform, setSelectedWaveform] = useState<Spooky2Waveform>('sine');
  const [amplitude, setAmplitudeState] = useState(5);
  const [channel, setChannel] = useState(1);
  const [isExpanded, setIsExpanded] = useState(false);
  const [syncWithAudio, setSyncWithAudio] = useState(true);

  const handleConnect = async () => {
    if (isConnected) {
      await disconnect();
    } else {
      await connect();
    }
  };

  const handleUploadSequence = async () => {
    if (!treatmentPoints || treatmentPoints.length === 0) return;
    const frequencies = treatmentPoints.map(p => ({
      frequency: p.frequency,
      duration: p.duration,
      amplitude,
      waveform: selectedWaveform,
    }));
    await uploadSequence(frequencies, channel);
  };

  const handleStartGenerator = async () => {
    if (currentFrequency) {
      await setFrequency(currentFrequency, channel);
    }
    await setAmplitude(amplitude, channel);
    await setWaveform(selectedWaveform, channel);
    await start(channel);
  };

  // Auto-sync frequency with audio when sequence is running
  if (syncWithAudio && isConnected && currentFrequency && isSequenceRunning) {
    setFrequency(currentFrequency, channel);
  }

  return (
    <Card className="border-border bg-card">
      <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
        <CollapsibleTrigger asChild>
          <CardHeader className="pb-2 cursor-pointer hover:bg-muted/30 transition-colors">
            <CardTitle className="text-base flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Radio className="w-5 h-5 text-primary" />
                Spooky2 Generator
                {isConnected && (
                  <Badge variant="default" className="text-[10px]">
                    {device?.name?.replace('Spooky2 ', '') || 'Verbunden'}
                  </Badge>
                )}
              </div>
              <Badge variant={isConnected ? 'default' : 'outline'} className="text-[10px]">
                {isConnected ? '● Verbunden' : '○ Getrennt'}
              </Badge>
            </CardTitle>
          </CardHeader>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="space-y-4">
            {/* Verbindung */}
            <Button
              variant={isConnected ? 'destructive' : 'default'}
              className="w-full gap-2"
              onClick={handleConnect}
              disabled={isConnecting}
            >
              {isConnecting ? (
                <div className="animate-spin w-4 h-4 border-2 border-current border-t-transparent rounded-full" />
              ) : isConnected ? (
                <PlugZap className="w-4 h-4" />
              ) : (
                <Plug className="w-4 h-4" />
              )}
              {isConnecting ? 'Verbinde...' : isConnected ? 'Trennen' : 'Generator verbinden'}
            </Button>

            {isConnected && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="space-y-4"
              >
                {/* Device Info */}
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Modell</span>
                    <p className="font-medium text-foreground">{device?.name}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Max. Freq.</span>
                    <p className="font-mono text-foreground">
                      {((device?.maxFrequency || 0) / 1_000_000).toFixed(0)} MHz
                    </p>
                  </div>
                </div>

                {/* Status */}
                {status && (
                  <div className="p-2 rounded-lg bg-muted/30 border border-border text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground">Status</span>
                      <Badge variant={status.running ? 'default' : 'secondary'}>
                        {status.running ? 'Aktiv' : 'Bereit'}
                      </Badge>
                    </div>
                    {status.running && (
                      <p className="font-mono text-primary mt-1">
                        {status.frequency.toFixed(2)} Hz @ {status.amplitude.toFixed(1)}V
                      </p>
                    )}
                  </div>
                )}

                {/* Wellenform */}
                <div className="space-y-2">
                  <Label className="text-sm">Wellenform</Label>
                  <Select value={selectedWaveform} onValueChange={(v) => setSelectedWaveform(v as Spooky2Waveform)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {WAVEFORM_OPTIONS.map(opt => (
                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Amplitude */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-sm">Amplitude</Label>
                    <span className="text-sm font-mono text-muted-foreground">{amplitude.toFixed(1)}V</span>
                  </div>
                  <Slider
                    value={[amplitude]}
                    onValueChange={(v) => setAmplitudeState(v[0])}
                    min={0.1}
                    max={device?.maxAmplitude || 20}
                    step={0.1}
                  />
                </div>

                {/* Kanal */}
                <div className="flex items-center gap-4">
                  <Label className="text-sm">Kanal</Label>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant={channel === 1 ? 'default' : 'outline'}
                      onClick={() => setChannel(1)}
                    >
                      CH1
                    </Button>
                    {(device?.channels || 1) > 1 && (
                      <Button
                        size="sm"
                        variant={channel === 2 ? 'default' : 'outline'}
                        onClick={() => setChannel(2)}
                      >
                        CH2
                      </Button>
                    )}
                  </div>
                </div>

                {/* Sync mit Audio */}
                <div className="flex items-center justify-between">
                  <Label className="text-sm">Sync mit Audio-Sequenz</Label>
                  <Switch checked={syncWithAudio} onCheckedChange={setSyncWithAudio} />
                </div>

                {/* Steuerung */}
                <div className="flex gap-2">
                  <Button onClick={handleStartGenerator} className="flex-1 gap-2">
                    <Play className="w-4 h-4" />
                    Start
                  </Button>
                  <Button onClick={() => stop(channel)} variant="destructive" className="flex-1 gap-2">
                    <Square className="w-4 h-4" />
                    Stop
                  </Button>
                </div>

                {/* Sequenz hochladen */}
                {treatmentPoints && treatmentPoints.length > 0 && (
                  <Button
                    variant="secondary"
                    className="w-full gap-2"
                    onClick={handleUploadSequence}
                  >
                    <Upload className="w-4 h-4" />
                    {treatmentPoints.length} Frequenzen hochladen
                  </Button>
                )}
              </motion.div>
            )}

            {!isConnected && (
              <p className="text-xs text-muted-foreground text-center">
                Verbinden Sie einen Spooky2 XM oder Generator X Pro über USB.
                WebSerial erfordert Chrome oder Edge.
              </p>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};

export default Spooky2Panel;
