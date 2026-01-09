import { useState, useCallback, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import Header from './components/Header';
import WorkflowViewer from './components/WorkflowViewer';
import TelemetryPanel from './components/TelemetryPanel';
import ApprovalPanel from './components/ApprovalPanel';
import StartForm from './components/StartForm';
import Confetti from './components/Confetti';
import ResultsDashboard from './components/ResultsDashboard';
import type { StartWorkflowRequest, AgentInfo } from './types';

const API_URL = import.meta.env.VITE_API_URL || '';

// Agent definitions for display
const AGENTS: AgentInfo[] = [
  {
    id: 'data_analyst',
    name: 'Data Analyst',
    description: 'Queries shipment data from PostgreSQL via MCP',
    tool: 'MCP (Model Context Protocol)',
    icon: 'database',
    color: '#3b82f6',
  },
  {
    id: 'capacity_calc',
    name: 'Capacity Calculator',
    description: 'Performs Python calculations for logistics planning',
    tool: 'Code Interpreter',
    icon: 'calculator',
    color: '#10b981',
  },
  {
    id: 'doc_researcher',
    name: 'Document Researcher',
    description: 'Searches policy documents and regulations',
    tool: 'File Search',
    icon: 'file-search',
    color: '#8b5cf6',
  },
  {
    id: 'planner',
    name: 'Planner',
    description: 'Synthesizes data into comprehensive capacity plan',
    tool: 'Synthesis',
    icon: 'clipboard-list',
    color: '#f59e0b',
  },
];

function App() {
  const { state, connect, approve, reject, reset } = useWebSocket();
  const [showTelemetry, setShowTelemetry] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [resultsMinimized, setResultsMinimized] = useState(false);

  // Trigger confetti and results dashboard on completion
  useEffect(() => {
    if (state.status === 'completed') {
      setShowConfetti(true);
      setShowResults(true);
      setResultsMinimized(false); // Start expanded
      const confettiTimer = setTimeout(() => setShowConfetti(false), 5000);
      return () => clearTimeout(confettiTimer);
    }
  }, [state.status]);

  const handleStart = useCallback(async (request: StartWorkflowRequest) => {
    setIsStarting(true);
    setShowResults(false); // Reset results when starting new workflow
    try {
      const response = await fetch(`${API_URL}/api/workflow/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error('Failed to start workflow');
      }

      const data = await response.json();
      console.log('Workflow started:', data);
      connect(data.session_id);
    } catch (error) {
      console.error('Error starting workflow:', error);
      alert('Failed to start workflow. Please try again.');
    } finally {
      setIsStarting(false);
    }
  }, [connect]);

  const handleApprove = useCallback(async () => {
    if (state.sessionId) {
      await fetch(`${API_URL}/api/workflow/${state.sessionId}/approve`, {
        method: 'POST',
      });
      approve();
    }
  }, [state.sessionId, approve]);

  const handleReject = useCallback(async () => {
    if (state.sessionId) {
      // Send reject via WebSocket - this triggers workflow re-run on backend
      reject();
    }
  }, [state.sessionId, reject]);

  const handleReset = useCallback(() => {
    setShowResults(false);
    reset();
  }, [reset]);

  const isIdle = state.status === 'idle';
  const showApproval = state.status === 'awaiting_approval' && state.approvalRequest;

  return (
    <div className="min-h-screen bg-dark-900 bg-grid bg-gradient-dark relative overflow-hidden">
      {/* Floating particles */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${100 + Math.random() * 20}%`,
              animationDelay: `${Math.random() * 15}s`,
              animationDuration: `${15 + Math.random() * 10}s`,
            }}
          />
        ))}
      </div>

      {/* Confetti celebration */}
      {showConfetti && <Confetti />}

      {/* Results Dashboard (shows after approval) */}
      <ResultsDashboard
        isVisible={showResults}
        isMinimized={resultsMinimized}
        onMinimizedChange={setResultsMinimized}
      />

      {/* Header */}
      <Header
        showTelemetry={showTelemetry}
        onToggleTelemetry={() => setShowTelemetry(!showTelemetry)}
        status={state.status}
        onReset={handleReset}
      />

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 relative z-10">
        {isIdle ? (
          /* Start Form */
          <div className="flex justify-center pt-8">
            <StartForm onStart={handleStart} isLoading={isStarting} />
          </div>
        ) : (
          /* Workflow View */
          <div className={`flex gap-6 transition-opacity duration-500 ${showResults && !resultsMinimized ? 'opacity-30 pointer-events-none' : 'opacity-100'}`}>
            {/* Left: Workflow Viewer */}
            <div className={`flex-1 ${showApproval ? 'max-w-4xl' : ''}`}>
              <WorkflowViewer
                agents={AGENTS}
                agentUpdates={state.agents}
                status={state.status}
              />
            </div>

            {/* Right: Telemetry or Approval Panel */}
            <div className={`w-[420px] flex-shrink-0 space-y-4 transition-all duration-500 ${showTelemetry || showApproval ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-10 w-0 overflow-hidden'}`}>
              {/* Telemetry Panel */}
              {showTelemetry && state.telemetry && (
                <TelemetryPanel
                  telemetry={state.telemetry}
                  agents={AGENTS}
                />
              )}

              {/* Approval Panel */}
              {showApproval && (
                <ApprovalPanel
                  request={state.approvalRequest!}
                  onApprove={handleApprove}
                  onReject={handleReject}
                />
              )}
            </div>
          </div>
        )}

        {/* Error Display */}
        {state.error && (
          <div className="fixed bottom-4 right-4 glass-card border-error/50 px-6 py-4 rounded-xl animate-slide-up flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-error animate-pulse" />
            <span className="text-text-primary">{state.error}</span>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 glass-card border-t border-dark-500 py-3 px-4 z-20">
        <div className="container mx-auto flex items-center justify-between text-sm">
          <div className="flex items-center gap-3">
            <span className="text-text-muted">Powered by</span>
            <span className="gradient-text font-semibold">Microsoft Foundry Agents</span>
          </div>
          <div className="flex items-center gap-4">
            {state.sessionId && (
              <span className="font-mono text-xs bg-dark-600 text-text-secondary px-3 py-1.5 rounded-lg border border-dark-500">
                Session: {state.sessionId.slice(0, 8)}...
              </span>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
