import { ShieldAlert, ShieldCheck, AlertTriangle, Info } from 'lucide-react';

const SEVERITY_CONFIG = {
  critical: { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', icon: ShieldAlert, glow: 'glow-border-red' },
  high: { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', icon: AlertTriangle, glow: '' },
  medium: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400', icon: AlertTriangle, glow: '' },
  low: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400', icon: Info, glow: '' },
  none: { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400', icon: ShieldCheck, glow: 'glow-border-green' },
};

export default function RiskScore({ severity = 'none', confidence = 0, threats = 0 }) {
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.none;
  const Icon = config.icon;
  const pct = Math.round(confidence * 100);
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className={`glass rounded-xl p-5 ${config.glow} transition-all duration-500`}>
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Risk Level</h3>
      <div className="flex items-center gap-5">
        {/* Circular gauge */}
        <div className="relative w-24 h-24">
          <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(30,41,59,0.5)" strokeWidth="8" />
            <circle cx="50" cy="50" r="40" fill="none"
              stroke={severity === 'critical' ? '#ef4444' : severity === 'high' ? '#f97316' : severity === 'medium' ? '#eab308' : severity === 'low' ? '#3b82f6' : '#22c55e'}
              strokeWidth="8" strokeLinecap="round"
              strokeDasharray={circumference} strokeDashoffset={offset}
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-xl font-bold font-mono ${config.text}`}>{pct}%</span>
          </div>
        </div>
        <div className="flex-1">
          <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.border} border ${config.text} mb-2`}>
            <Icon className="w-3.5 h-3.5" />
            {severity.toUpperCase()}
          </div>
          <p className="text-sm text-slate-400 mt-1">
            {threats > 0 ? `${threats} active threat${threats > 1 ? 's' : ''} detected` : 'System secure. No active threats.'}
          </p>
        </div>
      </div>
    </div>
  );
}
