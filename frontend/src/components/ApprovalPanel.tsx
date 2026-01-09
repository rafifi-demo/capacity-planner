import { useState } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Plane, Users, Shield, ArrowRight, MessageSquare, RefreshCw, X } from 'lucide-react';
import type { ApprovalRequest } from '../types';

interface ApprovalPanelProps {
  request: ApprovalRequest;
  onApprove: () => void;
  onReject: () => void;
}

export default function ApprovalPanel({ request, onApprove, onReject }: ApprovalPanelProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleApprove = async () => {
    setIsProcessing(true);
    await onApprove();
  };

  const handleRejectClick = () => {
    setShowRejectModal(true);
  };

  const handleRejectSubmit = async () => {
    setIsProcessing(true);
    setShowRejectModal(false);
    await onReject();
  };

  const handleRejectCancel = () => {
    setShowRejectModal(false);
    setFeedback('');
  };

  return (
    <div className="glass-card-elevated border-warning/40 rounded-2xl overflow-hidden animate-slide-up approval-glow">
      {/* Header */}
      <div className="bg-gradient-to-r from-warning/20 to-orange-500/20 p-5 border-b border-warning/30">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="w-14 h-14 bg-gradient-to-br from-warning to-orange-500 rounded-2xl flex items-center justify-center shadow-glow-warning">
              <Shield className="w-7 h-7 text-white" />
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-warning rounded-full flex items-center justify-center animate-pulse">
              <AlertTriangle className="w-2.5 h-2.5 text-white" />
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text-primary">Human Approval Required</h3>
            <p className="text-sm text-text-secondary">Review the capacity plan before execution</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-5 space-y-5 max-h-[500px] overflow-y-auto">
        {/* Summary */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-text-secondary flex items-center gap-2">
            <ArrowRight className="w-4 h-4 text-accent-blue" />
            Plan Summary
          </h4>
          <div className="bg-dark-700 rounded-xl p-4 border border-dark-500">
            <p className="text-sm text-text-secondary leading-relaxed">
              {request.plan_summary.slice(0, 300)}...
            </p>
          </div>
        </div>

        {/* Key Impact Summary */}
        <div className="bg-gradient-to-r from-success/10 via-accent-blue/10 to-accent-purple/10 rounded-xl p-4 border border-success/30">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-xl font-bold text-success">12.5%</div>
              <div className="text-xs text-text-muted">Fuel Savings</div>
            </div>
            <div className="text-center border-x border-dark-500">
              <div className="text-xl font-bold text-accent-blue">Zero</div>
              <div className="text-xs text-text-muted">Overtime Hours</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-accent-purple">100%</div>
              <div className="text-xs text-text-muted">On-Time Delivery</div>
            </div>
          </div>
        </div>

        {/* Aircraft Assignments */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-text-secondary flex items-center gap-2">
            <Plane className="w-4 h-4 text-accent-blue" />
            Aircraft Assignments
          </h4>
          <div className="space-y-2">
            {request.aircraft_assignments.map((assignment, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-dark-700 rounded-xl px-4 py-3 border border-dark-500 hover:border-accent-blue/30 transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-accent-blue/20 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Plane className="w-4 h-4 text-accent-blue" />
                  </div>
                  <span className="font-medium text-text-primary">{assignment.route}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-text-secondary">{assignment.aircraft}</span>
                  <span className="px-2.5 py-1 bg-accent-blue/20 text-accent-blue rounded-lg text-xs font-medium">
                    {assignment.cargo_kg.toLocaleString()} kg
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Crew Assignments */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-text-secondary flex items-center gap-2">
            <Users className="w-4 h-4 text-accent-purple" />
            Crew Assignments
          </h4>
          <div className="space-y-2">
            {request.crew_assignments.map((assignment, index) => (
              <div
                key={index}
                className="bg-dark-700 rounded-xl px-4 py-3 border border-dark-500 hover:border-accent-purple/30 transition-colors group"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-8 h-8 bg-accent-purple/20 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Users className="w-4 h-4 text-accent-purple" />
                  </div>
                  <span className="font-medium text-text-primary">{assignment.flight}</span>
                </div>
                <div className="ml-11 flex flex-wrap gap-2">
                  <span className="px-2 py-1 bg-dark-600 rounded-lg text-xs text-text-secondary">
                    Capt. {assignment.captain}
                  </span>
                  <span className="px-2 py-1 bg-dark-600 rounded-lg text-xs text-text-secondary">
                    FO {assignment.first_officer}
                  </span>
                  {assignment.flight_engineer && (
                    <span className="px-2 py-1 bg-dark-600 rounded-lg text-xs text-text-secondary">
                      FE {assignment.flight_engineer}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Proposed Actions */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-text-secondary flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-accent-cyan" />
            Actions to Execute
          </h4>
          <div className="space-y-2">
            {request.proposed_actions.map((action, index) => (
              <div
                key={index}
                className="bg-dark-700 rounded-xl p-4 border border-dark-500 hover:border-accent-cyan/30 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 bg-accent-cyan/20 rounded flex items-center justify-center">
                        <span className="text-xs font-bold text-accent-cyan">{index + 1}</span>
                      </div>
                      <span className="font-medium text-text-primary">{action.action}</span>
                    </div>
                    <p className="text-sm text-text-secondary mt-1.5 ml-8">{action.description}</p>
                  </div>
                  {action.estimated_cost > 0 && (
                    <span className="text-sm font-bold text-success ml-4">
                      ${action.estimated_cost.toLocaleString()}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="p-5 border-t border-dark-500 bg-dark-800/50">
        <div className="flex gap-3">
          <button
            onClick={handleRejectClick}
            disabled={isProcessing}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-3.5 glass-card border-error/30 text-error rounded-xl hover:bg-error/10 hover:border-error/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            <XCircle className="w-5 h-5 group-hover:scale-110 transition-transform" />
            <span className="font-semibold">Reject</span>
          </button>
          <button
            onClick={handleApprove}
            disabled={isProcessing}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-3.5 bg-gradient-to-r from-success to-emerald-500 text-white rounded-xl hover:shadow-glow-success transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {isProcessing ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <CheckCircle className="w-5 h-5 group-hover:scale-110 transition-transform" />
            )}
            <span className="font-semibold">Approve & Execute</span>
          </button>
        </div>
        <p className="text-center text-xs text-text-muted mt-4 flex items-center justify-center gap-2">
          <Shield className="w-3 h-3" />
          Approving will execute all proposed actions
        </p>
      </div>

      {/* Rejection Feedback Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-dark-900/80 backdrop-blur-sm"
            onClick={handleRejectCancel}
          />

          {/* Modal */}
          <div className="relative glass-card-elevated border-accent-purple/40 rounded-2xl w-full max-w-md overflow-hidden animate-slide-up">
            {/* Header */}
            <div className="bg-gradient-to-r from-accent-purple/20 to-accent-blue/20 p-5 border-b border-accent-purple/30">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-accent-purple to-accent-blue rounded-xl flex items-center justify-center">
                    <MessageSquare className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-text-primary">Provide Feedback</h3>
                    <p className="text-sm text-text-secondary">Help the AI improve</p>
                  </div>
                </div>
                <button
                  onClick={handleRejectCancel}
                  className="p-2 rounded-lg hover:bg-dark-600 transition-colors"
                >
                  <X className="w-5 h-5 text-text-muted" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-5 space-y-4">
              <div className="bg-dark-700/50 rounded-xl p-4 border border-dark-500">
                <div className="flex items-start gap-3">
                  <RefreshCw className="w-5 h-5 text-accent-cyan mt-0.5" />
                  <div>
                    <p className="text-sm text-text-primary font-medium">What happens next?</p>
                    <p className="text-sm text-text-secondary mt-1">
                      Your feedback will be sent to the AI agents. The workflow will re-run with your guidance to generate an improved capacity plan.
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-text-secondary mb-2 block">
                  What should be changed? (optional)
                </label>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="e.g., Reduce fuel costs, assign different aircraft to Tokyo route, avoid crew overtime..."
                  className="w-full h-28 px-4 py-3 bg-dark-700 border border-dark-500 rounded-xl text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-accent-purple focus:border-transparent resize-none"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="p-5 border-t border-dark-500 bg-dark-800/50 flex gap-3">
              <button
                onClick={handleRejectCancel}
                className="flex-1 px-4 py-3 glass-card border-dark-400 text-text-secondary rounded-xl hover:bg-dark-600 transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleRejectSubmit}
                disabled={isProcessing}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-accent-purple to-accent-blue text-white rounded-xl hover:shadow-glow-purple transition-all disabled:opacity-50"
              >
                <RefreshCw className="w-4 h-4" />
                <span className="font-semibold">Re-run Workflow</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
