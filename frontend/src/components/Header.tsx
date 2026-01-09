import { Plane, BarChart3, RotateCcw, Sparkles } from 'lucide-react';

interface HeaderProps {
  showTelemetry: boolean;
  onToggleTelemetry: () => void;
  status: string;
  onReset: () => void;
}

export default function Header({ showTelemetry, onToggleTelemetry, status, onReset }: HeaderProps) {
  const isRunning = status === 'running' || status === 'awaiting_approval';

  const statusConfig = {
    idle: { color: 'bg-dark-400', text: 'Ready' },
    running: { color: 'bg-accent-indigo', text: 'Running', pulse: true },
    awaiting_approval: { color: 'bg-warning', text: 'Awaiting Approval', pulse: true },
    completed: { color: 'bg-success', text: 'Completed' },
    error: { color: 'bg-error', text: 'Error' },
  };

  const currentStatus = statusConfig[status as keyof typeof statusConfig] || statusConfig.idle;

  return (
    <header className="glass-card border-b border-dark-500 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo and Title */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-accent-blue to-accent-purple rounded-xl flex items-center justify-center shadow-glow-purple">
                <Plane className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-accent-cyan rounded-full flex items-center justify-center">
                <Sparkles className="w-2.5 h-2.5 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-text-primary tracking-tight">
                Zava
              </h1>
              <p className="text-sm text-text-secondary -mt-0.5">
                AI Capacity Planner
              </p>
            </div>
          </div>

          {/* Center: Status */}
          <div className="flex items-center gap-3">
            {status !== 'idle' && (
              <div className="glass-card px-5 py-2.5 rounded-full flex items-center gap-3">
                <div className="relative">
                  <div className={`w-2.5 h-2.5 rounded-full ${currentStatus.color}`} />
                  {currentStatus.pulse && (
                    <div className={`absolute inset-0 w-2.5 h-2.5 rounded-full ${currentStatus.color} animate-ping`} />
                  )}
                </div>
                <span className="text-sm font-medium text-text-primary">
                  {currentStatus.text}
                </span>
              </div>
            )}
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            {/* Telemetry Toggle */}
            {status !== 'idle' && (
              <button
                onClick={onToggleTelemetry}
                className={`btn-glow flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all duration-300 ${
                  showTelemetry
                    ? 'bg-gradient-to-r from-accent-blue to-accent-indigo text-white shadow-glow-blue'
                    : 'glass-card text-text-secondary hover:text-text-primary'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span className="text-sm font-medium">Telemetry</span>
              </button>
            )}

            {/* Reset Button */}
            {status !== 'idle' && (
              <button
                onClick={onReset}
                disabled={isRunning}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all duration-300 ${
                  isRunning
                    ? 'glass-card text-dark-400 cursor-not-allowed opacity-50'
                    : 'glass-card text-text-secondary hover:text-text-primary hover:border-dark-400'
                }`}
              >
                <RotateCcw className="w-4 h-4" />
                <span className="text-sm font-medium">Reset</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
