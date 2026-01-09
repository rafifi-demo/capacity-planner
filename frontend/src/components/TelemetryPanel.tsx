import { useState, useEffect, useRef } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { Activity, Coins, Clock, Hash, TrendingUp, Zap, Cpu, Sparkles } from 'lucide-react';
import type { TelemetryMetrics, AgentInfo } from '../types';

interface TelemetryPanelProps {
  telemetry: TelemetryMetrics;
  agents: AgentInfo[];
}

// Animated counter component
function AnimatedCounter({
  value,
  decimals = 0,
  prefix = '',
  suffix = '',
  duration = 1000
}: {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
}) {
  const [displayValue, setDisplayValue] = useState(0);
  const previousValue = useRef(0);
  const startTime = useRef<number | null>(null);

  useEffect(() => {
    const startValue = previousValue.current;
    const endValue = value;
    startTime.current = null;

    const animate = (timestamp: number) => {
      if (!startTime.current) startTime.current = timestamp;
      const progress = Math.min((timestamp - startTime.current) / duration, 1);

      // Easing function for smooth animation
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const currentValue = startValue + (endValue - startValue) * easeOutQuart;

      setDisplayValue(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        previousValue.current = endValue;
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  const formattedValue = decimals > 0
    ? displayValue.toFixed(decimals)
    : Math.round(displayValue).toLocaleString();

  return (
    <span className="tabular-nums">
      {prefix}{formattedValue}{suffix}
    </span>
  );
}

// Custom tooltip for charts
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card-elevated px-3 py-2 rounded-lg text-xs">
        <p className="text-text-primary font-medium mb-1">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function TelemetryPanel({ telemetry, agents }: TelemetryPanelProps) {
  // Prepare data for charts
  const tokenData = agents.map(agent => ({
    name: agent.name.split(' ')[0],
    input: telemetry.agent_metrics[agent.id]?.input_tokens || 0,
    output: telemetry.agent_metrics[agent.id]?.output_tokens || 0,
    color: agent.color,
  }));

  const costData = agents
    .filter(agent => telemetry.agent_metrics[agent.id]?.cost_usd > 0)
    .map(agent => ({
      name: agent.name,
      value: telemetry.agent_metrics[agent.id]?.cost_usd || 0,
      color: agent.color,
    }));

  const durationData = agents.map(agent => ({
    name: agent.name.split(' ')[0],
    duration: (telemetry.agent_metrics[agent.id]?.duration_ms || 0) / 1000,
    color: agent.color,
  }));

  // Calculate progress percentage
  const progressPercent = (telemetry.agents_completed / telemetry.agents_total) * 100;

  return (
    <div className="glass-card-elevated rounded-2xl overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="p-5 border-b border-dark-500">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-accent-cyan to-accent-blue rounded-xl flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-text-primary">Live Telemetry</h3>
              <p className="text-xs text-text-muted">Real-time metrics</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-success/20 rounded-lg">
            <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
            <span className="text-xs font-medium text-success">Live</span>
          </div>
        </div>
      </div>

      <div className="p-5 space-y-6">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-text-secondary">Workflow Progress</span>
            <span className="text-text-primary font-medium">
              {telemetry.agents_completed}/{telemetry.agents_total} agents
            </span>
          </div>
          <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-accent-blue via-accent-indigo to-accent-purple rounded-full transition-all duration-500 relative"
              style={{ width: `${progressPercent}%` }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-data-flow" />
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 gap-3">
          {/* Total Tokens */}
          <div className="bg-dark-700/50 rounded-xl p-4 border border-dark-500 hover:border-accent-blue/30 transition-colors group">
            <div className="flex items-center gap-2 text-text-muted mb-2">
              <Hash className="w-4 h-4 text-accent-blue group-hover:scale-110 transition-transform" />
              <span className="text-xs font-medium">Total Tokens</span>
            </div>
            <div className="text-2xl font-bold text-text-primary">
              <AnimatedCounter value={telemetry.total_tokens} />
            </div>
            <div className="text-xs text-text-muted mt-1 flex items-center gap-2">
              <span className="text-accent-blue">{telemetry.total_input_tokens.toLocaleString()}</span>
              <span>/</span>
              <span className="text-accent-purple">{telemetry.total_output_tokens.toLocaleString()}</span>
            </div>
          </div>

          {/* Total Cost */}
          <div className="bg-dark-700/50 rounded-xl p-4 border border-dark-500 hover:border-success/30 transition-colors group">
            <div className="flex items-center gap-2 text-text-muted mb-2">
              <Coins className="w-4 h-4 text-success group-hover:scale-110 transition-transform" />
              <span className="text-xs font-medium">Total Cost</span>
            </div>
            <div className="text-2xl font-bold text-success">
              <AnimatedCounter value={telemetry.total_cost_usd} decimals={4} prefix="$" />
            </div>
            <div className="text-xs text-text-muted mt-1 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              <span>GPT-5-mini pricing</span>
            </div>
          </div>

          {/* Duration */}
          <div className="bg-dark-700/50 rounded-xl p-4 border border-dark-500 hover:border-accent-cyan/30 transition-colors group">
            <div className="flex items-center gap-2 text-text-muted mb-2">
              <Clock className="w-4 h-4 text-accent-cyan group-hover:scale-110 transition-transform" />
              <span className="text-xs font-medium">Duration</span>
            </div>
            <div className="text-2xl font-bold text-text-primary">
              <AnimatedCounter value={telemetry.total_duration_ms / 1000} decimals={1} suffix="s" />
            </div>
            <div className="text-xs text-text-muted mt-1">
              Execution time
            </div>
          </div>

          {/* Throughput */}
          <div className="bg-dark-700/50 rounded-xl p-4 border border-dark-500 hover:border-accent-purple/30 transition-colors group">
            <div className="flex items-center gap-2 text-text-muted mb-2">
              <Zap className="w-4 h-4 text-accent-purple group-hover:scale-110 transition-transform" />
              <span className="text-xs font-medium">Throughput</span>
            </div>
            <div className="text-2xl font-bold text-text-primary">
              <AnimatedCounter
                value={telemetry.total_duration_ms > 0
                  ? Math.round(telemetry.total_tokens / (telemetry.total_duration_ms / 1000))
                  : 0}
              />
            </div>
            <div className="text-xs text-text-muted mt-1">
              tokens/sec
            </div>
          </div>
        </div>

        {/* Token Distribution Chart */}
        <div className="bg-dark-700/30 rounded-xl p-4 border border-dark-500">
          <h4 className="text-sm font-medium text-text-secondary mb-4 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-accent-blue" />
            Token Distribution
          </h4>
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tokenData} layout="vertical">
                <XAxis
                  type="number"
                  tick={{ fontSize: 10, fill: '#64748b' }}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={{ stroke: '#334155' }}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fontSize: 10, fill: '#94a3b8' }}
                  width={60}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={false}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="input" stackId="a" fill="#3b82f6" name="Input" radius={[0, 0, 0, 0]} />
                <Bar dataKey="output" stackId="a" fill="#8b5cf6" name="Output" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-accent-blue" />
              <span className="text-xs text-text-muted">Input</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-accent-purple" />
              <span className="text-xs text-text-muted">Output</span>
            </div>
          </div>
        </div>

        {/* Cost Breakdown */}
        {costData.length > 0 && (
          <div className="bg-dark-700/30 rounded-xl p-4 border border-dark-500">
            <h4 className="text-sm font-medium text-text-secondary mb-4 flex items-center gap-2">
              <Coins className="w-4 h-4 text-success" />
              Cost by Agent
            </h4>
            <div className="h-32 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={costData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={35}
                    outerRadius={55}
                    paddingAngle={3}
                    strokeWidth={0}
                  >
                    {costData.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="glass-card-elevated px-3 py-2 rounded-lg text-xs">
                            <p className="text-text-primary font-medium">{payload[0].name}</p>
                            <p className="text-success">${(payload[0].value as number).toFixed(4)}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap justify-center gap-3 mt-3">
              {costData.map((item, index) => (
                <div key={index} className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-xs text-text-muted">{item.name.split(' ')[0]}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Duration Chart */}
        <div className="bg-dark-700/30 rounded-xl p-4 border border-dark-500">
          <h4 className="text-sm font-medium text-text-secondary mb-4 flex items-center gap-2">
            <Clock className="w-4 h-4 text-accent-cyan" />
            Execution Timeline
          </h4>
          <div className="h-24">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={durationData}>
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 10, fill: '#94a3b8' }}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: '#64748b' }}
                  width={30}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={{ stroke: '#334155' }}
                />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="glass-card-elevated px-3 py-2 rounded-lg text-xs">
                          <p className="text-text-primary font-medium">{label}</p>
                          <p className="text-accent-cyan">{(payload[0].value as number).toFixed(2)}s</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="duration" radius={[4, 4, 0, 0]}>
                  {durationData.map((entry, index) => (
                    <Cell key={index} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* OpenTelemetry Footer */}
        <div className="flex items-center justify-center gap-3 pt-4 border-t border-dark-500">
          <span className="text-xs text-text-muted">Powered by</span>
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-gradient-to-br from-accent-blue to-accent-indigo rounded flex items-center justify-center">
              <Activity className="w-3 h-3 text-white" />
            </div>
            <span className="text-xs font-medium text-accent-blue">OpenTelemetry</span>
          </div>
          <span className="text-xs text-text-muted">+</span>
          <span className="text-xs font-medium text-accent-purple">Application Insights</span>
        </div>
      </div>
    </div>
  );
}
