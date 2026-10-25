// System Status Dashboard Komponente
import { motion } from 'framer-motion';
import { 
  Cpu, 
  MonitorDot, 
  HardDrive, 
  Wifi, 
  Usb, 
  Activity,
  Thermometer,
  Zap,
  Server,
  CircuitBoard
} from 'lucide-react';
import { useSystemMonitor } from '@/hooks/useSystemMonitor';
import { useHardwareDiscovery } from '@/hooks/useHardwareDiscovery';
import { useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const SystemStatusDashboard = () => {
  const { 
    serverConfig, 
    currentMetrics, 
    isMonitoring, 
    startMonitoring, 
    stopMonitoring 
  } = useSystemMonitor();
  
  const { 
    devices, 
    isInitialized,
    isWebUSBSupported,
    isWebSerialSupported,
    requestUSBDAC,
    requestFrequencyGenerator,
    requestMicrocontroller,
    lastEvent
  } = useHardwareDiscovery();

  // Auto-Start Monitoring
  useEffect(() => {
    startMonitoring(1000);
    return () => stopMonitoring();
  }, [startMonitoring, stopMonitoring]);

  // Device Events
  useEffect(() => {
    if (lastEvent) {
      if (lastEvent.type === 'connect') {
        toast.success(`Gerät verbunden: ${lastEvent.device.name}`);
      } else if (lastEvent.type === 'disconnect') {
        toast.warning(`Gerät getrennt: ${lastEvent.device.name}`);
      }
    }
  }, [lastEvent]);

  const handleRequestUSBDAC = async () => {
    const device = await requestUSBDAC();
    if (device) {
      toast.success(`USB DAC verbunden: ${device.name}`);
    }
  };

  const handleRequestFrequencyGenerator = async () => {
    const device = await requestFrequencyGenerator();
    if (device) {
      toast.success(`Frequenzgenerator verbunden: ${device.name}`);
    }
  };

  const handleRequestMicrocontroller = async () => {
    const device = await requestMicrocontroller();
    if (device) {
      toast.success(`Mikrocontroller verbunden: ${device.name}`);
    }
  };

  return (
    <section className="py-16 px-4 bg-field-pattern">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="font-display text-3xl md:text-4xl text-foreground mb-4">
            System <span className="text-gradient-primary">Status</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Echtzeit-Überwachung der Server-Hardware und verbundener Geräte
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Server Hardware Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="bg-card rounded-lg border border-border p-6 shadow-card"
          >
            <div className="flex items-center gap-3 mb-6">
              <Server className="w-6 h-6 text-primary" />
              <h3 className="font-display text-xl text-foreground">
                {serverConfig.gpu.cudaCores ? 'GPU Server M G1' : 'Development PC'}
              </h3>
              <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded">
                {serverConfig.gpu.cudaCores ? 'Production' : 'Dev-Mode'}
              </span>
            </div>

            {/* CPU */}
            <div className="space-y-4">
              <div className="p-4 bg-muted/30 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-primary" />
                    <span className="font-medium text-foreground">{serverConfig.cpu.name}</span>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {serverConfig.cpu.cores}C/{serverConfig.cpu.threads}T
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 mt-3">
                  <MetricBadge 
                    label="Auslastung" 
                    value={`${currentMetrics?.cpu.usage || 0}%`}
                    color={getUsageColor(currentMetrics?.cpu.usage || 0)}
                  />
                  <MetricBadge 
                    label="Frequenz" 
                    value={`${currentMetrics?.cpu.frequency || serverConfig.cpu.baseFrequency} MHz`}
                  />
                  <MetricBadge 
                    label="Temp" 
                    value={`${currentMetrics?.cpu.temperature || '--'}°C`}
                    icon={<Thermometer className="w-3 h-3" />}
                    color={getTempColor(currentMetrics?.cpu.temperature || 0)}
                  />
                </div>
                <div className="mt-3">
                  <ProgressBar value={currentMetrics?.cpu.usage || 0} color="primary" />
                </div>
              </div>

              {/* GPU */}
              <div className="p-4 bg-muted/30 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <MonitorDot className="w-5 h-5 text-secondary" />
                    <span className="font-medium text-foreground">{serverConfig.gpu.name}</span>
                  </div>
                  <span className="text-sm text-muted-foreground">{serverConfig.gpu.vram / 1024} GB VRAM</span>
                </div>
                <div className="grid grid-cols-3 gap-4 mt-3">
                  <MetricBadge 
                    label="GPU Load" 
                    value={`${currentMetrics?.gpu.usage || 0}%`}
                    color={getUsageColor(currentMetrics?.gpu.usage || 0)}
                  />
                  <MetricBadge 
                    label="VRAM" 
                    value={`${Math.round((currentMetrics?.gpu.vramUsed || 0) / 1024)} GB`}
                  />
                  <MetricBadge 
                    label="Temp" 
                    value={`${currentMetrics?.gpu.temperature || '--'}°C`}
                    icon={<Thermometer className="w-3 h-3" />}
                    color={getTempColor(currentMetrics?.gpu.temperature || 0)}
                  />
                </div>
                <div className="mt-3">
                  <ProgressBar value={currentMetrics?.gpu.usage || 0} color="secondary" />
                </div>
              </div>

              {/* RAM */}
              <div className="p-4 bg-muted/30 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <CircuitBoard className="w-5 h-5 text-accent" />
                    <span className="font-medium text-foreground">
                      {serverConfig.memory.total / 1024} GB {serverConfig.memory.type}
                    </span>
                  </div>
                  <span className="text-sm text-muted-foreground">{serverConfig.memory.speed} MHz</span>
                </div>
                <div className="grid grid-cols-3 gap-4 mt-3">
                  <MetricBadge 
                    label="Verwendet" 
                    value={`${Math.round((currentMetrics?.memory.used || 0) / 1024)} GB`}
                  />
                  <MetricBadge 
                    label="Verfügbar" 
                    value={`${Math.round((currentMetrics?.memory.available || 0) / 1024)} GB`}
                  />
                  <MetricBadge 
                    label="Jitter" 
                    value={`${currentMetrics?.memory.jitter?.toFixed(2) || '--'} ms`}
                    icon={<Activity className="w-3 h-3" />}
                  />
                </div>
              </div>

              {/* Storage & Network */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <HardDrive className="w-4 h-4 text-primary" />
                    <span className="text-sm font-medium text-foreground">Storage</span>
                  </div>
                  <p className="text-lg font-semibold text-foreground">2x 1TB NVMe</p>
                  <p className="text-xs text-muted-foreground">RAID-fähig</p>
                </div>
                <div className="p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Wifi className="w-4 h-4 text-primary" />
                    <span className="text-sm font-medium text-foreground">Netzwerk</span>
                  </div>
                  <p className="text-lg font-semibold text-foreground">2x 1 Gbit/s</p>
                  <p className="text-xs text-muted-foreground">
                    Latenz: {currentMetrics?.latency.websocket?.toFixed(2) || '--'} ms
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          {/* External Devices Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="bg-card rounded-lg border border-border p-6 shadow-card"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Usb className="w-6 h-6 text-primary" />
                <h3 className="font-display text-xl text-foreground">Hardware-Discovery</h3>
              </div>
              <div className="flex items-center gap-2">
                <StatusIndicator 
                  active={isInitialized} 
                  label={isInitialized ? 'Aktiv' : 'Initialisiere...'} 
                />
              </div>
            </div>

            {/* API Support Status */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className={cn(
                "p-3 rounded-lg border",
                isWebUSBSupported ? "border-primary/30 bg-primary/5" : "border-destructive/30 bg-destructive/5"
              )}>
                <div className="flex items-center gap-2">
                  <div className={cn(
                    "w-2 h-2 rounded-full",
                    isWebUSBSupported ? "bg-primary" : "bg-destructive"
                  )} />
                  <span className="text-sm font-medium text-foreground">WebUSB</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {isWebUSBSupported ? 'Unterstützt' : 'Nicht verfügbar'}
                </p>
              </div>
              <div className={cn(
                "p-3 rounded-lg border",
                isWebSerialSupported ? "border-primary/30 bg-primary/5" : "border-destructive/30 bg-destructive/5"
              )}>
                <div className="flex items-center gap-2">
                  <div className={cn(
                    "w-2 h-2 rounded-full",
                    isWebSerialSupported ? "bg-primary" : "bg-destructive"
                  )} />
                  <span className="text-sm font-medium text-foreground">WebSerial</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {isWebSerialSupported ? 'Unterstützt' : 'Nicht verfügbar'}
                </p>
              </div>
            </div>

            {/* Device Request Buttons */}
            <div className="flex flex-wrap gap-2 mb-6">
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRequestUSBDAC}
                disabled={!isWebUSBSupported}
              >
                <Zap className="w-4 h-4 mr-2" />
                USB DAC
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRequestFrequencyGenerator}
                disabled={!isWebSerialSupported}
              >
                <Activity className="w-4 h-4 mr-2" />
                Frequenzgenerator
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRequestMicrocontroller}
                disabled={!isWebSerialSupported}
              >
                <CircuitBoard className="w-4 h-4 mr-2" />
                Mikrocontroller
              </Button>
            </div>

            {/* Connected Devices List */}
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">
                Verbundene Geräte ({devices.length})
              </h4>
              
              {devices.length === 0 ? (
                <div className="p-8 text-center border border-dashed border-border rounded-lg">
                  <Usb className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">
                    Keine externen Geräte verbunden
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Klicke oben auf einen Button, um ein Gerät zu verbinden
                  </p>
                </div>
              ) : (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {devices.map((device) => (
                    <motion.div
                      key={device.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-3 bg-muted/30 rounded-lg border border-border/50"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <DeviceIcon type={device.type} />
                          <div>
                            <p className="font-medium text-foreground text-sm">{device.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {device.manufacturer || device.type}
                            </p>
                          </div>
                        </div>
                        <StatusIndicator 
                          active={device.status === 'connected' || device.status === 'ready'} 
                          label={device.status} 
                        />
                      </div>
                      {device.capabilities.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {device.capabilities.map((cap, idx) => (
                            <span 
                              key={idx}
                              className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded"
                            >
                              {cap.name}
                            </span>
                          ))}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

// Helper Components
interface MetricBadgeProps {
  label: string;
  value: string;
  color?: 'green' | 'yellow' | 'red' | 'default';
  icon?: React.ReactNode;
}

const MetricBadge = ({ label, value, color = 'default', icon }: MetricBadgeProps) => (
  <div className="text-center">
    <p className="text-xs text-muted-foreground mb-1">{label}</p>
    <p className={cn(
      "text-sm font-semibold flex items-center justify-center gap-1",
      color === 'green' && "text-green-400",
      color === 'yellow' && "text-yellow-400",
      color === 'red' && "text-red-400",
      color === 'default' && "text-foreground"
    )}>
      {icon}
      {value}
    </p>
  </div>
);

interface ProgressBarProps {
  value: number;
  color?: 'primary' | 'secondary' | 'accent';
}

const ProgressBar = ({ value, color = 'primary' }: ProgressBarProps) => (
  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
    <motion.div
      className={cn(
        "h-full rounded-full",
        color === 'primary' && "bg-primary",
        color === 'secondary' && "bg-secondary",
        color === 'accent' && "bg-accent"
      )}
      initial={{ width: 0 }}
      animate={{ width: `${Math.min(value, 100)}%` }}
      transition={{ duration: 0.5 }}
    />
  </div>
);

interface StatusIndicatorProps {
  active: boolean;
  label: string;
}

const StatusIndicator = ({ active, label }: StatusIndicatorProps) => (
  <div className="flex items-center gap-2">
    <div className={cn(
      "w-2 h-2 rounded-full",
      active ? "bg-green-400 animate-pulse" : "bg-muted-foreground"
    )} />
    <span className="text-xs text-muted-foreground">{label}</span>
  </div>
);

const DeviceIcon = ({ type }: { type: string }) => {
  const iconClass = "w-5 h-5 text-primary";
  
  switch (type) {
    case 'usb-dac':
      return <Zap className={iconClass} />;
    case 'frequency-generator':
      return <Activity className={iconClass} />;
    case 'microcontroller':
      return <CircuitBoard className={iconClass} />;
    case 'biosensor':
      return <Activity className={iconClass} />;
    default:
      return <Usb className={iconClass} />;
  }
};

// Helper Functions
const getUsageColor = (usage: number): 'green' | 'yellow' | 'red' => {
  if (usage < 50) return 'green';
  if (usage < 80) return 'yellow';
  return 'red';
};

const getTempColor = (temp: number): 'green' | 'yellow' | 'red' => {
  if (temp < 50) return 'green';
  if (temp < 70) return 'yellow';
  return 'red';
};

export default SystemStatusDashboard;
