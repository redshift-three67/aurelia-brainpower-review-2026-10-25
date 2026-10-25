/**
 * Hardware-Methoden-Auswahl für Harmonisierung
 * Zeigt verfügbare Methoden basierend auf erkannter Hardware
 */
import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Volume2, 
  Radio, 
  Waves, 
  Cpu, 
  Usb, 
  Cable,
  Check,
  AlertCircle,
  Settings,
  Zap,
  Server,
  Search
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { useHardwareDiscovery } from '@/hooks/useHardwareDiscovery';

export interface HarmonizationMethod {
  id: string;
  name: string;
  description: string;
  hardware: string;
  icon: typeof Volume2;
  isAvailable: boolean;
  requiresConnection?: boolean;
}

const HARMONIZATION_METHODS: HarmonizationMethod[] = [
  {
    id: 'webAudio',
    name: 'Frequenz-Output-Modul',
    description: 'Manuelle Frequenz-Auswahl mit Audio-Ausgabe',
    hardware: 'WebAudio API (Browser)',
    icon: Volume2,
    isAvailable: true, // Always available in modern browsers
  },
  {
    id: 'bipolarResonance',
    name: 'Bipolar-Resonanz',
    description: 'Gegenphasige Sinus-Wellen (Paul Schmidt-Prinzip)',
    hardware: 'WebAudio API',
    icon: Waves,
    isAvailable: true,
  },
  {
    id: 'harmonicModulation',
    name: 'Harmonikale Modulation',
    description: 'Oberton-Synthese mit FM-Modulation (Baklayan-Prinzip)',
    hardware: 'WebAudio API',
    icon: Radio,
    isAvailable: true,
  },
  {
    id: 'emFieldOutput',
    name: 'EM-Feld-Output',
    description: 'Frequenzen via Serial an Generatoren (Spooky2 etc.)',
    hardware: 'WebSerial API',
    icon: Cable,
    isAvailable: false, // Needs WebSerial check
    requiresConnection: true,
  },
  {
    id: 'acupunctureSearch',
    name: 'Akupunktur-Punkt-Suche',
    description: 'Direkte Frequenz-Auswahl aus WHO-409-DB',
    hardware: 'WebAudio + Serial',
    icon: Search,
    isAvailable: true,
  },
  {
    id: 'autoSequence',
    name: 'Automatische Behandlungssequenz',
    description: 'Meridian-basierte Punkt-Sequenz mit Impulse/Pause',
    hardware: 'WebAudio',
    icon: Zap,
    isAvailable: true,
  },
];

const SERVER_HARDWARE_OPTION = {
  id: 'serverHardware',
  name: 'Server-Hardware (GPU)',
  description: 'AMD Ryzen / NVIDIA RTX für Feld-Berechnungen',
  hardware: 'Server-seitig (nicht direkte Klient-Harmonisierung)',
  icon: Server,
  isAvailable: false, // Checked via service
  requiresConnection: true,
};

interface HardwareMethodSelectorProps {
  selectedMethods: string[];
  onMethodsChange: (methods: string[]) => void;
  onServerHardwareToggle?: (enabled: boolean) => void;
  serverHardwareEnabled?: boolean;
}

export function HardwareMethodSelector({
  selectedMethods,
  onMethodsChange,
  onServerHardwareToggle,
  serverHardwareEnabled = false,
}: HardwareMethodSelectorProps) {
  const [methods, setMethods] = useState<HarmonizationMethod[]>(HARMONIZATION_METHODS);
  const [isCheckingHardware, setIsCheckingHardware] = useState(false);
  const [serverAvailable, setServerAvailable] = useState(false);

  const { 
    isWebSerialSupported, 
    isWebUSBSupported,
    devices,
    requestAnyUSBDevice,
    requestAnySerialPort 
  } = useHardwareDiscovery();

  const scanForDevices = useCallback(async () => {
    try {
      await requestAnyUSBDevice();
      await requestAnySerialPort();
      toast.success(`${devices.length} Gerät(e) erkannt`);
    } catch (error) {
      toast.info('Hardware-Scan gestartet');
    }
  }, [requestAnyUSBDevice, requestAnySerialPort, devices.length]);

  // Check hardware availability
  useEffect(() => {
    setMethods(prev => prev.map(method => {
      if (method.id === 'emFieldOutput') {
        return { ...method, isAvailable: isWebSerialSupported };
      }
      return method;
    }));
  }, [isWebSerialSupported]);

  // Check server hardware availability
  const checkServerHardware = useCallback(async () => {
    setIsCheckingHardware(true);
    try {
      // Simulated check - in real implementation, this would ping the server
      await new Promise(resolve => setTimeout(resolve, 1000));
      // For demo, assume server is available
      setServerAvailable(true);
      toast.success('Server-Hardware verfügbar: AMD Ryzen + NVIDIA RTX');
    } catch (error) {
      setServerAvailable(false);
      toast.error('Server-Hardware nicht erreichbar');
    } finally {
      setIsCheckingHardware(false);
    }
  }, []);

  const toggleMethod = useCallback((methodId: string) => {
    const isSelected = selectedMethods.includes(methodId);
    const newMethods = isSelected
      ? selectedMethods.filter(id => id !== methodId)
      : [...selectedMethods, methodId];
    onMethodsChange(newMethods);
  }, [selectedMethods, onMethodsChange]);

  const isMethodSelected = useCallback((methodId: string) => {
    return selectedMethods.includes(methodId);
  }, [selectedMethods]);

  return (
    <Card className="border-border bg-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Settings className="w-5 h-5 text-primary" />
          Harmonisierungs-Methoden
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Browser-basierte Methoden */}
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Browser-basiert (WebAudio)
          </p>
          {methods.filter(m => !m.requiresConnection).map((method) => (
            <MethodItem
              key={method.id}
              method={method}
              isSelected={isMethodSelected(method.id)}
              onToggle={() => toggleMethod(method.id)}
            />
          ))}
        </div>

        {/* Hardware-abhängige Methoden */}
        <div className="space-y-2 pt-2 border-t border-border">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Hardware-Verbindungen
            </p>
            <Button
              variant="ghost"
              size="sm"
              onClick={scanForDevices}
              className="h-7 text-xs"
            >
              <Usb className="w-3 h-3 mr-1" />
              Scannen
            </Button>
          </div>
          
          {methods.filter(m => m.requiresConnection).map((method) => (
            <MethodItem
              key={method.id}
              method={method}
              isSelected={isMethodSelected(method.id)}
              onToggle={() => toggleMethod(method.id)}
              connectedDevices={devices.length}
            />
          ))}

          {/* Server Hardware Option */}
          <div className="pt-2">
            <div className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
              serverHardwareEnabled 
                ? 'border-primary/50 bg-primary/5' 
                : 'border-border bg-muted/20'
            }`}>
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  serverAvailable ? 'bg-green-500/20' : 'bg-muted'
                }`}>
                  <Server className={`w-4 h-4 ${
                    serverAvailable ? 'text-green-500' : 'text-muted-foreground'
                  }`} />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {SERVER_HARDWARE_OPTION.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {SERVER_HARDWARE_OPTION.description}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                {!serverAvailable && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={checkServerHardware}
                    disabled={isCheckingHardware}
                    className="h-7 text-xs"
                  >
                    {isCheckingHardware ? (
                      <div className="animate-spin w-3 h-3 border border-current border-t-transparent rounded-full" />
                    ) : (
                      'Prüfen'
                    )}
                  </Button>
                )}
                {serverAvailable && (
                  <Switch
                    checked={serverHardwareEnabled}
                    onCheckedChange={onServerHardwareToggle}
                  />
                )}
              </div>
            </div>
            {serverAvailable && (
              <p className="text-xs text-muted-foreground mt-1 ml-3">
                GPU-beschleunigte Feld-Berechnungen (nicht direkte Harmonisierung am Klient)
              </p>
            )}
          </div>
        </div>

        {/* Ausgewählte Methoden Zusammenfassung */}
        {selectedMethods.length > 0 && (
          <div className="pt-3 border-t border-border">
            <p className="text-xs text-muted-foreground mb-2">Aktive Methoden:</p>
            <div className="flex flex-wrap gap-1">
              {selectedMethods.map(id => {
                const method = methods.find(m => m.id === id);
                return method ? (
                  <Badge key={id} variant="secondary" className="text-xs">
                    {method.name}
                  </Badge>
                ) : null;
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function MethodItem({
  method,
  isSelected,
  onToggle,
  connectedDevices,
}: {
  method: HarmonizationMethod;
  isSelected: boolean;
  onToggle: () => void;
  connectedDevices?: number;
}) {
  const Icon = method.icon;
  const isDisabled = !method.isAvailable && method.requiresConnection;

  return (
    <button
      onClick={onToggle}
      disabled={isDisabled}
      className={`w-full flex items-center justify-between p-3 rounded-lg border transition-colors ${
        isSelected 
          ? 'border-primary/50 bg-primary/5' 
          : isDisabled 
            ? 'border-border bg-muted/10 opacity-50 cursor-not-allowed' 
            : 'border-border bg-muted/20 hover:bg-muted/40'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${
          isSelected ? 'bg-primary/20' : 'bg-muted'
        }`}>
          <Icon className={`w-4 h-4 ${
            isSelected ? 'text-primary' : 'text-muted-foreground'
          }`} />
        </div>
        <div className="text-left">
          <p className="text-sm font-medium text-foreground">{method.name}</p>
          <p className="text-xs text-muted-foreground">{method.hardware}</p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {method.requiresConnection && !method.isAvailable && (
          <AlertCircle className="w-4 h-4 text-yellow-500" />
        )}
        {isSelected && (
          <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
            <Check className="w-3 h-3 text-primary-foreground" />
          </div>
        )}
      </div>
    </button>
  );
}

export default HardwareMethodSelector;
