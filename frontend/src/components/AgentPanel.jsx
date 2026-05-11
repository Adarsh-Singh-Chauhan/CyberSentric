import { Shield, Brain, Zap, MonitorDot, Swords } from 'lucide-react';

const AGENT_CONFIG = {
  Defender: { icon: Shield, color: 'cyan', gradient: 'from-cyan-500 to-blue-500' },
  Analyzer: { icon: Brain, color: 'purple', gradient: 'from-purple-500 to-pink-500' },
  Response: { icon: Zap, color: 'orange', gradient: 'from-orange-500 to-red-500' },
  Monitor: { icon: MonitorDot, color: 'green', gradient: 'from-green-500 to-emerald-500' },
  RedTeam: { icon: Swords, color: 'red', gradient: 'from-red-500 to-rose-500' },
};

const STATUS_COLORS = {
  idle: 'bg-emerald-400',
  processing: 'bg-blue-400 animate-pulse',
  alert: 'bg-red-400 animate-pulse',
  error: 'bg-yellow-400',
};

export default function AgentPanel({ agents = [] }) {
  return (
    <div className="glass rounded-xl p-5">
      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">Agent Activity</h3>
      <div className="space-y-3">
        {agents.map(agent => {
          const config = AGENT_CONFIG[agent.name] || AGENT_CONFIG.Defender;
          const Icon = config.icon;
          return (
            <div key={agent.name}
              className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.02] border border-transparent hover:border-white/5 transition-all group">
              <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${config.gradient} flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform`}>
                <Icon className="w-4.5 h-4.5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-200">{agent.name}</span>
                  <div className={`pulse-dot ${STATUS_COLORS[agent.status] || STATUS_COLORS.idle}`} />
                </div>
                <div className="flex items-center gap-3 mt-0.5">
                  <span className="text-[10px] font-mono text-slate-500">Processed: {agent.processed_count}</span>
                  <span className="text-[10px] font-mono text-slate-500">Threats: {agent.threats_detected}</span>
                </div>
              </div>
              <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded-full ${
                agent.status === 'alert' ? 'bg-red-500/20 text-red-400' :
                agent.status === 'processing' ? 'bg-blue-500/20 text-blue-400' :
                'bg-green-500/20 text-green-400'
              }`}>{agent.status}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
