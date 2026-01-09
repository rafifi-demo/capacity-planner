import { useState, useEffect } from 'react';
import { Plane, Users, Fuel, Package, DollarSign, Clock, TrendingUp, CheckCircle2, MapPin, Minimize2, Maximize2 } from 'lucide-react';

interface ResultsDashboardProps {
  isVisible: boolean;
  isMinimized: boolean;
  onMinimizedChange: (minimized: boolean) => void;
}

// Flight destinations from Seattle
const DESTINATIONS = [
  { code: 'NRT', name: 'Tokyo', x: 85, y: 35, delay: 0 },
  { code: 'HKG', name: 'Hong Kong', x: 80, y: 50, delay: 0.2 },
  { code: 'LHR', name: 'London', x: 48, y: 25, delay: 0.4 },
  { code: 'FRA', name: 'Frankfurt', x: 52, y: 28, delay: 0.6 },
  { code: 'JFK', name: 'New York', x: 28, y: 35, delay: 0.8 },
  { code: 'ORD', name: 'Chicago', x: 22, y: 38, delay: 1.0 },
  { code: 'LAX', name: 'Los Angeles', x: 12, y: 45, delay: 1.2 },
  { code: 'SIN', name: 'Singapore', x: 78, y: 60, delay: 1.4 },
];

// Seattle hub position
const SEATTLE = { x: 12, y: 32 };

// Results metrics
const RESULTS_METRICS = [
  { icon: Plane, label: 'Aircraft Assigned', value: '6', color: 'text-accent-blue', bgColor: 'bg-accent-blue/20' },
  { icon: Users, label: 'Crew Scheduled', value: '18', color: 'text-accent-purple', bgColor: 'bg-accent-purple/20' },
  { icon: Package, label: 'Shipments Routed', value: '487', color: 'text-accent-cyan', bgColor: 'bg-accent-cyan/20' },
  { icon: Fuel, label: 'Fuel Optimized', value: '12.5K gal', color: 'text-warning', bgColor: 'bg-warning/20' },
];

const SAVINGS_METRICS = [
  { icon: DollarSign, label: 'Estimated Savings', value: '$127,450', color: 'text-success' },
  { icon: Clock, label: 'Planning Time', value: '4 min vs 3 days', color: 'text-accent-purple' },
  { icon: TrendingUp, label: 'Efficiency Gain', value: '+18%', color: 'text-accent-cyan' },
];

// Animated counter component
function AnimatedValue({ value, delay = 0 }: { value: string; delay?: number }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay * 1000);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <span className={`transition-all duration-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}`}>
      {value}
    </span>
  );
}

// Flying aircraft component
function FlyingAircraft({ destination, index }: { destination: typeof DESTINATIONS[0]; index: number }) {
  const [isFlying, setIsFlying] = useState(false);
  const [hasArrived, setHasArrived] = useState(false);

  useEffect(() => {
    const flyTimer = setTimeout(() => setIsFlying(true), destination.delay * 1000 + 500);
    const arriveTimer = setTimeout(() => setHasArrived(true), destination.delay * 1000 + 2500);
    return () => {
      clearTimeout(flyTimer);
      clearTimeout(arriveTimer);
    };
  }, [destination.delay]);

  // Calculate angle for the aircraft
  const dx = destination.x - SEATTLE.x;
  const dy = destination.y - SEATTLE.y;
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);

  return (
    <g>
      {/* Flight path line */}
      <line
        x1={`${SEATTLE.x}%`}
        y1={`${SEATTLE.y}%`}
        x2={`${destination.x}%`}
        y2={`${destination.y}%`}
        stroke="url(#flightGradient)"
        strokeWidth="1"
        strokeDasharray="4 2"
        className={`transition-opacity duration-500 ${isFlying ? 'opacity-40' : 'opacity-0'}`}
      />

      {/* Animated aircraft */}
      {isFlying && !hasArrived && (
        <g
          className="animate-flight"
          style={{
            animation: `flight-${index} 2s ease-out forwards`,
            transformOrigin: 'center',
          }}
        >
          <text
            fontSize="16"
            style={{ transform: `rotate(${angle}deg)` }}
            className="fill-accent-blue"
          >
            ✈
          </text>
        </g>
      )}

      {/* Destination marker */}
      <g
        className={`transition-all duration-500 ${hasArrived ? 'opacity-100 scale-100' : 'opacity-0 scale-0'}`}
        style={{ transformOrigin: `${destination.x}% ${destination.y}%` }}
      >
        <circle
          cx={`${destination.x}%`}
          cy={`${destination.y}%`}
          r="8"
          className="fill-success/30"
        />
        <circle
          cx={`${destination.x}%`}
          cy={`${destination.y}%`}
          r="4"
          className="fill-success"
        />
        <text
          x={`${destination.x}%`}
          y={`${destination.y + 5}%`}
          textAnchor="middle"
          className="fill-text-secondary text-[8px] font-medium"
        >
          {destination.code}
        </text>
      </g>
    </g>
  );
}

export default function ResultsDashboard({ isVisible, isMinimized, onMinimizedChange }: ResultsDashboardProps) {
  const [showMap, setShowMap] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    if (isVisible) {
      const mapTimer = setTimeout(() => setShowMap(true), 300);
      const resultsTimer = setTimeout(() => setShowResults(true), 800);
      return () => {
        clearTimeout(mapTimer);
        clearTimeout(resultsTimer);
      };
    }
  }, [isVisible]);

  if (!isVisible) return null;

  // Minimized view
  if (isMinimized) {
    return (
      <div className="fixed bottom-20 right-4 z-40 animate-slide-up">
        <button
          onClick={() => onMinimizedChange(false)}
          className="glass-card-elevated border-success/30 rounded-2xl px-5 py-4 flex items-center gap-4 hover:border-success/50 transition-all group cursor-pointer"
        >
          <div className="w-12 h-12 bg-gradient-to-br from-success to-emerald-400 rounded-xl flex items-center justify-center shadow-glow-success">
            <CheckCircle2 className="w-6 h-6 text-white" />
          </div>
          <div className="text-left">
            <h3 className="text-sm font-semibold text-text-primary">Capacity Plan Executed</h3>
            <p className="text-xs text-text-secondary">Click to view results</p>
          </div>
          <Maximize2 className="w-5 h-5 text-text-muted group-hover:text-text-primary transition-colors ml-2" />
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center p-8 pointer-events-none">
      <div className="w-full max-w-6xl pointer-events-auto">
        {/* Main Results Card */}
        <div className={`glass-card-elevated rounded-3xl overflow-hidden transition-all duration-700 ${isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
          {/* Header */}
          <div className="bg-gradient-to-r from-success/20 via-accent-blue/20 to-accent-purple/20 p-6 border-b border-dark-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-success to-emerald-400 rounded-2xl flex items-center justify-center shadow-glow-success">
                  <CheckCircle2 className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-text-primary">Capacity Plan Executed</h2>
                  <p className="text-text-secondary">All operations have been optimized and scheduled</p>
                </div>
              </div>
              <button
                onClick={() => onMinimizedChange(true)}
                className="p-3 rounded-xl bg-dark-700/50 border border-dark-500 hover:border-dark-400 hover:bg-dark-600/50 transition-all group"
                title="Minimize"
              >
                <Minimize2 className="w-5 h-5 text-text-muted group-hover:text-text-primary transition-colors" />
              </button>
            </div>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-2 gap-6">
              {/* Left: Flight Map Visualization */}
              <div className={`transition-all duration-700 ${showMap ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-10'}`}>
                <h3 className="text-sm font-medium text-text-secondary mb-4 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-accent-blue" />
                  Optimized Flight Routes from Seattle Hub
                </h3>
                <div className="relative bg-dark-800 rounded-2xl border border-dark-500 overflow-hidden" style={{ aspectRatio: '16/10' }}>
                  {/* World map background (simplified) */}
                  <div className="absolute inset-0 opacity-20">
                    <svg viewBox="0 0 100 60" className="w-full h-full">
                      {/* Simplified continent shapes */}
                      <ellipse cx="20" cy="35" rx="15" ry="12" className="fill-dark-400" /> {/* North America */}
                      <ellipse cx="50" cy="28" rx="12" ry="8" className="fill-dark-400" /> {/* Europe */}
                      <ellipse cx="75" cy="45" rx="18" ry="12" className="fill-dark-400" /> {/* Asia */}
                    </svg>
                  </div>

                  {/* Flight routes SVG */}
                  <svg viewBox="0 0 100 60" className="absolute inset-0 w-full h-full">
                    <defs>
                      <linearGradient id="flightGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#10b981" />
                      </linearGradient>
                    </defs>

                    {/* Seattle Hub */}
                    <g>
                      <circle cx={`${SEATTLE.x}%`} cy={`${SEATTLE.y}%`} r="10" className="fill-accent-blue/30 animate-pulse" />
                      <circle cx={`${SEATTLE.x}%`} cy={`${SEATTLE.y}%`} r="6" className="fill-accent-blue" />
                      <text x={`${SEATTLE.x}%`} y={`${SEATTLE.y + 6}%`} textAnchor="middle" className="fill-text-primary text-[8px] font-bold">
                        SEA
                      </text>
                    </g>

                    {/* Flight paths and destinations */}
                    {DESTINATIONS.map((dest, index) => (
                      <FlyingAircraft key={dest.code} destination={dest} index={index} />
                    ))}
                  </svg>

                  {/* Legend */}
                  <div className="absolute bottom-2 left-2 flex items-center gap-3 text-xs">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-accent-blue" />
                      <span className="text-text-muted">Hub</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-success" />
                      <span className="text-text-muted">Destination</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right: Results Metrics */}
              <div className={`space-y-4 transition-all duration-700 ${showResults ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-10'}`}>
                {/* Operations Summary */}
                <div>
                  <h3 className="text-sm font-medium text-text-secondary mb-3 flex items-center gap-2">
                    <Package className="w-4 h-4 text-accent-cyan" />
                    Operations Summary
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    {RESULTS_METRICS.map((metric, index) => {
                      const Icon = metric.icon;
                      return (
                        <div
                          key={metric.label}
                          className="bg-dark-700/50 rounded-xl p-4 border border-dark-500 hover:border-dark-400 transition-all group"
                        >
                          <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 ${metric.bgColor} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform`}>
                              <Icon className={`w-5 h-5 ${metric.color}`} />
                            </div>
                            <div>
                              <div className={`text-xl font-bold ${metric.color}`}>
                                <AnimatedValue value={metric.value} delay={0.5 + index * 0.2} />
                              </div>
                              <div className="text-xs text-text-muted">{metric.label}</div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Business Impact */}
                <div>
                  <h3 className="text-sm font-medium text-text-secondary mb-3 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-success" />
                    Business Impact
                  </h3>
                  <div className="bg-gradient-to-r from-success/10 via-accent-blue/10 to-accent-purple/10 rounded-xl p-4 border border-success/30">
                    <div className="grid grid-cols-3 gap-4">
                      {SAVINGS_METRICS.map((metric, index) => {
                        const Icon = metric.icon;
                        return (
                          <div key={metric.label} className="text-center">
                            <Icon className={`w-5 h-5 ${metric.color} mx-auto mb-1`} />
                            <div className={`text-lg font-bold ${metric.color}`}>
                              <AnimatedValue value={metric.value} delay={1.2 + index * 0.2} />
                            </div>
                            <div className="text-xs text-text-muted">{metric.label}</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* AI Summary */}
                <div className="bg-dark-700/50 rounded-xl p-4 border border-dark-500">
                  <p className="text-sm text-text-secondary leading-relaxed">
                    <span className="text-accent-cyan font-medium">AI Analysis Complete:</span> Optimal aircraft assignments reduce fuel consumption by
                    <span className="text-success font-semibold"> 12.5%</span>. Crew scheduling eliminates overtime, saving
                    <span className="text-warning font-semibold"> $45,000</span> monthly. All shipments routed for on-time delivery.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CSS for flight animations */}
      <style>{`
        ${DESTINATIONS.map((dest, index) => `
          @keyframes flight-${index} {
            0% {
              transform: translate(${SEATTLE.x}%, ${SEATTLE.y}%);
              opacity: 1;
            }
            100% {
              transform: translate(${dest.x}%, ${dest.y}%);
              opacity: 0;
            }
          }
        `).join('\n')}
      `}</style>
    </div>
  );
}
