import { motion } from 'motion/react';
import { LucideIcon } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { cn } from '../utils/cn';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: LucideIcon;
  iconColor?: string;
  delay?: number;
}

export function StatCard({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  iconColor = 'bg-primary',
  delay = 0,
}: StatCardProps) {
  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
    >
      <Card className="relative overflow-hidden border-border shadow-sm hover:shadow-lg transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-muted-foreground mb-2">{title}</p>
              <h3 className="mb-2">{value}</h3>
              {change && (
                <div className="flex items-center gap-1">
                  <span
                    className={cn(
                      changeType === 'positive' && 'text-success',
                      changeType === 'negative' && 'text-destructive',
                      changeType === 'neutral' && 'text-muted-foreground'
                    )}
                  >
                    {change}
                  </span>
                  <span className="text-muted-foreground">vs last month</span>
                </div>
              )}
            </div>
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.6 }}
              className={cn(
                'flex h-12 w-12 items-center justify-center rounded-xl',
                iconColor
              )}
            >
              <Icon className="h-6 w-6 text-white" />
            </motion.div>
          </div>
          {/* Decorative gradient */}
          <div className="absolute bottom-0 right-0 h-24 w-24 rounded-full bg-gradient-to-br from-primary/5 to-accent/5 blur-2xl" />
        </CardContent>
      </Card>
    </motion.div>
  );
}
