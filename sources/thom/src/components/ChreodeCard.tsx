import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface ChreodeCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  delay?: number;
  variant?: "primary" | "secondary" | "accent";
}

const ChreodeCard = ({ title, description, icon: Icon, delay = 0, variant = "primary" }: ChreodeCardProps) => {
  const variants = {
    primary: {
      border: "border-primary/20 hover:border-primary/50",
      glow: "hover:shadow-glow-primary",
      icon: "text-primary bg-primary/10",
      accent: "from-primary/20",
    },
    secondary: {
      border: "border-chreode/20 hover:border-chreode/50",
      glow: "hover:shadow-glow-secondary",
      icon: "text-chreode bg-chreode/10",
      accent: "from-chreode/20",
    },
    accent: {
      border: "border-accent/20 hover:border-accent/50",
      glow: "hover:shadow-[0_0_40px_hsl(270_60%_55%/0.3)]",
      icon: "text-accent bg-accent/10",
      accent: "from-accent/20",
    },
  };

  const style = variants[variant];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      viewport={{ once: true }}
      className={`
        group relative overflow-hidden rounded-2xl border bg-card p-6 
        transition-all duration-500 cursor-pointer
        ${style.border} ${style.glow}
      `}
    >
      {/* Background gradient on hover */}
      <div className={`absolute inset-0 bg-gradient-to-br ${style.accent} to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
      
      {/* Content */}
      <div className="relative z-10">
        <div className={`w-12 h-12 rounded-xl ${style.icon} flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110`}>
          <Icon className="w-6 h-6" />
        </div>
        
        <h3 className="font-display text-xl font-semibold text-foreground mb-2 group-hover:text-gradient-primary transition-all">
          {title}
        </h3>
        
        <p className="text-muted-foreground text-sm leading-relaxed">
          {description}
        </p>
      </div>

      {/* Animated corner accent */}
      <div className={`absolute bottom-0 right-0 w-20 h-20 bg-gradient-to-tl ${style.accent} to-transparent opacity-0 group-hover:opacity-50 transition-opacity duration-500 rounded-tl-full`} />
    </motion.div>
  );
};

export default ChreodeCard;
