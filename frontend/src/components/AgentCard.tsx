import { useState, useEffect, useRef } from 'react';
import { ChevronDown, ChevronUp, Clock, Hash, Wrench, Terminal, FileText, Sparkles } from 'lucide-react';
import type { AgentInfo, AgentUpdate, AgentStatus } from '../types';

interface AgentCardProps {
  agent: AgentInfo;
  update?: AgentUpdate;
  icon: React.ReactNode;
  status: AgentStatus;
  index: number;
  isExpanded: boolean;
}

// Streaming text component
function StreamingText({ text, isStreaming }: { text: string; isStreaming: boolean }) {
  const [displayedText, setDisplayedText] = useState('');
  const indexRef = useRef(0);

  useEffect(() => {
    if (!isStreaming) {
      setDisplayedText(text);
      return;
    }

    setDisplayedText('');
    indexRef.current = 0;

    const interval = setInterval(() => {
      if (indexRef.current < text.length) {
        setDisplayedText(text.slice(0, indexRef.current + 1));
        indexRef.current++;
      } else {
        clearInterval(interval);
      }
    }, 5);

    return () => clearInterval(interval);
  }, [text, isStreaming]);

  return (
    <span>
      {displayedText}
      {isStreaming && indexRef.current < text.length && (
        <span className="typing-cursor" />
      )}
    </span>
  );
}

export default function AgentCard({ agent, update, icon, status, index, isExpanded: defaultExpanded }: AgentCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [isNewOutput, setIsNewOutput] = useState(false);

  useEffect(() => {
    setIsExpanded(defaultExpanded);
  }, [defaultExpanded]);

  useEffect(() => {
    if (update?.output_text) {
      setIsNewOutput(true);
      const timer = setTimeout(() => setIsNewOutput(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [update?.output_text]);

  const statusConfig = {
    pending: {
      bg: 'bg-dark-600',
      text: 'text-text-muted',
      border: 'border-dark-500',
      badge: 'bg-dark-500 text-text-muted',
    },
    running: {
      bg: 'bg-dark-700',
      text: 'text-accent-indigo',
      border: 'border-accent-indigo/50',
      badge: 'bg-accent-indigo/20 text-accent-indigo',
    },
    completed: {
      bg: 'bg-dark-700',
      text: 'text-success',
      border: 'border-success/30',
      badge: 'bg-success/20 text-success',
    },
    error: {
      bg: 'bg-dark-700',
      text: 'text-error',
      border: 'border-error/30',
      badge: 'bg-error/20 text-error',
    },
  };

  const config = statusConfig[status];

  return (
    <div
      className={`glass-card rounded-2xl overflow-hidden transition-all duration-500 ${config.border} ${
        status === 'running' ? 'agent-running shadow-glow-purple' : ''
      } ${status === 'completed' ? 'shadow-glow-success' : ''}`}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between p-5 cursor-pointer hover:bg-dark-600/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-4">
          {/* Agent Icon */}
          <div className="relative">
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-300"
              style={{
                background: status === 'pending' ? 'rgba(45, 45, 70, 0.8)' : `${agent.color}20`,
                border: status === 'pending' ? '1px solid rgba(255,255,255,0.1)' : `1px solid ${agent.color}40`,
              }}
            >
              <div style={{ color: status === 'pending' ? '#64748b' : agent.color }}>
                {icon}
              </div>
            </div>
            {status === 'running' && (
              <div className="absolute -top-1 -right-1">
                <div className="w-3 h-3 bg-accent-indigo rounded-full animate-pulse" />
              </div>
            )}
            {status === 'completed' && (
              <div className="absolute -top-1 -right-1">
                <div className="w-3 h-3 bg-success rounded-full" />
              </div>
            )}
          </div>

          {/* Agent Info */}
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-text-primary">{agent.name}</h3>
              <span className="text-xs text-text-muted">#{index + 1}</span>
            </div>
            <p className="text-sm text-text-secondary">{agent.description}</p>
          </div>
        </div>

        {/* Status & Metrics */}
        <div className="flex items-center gap-4">
          {/* Quick Metrics */}
          {update?.metrics && (
            <div className="hidden md:flex items-center gap-4 text-sm">
              <span className="flex items-center gap-1.5 text-text-secondary">
                <Hash className="w-3.5 h-3.5 text-accent-blue" />
                <span className="font-mono">
                  {(update.metrics.input_tokens + update.metrics.output_tokens).toLocaleString()}
                </span>
              </span>
              <span className="flex items-center gap-1.5 text-text-secondary">
                <Clock className="w-3.5 h-3.5 text-accent-purple" />
                <span className="font-mono">{(update.metrics.duration_ms / 1000).toFixed(1)}s</span>
              </span>
            </div>
          )}

          {/* Status Badge */}
          <span className={`status-badge ${config.badge}`}>
            {status}
          </span>

          {/* Expand Icon */}
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-text-muted" />
          ) : (
            <ChevronDown className="w-5 h-5 text-text-muted" />
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-dark-500 p-5 space-y-5 animate-slide-up">
          {/* Tool Badge */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-dark-600 rounded-lg">
              <Wrench className="w-4 h-4 text-accent-cyan" />
              <span className="text-sm font-medium text-text-secondary">{agent.tool}</span>
            </div>
            {update?.tool_use?.tools && update.tool_use.tools.length > 0 && (
              <span className="text-xs text-text-muted">
                {update.tool_use.tools.length} tool calls
              </span>
            )}
          </div>

          {/* Input */}
          {update?.input_text && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-text-secondary flex items-center gap-2">
                <Terminal className="w-4 h-4 text-accent-blue" />
                Input Prompt
              </h4>
              <div className="bg-dark-800 rounded-xl p-4 border border-dark-500">
                <p className="text-sm text-text-secondary leading-relaxed">
                  {update.input_text}
                </p>
              </div>
            </div>
          )}

          {/* Tool Execution */}
          {update?.tool_use && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-text-secondary flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-accent-purple" />
                Tool Execution
              </h4>
              <div className="bg-dark-800 rounded-xl p-4 border border-dark-500 space-y-3">
                {update.tool_use.tools && (
                  <div className="flex flex-wrap gap-2">
                    {update.tool_use.tools.map((tool, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 bg-accent-purple/20 text-accent-purple rounded-lg text-xs font-medium"
                      >
                        {tool}
                      </span>
                    ))}
                  </div>
                )}
                {update.tool_use.documents && (
                  <div className="flex items-center gap-2 text-xs text-text-muted">
                    <FileText className="w-3.5 h-3.5" />
                    <span>Searched: {update.tool_use.documents.join(', ')}</span>
                  </div>
                )}
                {update.tool_use.code_executed && (
                  <div className="flex items-center gap-2 text-xs text-success">
                    <div className="w-1.5 h-1.5 rounded-full bg-success" />
                    <span>Python code executed successfully</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Output */}
          {update?.output_text && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-text-secondary flex items-center gap-2">
                <FileText className="w-4 h-4 text-success" />
                Output
                {isNewOutput && status === 'running' && (
                  <span className="text-xs text-accent-indigo animate-pulse">Streaming...</span>
                )}
              </h4>
              <div className="bg-dark-800 rounded-xl p-4 border border-dark-500 max-h-80 overflow-y-auto">
                <pre className="text-sm text-text-secondary whitespace-pre-wrap font-mono leading-relaxed">
                  <StreamingText
                    text={update.output_text.slice(0, 2000) + (update.output_text.length > 2000 ? '...' : '')}
                    isStreaming={isNewOutput && status === 'running'}
                  />
                </pre>
              </div>
            </div>
          )}

          {/* Metrics Grid */}
          {update?.metrics && (
            <div className="grid grid-cols-4 gap-3 pt-3 border-t border-dark-500">
              {[
                { label: 'Input Tokens', value: update.metrics.input_tokens.toLocaleString(), color: 'text-accent-blue' },
                { label: 'Output Tokens', value: update.metrics.output_tokens.toLocaleString(), color: 'text-accent-purple' },
                { label: 'Duration', value: `${(update.metrics.duration_ms / 1000).toFixed(2)}s`, color: 'text-accent-cyan' },
                { label: 'Cost', value: `$${update.metrics.cost_usd.toFixed(4)}`, color: 'text-success' },
              ].map((metric) => (
                <div key={metric.label} className="text-center p-3 bg-dark-800 rounded-xl">
                  <div className={`text-lg font-bold font-mono ${metric.color}`}>
                    {metric.value}
                  </div>
                  <div className="text-xs text-text-muted mt-1">{metric.label}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
