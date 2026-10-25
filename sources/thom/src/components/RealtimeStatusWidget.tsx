// Realtime-Status Widget für Latenz-Anzeige
import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Wifi, WifiOff, Zap, Users } from 'lucide-react';
import { useRealtimeSync } from '@/hooks/useRealtimeSync';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

const RealtimeStatusWidget = () => {
  const {
    isConnected,
    clientId,
    latency,
    connectedClients,
    connect,
    disconnect,
  } = useRealtimeSync();

  // Auto-Connect bei Mount
  useEffect(() => {
    connect().catch((error) => {
      console.error('[RealtimeWidget] Connection failed:', error);
    });

    return () => {
      // Nicht auto-disconnect - Verbindung bleibt bestehen
    };
  }, [connect]);

  const handleToggleConnection = async () => {
    if (isConnected) {
      disconnect();
      toast.info('Realtime-Verbindung getrennt');
    } else {
      try {
        await connect();
        toast.success('Realtime-Verbindung hergestellt');
      } catch (error) {
        toast.error('Verbindung fehlgeschlagen');
      }
    }
  };

  // Latenz-Farbe bestimmen
  const getLatencyColor = (ms: number): string => {
    if (ms < 5) return 'text-green-400';
    if (ms < 20) return 'text-yellow-400';
    if (ms < 50) return 'text-orange-400';
    return 'text-red-400';
  };

  const getLatencyBg = (ms: number): string => {
    if (ms < 5) return 'bg-green-400/20';
    if (ms < 20) return 'bg-yellow-400/20';
    if (ms < 50) return 'bg-orange-400/20';
    return 'bg-red-400/20';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-4 right-4 z-50"
    >
      <div className="bg-card/95 backdrop-blur-sm border border-border rounded-lg shadow-lg p-3 min-w-[200px]">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Wifi className="w-4 h-4 text-green-400" />
            ) : (
              <WifiOff className="w-4 h-4 text-muted-foreground" />
            )}
            <span className="text-sm font-medium text-foreground">
              Realtime
            </span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2 text-xs"
            onClick={handleToggleConnection}
          >
            {isConnected ? 'Trennen' : 'Verbinden'}
          </Button>
        </div>

        {isConnected ? (
          <div className="space-y-2">
            {/* Latenz */}
            <div className={cn(
              "flex items-center justify-between p-2 rounded",
              getLatencyBg(latency.current)
            )}>
              <div className="flex items-center gap-2">
                <Zap className={cn("w-3 h-3", getLatencyColor(latency.current))} />
                <span className="text-xs text-muted-foreground">Latenz</span>
              </div>
              <span className={cn("text-sm font-mono font-bold", getLatencyColor(latency.current))}>
                {latency.current.toFixed(1)} ms
              </span>
            </div>

            {/* Latenz-Statistiken */}
            <div className="grid grid-cols-3 gap-1 text-xs">
              <div className="text-center p-1 bg-muted/30 rounded">
                <p className="text-muted-foreground">Min</p>
                <p className="font-mono text-foreground">
                  {latency.min === Infinity ? '--' : latency.min.toFixed(1)}
                </p>
              </div>
              <div className="text-center p-1 bg-muted/30 rounded">
                <p className="text-muted-foreground">Avg</p>
                <p className="font-mono text-foreground">
                  {latency.avg.toFixed(1)}
                </p>
              </div>
              <div className="text-center p-1 bg-muted/30 rounded">
                <p className="text-muted-foreground">Max</p>
                <p className="font-mono text-foreground">
                  {latency.max === 0 ? '--' : latency.max.toFixed(1)}
                </p>
              </div>
            </div>

            {/* Verbundene Clients */}
            <div className="flex items-center justify-between text-xs pt-1 border-t border-border">
              <div className="flex items-center gap-1 text-muted-foreground">
                <Users className="w-3 h-3" />
                <span>Clients</span>
              </div>
              <span className="font-medium text-foreground">{connectedClients}</span>
            </div>

            {/* Client-ID */}
            {clientId && (
              <p className="text-xs text-muted-foreground font-mono truncate">
                ID: {clientId.slice(-8)}
              </p>
            )}
          </div>
        ) : (
          <div className="text-center py-2">
            <p className="text-xs text-muted-foreground">Nicht verbunden</p>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default RealtimeStatusWidget;
