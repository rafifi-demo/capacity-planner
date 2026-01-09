import { Database, Calculator, FileSearch, ClipboardList, CheckCircle2, Loader2, ArrowRight, Zap } from 'lucide-react';
import type { AgentInfo, AgentUpdate, AgentStatus } from '../types';
import AgentCard from './AgentCard';

interface WorkflowViewerProps {
  agents: AgentInfo[];
  agentUpdates: Record<string, AgentUpdate>;
  status: string;
}

const ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  database: Database,
  calculator: Calculator,
  'file-search': FileSearch,
  'clipboard-list': ClipboardList,
};

export default function WorkflowViewer({ agents, agentUpdates, status }: WorkflowViewerProps) {
  return (
    <div className="space-y-6">
      {/* Pipeline Header */}
      <div className="glass-card rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-accent-indigo to-accent-purple rounded-xl flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-text-primary">Agent Pipeline</h2>
              <p className="text-sm text-text-muted">Sequential execution with human-in-the-loop</p>
            </div>
          </div>
        </div>

        {/* Visual Pipeline */}
        <div className="flex items-center justify-between px-4">
          {agents.map((agent, index) => {
            const update = agentUpdates[agent.id];
            const agentStatus = update?.status || 'pending';
            const Icon = ICONS[agent.icon] || Database;

            return (
              <div key={agent.id} className="flex items-center">
                {/* Agent Node */}
                <div className="flex flex-col items-center">
                  <div className="relative">
                    {/* Glow ring for running agent */}
                    {agentStatus === 'running' && (
                      <div
                        className="absolute inset-0 rounded-2xl animate-pulse-ring"
                        style={{ background: agent.color, opacity: 0.3 }}
                      />
                    )}

                    {/* Agent icon container */}
                    <div
                      className={`relative w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-500 ${
                        agentStatus === 'completed'
                          ? 'shadow-glow-success'
                          : agentStatus === 'running'
                          ? 'shadow-glow-purple agent-running'
                          : ''
                      }`}
                      style={{
                        background:
                          agentStatus === 'completed'
                            ? 'linear-gradient(135deg, #10b981, #059669)'
                            : agentStatus === 'running'
                            ? `linear-gradient(135deg, ${agent.color}, ${agent.color}cc)`
                            : 'rgba(45, 45, 70, 0.8)',
                        border:
                          agentStatus === 'pending'
                            ? '1px solid rgba(255,255,255,0.1)'
                            : 'none',
                      }}
                    >
                      {agentStatus === 'completed' ? (
                        <CheckCircle2 className="w-7 h-7 text-white" />
                      ) : agentStatus === 'running' ? (
                        <Loader2 className="w-7 h-7 text-white animate-spin" />
                      ) : (
                        <Icon className="w-7 h-7 text-text-muted" />
                      )}
                    </div>
                  </div>

                  {/* Agent label */}
                  <div className="mt-3 text-center">
                    <div className={`text-xs font-medium ${
                      agentStatus === 'completed'
                        ? 'text-success'
                        : agentStatus === 'running'
                        ? 'text-accent-indigo'
                        : 'text-text-muted'
                    }`}>
                      {agent.name.split(' ')[0]}
                    </div>
                    <div className="text-[10px] text-text-muted">
                      {agent.name.split(' ').slice(1).join(' ')}
                    </div>
                  </div>
                </div>

                {/* Connector */}
                {index < agents.length - 1 && (
                  <div className="flex items-center mx-4 mb-8">
                    <div
                      className={`w-16 h-1 rounded-full relative overflow-hidden ${
                        agentStatus === 'completed'
                          ? 'bg-gradient-to-r from-success to-success/50'
                          : 'bg-dark-500'
                      }`}
                    >
                      {agentStatus === 'running' && (
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-accent-indigo to-transparent animate-data-flow" />
                      )}
                    </div>
                    <ArrowRight
                      className={`w-4 h-4 -ml-1 ${
                        agentStatus === 'completed' ? 'text-success' : 'text-dark-400'
                      }`}
                    />
                  </div>
                )}
              </div>
            );
          })}

          {/* Human Approval Node */}
          {status === 'awaiting_approval' && (
            <>
              <div className="flex items-center mx-4 mb-8">
                <div className="w-16 h-1 rounded-full bg-gradient-to-r from-success to-warning" />
                <ArrowRight className="w-4 h-4 -ml-1 text-warning" />
              </div>
              <div className="flex flex-col items-center">
                <div className="relative">
                  <div className="absolute inset-0 rounded-2xl bg-warning opacity-30 animate-pulse" />
                  <div className="relative w-16 h-16 rounded-2xl bg-gradient-to-br from-warning to-orange-500 flex items-center justify-center shadow-glow-warning">
                    <span className="text-2xl">👤</span>
                  </div>
                </div>
                <div className="mt-3 text-center">
                  <div className="text-xs font-medium text-warning">Human</div>
                  <div className="text-[10px] text-text-muted">Approval</div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Agent Cards */}
      <div className="space-y-4">
        {agents.map((agent, index) => {
          const update = agentUpdates[agent.id];
          const Icon = ICONS[agent.icon] || Database;
          const agentStatus: AgentStatus = update?.status || 'pending';

          const isActive = agentStatus === 'running';
          const isCompleted = agentStatus === 'completed';
          const isPending = agentStatus === 'pending';

          return (
            <div
              key={agent.id}
              className={`transition-all duration-500 ${
                isPending ? 'opacity-40' : 'opacity-100'
              }`}
              style={{
                animationDelay: `${index * 0.1}s`,
              }}
            >
              <AgentCard
                agent={agent}
                update={update}
                icon={<Icon className="w-5 h-5" />}
                status={agentStatus}
                index={index}
                isExpanded={isActive || isCompleted}
              />
            </div>
          );
        })}
      </div>

      {/* Human in the Loop Indicator */}
      {status === 'awaiting_approval' && (
        <div className="glass-card-elevated border-warning/30 rounded-2xl p-6 animate-slide-up approval-glow">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-warning to-orange-500 rounded-2xl flex items-center justify-center">
              <span className="text-2xl">👤</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                Human Approval Required
              </h3>
              <p className="text-sm text-text-secondary">
                Review the capacity plan and approve or reject the proposed actions
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {status === 'completed' && (
        <div className="glass-card-elevated border-success/30 rounded-2xl p-6 animate-slide-up glow-success">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-success to-emerald-400 rounded-2xl flex items-center justify-center">
              <CheckCircle2 className="w-7 h-7 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-text-primary">
                Workflow Complete
              </h3>
              <p className="text-sm text-text-secondary">
                All agents have completed their tasks. The capacity plan has been processed.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
