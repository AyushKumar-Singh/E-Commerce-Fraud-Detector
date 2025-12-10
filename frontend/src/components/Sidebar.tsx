import {
  BarChart3,
  FileText,
  LayoutDashboard,
  MessageSquare,
  Settings,
  Shield,
  Users,
} from 'lucide-react';
import { motion } from 'motion/react';
import { cn } from '../utils/cn';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  isCollapsed: boolean;
}

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'transactions', label: 'Transactions', icon: FileText },
  { id: 'reviews', label: 'Review Analysis', icon: MessageSquare },
  { id: 'users', label: 'User Management', icon: Users },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ currentPage, onNavigate, isCollapsed }: SidebarProps) {
  return (
    <motion.aside
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className={cn(
        'sticky top-16 h-[calc(100vh-4rem)] border-r border-border bg-card transition-all duration-300',
        isCollapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex h-full flex-col gap-2 p-3">
        {/* Navigation Items */}
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;

            return (
              <motion.button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                whileHover={{ x: 4 }}
                whileTap={{ scale: 0.98 }}
                className={cn(
                  'relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 transition-all',
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-md'
                    : 'text-foreground hover:bg-accent/10'
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-lg bg-primary"
                    transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <Icon className={cn('relative z-10 h-5 w-5 flex-shrink-0')} />
                {!isCollapsed && (
                  <span className="relative z-10 truncate">{item.label}</span>
                )}
              </motion.button>
            );
          })}
        </nav>

        {/* Bottom Section */}
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="glass mt-auto rounded-lg p-4"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-success/10">
                <Shield className="h-5 w-5 text-success" />
              </div>
              <div className="flex-1">
                <p className="text-success">Protected</p>
                <p className="text-muted-foreground">All systems active</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.aside>
  );
}
