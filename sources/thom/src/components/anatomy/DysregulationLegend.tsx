/**
 * Dysregulations-Intensitätsskala für 3D-Anatomie-Viewer
 * 5 Farben mit Intensitätsstufen
 */
import { motion } from 'framer-motion';
import { DYSREGULATION_LEVELS } from './dysregulation-utils';

interface DysregulationLegendProps {
  className?: string;
}

export function DysregulationLegend({ className }: DysregulationLegendProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`bg-background/90 backdrop-blur-sm p-3 rounded-lg border border-border shadow-lg ${className}`}
    >
      <p className="text-xs font-medium text-foreground mb-2">Dysregulations-Intensität</p>
      <div className="space-y-1">
        {DYSREGULATION_LEVELS.map((level) => (
          <div key={level.level} className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: level.color }}
            />
            <span className="text-xs text-muted-foreground">{level.label}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

export default DysregulationLegend;
