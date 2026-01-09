import { useState } from 'react';
import { Play, Calendar, MapPin, Sparkles, Zap, Brain, Database, FileSearch, ClipboardList, Calculator, TrendingUp, Clock, DollarSign, Users } from 'lucide-react';
import type { StartWorkflowRequest } from '../types';

interface StartFormProps {
  onStart: (request: StartWorkflowRequest) => void;
  isLoading: boolean;
}

const AGENT_ICONS = {
  'Data Analyst': Database,
  'Capacity Calculator': Calculator,
  'Document Researcher': FileSearch,
  'Planner': ClipboardList,
};

// Business value metrics from historical data
const BUSINESS_METRICS = [
  {
    icon: DollarSign,
    value: '$2.3M',
    label: 'Route Optimization Savings',
    color: 'text-success',
  },
  {
    icon: TrendingUp,
    value: '12%',
    label: 'Crew Efficiency Gains',
    color: 'text-accent-blue',
  },
  {
    icon: Clock,
    value: 'Minutes',
    label: 'vs Days for Planning',
    color: 'text-accent-purple',
  },
  {
    icon: Users,
    value: '22%',
    label: 'Reduced Overtime Costs',
    color: 'text-accent-cyan',
  },
];

export default function StartForm({ onStart, isLoading }: StartFormProps) {
  const [dateFrom, setDateFrom] = useState('2026-01-01');
  const [dateTo, setDateTo] = useState('2026-01-31');
  const [hub, setHub] = useState('Seattle');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onStart({
      date_from: dateFrom,
      date_to: dateTo,
      hub,
      demo_mode: true,
    });
  };

  const agents = [
    { name: 'Data Analyst', tool: 'MCP Protocol', color: '#3b82f6', description: 'Query shipment data' },
    { name: 'Capacity Calculator', tool: 'Code Interpreter', color: '#10b981', description: 'Python calculations' },
    { name: 'Document Researcher', tool: 'File Search', color: '#8b5cf6', description: 'Policy lookup' },
    { name: 'Planner', tool: 'Synthesis', color: '#f59e0b', description: 'Create plan' },
  ];

  return (
    <div className="w-full max-w-4xl">
      {/* Business Value Section - "Slide 1" */}
      <div className="glass-card rounded-2xl p-6 mb-40 animate-fade-in border-accent-blue/20">
        <div className="flex items-start gap-4 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-accent-blue to-accent-indigo rounded-xl flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-text-primary mb-1">The Business Challenge</h2>
            <p className="text-text-secondary leading-relaxed">
              Manual capacity planning costs logistics companies <span className="text-success font-semibold">millions in lost efficiency</span>.
              Traditional analysis takes <span className="text-accent-purple font-semibold">days of manual work</span>, leading to
              suboptimal aircraft assignments, crew scheduling conflicts, and <span className="text-warning font-semibold">$450K+ in missed opportunities</span> during peak seasons.
            </p>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-4 gap-4">
          {BUSINESS_METRICS.map((metric) => {
            const Icon = metric.icon;
            return (
              <div key={metric.label} className="bg-dark-700/50 rounded-xl p-4 border border-dark-500 text-center group hover:border-dark-400 transition-colors">
                <div className="flex justify-center mb-2">
                  <Icon className={`w-5 h-5 ${metric.color} group-hover:scale-110 transition-transform`} />
                </div>
                <div className={`text-2xl font-bold ${metric.color}`}>{metric.value}</div>
                <div className="text-xs text-text-muted mt-1">{metric.label}</div>
              </div>
            );
          })}
        </div>

        <div className="mt-4 pt-4 border-t border-dark-500">
          <p className="text-sm text-text-secondary text-center">
            <span className="text-accent-cyan font-medium">AI-powered capacity planning</span> delivers optimized recommendations in minutes,
            enabling faster decisions and <span className="text-success font-medium">significant cost savings</span>.
          </p>
        </div>
      </div>

      {/* Hero Section - "Slide 2" */}
      <div className="text-center mb-20 animate-fade-in">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-5 py-2.5 glass-card rounded-full mb-6">
          <Sparkles className="w-4 h-4 text-accent-cyan" />
          <span className="text-sm font-medium text-text-secondary">Powered by Microsoft Foundry Agents</span>
        </div>

        {/* Title */}
        <h1 className="text-5xl md:text-6xl font-bold mb-4">
          <span className="text-text-primary">AI-Powered </span>
          <span className="gradient-text">Capacity Planning</span>
        </h1>

        {/* Subtitle */}
        <p className="text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed">
          Watch four AI agents collaborate in real-time to analyze shipments,
          calculate capacity, and create an optimized logistics plan.
        </p>
      </div>

      {/* Agent Pipeline Preview - "Slide 3" */}
      <div className="mb-28 animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <div className="flex items-center justify-center gap-2">
          {agents.map((agent, index) => {
            const Icon = AGENT_ICONS[agent.name as keyof typeof AGENT_ICONS];
            return (
              <div key={agent.name} className="flex items-center">
                <div className="group relative">
                  <div
                    className="w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300 group-hover:scale-110"
                    style={{
                      background: `linear-gradient(135deg, ${agent.color}20, ${agent.color}10)`,
                      border: `1px solid ${agent.color}40`,
                    }}
                  >
                    <Icon className="w-7 h-7" style={{ color: agent.color }} />
                  </div>
                  {/* Tooltip */}
                  <div className="absolute -bottom-16 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
                    <div className="glass-card-elevated px-3 py-2 rounded-lg whitespace-nowrap">
                      <div className="text-xs font-semibold text-text-primary">{agent.name}</div>
                      <div className="text-xs text-text-muted">{agent.tool}</div>
                    </div>
                  </div>
                </div>
                {index < agents.length - 1 && (
                  <div className="w-12 h-0.5 mx-1 bg-gradient-to-r from-dark-500 to-dark-500 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-accent-blue to-accent-purple opacity-50" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Form Card - "Slide 4" */}
      <div className="glass-card-elevated rounded-3xl p-8 animate-slide-up" style={{ animationDelay: '0.3s' }}>
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-gradient-to-br from-accent-blue to-accent-indigo rounded-xl flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-text-primary">Configure Workflow</h2>
            <p className="text-sm text-text-muted">Set parameters for capacity analysis</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Date Range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-text-secondary mb-2">
                <Calendar className="w-4 h-4 text-accent-blue" />
                Start Date
              </label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full px-4 py-3.5 bg-dark-700 border border-dark-500 rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-indigo focus:border-transparent transition-all"
              />
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-text-secondary mb-2">
                <Calendar className="w-4 h-4 text-accent-blue" />
                End Date
              </label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full px-4 py-3.5 bg-dark-700 border border-dark-500 rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-indigo focus:border-transparent transition-all"
              />
            </div>
          </div>

          {/* Hub Selection */}
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-text-secondary mb-2">
              <MapPin className="w-4 h-4 text-accent-purple" />
              Hub Location
            </label>
            <select
              value={hub}
              onChange={(e) => setHub(e.target.value)}
              className="w-full px-4 py-3.5 bg-dark-700 border border-dark-500 rounded-xl text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-indigo focus:border-transparent transition-all appearance-none cursor-pointer"
            >
              <option value="Seattle">Seattle (SEA) - Primary Hub</option>
              <option value="Chicago">Chicago (ORD)</option>
              <option value="Los Angeles">Los Angeles (LAX)</option>
              <option value="New York">New York (JFK)</option>
            </select>
          </div>

          {/* Agent Cards Grid */}
          <div className="bg-dark-800 rounded-2xl p-5 border border-dark-500">
            <h3 className="text-sm font-medium text-text-secondary mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-accent-cyan" />
              Agents in this workflow
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {agents.map((agent) => {
                const Icon = AGENT_ICONS[agent.name as keyof typeof AGENT_ICONS];
                return (
                  <div
                    key={agent.name}
                    className="flex items-center gap-3 bg-dark-700/50 rounded-xl px-4 py-3 border border-dark-500 hover:border-dark-400 transition-all group"
                  >
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110"
                      style={{ background: `${agent.color}20` }}
                    >
                      <Icon className="w-5 h-5" style={{ color: agent.color }} />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-text-primary">{agent.name}</div>
                      <div className="text-xs text-text-muted">{agent.description}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="btn-glow w-full flex items-center justify-center gap-3 bg-gradient-to-r from-accent-blue via-accent-indigo to-accent-purple text-white py-4 rounded-xl font-semibold text-lg shadow-glow-purple hover:shadow-glow-blue transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Initializing Agents...</span>
              </>
            ) : (
              <>
                <Play className="w-6 h-6" />
                <span>Start Capacity Planning</span>
              </>
            )}
          </button>
        </form>

        {/* Info */}
        <p className="text-center text-sm text-text-muted mt-6">
          This workflow will analyze ~500 shipments and create a comprehensive capacity plan
        </p>
      </div>
    </div>
  );
}
